// timeUtils.js
// Helper functions for the Weekly Calendar. Uses 60px per hour scale.

export const HOURS_START = 8; // 8:00
export const HOURS_END = 22; // 22:00
export const HOUR_HEIGHT_PX = 80; // 60px per hour

export function timeToMinutes(timeString) {
  // Expects "HH:MM"
  if (!timeString || typeof timeString !== "string") return 0;
  const [hh, mm] = timeString.split(":").map((n) => parseInt(n, 10));
  return hh * 60 + (Number.isFinite(mm) ? mm : 0);
}

export function minutesToPixels(minutesFromStart) {
  // 80px per hour => 1.333px per minute
  return (minutesFromStart * HOUR_HEIGHT_PX) / 60;
}

export function calculateEventPosition(start, end) {
  // Returns { top, height } in pixels within the day column
  const startMin = timeToMinutes(start);
  const endMin = timeToMinutes(end);
  const baseMin = HOURS_START * 60;
  const fromStart = Math.max(0, startMin - baseMin);
  const duration = Math.max(0, endMin - startMin);
  return {
    top: minutesToPixels(fromStart),
    height: minutesToPixels(duration),
  };
}

export function getHourLabels() {
  const labels = [];
  for (let h = HOURS_START; h <= HOURS_END; h++) {
    const label = `${String(h).padStart(2, "0")}:00`;
    labels.push(label);
  }
  return labels;
}

export function minutesToTimeString(totalMinutes) {
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(
    2,
    "0"
  )}`;
}
