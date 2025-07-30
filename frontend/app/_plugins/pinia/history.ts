/* eslint-disable @typescript-eslint/no-explicit-any */
import { defineStore } from "pinia";
import { useStorage } from "@vueuse/core";

export const useHistoryStore = defineStore("history", () => {
  const readings = useStorage<any[]>("history.readings", []);
  const events = useStorage<any[]>("history.events", []);

  function addReading(r: any) {
    readings.value.unshift(r);
    if (readings.value.length > 1000) readings.value.splice(1000); // limit
  }
  function clearReadings() {
    readings.value = [];
  }

  function addEvent(e: any) {
    events.value.unshift(e);
    if (events.value.length > 1000) events.value.splice(1000);
  }
  function clearEvents() {
    events.value = [];
  }

  return { readings, events, addReading, clearReadings, addEvent, clearEvents };
});
