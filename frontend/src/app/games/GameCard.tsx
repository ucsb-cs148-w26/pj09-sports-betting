import Image from "next/image";

type Stats = {
    rebounds: number;
    assists: number;
    turnovers: number;
    fg_percentage: number;
    tp_percentage: number;
};

type Game = {
    game_id: string;
    home_team: string;
    away_team: string;
    home_abbreviation: string;
    away_abbreviation: string;
    home_score: number;
    away_score: number;
    home_record: string;
    away_record: string;
    home_stats: Stats;
    away_stats: Stats;
    quarter: string;
    clock: string;
    hitChance: number;
};

function pct(n: number) {
  return Math.round(n * 100);
}

export default function GameCard({ data } : {data: Game}){
    const p = pct(data.hitChance);
    const logoSize = 256;

    return (
        <div className="border border-gray-300 rounded-lg p-6 bg-white shadow-md hover:shadow-lg transition-shadow">
            {/* Game Time and Quarter */}
            <div className="text-center mb-4">
                <p className="text-sm text-gray-500">{data.quarter} - {data.clock}</p>
            </div>

            {/* Teams and Scores */}
            <div className="flex justify-between items-center mb-4">
                {/* Away Team */}
                <div className="flex-1 text-center relative group">
                    <div className="flex justify-center">
                        <Image src={`https://a1.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/scoreboard/${data.away_abbreviation}.png&h=${logoSize}&w=${logoSize}`} alt={`${data.away_team} logo`} width={100} height={100} />
                    </div>
                    <h3 className="font-bold text-lg cursor-default" data-popover-target={`#popover-away-${data.game_id}`}>{data.away_team}</h3>
                    <p className="text-sm text-gray-600">{data.away_record}</p>
                    <p className="text-3xl font-bold text-red-600 mt-2">{data.away_score}</p>

                    <div id={`popover-away-${data.game_id}`} role="tooltip" className="absolute z-10 left-1/2 top-full -translate-x-1/2 mt-2 invisible inline-block w-64 p-4 text-sm font-normal text-gray-700 bg-white border border-gray-300 rounded-lg shadow-sm opacity-0 transition-opacity duration-300 group-hover:visible group-hover:opacity-100">
                        <h4 className="font-bold mb-2">Stats</h4>
                        <ul className="list-disc list-inside text-left">
                            <li>Rebounds: {data.away_stats.rebounds}</li>
                            <li>Assists: {data.away_stats.assists}</li>
                            <li>Turnovers: {data.away_stats.turnovers}</li>
                            <li>FG%: {pct(data.away_stats.fg_percentage)}%</li>
                            <li>3P%: {pct(data.away_stats.tp_percentage)}%</li>
                        </ul>
                    </div>
                </div>

                {/* Divider */}
                <div className="px-4 text-gray-300 text-2xl">@</div>

                {/* Home Team */}
                <div className="flex-1 text-center relative group">
                    <div className="flex justify-center">
                        <Image src={`https://a1.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/scoreboard/${data.home_abbreviation}.png&h=${logoSize}&w=${logoSize}`} alt={`${data.home_team} logo`} width={100} height={100} />
                    </div>
                    <h3 className="font-bold text-lg cursor-default" data-popover-target={`#popover-home-${data.game_id}`}>{data.home_team}</h3>
                    <p className="text-sm text-gray-600">{data.home_record}</p>
                    <p className="text-3xl font-bold text-blue-600 mt-2">{data.home_score}</p>

                    <div id={`popover-home-${data.game_id}`} role="tooltip" className="absolute z-10 left-1/2 top-full -translate-x-1/2 mt-2 invisible inline-block w-64 p-4 text-sm font-normal text-gray-700 bg-white border border-gray-300 rounded-lg shadow-sm opacity-0 transition-opacity duration-300 group-hover:visible group-hover:opacity-100">
                        <h4 className="font-bold mb-2">Stats</h4>
                        <ul className="list-disc list-inside text-left">
                            <li>Rebounds: {data.home_stats.rebounds}</li>
                            <li>Assists: {data.home_stats.assists}</li>
                            <li>Turnovers: {data.home_stats.turnovers}</li>
                            <li>FG%: {pct(data.home_stats.fg_percentage)}%</li>
                            <li>3P%: {pct(data.home_stats.tp_percentage)}%</li>
                        </ul>
                    </div>
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