'use client';

import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
    ResponsiveContainer, ReferenceLine
} from 'recharts';

export type WinProbPoint = {
    time: string;
    home: number;
    away: number;
};

interface WinProbChartProps {
    data: WinProbPoint[];
    homeTeam: string;
    awayTeam: string;
}

export default function WinProbChart({ data, homeTeam, awayTeam }: WinProbChartProps) {
    return (
        <div className="mt-8 p-6 rounded-lg border border-gray-200 shadow-sm">
            <h2 className="text-lg font-bold text-gray-900 mb-4 text-center">Win Probability</h2>
            <ResponsiveContainer width="100%" height={300}>
                <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="time" tick={{ fontSize: 11 }} stroke="#9ca3af" />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} stroke="#9ca3af" tickFormatter={(v: number) => `${v}%`} />
                    <Tooltip formatter={(value) => `${value}%`} />
                    <Legend />
                    <ReferenceLine y={50} stroke="#d1d5db" strokeDasharray="4 4" />
                    <Line
                        type="monotone"
                        dataKey="home"
                        name={homeTeam}
                        stroke="#2563eb"
                        strokeWidth={2}
                        dot={{ r: 3 }}
                        activeDot={{ r: 5 }}
                    />
                    <Line
                        type="monotone"
                        dataKey="away"
                        name={awayTeam}
                        stroke="#dc2626"
                        strokeWidth={2}
                        dot={{ r: 3 }}
                        activeDot={{ r: 5 }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
