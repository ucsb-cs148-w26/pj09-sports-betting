export default function Home() {  

  let games : Array<{ id: number; home: string; away: string; hscore: number; ascore: number; time: string }> = [
    { id: 1, home: "T1", away: "T2", hscore: 75, ascore: 80, time: "Q4 02:15" },
    { id: 2, home: "T3", away: "T4", hscore: 90, ascore: 85, time: "Q4 02:15" },
    { id: 3, home: "T5", away: "T6", hscore: 60, ascore: 70, time: "Q4 02:15" },
  ]; 
  //TODO: GET GAME DATA FROM BACKEND
  //TODO: CONNECT SOCKET AND LIVE UPDATE WITH STATE HOOK

  return (
  <div className="flex min-h-screen items-center justify-center gap-6 bg-blue-975 text-white font-sans">
      {games.map((game) => ( //TODO: REPLACE WITH GAME CARD COMPONENT
        <div key={game.id} className="game-card a1 rounded-lg border border-zinc-200 dark:border-zinc-800 p-4">
          <h1>{game.home} {game.hscore} - {game.ascore} {game.away}</h1>
          <span>{game.time}</span>
        </div>
      ))}
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