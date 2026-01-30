import PlayerPropCard from "./PropCard";
import { mockProp } from "./mock";

export default function PropsPage() {
  return (
    <main className="min-h-screen bg-zinc-50 p-6">
      <div className="mx-auto max-w-4xl">
        <h1 className="text-2xl font-semibold">Live Player Props - Coming Soon</h1>
        <p className="mt-1 text-zinc-600"></p>

        <div className="mt-6">
          <PlayerPropCard data={mockProp} /> 
        </div>
      </div>
    </main>
  );
}