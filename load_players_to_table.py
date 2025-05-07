import requests
import sqlite3
import statsapi
import pandas as pd
import hashlib
from tensorflow.keras.models import load_model
import numpy as np


# Constants
MLB_STATS_API_URL = "https://api.mlb.com/stats/players"  # Replace with the actual API URL
DB_PATH = "/Users/zach/Projects/leadoffAI/leadoffAIfrontend/db.sqlite3"
model_path = "/Users/zach/Projects/leadoffAI/player_ops_model_seasonal.h5"


def fetch_players_from_api(number_of_players=10):
    players = []
    try:
        all_players = statsapi.get('sports_players', {'season': 2022, 'gameType': 'W'})['people']
        players = [player['fullName'] for player in all_players[:number_of_players]]
    except Exception as e:
        print(f"Error retrieving player list: {e}")

    return players

def check_and_insert_players(players):
    """Check if players exist in the database and insert if not."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for player in players:
        # Convert player name to numeric ID
        # Use a hash function to generate a numeric representation
        hash_object = hashlib.md5(player.encode())  # MD5 hash
        hash_value = int(hash_object.hexdigest(), 16)  # Convert hash to an integer
        player_id = hash_value % 1e6  # Reduce the size of the number to avoid overflow
        player_name = player

        if not player_id or not player_name:
            print("Invalid player data, skipping...")
            continue


        # LOAD INTO PLAYER_STATS_PLAYER TABLE

        # Check if the player exists in the table
        cursor.execute(f"SELECT COUNT(*) FROM player_stats_player WHERE id = ?", (player_id,))
        exists = cursor.fetchone()[0]

        if exists:
            print(f"Player {player_name} (ID: {player_id}) already exists in the database.")
        else:

            # Insert the player into the table
            cursor.execute(
                f"INSERT INTO player_stats_player (id, name) VALUES (?, ?)",
                (player_id, player_name),
            )
            print(f"Inserted player {player_name} (ID: {player_id}) into the database.")

        
        # LOAD INTO PLAYER_STATS_HISTORICALSTATS TABLE

        # Check if the player exists in the historical stats table
        cursor.execute(f"SELECT COUNT(*) FROM player_stats_historicalstats WHERE player_id = ?", (player_id,))
        exists = cursor.fetchone()[0]

        # Track if historical data loaded
        historical_data_loaded = False

        if exists:
            print(f"Player {player_name} (ID: {player_id}) already exists in the historical stats table.")
        else:
            
            # Fetch player stats from the API
            historical_data_loaded = True
            try:
                player_api_id = next(x['id'] for x in statsapi.get('sports_players', {'season': 2022, 'gameType': 'W'})['people'] if x['fullName'] == player)
                stats_dict = {'player': player}
                for season in range(2020, 2024):
                    stats_dict['season'] = season
                    season_stats_url = f"https://statsapi.mlb.com/api/v1/people/{player_api_id}/stats?stats=season&season={season}&group=hitting"
                    response = requests.get(season_stats_url)
                    if response.status_code == 200:
                        season_stats = response.json()
                        if season_stats and 'stats' in season_stats and len(season_stats['stats']) > 0:
                            for stat, value in season_stats['stats'][0]['splits'][0]['stat'].items():
                                column_name = f'{season} {stat}'
                                stats_dict[column_name] = value
                    
                    # Insert the player into the historical stats table
                    strike_outs = stats_dict.get(f"{season} strikeOuts", None)
                    ops = stats_dict.get(f"{season} ops", None)
                    at_bats = stats_dict.get(f"{season} atBats", None)
                    cursor.execute(
                        f"INSERT INTO player_stats_historicalstats (player_id, year, OPS, K, AB) VALUES (?, ?, ?, ?, ?)",
                        (player_id, season, ops, strike_outs, at_bats),  # Replace with actual stats
                    )
                    print(f"Inserted player {player_name} (ID: {player_id}, season: {season}) into the historical stats table.")
            except StopIteration:
                print(f"Player {player} not found in the 2022 season.")
            except Exception as e:
                print(f"Error retrieving stats for {player}: {e}")
            



        # LOAD INTO PLAYER_STATS_PREDICTEDSTATS TABLE
              
        # Check if the player exists in the historical stats table
        cursor.execute(f"SELECT COUNT(*) FROM player_stats_predictedstats WHERE player_id = ?", (player_id,))
        exists = cursor.fetchone()[0]

        if exists:
            print(f"Player {player_name} (ID: {player_id}) already exists in the predicted stats table.")
        else:
            try:
                data = {}
                df = pd.DataFrame(data)
                player_id = next(x['id'] for x in statsapi.get('sports_players', {'season': 2022, 'gameType': 'W'})['people'] if x['fullName'] == player)
                stats_dict = {'player': player}
                for season in range(2000, 2024):
                    stats_dict['season'] = season
                    season_stats_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=season&season={season}&group=hitting"
                    response = requests.get(season_stats_url)
                    if response.status_code == 200:
                        season_stats = response.json()
                        if season_stats and 'stats' in season_stats and len(season_stats['stats']) > 0:
                            for stat, value in season_stats['stats'][0]['splits'][0]['stat'].items():
                                column_name = f'{season} {stat}'
                                stats_dict[column_name] = value
                df = pd.concat([df, pd.DataFrame([stats_dict])], ignore_index=True)
                
                # Fix unsupported types
                df.fillna(0, inplace=True)
                df.replace(['---', '-.--','.---'], 0, inplace=True)

                # Convert 'player' column into a numeric representation using hashing
                def convert_player_to_numeric(player_name):
                    # Use a hash function to generate a numeric representation
                    hash_object = hashlib.md5(player_name.encode())  # MD5 hash
                    hash_value = int(hash_object.hexdigest(), 16)  # Convert hash to an integer
                    return hash_value % 1e6  # Reduce the size of the number to avoid overflow

                df['player_numeric'] = df['player'].apply(convert_player_to_numeric).astype('float32')

                # Drop the original 'player' column
                df.drop(columns=['player'], inplace=True)

                model_input = df
                
                #print model input
                print(f"Model input: {model_input}")

                # Load the pre-trained model
                player_ops_model = load_model(model_path)


                # Dynamically extract all features from stats_dict for the model input
                #model_input = [value for key, value in stats_dict.items() if isinstance(value, (int, float))]


                # Ensure the input has the correct number of features
                if len(model_input) != 33:
                    print(f"Skipping player {player_name} (ID: {player_id}) due to incorrect input shape. Expected 33 features, got {len(model_input)}.")
                    continue  # Skip this player if the input shape is incorrect

                # Convert to numpy array and reshape
                model_input = np.array(model_input).reshape(1, -1)
                print(f"Shape of model_input: {model_input.shape}")

                # Run the model to predict OPS
                predicted_ops = player_ops_model.predict(model_input)[0][0]

                # Insert the predicted OPS into the predicted stats table
                cursor.execute(
                    f"INSERT INTO player_stats_predictedstats (player_id, OPS, K, AB) VALUES (?, ?, ?, ?)",
                    (player_id, predicted_ops, 0, 0),  # Replace K and AB with actual predicted values if available
                )
                print(f"Inserted predicted OPS {predicted_ops} for player {player_name} (ID: {player_id}) into the predicted stats table.")
                
                
            except StopIteration:
                print(f"Player {player} not found in the 2022 season.")
            except Exception as e:
                print(f"Error retrieving stats for {player}: {e}")

            
                

    conn.commit()
    conn.close()

def main():
    players = fetch_players_from_api()
    if not players:
        print("No players fetched from the API.")
        return

    check_and_insert_players(players)

if __name__ == "__main__":
    main()