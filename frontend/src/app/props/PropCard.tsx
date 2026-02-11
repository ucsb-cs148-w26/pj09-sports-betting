type Prop = {
  player: string;
  team: string;
  opponent: string;

  projected: {
    pts: number;
    reb: number;
    ast: number;
  };

  onFloor: boolean;

  game: {
    teamScore: number;
    oppScore: number;
    quarter: string;
    clock: string;
  };
};

function FloorIndicator({ on }: { on: boolean }) {
  return (
    <div className="flex items-center gap-2 text-xs font-medium">
      <span
        className={`h-2.5 w-2.5 rounded-full ${
          on ? "bg-emerald-500" : "bg-zinc-300"
        }`}
      />
      <span className={on ? "text-emerald-600" : "text-zinc-500"}>
        {on ? "On floor" : "Off floor"}
      </span>
    </div>
  );
}

export default function PlayerPropCard({ data }: { data: Prop }) {
  return (
    <div className="w-full max-w-md rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="text-lg font-semibold leading-tight">
            {data.player}
          </div>
          <div className="mt-1 text-sm text-zinc-500">
            {data.team} vs {data.opponent}
          </div>
        </div>

        <FloorIndicator on={data.onFloor} />
      </div>

      {/* Projected Stats */}
      <div className="mt-4 rounded-xl border border-zinc-200 bg-zinc-50 px-4 py-3">
        <div className="mb-3 text-center">
          <div className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
            Projected Stats
          </div>
          <div className="mt-3 h-px w-full bg-zinc-200" />
        </div>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-xs text-zinc-500">PTS</div>
            <div className="mt-1 text-xl font-semibold">
              {data.projected.pts}
            </div>
          </div>
          <div>
            <div className="text-xs text-zinc-500">REB</div>
            <div className="mt-1 text-xl font-semibold">
              {data.projected.reb}
            </div>
          </div>
          <div>
            <div className="text-xs text-zinc-500">AST</div>
            <div className="mt-1 text-xl font-semibold">
              {data.projected.ast}
            </div>
          </div>
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
