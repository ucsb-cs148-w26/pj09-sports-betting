"use client";

import GameCard, { type Game } from "./games/GameCard";
import { useEffect, useState } from "react";

export default function GamesPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    fetch("http://localhost:8000/api/games")
      .then((res) => res.json())
      .then((data) => setGames(data))
      .catch(() => setGames([]))
      .finally(() => setLoading(false));
  }, []);
  return (
    <main className="min-h-screen bg-zinc-50 p-6 pt-20">
      <div className="mx-auto max-w-4xl">
        <h1 className="text-2xl font-semibold text-emerald-400">Live Games</h1>
        <p className="mt-1 text-zinc-600">Check out today's games and predictions</p>

        <div className="mt-6 grid gap-6">
        {!loading &&
          games.map((game) => (
            <GameCard key={game.game_id} data={game} />
          ))}
        </div>
      </div>
    </main>
  );
}

/* <div className="">
        <h1 className="max-w-xs text-3xl font-semibold leading-10 tracking-tight text-white">
          GC1.
        </h1>
      </div>
      <div className="a2 rounded-lg border border-zinc-200 dark:border-zinc-800 p-4">
        <h1 className="max-w-xs text-3xl font-semibold leading-10 tracking-tight text-white">
          GC2
        </h1>
      </div>
*/