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
  if (p >= 80) return "text-emerald-600 bg-emerald-50 border-emerald-200";
  if (p >= 60) return "text-amber-600 bg-amber-50 border-amber-200";
  return "text-rose-600 bg-rose-50 border-rose-200";
}

export default function PlayerPropCard({ data }: { data: Prop }) {
  const p = pct(data.hitChance);
  const badge = chanceColor(p);

  return (
    <div className="w-full max-w-md rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
      {/* Game Info */}
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="text-lg font-semibold leading-tight">{data.player}</div>
          <div className="mt-1 text-sm text-zinc-500">
            {data.team} vs {data.opponent}
          </div>
        </div>

        <div className={`rounded-full border px-3 py-1 text-sm font-semibold ${badge}`}>
          {p}% to hit
        </div>
      </div>

      {/* Prop line */}
      <div className="mt-4 flex items-center justify-between rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2">
        <div className="text-sm text-zinc-500">Player Prop</div>
        <div className="text-base font-semibold">
          {data.prop.overUnder} {data.prop.line} {data.prop.type}
        </div>
      </div>

      {/* Game state + Current stat */}
      <div className="mt-4 grid grid-cols-2 gap-3">
        <div className="rounded-xl border border-zinc-200 p-3">
          <div className="text-sm text-zinc-500">Game</div>
          <div className="mt-1 text-base font-semibold">
            {data.game.teamScore}–{data.game.oppScore}
          </div>
          <div className="mt-1 text-sm text-zinc-600">
            {data.game.quarter} • {data.game.clock}
          </div>
        </div>

        <div className="rounded-xl border border-zinc-200 p-3">
          <div className="text-sm text-zinc-500">Current</div>
          <div className="mt-1 text-base font-semibold">
            {data.current.value} {data.current.label}
          </div>
          <div className="mt-1 text-sm text-zinc-600">
            Needs <span className="font-medium">{Math.max(0, Math.ceil(data.prop.line - data.current.value))}</span>{" "}
            more
          </div>
        </div>
      </div>
      {/* Progress bar */}
      <div className="mt-4">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="text-zinc-500">Progress to line</span>
          <span className="font-medium">
            {data.current.value} / {data.prop.line}
          </span>
        </div>
        <div className="h-2 w-full rounded-full bg-zinc-100">
          <div
            className="h-2 rounded-full bg-zinc-900"
            style={{
              width: `${Math.min(100, (data.current.value / data.prop.line) * 100)}%`,
            }}
          />
        </div>
      </div>
    </div>
  );
}