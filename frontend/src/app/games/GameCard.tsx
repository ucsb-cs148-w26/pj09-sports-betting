type Game = {
    game_id: string;
    home_team: string;
    away_team: string;
    home_score: number;
    away_score: number;
    home_record: string;
    away_record: string;
    quarter: string;
    clock: string;
    hitChance: number;
};

function pct(n: number) {
  return Math.round(n * 100);
}

export default function GameCard({ data } : {data: Game}){
    const p = pct(data.hitChance);

    return (
        <div className="border border-gray-300 rounded-lg p-6 bg-white shadow-md hover:shadow-lg transition-shadow">
            {/* Game Time and Quarter */}
            <div className="text-center mb-4">
                <p className="text-sm text-gray-500">{data.quarter} - {data.clock}</p>
            </div>

            {/* Teams and Scores */}
            <div className="flex justify-between items-center mb-4">
                {/* Team 1 */}
                <div className="flex-1 text-center">
                    <h3 className="font-bold text-lg">{data.home_team}</h3>
                    <p className="text-sm text-gray-600">{data.home_record}</p>
                    <p className="text-3xl font-bold text-blue-600 mt-2">{data.home_score}</p>
                </div>

                {/* Divider */}
                <div className="px-4 text-gray-300 text-2xl">vs</div>

                {/* Team 2 */}
                <div className="flex-1 text-center">
                    <h3 className="font-bold text-lg">{data.away_team}</h3>
                    <p className="text-sm text-gray-600">{data.away_record}</p>
                    <p className="text-3xl font-bold text-red-600 mt-2">{data.away_score}</p>
                </div>
            </div>

            {/* Hit Chance / Prediction */}
            <div className="mt-6 pt-4 border-t border-gray-200">
                <div className="flex justify-between items-center">
                    <span className="text-gray-700 font-medium">Prediction:</span>
                    <div className="flex items-center gap-2">
                        <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-green-500 transition-all duration-300"
                                style={{ width: `${p}%` }}
                            ></div>
                        </div>
                        <span className="font-bold text-lg text-green-600">{p}%</span>
                    </div>
                </div>
            </div>
        </div>
    )
}