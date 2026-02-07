export default async function GameDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <main className="min-h-screen bg-zinc-50 p-6 pt-24">
      <div className="mx-auto max-w-4xl text-center">
        <h1 className="text-3xl font-bold text-zinc-900">Game Details</h1>
        <div className="mt-8 rounded-xl border border-zinc-200 bg-white p-12 shadow-sm">
          <p className="text-zinc-500">
            Placeholder content for Game ID: <span className="font-mono text-emerald-600 font-bold">{id}</span>
          </p>
          <p className="mt-2 text-sm text-zinc-400">
            Deep dive stats and charts coming soon...
          </p>
        </div>
      </div>
    </main>
  );
}