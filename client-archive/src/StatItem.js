import * as React from "react";

export function StatItem({ label, value }) {
  return (
    <div className="p-4 text-center rounded-xl bg-slate-50">
      <p className="text-2xl text-indigo-600 font-bold">{value}</p>
      <p className="text-sm capitalize text-slate-500">{label}</p>
    </div>
  );
}
