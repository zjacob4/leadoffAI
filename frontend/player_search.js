// player_search.js

document.addEventListener("DOMContentLoaded", () => {
    const searchForm = document.getElementById("search-form");
    const predictionsTile = document.getElementById("predictions-tile");

    // Handle search form submission
    searchForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        const searchQuery = document.getElementById("search-bar").value;

        // Redirect back to player_search.html with query as a parameter
        window.location.href = `player_search.html?query=${encodeURIComponent(searchQuery)}`;
    });

    // Fetch AI predictions when the page loads
    const fetchPredictions = async () => {
        try {
            const response = await fetch("/api/get_predictions");
            if (!response.ok) {
                throw new Error("Failed to fetch predictions");
            }
            const data = await response.json();

            // Render predictions in the tile
            predictionsTile.innerHTML = data.results
                .map((result) => `<div>${result.player_name}: ${result.prediction}</div>`)
                .join("");
        } catch (error) {
            console.error("Error fetching predictions:", error);
            predictionsTile.innerHTML = "<div>Error loading predictions</div>";
        }
    };

    fetchPredictions();
});