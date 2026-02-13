"use client";

import { useState, useMemo } from "react";
import PlayerPropCard from "./PropCard";
import { mockProps } from "./mock";

export default function PropsPage() {
  const [selectedTeam, setSelectedTeam] = useState<string>("All");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");

  const uniqueTeams = useMemo(() => {
    const teams = mockProps.map((p) => p.team);
    return Array.from(new Set(teams)).sort();
  }, []);

  const filteredProps = useMemo(() => {
    let result = [...mockProps];

    if (selectedTeam !== "All") {
      result = result.filter((p) => p.team === selectedTeam);
    }

    if (selectedCategory !== "All") {
      result.sort((a, b) => {
        const key = selectedCategory.toLowerCase() as "pts" | "reb" | "ast";
        return b.projected[key] - a.projected[key];
      });
    }

    return result;
  }, [selectedTeam, selectedCategory]);

  const clearFilters = () => {
    setSelectedTeam("All");
    setSelectedCategory("All");
  };

  return (
    <main className="min-h-screen bg-zinc-50 p-6 pt-20">
      <div className="mx-auto max-w-7xl">
        <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-emerald-600">
              Live Player Props
            </h1>
            <p className="mt-1 text-zinc-600">
              Check out today&apos;s player props and predictions
            </p>
          </div>
        </div>


        <div className="mt-8 flex flex-col gap-4 rounded-xl border border-zinc-200 bg-white p-4 shadow-sm md:flex-row md:items-center">
          
          <div className="flex flex-col gap-1.5">
            <label className="font-semibold uppercase text-neutral-950">
              Select Team
            </label>
            <select
              value={selectedTeam}
              onChange={(e) => setSelectedTeam(e.target.value)}
              className="h-10 w-full rounded-lg border border-zinc-300 bg-white px-3 text-sm font-medium text-zinc-700 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 md:w-48"
            >
              <option value="All">All Teams</option>
              {uniqueTeams.map((team) => (
                <option key={team} value={team}>
                  {team}
                </option>
              ))}
            </select>
          </div>


          <div className="flex flex-col gap-1.5">
            <label className="font-semibold uppercase text-emerald-600">
              Sort By Category
            </label>
            <div className="flex gap-2">
              {["All", "PTS", "REB", "AST"].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`h-10 rounded-lg px-4 text-sm font-medium transition-colors ${
                    selectedCategory === cat
                      ? "bg-emerald-100 text-emerald-700 ring-1 ring-emerald-500"
                      : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>


          {(selectedTeam !== "All" || selectedCategory !== "All") && (
            <div className="md:ml-auto md:self-end">
              <button
                onClick={clearFilters}
                className="h-10 rounded-lg px-4 text-sm font-medium text-red-500 hover:bg-red-50 transition-colors"
              >
                Clear All
              </button>
            </div>
          )}
        </div>

        <div className="mt-6 grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredProps.length > 0 ? (
            filteredProps.map((player) => (
              <PlayerPropCard
                key={`${player.player}-${player.team}`}
                data={player}
              />
            ))
          ) : (
            <div className="col-span-full py-12 text-center text-zinc-500">
              No props found matching your filters.
            </div>
          )}
        </div>
      </div>
    </main>
  );
}