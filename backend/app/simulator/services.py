from __future__ import annotations
import threading
import time
import math
import random
from typing import Dict, List
from django.conf import settings

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from core.models import Sensor, Event, Reading


def run_inline_cycles(workspace_id: int, cycles: int = 4) -> None:
    sensors = sensors_of_sync(workspace_id)
    if not sensors:
        return
    waves: Dict[int, WaveState] = {s["id"]: WaveState(s["kind"]) for s in sensors}
    for _ in range(cycles):
        for s in sensors:
            sid, unit, thr = s["id"], s["unit"], s.get("threshold")
            val = waves[sid].next()
            # (WS można pominąć w testach, ale jak chcesz – zostaw)
            async_to_sync(get_channel_layer().group_send)(
                f"ws_{workspace_id}",
                {
                    "type": "ws.message",
                    "data": {
                        "type": "reading",
                        "sensor_id": sid,
                        "value": val,
                        "unit": unit,
                    },
                },
            )
            if isinstance(thr, (int, float)) and val > thr:
                Event.objects.create(
                    workspace_id=workspace_id,
                    sensor_id=sid,
                    level="WARN",
                    message=f"{s['kind']} > {thr}",
                )
            Reading.objects.create(sensor_id=sid, value=val)


# ---- DB helpers (SYNC ORM) ----
def sensors_of_sync(workspace_id: int) -> List[dict]:
    return list(
        Sensor.objects.select_related("machine")
        .filter(machine__workspace_id=workspace_id)
        .values("id", "kind", "unit", "threshold")
    )


def params_for(kind: str) -> dict:
    k = (kind or "").lower()
    if "temp" in k:
        return {"base": 60.0, "amp": 8.0, "noise": 1.2, "spike": (0.03, 25.0)}
    if "vib" in k or "vibration" in k:
        return {"base": 3.0, "amp": 2.0, "noise": 0.6, "spike": (0.02, 6.0)}
    if "curr" in k or "amp" in k:
        return {"base": 8.0, "amp": 3.0, "noise": 0.8, "spike": (0.02, 5.0)}
    return {"base": 10.0, "amp": 4.0, "noise": 1.0, "spike": (0.02, 8.0)}


class WaveState:
    def __init__(self, kind: str):
        self.t = random.random() * math.tau
        self.p = params_for(kind)

    def next(self) -> float:
        self.t += 0.35
        val = (
            self.p["base"]
            + self.p["amp"] * math.sin(self.t)
            + random.gauss(0, self.p["noise"])
        )
        if random.random() < self.p["spike"][0]:
            val += self.p["spike"][1]
        return round(val, 2)


# ---- runner (SYNC, wątek) ----
def run_sync(workspace_id: int, stop_evt: threading.Event) -> None:
    layer = get_channel_layer()
    sensors = sensors_of_sync(workspace_id)
    if not sensors:
        return

    waves: Dict[int, WaveState] = {s["id"]: WaveState(s["kind"]) for s in sensors}

    while not stop_evt.is_set():
        for s in sensors:
            sid, unit, thr = s["id"], s["unit"], s.get("threshold")
            val = waves[sid].next()

            # push LIVE po WS (działa z InMemory i Redis)
            async_to_sync(layer.group_send)(
                f"ws_{workspace_id}",
                {
                    "type": "ws.message",
                    "data": {
                        "type": "reading",
                        "sensor_id": sid,
                        "value": val,
                        "unit": unit,
                    },
                },
            )

            if isinstance(thr, (int, float)) and val > thr:
                Event.objects.create(
                    workspace_id=workspace_id,
                    sensor_id=sid,
                    level="WARN",
                    message=f"{s['kind']} > {thr}",
                )
                async_to_sync(layer.group_send)(
                    f"ws_{workspace_id}",
                    {
                        "type": "ws.message",
                        "data": {
                            "type": "event",
                            "level": "WARN",
                            "sensor_id": sid,
                            "message": f"{s['kind']} alert",
                        },
                    },
                )

            Reading.objects.create(sensor_id=sid, value=val)

        time.sleep(0.5)


# ---- manager instancji (per-proces) ----
_threads: Dict[int, threading.Thread] = {}
_stops: Dict[int, threading.Event] = {}


def start_sim(workspace_id: int) -> bool:
    # ⬇️ TEST MODE – bez wątku
    if getattr(settings, "SIMULATOR_INLINE", False):
        run_inline_cycles(workspace_id, cycles=4)
        return True
    # ⬇️ normalny tryb wątku
    t = _threads.get(workspace_id)
    if t and t.is_alive():
        return False
    stop = threading.Event()
    _stops[workspace_id] = stop
    t = threading.Thread(target=run_sync, args=(workspace_id, stop), daemon=True)
    _threads[workspace_id] = t
    t.start()
    return True


from django.conf import settings


def stop_sim(workspace_id: int) -> bool:
    if getattr(settings, "SIMULATOR_INLINE", False):
        return True

    t = _threads.get(workspace_id)
    stop = _stops.get(workspace_id)
    if not t or not stop:
        return True
    stop.set()
    t.join(timeout=2)
    _threads.pop(workspace_id, None)
    _stops.pop(workspace_id, None)
    return True
