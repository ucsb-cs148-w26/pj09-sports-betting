'use client';

import { Game } from '@/app/types';
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ReferenceLine,
    ResponsiveContainer,
} from 'recharts';

interface WinProbabilityGraphProps {
    game: Game;
}

interface DataPoint {
    index: number;
    home: number;
    away: number;
    clock: string;
    homeScore: number;
    awayScore: number;
}

/**
 * Extract a period identifier from the game-clock string for tick labeling.
 * ESPN clock strings look like "7:07 - 3rd", "Halftime", "Final", etc.
 */
function extractPeriod(clock: string): string {
    if (!clock) return '';
    if (/halftime/i.test(clock)) return 'HT';
    if (/final/i.test(clock)) return 'F';
    if (/end of/i.test(clock)) {
        if (clock.includes('1st')) return 'Q1';
        if (clock.includes('2nd')) return 'Q2';
        if (clock.includes('3rd')) return 'Q3';
        if (clock.includes('4th')) return 'Q4';
    }
    if (/1st/.test(clock)) return 'Q1';
    if (/2nd/.test(clock)) return 'Q2';
    if (/3rd/.test(clock)) return 'Q3';
    if (/4th/.test(clock)) return 'Q4';
    if (/overtime|ot/i.test(clock)) return 'OT';
    if (/pregame|scheduled/i.test(clock)) return 'Pre';
    if (/est|et\b|pm|am/i.test(clock)) return 'Pre';
    return '';
}

/**
 * Build the chart data array directly from backend probability snapshots.
 * No frontend estimation — every point is an ML-produced probability.
 */
function buildData(game: Game): DataPoint[] {
    const history = game.probability_history;

    if (!history || history.length === 0) {
        // No history yet — show just the current ML probability as a single point
        const home = game.home_win_prob;
        const away = game.away_win_prob;
        if (home != null && away != null) {
            return [
                {
                    index: 0,
                    home,
                    away,
                    clock: game.status,
                    homeScore: game.home_score ?? 0,
                    awayScore: game.away_score ?? 0,
                },
            ];
        }
        return [];
    }

    return history.map((snap, i) => ({
        index: i,
        home: snap.home_win_prob,
        away: snap.away_win_prob,
        clock: snap.clock,
        homeScore: snap.home_score ?? 0,
        awayScore: snap.away_score ?? 0,
    }));
}

/**
 * Compute tick positions at period transitions so the X-axis shows
 * meaningful labels (Q1, Q2, HT, Q3, Q4, F) instead of every data point.
 */
function computeTicks(data: DataPoint[]): {
    positions: number[];
    labels: Record<number, string>;
} {
    const positions: number[] = [];
    const labels: Record<number, string> = {};

    if (data.length === 0) return { positions, labels };

    // Single data point — just label it
    if (data.length === 1) {
        positions.push(0);
        labels[0] = extractPeriod(data[0].clock) || data[0].clock;
        return { positions, labels };
    }

    let prevPeriod = '';
    for (let i = 0; i < data.length; i++) {
        const period = extractPeriod(data[i].clock);
        if (period && period !== prevPeriod) {
            positions.push(i);
            labels[i] = period;
            prevPeriod = period;
        }
    }

    // Always include the last point so the axis stretches to the end
    const lastIdx = data.length - 1;
    if (!positions.includes(lastIdx)) {
        const lastPeriod = extractPeriod(data[lastIdx].clock);
        if (lastPeriod) {
            positions.push(lastIdx);
            labels[lastIdx] = lastPeriod;
        }
    }

    return { positions, labels };
}

/** Format the raw ESPN clock string into a human-readable time remaining. */
function formatTimeRemaining(clock: string): string {
    if (!clock) return '';
    if (/halftime/i.test(clock)) return 'Halftime';
    if (/final/i.test(clock)) return 'Final';
    if (/pregame|scheduled/i.test(clock)) return 'Pregame';
    if (/\d{1,2}:\d{2}\s*(AM|PM)\s*(E[SD]?T|ET)/i.test(clock)) return 'Pregame';

    const endMatch = clock.match(/end of (\d)(?:st|nd|rd|th)/i);
    if (endMatch) return `End of Q${endMatch[1]}`;

    // "7:07 - 3rd" → "7:07 remaining in Q3"
    const match = clock.match(/^(.+?)\s*-\s*(\d)(?:st|nd|rd|th)$/i);
    if (match) return `${match[1].trim()} remaining in Q${match[2]}`;

    // OT variants: "2:30 - OT" or "1:15 - 2OT"
    const otMatch = clock.match(/^(.+?)\s*-\s*(\d*OT)$/i);
    if (otMatch)
        return `${otMatch[1].trim()} remaining in ${otMatch[2].toUpperCase()}`;
    if (/overtime|ot/i.test(clock)) return 'Overtime';

    return clock;
}

/** Format a probability delta with arrow and sign, e.g. "▲ +2.3%" */
function formatShift(delta: number): {
    text: string;
    className: string;
} {
    if (delta === 0) return { text: '—', className: 'text-gray-400 dark:text-zinc-500' };
    const arrow = delta > 0 ? '▲' : '▼';
    const sign = delta > 0 ? '+' : '';
    const cls =
        delta > 0
            ? 'text-green-600 dark:text-emerald-400'
            : 'text-red-500 dark:text-red-400';
    return { text: `${arrow} ${sign}${delta.toFixed(1)}%`, className: cls };
}

/* Custom tooltip for the chart */
function ProbTooltip({
    active,
    payload,
    game,
    data,
}: any & { game: Game; data: DataPoint[] }) {
    if (!active || !payload?.length) return null;

    const point: DataPoint = payload[0]?.payload;
    if (!point) return null;

    const homeVal: number = point.home;
    const awayVal: number = point.away;
    const idx: number = point.index;

    // Probability shift compared to the previous snapshot
    const prev: DataPoint | undefined = data[idx - 1];
    const homeShift = prev != null ? homeVal - prev.home : 0;
    const awayShift = prev != null ? awayVal - prev.away : 0;
    const hs = formatShift(homeShift);
    const as = formatShift(awayShift);

    // Score differential
    const diff = point.homeScore - point.awayScore;
    const diffLabel =
        diff === 0
            ? 'Tied'
            : diff > 0
              ? `${game.home_team} +${diff}`
              : `${game.away_team} +${Math.abs(diff)}`;

    return (
        <div className="rounded-lg border border-gray-200 dark:border-zinc-600 bg-white dark:bg-zinc-800 px-3.5 py-2.5 shadow-md text-xs min-w-[180px]">
            {/* Time remaining */}
            <div className="font-semibold text-gray-700 dark:text-zinc-200 mb-1.5">
                {formatTimeRemaining(point.clock)}
            </div>

            {/* Score + differential */}
            <div className="flex items-center justify-between gap-3 mb-2 pb-2 border-b border-gray-100 dark:border-zinc-700">
                <span className="text-gray-700 dark:text-zinc-300 font-medium">
                    {game.away_abbreviation} {point.awayScore} –{' '}
                    {game.home_abbreviation} {point.homeScore}
                </span>
                <span className="text-gray-500 dark:text-zinc-400 font-medium">
                    {diffLabel}
                </span>
            </div>

            {/* Home team probability + shift */}
            <div className="flex items-center justify-between gap-3 mb-1">
                <div className="flex items-center gap-1.5">
                    <span
                        className="inline-block h-2 w-2 rounded-full"
                        style={{ background: '#16a34a' }}
                    />
                    <span className="text-gray-600 dark:text-zinc-400">
                        {game.home_team}:
                    </span>
                    <span className="font-bold text-gray-900 dark:text-zinc-100">
                        {homeVal.toFixed(1)}%
                    </span>
                </div>
                <span className={`font-medium ${hs.className}`}>{hs.text}</span>
            </div>

            {/* Away team probability + shift */}
            <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-1.5">
                    <span
                        className="inline-block h-2 w-2 rounded-full"
                        style={{ background: '#ef4444' }}
                    />
                    <span className="text-gray-600 dark:text-zinc-400">
                        {game.away_team}:
                    </span>
                    <span className="font-bold text-gray-900 dark:text-zinc-100">
                        {awayVal.toFixed(1)}%
                    </span>
                </div>
                <span className={`font-medium ${as.className}`}>{as.text}</span>
            </div>
        </div>
    );
}

export default function WinProbabilityGraph({
    game,
}: WinProbabilityGraphProps) {
    if (!game) return null;

    const data = buildData(game);

    // Nothing to show yet
    if (data.length === 0) {
        return (
            <div className="mt-10 mx-auto max-w-4xl">
                <h4 className="text-center text-lg font-semibold text-gray-900 dark:text-zinc-100 mb-1">
                    Win Probability
                </h4>
                <p className="text-center text-sm text-gray-500 dark:text-zinc-400 mt-4">
                    Probability data is not available yet.
                </p>
            </div>
        );
    }

    const homeProb = game.home_win_prob ?? 50;
    const awayProb = game.away_win_prob ?? 50;
    const homeFavored = homeProb >= awayProb;

    const { positions: tickPositions, labels: tickLabels } =
        computeTicks(data);

    return (
        <div className="mt-10 mx-auto max-w-4xl">
            <h4 className="text-center text-lg font-semibold text-gray-900 dark:text-zinc-100 mb-1">
                Win Probability
            </h4>
            <p className="text-center text-xs text-gray-500 dark:text-zinc-400 mb-4">
                {game.away_team} vs {game.home_team}
            </p>

            <div className="mb-5 border-b border-gray-200 dark:border-zinc-800 pb-4">
                <div className="flex items-center justify-between gap-4">
                    <div className="min-w-0">
                        <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-zinc-400">
                            {game.away_abbreviation}
                        </div>
                        <div className="truncate text-sm font-medium text-gray-700 dark:text-zinc-200">
                            {game.away_team}
                        </div>
                        <div className={`text-3xl font-black leading-none ${!homeFavored ? 'text-red-500 dark:text-red-400' : 'text-gray-900 dark:text-zinc-100'}`}>
                            {awayProb.toFixed(1)}%
                        </div>
                    </div>

                    <div className="flex flex-col items-center justify-center px-3 text-center">
                        <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-400 dark:text-zinc-500">
                            Model Projection
                        </div>
                        <div className="mt-1 text-sm font-semibold text-gray-700 dark:text-zinc-200">
                            {Math.abs(homeProb - awayProb).toFixed(1)} pt edge
                        </div>
                    </div>

                    <div className="min-w-0 text-right">
                        <div className="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-zinc-400">
                            {game.home_abbreviation}
                        </div>
                        <div className="truncate text-sm font-medium text-gray-700 dark:text-zinc-200">
                            {game.home_team}
                        </div>
                        <div className={`text-3xl font-black leading-none ${homeFavored ? 'text-green-600 dark:text-emerald-400' : 'text-gray-900 dark:text-zinc-100'}`}>
                            {homeProb.toFixed(1)}%
                        </div>
                    </div>
                </div>
            </div>

            {/* Chart */}
            <div className="w-full h-72 sm:h-80">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart
                        data={data}
                        margin={{ top: 10, right: 10, left: -10, bottom: 0 }}
                    >
                        <defs>
                            <linearGradient
                                id="gradHome"
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                            >
                                <stop
                                    offset="5%"
                                    stopColor="#16a34a"
                                    stopOpacity={0.3}
                                />
                                <stop
                                    offset="95%"
                                    stopColor="#16a34a"
                                    stopOpacity={0.02}
                                />
                            </linearGradient>
                            <linearGradient
                                id="gradAway"
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                            >
                                <stop
                                    offset="5%"
                                    stopColor="#ef4444"
                                    stopOpacity={0.3}
                                />
                                <stop
                                    offset="95%"
                                    stopColor="#ef4444"
                                    stopOpacity={0.02}
                                />
                            </linearGradient>
                        </defs>

                        <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="#e5e7eb"
                        />

                        <XAxis
                            dataKey="index"
                            type="number"
                            domain={[0, data.length - 1]}
                            ticks={tickPositions}
                            tickFormatter={(value: number) =>
                                tickLabels[value] || ''
                            }
                            tick={{ fontSize: 12, fill: '#6b7280' }}
                            axisLine={{ stroke: '#d1d5db' }}
                            tickLine={false}
                        />
                        <YAxis
                            domain={[0, 100]}
                            ticks={[0, 25, 50, 75, 100]}
                            tick={{ fontSize: 11, fill: '#9ca3af' }}
                            axisLine={false}
                            tickLine={false}
                            tickFormatter={(v: number) => `${v}%`}
                        />

                        <ReferenceLine
                            y={50}
                            stroke="#9ca3af"
                            strokeDasharray="4 4"
                            strokeWidth={1}
                        />

                        <Tooltip
                            content={
                                <ProbTooltip game={game} data={data} />
                            }
                        />

                        <Area
                            type="monotone"
                            dataKey="home"
                            name="Home"
                            stroke="#16a34a"
                            strokeWidth={2}
                            fill="url(#gradHome)"
                            dot={false}
                            activeDot={{
                                r: 4,
                                fill: '#16a34a',
                                stroke: '#fff',
                                strokeWidth: 2,
                            }}
                        />
                        <Area
                            type="monotone"
                            dataKey="away"
                            name="Away"
                            stroke="#ef4444"
                            strokeWidth={2}
                            fill="url(#gradAway)"
                            dot={false}
                            activeDot={{
                                r: 4,
                                fill: '#ef4444',
                                stroke: '#fff',
                                strokeWidth: 2,
                            }}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
