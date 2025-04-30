const express = require("express");
const cors = require("cors");
const sqlite3 = require("sqlite3").verbose();
const path = require("path");
const { spawn } = require("child_process");

const app = express();
const PORT = 5000;

// Middleware
app.use(cors()); // Enable CORS to allow requests from the frontend
app.use(express.json()); // Parse JSON request bodies

// Player stats data
const dbPath = path.join(__dirname, "../leadoffAI.db");
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error("Error connecting to the database:", err.message);
    } else {
        console.log("Connected to the SQLite database.");
    }
});

let players = [];
db.all("SELECT * FROM player_stats", [], (err, rows) => {
    if (err) {
        console.error("Error fetching player data:", err.message);
    } else {
        players = rows.map((row) => ({
            ...Object.fromEntries(Object.entries(row).filter(([key]) => key.startsWith("2023")))
        }));
    }
});


// Define the /api/player endpoint
app.get("/api/player", (req, res) => {
    const playerName = req.query.name;

    // Find the player by name
    const player = players.find((p) => p.name.toLowerCase() === playerName.toLowerCase());

    if (player) {
        const pythonProcess = spawn("python3", ["path/to/your_script.py", JSON.stringify(player)]);

        pythonProcess.stdout.on("data", (data) => {
            console.log(`Python output: ${data}`);
            res.json({ player, pythonResult: data.toString() });
        });

        pythonProcess.stderr.on("data", (data) => {
            console.error(`Python error: ${data}`);
            res.status(500).json({ error: "Error processing Python script" });
        });

        pythonProcess.on("close", (code) => {
            console.log(`Python script exited with code ${code}`);
        });
    }

    if (player) {
        res.json(player);
    } else {
        res.status(404).json({ error: "Player not found" });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});