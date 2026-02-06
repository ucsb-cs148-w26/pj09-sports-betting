type Prop = {
  player: string;
  team: string;
  opponent: string;
  prop: { type: string; line: number; overUnder: string };
  hitChance: number; // 0..1
  game: { teamScore: number; oppScore: number; quarter: string; clock: string };
  current: { value: number; label: string };
};

function pct(n: number) {
  return Math.round(n * 100);
}

function chanceColor(p: number) {
  if (p >= 70) return "text-emerald-600 bg-emerald-50 border-emerald-200";
  if (p >= 30) return "text-amber-600 bg-amber-50 border-amber-200";
  return "text-rose-600 bg-rose-50 border-rose-200";
}

export default function PlayerPropCard({ data }: { data: Prop }) {
  const p = pct(data.hitChance);
  const badge = chanceColor(p);

  const needs = Math.max(0, Math.ceil(data.prop.line - data.current.value));
  const progressPct =
    data.prop.line > 0
      ? Math.min(100, (data.current.value / data.prop.line) * 100)
      : 0;

  return (
    <div className="w-full max-w-md rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-lg font-semibold leading-tight">
            {data.player}
          </div>
          <div className="mt-1 text-sm text-zinc-500">
            {data.team} vs {data.opponent}
          </div>
        </div>

        <div
          className={`rounded-full border px-3 py-1 text-sm font-semibold ${badge}`}
        >
          {p}% to hit
        </div>
      </div>

      {/* Prop Section */}
      <div className="mt-4 rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-3">
        <div className="flex items-center justify-between">
          <div className="text-sm text-zinc-500">Player Prop</div>
          <div className="text-base font-semibold">
            {data.prop.overUnder} {data.prop.line} {data.prop.type}
          </div>
        </div>

        {/* Current + Needs */}
        <div className="mt-3 flex items-center justify-between text-sm">
          <span>
            <span className="text-zinc-500">Current:</span>{" "}
            <span className="font-medium">
              {data.current.value} {data.current.label}
            </span>
          </span>

          <span>
            <span className="text-zinc-500">Needs:</span>{" "}
            <span className="font-medium">
              {needs} {data.current.label}
            </span>
          </span>
        </div>

        {/* Progress bar */}
        <div className="mt-3 h-2 w-full rounded-full bg-zinc-200">
          <div
            className="h-2 rounded-full bg-zinc-900 transition-all duration-500"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      {/* Bottom Game Info */}
      <div className="mt-4 flex items-center justify-between text-xs text-zinc-500">
        <span>
          <span className="font-medium text-zinc-600">Game Score:</span>{" "}
          {data.game.teamScore}–{data.game.oppScore}
        </span>

        <span>
          {data.game.quarter} • {data.game.clock}
        </span>
      </div>
    </div>
  );
}
