"use client";

import { useEffect, useState } from "react";

// Matches the dictionary structure from standings.py
interface TeamData {
  team_id: number;
  team_city: string;
  team_name: string;
  conference: string;
  rank: number;
  record: string;
  win_pct: number;
  team_L10: string;
  curr_streak: string;
}

// Matches the return signature: List[Dict] -> [{ east_standings: ..., west_standings: ... }]
interface StandingsResponse {
  east_standings: TeamData[];
  west_standings: TeamData[];
}

export default function Standings() {
  const [data, setData] = useState<StandingsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [conference, setConference] = useState<"East" | "West">("East");

  useEffect(() => {
    async function fetchStandings() {
      try {
        // Replace with your actual backend endpoint (e.g., 'http://127.0.0.1:8000/standings')
        const res = await fetch("https://pj09-sports-betting.onrender.com/api/standings"); 
        const json = await res.json();
        
        // standings.py returns a list containing one dict: [{...}]
        if (Array.isArray(json) && json.length > 0) {
          setData(json[0]);
        }
      } catch (error) {
        console.error("Failed to fetch standings:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchStandings();
  }, []);

  // Determine which list to show based on tab selection
  const currentStandings =
    conference === "East" ? data?.east_standings : data?.west_standings;

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-zinc-900">NBA Standings</h2>
        
        {/* Conference Toggle */}
        <div className="flex rounded-md bg-zinc-100 p-1">
          <button
            onClick={() => setConference("East")}
            className={`rounded px-3 py-1 text-xs font-medium transition-all ${
              conference === "East"
                ? "bg-white text-zinc-900 shadow-sm"
                : "text-zinc-500 hover:text-zinc-700"
            }`}
          >
            East
          </button>
          <button
            onClick={() => setConference("West")}
            className={`rounded px-3 py-1 text-xs font-medium transition-all ${
              conference === "West"
                ? "bg-white text-zinc-900 shadow-sm"
                : "text-zinc-500 hover:text-zinc-700"
            }`}
          >
            West
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-hidden">
        {loading ? (
          <div className="flex h-40 items-center justify-center text-sm text-zinc-400">
            Loading...
          </div>
        ) : !currentStandings ? (
          <div className="flex h-40 items-center justify-center text-sm text-zinc-400">
            No data available
          </div>
        ) : (
          <div className="relative overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-zinc-100 text-xs font-medium text-zinc-400 uppercase">
                <tr>
                  <th className="pb-2 pl-2">#</th>
                  <th className="pb-2">Team</th>
                  <th className="pb-2 text-right pr-2">W-L</th>
                  <th className="pb-2 text-center">Last 10</th>
                  <th className="pb-2 text-center">Streak</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-50">
                {currentStandings.map((team) => (
                  <tr key={team.team_id} className="hover:bg-zinc-50 transition-colors">
                    <td className="py-2.5 pl-2 font-medium text-zinc-500 w-8">{team.rank}</td>
                    <td className="py-2.5">
                      <div className="flex flex-col">
                        <span className="font-medium text-zinc-900">{team.team_city}</span>
                        <span className="text-xs text-zinc-400">{team.team_name}</span>
                      </div>
                    </td>
                    <td className="py-2.5 text-right pr-2 font-medium text-zinc-700">{team.record}</td>
                    <td className="py-2.5 text-center text-xs text-zinc-600">{team.team_L10}</td>
                    <td className={`py-2.5 text-center text-xs font-medium ${
                      team.curr_streak.includes('W') ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {team.curr_streak.replaceAll(' ', '')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}