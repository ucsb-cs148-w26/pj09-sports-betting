import { Game } from '../types';
import abbr from './abbrMap';
import Image from 'next/image';
import Link from 'next/link';

function formatProb(n: number | null) {
  if (n === null || Number.isNaN(n)) return "N/A";
  return `${Math.round(n)}%`;
}

const imgSize = 100;

export default function GameCard({ data }: { data: Game }) {
  return (
    <Link 
      href={`/games/${data.game_id}`}
       className="border border-gray-300 rounded-lg p-6 bg-white shadow-md hover:shadow-lg transition-shadow cursor-pointer">
      {/* Status / Time Remaining */}
      <div className="text-center mb-4">
        <p className="text-sm text-gray-500">{data.status}</p>
      </div>

      {/* Teams and Scores */}
      <div className="flex justify-between items-center mb-4">
        {/* Team 1 */}
        <div className="flex-1 text-center">
          <div className="flex-1 justify-center mb-2">
            <Image
              src={`https://a1.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/scoreboard/${abbr[data.home_team]}.png&h=456&w=456`}
              alt={`${data.home_team} logo`}
              width={imgSize}
              height={imgSize}
              className="mx-auto"
            />
          </div>
          <h3 className="font-bold text-lg">{data.home_team}</h3>
          <p className="text-sm text-gray-600">
            {data.home_wins}-{data.home_losses}
          </p>
          <p className="text-3xl font-bold text-blue-600 mt-2">
            {data.home_score}
          </p>
        </div>

        {/* Divider */}
        <div className="px-4 text-gray-300 text-2xl">vs</div>

        {/* Team 2 */}
        <div className="flex-1 text-center">
            <Image
              src={`https://a1.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/scoreboard/${abbr[data.away_team]}.png&h=456&w=456`}
              alt={`${data.away_team} logo`}
              width={imgSize}
              height={imgSize}
              className="mx-auto"
            />

          <h3 className="font-bold text-lg">{data.away_team}</h3>
          <p className="text-sm text-gray-600">
            {data.away_wins}-{data.away_losses}
          </p>
          <p className="text-3xl font-bold text-red-600 mt-2">
            {data.away_score}
          </p>
        </div>
      </div>

      {/* Win Probabilities */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <span className="text-gray-700 font-medium">Win Prob:</span>
          <span className="font-bold text-lg text-green-600">
            {formatProb(data.home_win_prob ?? null)} / {formatProb(data.away_win_prob ?? null)}
          </span>
        </div>
      </div>
    </Link>
  );
}
