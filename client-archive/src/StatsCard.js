import * as React from "react";

export function StatsCard({ title, children }) {
  return (
    <article className="p-8 rounded-2xl shadow-lg">
      <h2 className="mb-6 text-2xl text-slate-800">{title}</h2>
      {children}
    </article>
  );
}
