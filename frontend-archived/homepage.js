// homepage.js

// Function to navigate to player_search.html
function goToPlayerSearch() {
    window.location.href = 'player_search.html';
}

// Function to navigate to position_search.html
function goToPositionSearch() {
    window.location.href = 'position_search.html';
}

// Attach event listeners to buttons
document.getElementById('playerSearchButton').addEventListener('click', goToPlayerSearch);
document.getElementById('positionSearchButton').addEventListener('click', goToPositionSearch);