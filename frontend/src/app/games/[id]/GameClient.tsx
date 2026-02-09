'use client';

import Image from "next/image";
import { Game } from '@/app/types';
import { useGameData } from '@/app/useGameData';
import { mockGames } from '../mock';

export default function GameClient({ id }: { id: string }) {
    const imgSize = 150;
    let { games, status, error } = useGameData();
    if (!games.length) games = mockGames;
    console.log(games[0].game_id, id);
    const game: Game | undefined = games.find((g) => g.game_id === id);
    if (!game) {
        
    }

    return (
        <div className="min-h-screen bg-white p-6 pt-20 text-gray-900">
            <div className="mx-auto max-w-7xl">
                <div className="p-6 sm:p-8">
                    <div className="flex items-center justify-between gap-4 sm:gap-8">
                        <div className="flex-1 text-center">
                            <Image
                                src={`https://a1.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/scoreboard/${game?.away_abbreviation}.png&h=456&w=456`}
                                alt={`${game?.away_team} logo`}
                                width={imgSize}
                                height={imgSize}
                                className="mx-auto mb-3"
                            />
                            <div className="text-xs font-bold uppercase tracking-widest text-gray-600">
                                {game?.away_city}
                            </div>
                            <div className="text-lg font-bold text-gray-900 sm:text-2xl">
                                {game?.away_team}
                            </div>
                            <div className="text-xs text-gray-600">
                                {game?.away_wins}-{game?.away_losses}
                            </div>
                        </div>

                        <div className="flex flex-col items-center gap-2">
                            <div className="flex items-center gap-3 sm:gap-4">
                                <div className="rounded-lg px-3 py-2 sm:px-4 sm:py-3">
                                    <div className="text-3xl font-black text-black sm:text-4xl">
                                        {game?.away_score}
                                    </div>
                                </div>
                                <div className="text-lg font-bold text-gray-600 sm:text-xl">
                                    -
                                </div>
                                <div className="rounded-lg px-3 py-2 sm:px-4 sm:py-3">
                                    <div className="text-3xl font-black text-black sm:text-4xl">
                                        {game?.home_score}
                                    </div>
                                </div>
                            </div>
                            <div className="rounded-full px-3 py-1 text-xs font-bold tracking-widest">
                                {game?.status}
                            </div>

                            <div className="mt-8 mx-auto max-w-4xl">
                                <table className="w-full text-xs">
                                    <thead>
                                        <tr>
                                            <th className="p-1 text-left font-semibold">Team</th>
                                            <th className="p-1 text-center font-semibold">Q1</th>
                                            <th className="p-1 text-center font-semibold">Q2</th>
                                            <th className="p-1 text-center font-semibold">Q3</th>
                                            <th className="p-1 text-center font-semibold">Q4</th>
                                            <th className="p-1 text-center font-semibold">Total</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td className="p-1 font-semibold">{game?.home_team}</td>
                                            <td className="p-1 text-center">{game?.home_q1 ?? '-'}</td>
                                            <td className="p-1 text-center">{game?.home_q2 ?? '-'}</td>
                                            <td className="p-1 text-center">{game?.home_q3 ?? '-'}</td>
                                            <td className="p-1 text-center">{game?.home_q4 ?? '-'}</td>
                                            <td className="p-1 text-center font-semibold">{game?.home_score}</td>
                                        </tr>
                                        <tr>
                                            <td className="p-1 font-semibold">{game?.away_team}</td>
                                            <td className="p-1 text-center">{game?.away_q1 ?? '-'}</td>
                                            <td className="p-1 text-center">{game?.away_q2 ?? '-'}</td>
                                            <td className="p-1 text-center">{game?.away_q3 ?? '-'}</td>
                                            <td className="p-1 text-center">{game?.away_q4 ?? '-'}</td>
                                            <td className="p-1 text-center font-semibold">{game?.away_score}</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <div className="flex-1 text-center">
                            <Image
                                src={`https://a1.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/scoreboard/${game?.home_abbreviation}.png&h=456&w=456`}
                                alt={`${game?.home_team} logo`}
                                width={imgSize}
                                height={imgSize}
                                className="mx-auto mb-3"
                            />
                            <div className="text-xs font-bold uppercase tracking-widest text-gray-600">
                                {game?.home_city}
                            </div>
                            <div className="text-lg font-bold text-gray-900 sm:text-2xl">
                                {game?.home_team}
                            </div>
                            <div className="text-xs text-gray-600">
                                {game?.home_wins}-{game?.home_losses}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="mx-auto mt-8 max-w-4xl text-gray-700">
                <div className="grid grid-cols-1 gap-6 items-center md:grid-cols-3 border-b border-gray-200 pb-6">
                    <div className="text-left">
                        <h4 className="text-sm font-medium text-gray-600 mb-3">{game?.away_team}</h4>
                        <div className="space-y-4">
                            <div className="">
                                <span className="font-semibold text-gray-900">{game?.away_leader_pts_name} {game?.away_leader_pts_val}</span>
                            </div>
                            <div className="">
                                <span className="font-semibold text-gray-900 ">{game?.away_leader_reb_name} {game?.away_leader_reb_val}</span>
                            </div>
                            <div className="">
                                <span className="font-semibold text-gray-900">{game?.away_leader_ast_name} {game?.away_leader_ast_val}</span>
                            </div>
                        </div>
                    </div>

                    <div className="text-center">
                        <h4 className="text-gray-900 font-semibold">Player Stats</h4>
                        <div className="space-y-6">
                            <div className="text-gray-600 font-semibold">Points</div>
                            <div className="text-gray-600 font-semibold">Rebounds</div>
                            <div className="text-gray-600 font-semibold">Assists</div>
                        </div>
                    </div>

                    <div className="text-right">
                        <h4 className="text-sm font-medium text-gray-600 mb-3">{game?.home_team}</h4>
                        <div className="space-y-4">
                            <div className="">
                                <span className="font-semibold text-gray-900">{game?.home_leader_pts_name} {game?.home_leader_pts_val}</span>
                            </div>
                            <div className="">
                                <span className="font-semibold text-gray-900">{game?.home_leader_reb_name} {game?.home_leader_reb_val}</span>
                            </div>
                            <div className="">
                                <span className="font-semibold text-gray-900">{game?.home_leader_ast_name} {game?.home_leader_ast_val}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Team Stats */}
                <div className="mt-8 mx-auto max-w-4xl">
                    <div className="grid grid-cols-3 gap-4 items-start text-sm">
                        <div className="text-left space-y-2 text-gray-900">
                            <div>{game?.away_team}</div>
                            <div className="font-semibold">{game?.away_points ?? game?.away_score}</div>
                            <div className="font-semibold">{game?.away_reb ?? '-'}</div>
                            <div className="font-semibold">{game?.away_ast ?? '-'}</div>
                            <div className="font-semibold">{game?.away_fgm ?? '-'} / {game?.away_fga ?? '-'}</div>
                            <div className="font-semibold">{game?.away_3pm ?? '-'} / {game?.away_3pa ?? '-'}</div>
                            <div className="font-semibold">{game?.away_ftm ?? '-'} / {game?.away_fta ?? '-'}</div>
                        </div>

                        <div className="text-center space-y-2 text-gray-600">
                            <h4 className="text-gray-900 font-semibold">Team Stats</h4>
                            <div className="space-y-2">
                                <div>Points</div>
                                <div>Rebounds</div>
                                <div>Assists</div>
                                <div>FGM / FGA</div>
                                <div>3PM / 3PA</div>
                                <div>FTM / FTA</div>
                            </div>
                        </div>                

                        <div className="text-right space-y-2 text-gray-900">
                            <div>{game?.home_team}</div>
                            <div className="font-semibold">{game?.home_points ?? game?.home_score}</div>
                            <div className="font-semibold">{game?.home_reb ?? '-'}</div>
                            <div className="font-semibold">{game?.home_ast ?? '-'}</div>
                            <div className="font-semibold">{game?.home_fgm ?? '-'} / {game?.home_fga ?? '-'}</div>
                            <div className="font-semibold">{game?.home_3pm ?? '-'} / {game?.home_3pa ?? '-'}</div>
                            <div className="font-semibold">{game?.home_ftm ?? '-'} / {game?.home_fta ?? '-'}</div>
                        </div>
                    </div>
                </div>

                <div className="mt-8 p-6 rounded-lg text-center">
                    <h1 className="text-xl font-bold text-gray-900">Graph here later</h1>
                </div>
                <div className="mt-6 text-sm text-gray-500">
                    {error ? ` • ${error}` : null}
                </div>
            </div>
        </div>
    );
}