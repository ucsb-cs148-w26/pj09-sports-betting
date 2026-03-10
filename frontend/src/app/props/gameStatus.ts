export type GamePhase = "live" | "pregame" | "final" | "unknown";

export function classifyGameStatus(status: string | undefined): GamePhase {
  const s = (status ?? "").trim().toLowerCase();
  if (!s) return "unknown";

  if (s.includes("final") || s.includes("game over") || s.includes("f/ot")) {
    return "final";
  }

  if (s.includes("pregame") || s.includes("scheduled")) {
    return "pregame";
  }

  const hasScheduledTime = /\b(am|pm)\b/.test(s);
  const hasUsTimezone = /\b(?:[ecmp](?:s|d)?t)\b/.test(s);

  if (hasScheduledTime && hasUsTimezone) {
    return "pregame";
  }

  return "live";
}
