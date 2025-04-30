import * as React from "react";

export function HistoricalStatsTable({ stats }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b-2 border-solid border-b-slate-200">
            <th className="p-3 text-left text-slate-500">Year</th>
            <th className="p-3 text-right text-slate-500">Points</th>
            <th className="p-3 text-right text-slate-500">Assists</th>
            <th className="p-3 text-right text-slate-500">Rebounds</th>
          </tr>
        </thead>
        <tbody>
          {stats.map((stat) => (
            <tr
              className="border-b border-solid border-b-slate-200"
              key={stat.year}
            >
              <td className="p-3 text-slate-800">{stat.year}</td>
              <td className="p-3 text-right text-slate-800">{stat.points}</td>
              <td className="p-3 text-right text-slate-800">{stat.assists}</td>
              <td className="p-3 text-right text-slate-800">{stat.rebounds}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
