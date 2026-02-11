import PlayerPropCard from "./PropCard";
import { mockProps } from "./mock";

export default function PropsPage() {
  return (
    <main className="min-h-screen bg-zinc-50 p-6 pt-20">
      <div className="mx-auto max-w-7xl">
        <h1 className="text-2xl font-semibold text-emerald-400">Live Player Props</h1>
        <p className="mt-1 text-zinc-600">
          Check out today&apos;s player props and predictions
        </p>

        <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {mockProps.map((player) => (
            <PlayerPropCard key={`${player.player}-${player.team}`} data={player} />
          ))}
        </div>
      </div>
    </main>
  );
}