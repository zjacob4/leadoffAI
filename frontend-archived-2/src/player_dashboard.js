import React, { useState } from "react";
import axios from "axios";
import "./player_dashboard.css"; // Create a CSS file for styling

const PlayerDashboard = () => {
    const [searchQuery, setSearchQuery] = useState("");
    const [playerData, setPlayerData] = useState({
        profilePicture: "",
        predictedOPS: "",
        bio: "",
        historicalData: [],
    });

    const handleSearch = async () => {
        try {
            const response = await axios.get(`/api/player?name=${searchQuery}`);
            const { profilePicture, predictedOPS, bio, historicalData } = response.data;
            setPlayerData({ profilePicture, predictedOPS, bio, historicalData });
        } catch (error) {
            console.error("Error fetching player data:", error);
        }
    };

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <div className="search-bar">
                    <input
                        type="text"
                        placeholder="Search player..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                    <button onClick={handleSearch}>Search</button>
                </div>
                <div className="logo">leadoff.ai</div>
            </header>
            <main className="dashboard-main">
                <div className="tile profile-picture">
                    {playerData.profilePicture ? (
                        <img src={playerData.profilePicture} alt="Player" />
                    ) : (
                        <p>No profile picture available</p>
                    )}
                </div>
                <div className="tile ai-prediction">
                    <h3>AI Prediction Stats</h3>
                    <p>Predicted OPS: {playerData.predictedOPS || "N/A"}</p>
                </div>
                <div className="tile player-bio">
                    <h3>Player Bio</h3>
                    <p>{playerData.bio || "No bio available"}</p>
                </div>
                <div className="tile historical-data">
                    <h3>Historical Data</h3>
                    {playerData.historicalData.length > 0 ? (
                        <ul>
                            {playerData.historicalData.map((stat, index) => (
                                <li key={index}>{stat}</li>
                            ))}
                        </ul>
                    ) : (
                        <p>No historical data available</p>
                    )}
                </div>
            </main>
        </div>
    );
};

export default PlayerDashboard;