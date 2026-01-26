"use client";

import { useGameData } from "./useGameData";

export default function Home() {
  const { games, status, error, reconnect } = useGameData();

  return (
    <div className="flex min-h-screen items-center justify-center gap-6 bg-blue-975 text-white font-sans">
      {games.map(
        (
          game, //TODO: REPLACE WITH GAME CARD COMPONENT
        ) => (
          <div
            key={game.game_id}
            className="game-card a1 rounded-lg border border-zinc-200 dark:border-zinc-800 p-4"
          >
            <h1>
              {game.home_team} {game.home_score} - {game.away_score}{" "}
              {game.away_team}
            </h1>
            <h2>
              {game.home_record} - {game.away_record}
            </h2>
            <h2>
              {game.home_win_prob} - {game.away_win_prob}
            </h2>
            <span>{game.status}</span>
          </div>
        ),
      )}
    </div>
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
