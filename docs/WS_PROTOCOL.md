# WebSocket Protocol (Workspaces)

**URL**: `ws://<HOST>/ws/workspaces/{workspace_id}/`

This document describes the **message formats** and **semantics** for real‑time events in a workspace channel.

> In local dev, Nitro proxies `/ws/**` to the Django ASGI server, so the browser connects to `ws://localhost:3000/ws/...` and the proxy forwards to `:8000`.

---

## Authentication

In development, the workspace WS endpoint is typically open. For production you can add one of the following:

* **Query token**: `ws://<HOST>/ws/workspaces/{id}/?token=YOUR_TOKEN`
* **Subprotocol header**: `Sec-WebSocket-Protocol: Token <YOUR_TOKEN>` (requires a Channels middleware to validate)

If auth is enabled, the server MUST close the connection with an error code (e.g., 4401) on invalid/expired tokens.

---

## Message Types

Two primary message types are sent by the server. All messages are UTF‑8 JSON objects with a string `type`.

### 1) Reading

A single sensor sample.

```json
{
  "type": "reading",
  "sensor_id": 1,
  "value": 61.5,
  "unit": "°C",
  "ts": "2025-07-31T15:47:51Z"
}
```

**Fields**

* `sensor_id`*(number, required)* – ID of the sensor in the database.
* `value`*(number, required)* – Measured value.
* `unit`*(string, required)* – Unit for the value (e.g., `°C`, `A`, `mm/s`).
* `ts`*(ISO‑8601 string, optional)* – Server timestamp of the sample.

**Notes**

* The `unit` should match the `Sensor.unit` field; the frontend may override display based on metadata.
* The simulator typically emits 1–3 readings/sec depending on configuration.

### 2) Event

A threshold/diagnostic message associated with a workspace and optionally a sensor.

```json
{
  "type": "event",
  "level": "WARN",
  "sensor_id": 1,
  "message": "temperature threshold exceeded",
  "ts": "2025-07-31T15:47:52Z"
}
```

**Fields**

* `level`*(string, required)* – One of `INFO`, `WARN`, `CRIT`.
* `sensor_id`*(number, optional)* – If present, links to a specific sensor.
* `message`*(string, required)* – Human‑readable text.
* `ts`*(ISO‑8601 string, optional)* – Timestamp of the event.

**Notes**

* Clients should not rely on `sensor_id` being present for all events (workspace‑level notices may lack it).

---

## Client Behavior (Recommended)

* **Debounce UI updates** if you render charts; avoid reflow on each message.
* **Backoff reconnect** (e.g., 500ms → 1s → 2s → max 5s) on socket close.
* **Graceful degrade**: if WS is unavailable for > N seconds, poll `/api/workspaces/{id}/latest-readings/`.
* **Highlight thresholds**: compare incoming `value` against the sensor’s `threshold` (from REST metadata) and mark red when exceeded.

---

## Error Handling & Control Frames

The server may send control/info messages with a `type` other than the two above, for example:

```json
{ "type": "info", "message": "simulator_started" }
{ "type": "error", "message": "workspace_not_found" }
```

Clients SHOULD ignore unknown `type` values and MAY log them for diagnostics.

---

## Versioning

If the wire format changes, the server SHOULD include a `version` field in messages or expose a separate path `/ws/v2/workspaces/{id}/`. Clients SHOULD gate new behavior behind a version check.

---

## Examples

### Burst of readings

```json
{"type":"reading","sensor_id":2,"value":11.2,"unit":"A","ts":"2025-07-31T15:47:50Z"}
{"type":"reading","sensor_id":3,"value":4.8,"unit":"mm/s","ts":"2025-07-31T15:47:50Z"}
{"type":"reading","sensor_id":1,"value":74.1,"unit":"°C","ts":"2025-07-31T15:47:51Z"}
```

### Alert with no sensor context

```json
{"type":"event","level":"CRIT","message":"workspace overload","ts":"2025-07-31T15:47:55Z"}
```

---

## Test Checklist

* Connect to `ws://localhost:3000/ws/workspaces/1/` (via proxy).
* Ensure you receive both `reading` and `event` after hitting `POST /api/sim/start/1/`.
* Disconnect/reconnect path behaves with exponential backoff.
* With auth enabled, invalid token gets a clean close and no messages are delivered.
