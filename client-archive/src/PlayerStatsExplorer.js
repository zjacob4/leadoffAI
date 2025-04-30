"use client";
import * as React from "react";
import { useState, useEffect } from "react";
import { SearchBar } from "./SearchBar";
import { StatsCard } from "./StatsCard";
import { StatItem } from "./StatItem";
import { HistoricalStatsTable } from "./HistoricalStatsTable";

function PlayerStatsExplorer() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [predictedStats, setPredictedStats] = useState({
    points: 25.4,
    assists: 6.2,
    rebounds: 5.1,
    steals: 1.3,
    blocks: 0.8,
  });
  const [historicalStats, setHistoricalStats] = useState([
    {
      year: "2023",
      points: 24.1,
      assists: 5.8,
      rebounds: 4.9,
    },
    {
      year: "2022",
      points: 22.3,
      assists: 5.2,
      rebounds: 4.5,
    },
    {
      year: "2021",
      points: 20.8,
      assists: 4.9,
      rebounds: 4.2,
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  function handleSearch(event) {
    setSearchQuery(event.target.value);
  }

  async function handleSearchSubmit(query) {
    if (!query.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      // In a real application, this would be a call to a sports statistics API
      // For demonstration purposes, we're simulating an API call with a timeout
      console.log(`Searching for player: ${query}`);

      // Simulate API call
      const response = await fetch(`/api/player?name=${encodeURIComponent(query)}`);
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const playerData = await response.json();

      // Update state with the fetched data
      setSelectedPlayer(playerData.name);
      setPredictedStats(playerData.predictedStats);
      setHistoricalStats(playerData.historicalStats);

    } catch (err) {
      console.error("Error fetching player data:", err);
      setError("Failed to fetch player data. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="px-5 py-10 mx-auto my-0 max-w-[1200px] max-sm:p-5">
      <header className="mb-10 text-center">
        <h1 className="mb-6 text-5xl">Player Stats Explorer</h1>
        <SearchBar
          searchQuery={searchQuery}
          onSearch={handleSearch}
          onSearchSubmit={handleSearchSubmit}
        />
        {isLoading && (
          <p className="mt-4 text-indigo-600">Loading player data...</p>
        )}
        {error && <p className="mt-4 text-red-600">{error}</p>}
        {selectedPlayer && !isLoading && !error && (
          <p className="mt-4 text-xl text-slate-700">
            Showing stats for{" "}
            <span className="font-bold">{selectedPlayer}</span>
          </p>
        )}
      </header>

      <section className="grid gap-10 mt-16 grid-cols-[1fr_1fr] max-md:gap-8 max-md:grid-cols-[1fr]">
        <StatsCard title="2024 Predicted Stats">
          <div className="grid gap-5 grid-cols-[repeat(auto-fit,minmax(120px,1fr))]">
            {Object.entries(predictedStats).map(([key, value]) => (
              <StatItem
                key={key}
                label={key}
                value={parseFloat(value.toFixed(1))}
              />
            ))}
          </div>
        </StatsCard>

        <StatsCard title="Historical Performance">
          <HistoricalStatsTable stats={historicalStats} />
        </StatsCard>
      </section>
    </main>
  );
}

export default PlayerStatsExplorer;
