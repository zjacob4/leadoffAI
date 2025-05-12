import requests
import sqlite3
import statsapi
import pandas as pd
import hashlib
from tensorflow.keras.models import load_model
import numpy as np

# LOAD PREDICTED OPS

start_year = 2018
end_year = 2023

def predict_ops(player, model_path):

    player_str = player

    player_df_col = []
    player_df_stats = ['gamesPlayed','groundOuts','airOuts','runs','doubles','triples','homeRuns','strikeOuts','baseOnBalls','intentionalWalks','hits','hitByPitch','avg','atBats','obp','slg','ops','caughtStealing','stolenBases','stolenBasePercentage','groundIntoDoublePlay','numberOfPitches','plateAppearances','totalBases','rbi','leftOnBase','sacBunts','sacFlies','babip','groundOutsToAirouts','catchersInterference','atBatsPerHomeRun']

    # Create column names for the player_df DataFrame
    for season_col in range(start_year, end_year+1):
        for stat in player_df_stats:
            player_df_col.append(f"{season_col} {stat}")
    player_df_col.append('player')

    # Create an empty DataFrame with the correct columns
    player_df = pd.DataFrame(columns=player_df_col)

    # Assign the column names to the DataFrame
    player_df.columns = player_df_col

    # Convert 'player' column into a numeric representation using hashing
    def convert_player_to_numeric(player_name):
        # Use a hash function to generate a numeric representation
        hash_object = hashlib.md5(player_name.encode())  # MD5 hash
        hash_value = int(hash_object.hexdigest(), 16)  # Convert hash to an integer
        return hash_value % 1e6  # Reduce the size of the number to avoid overflow
    
    player = convert_player_to_numeric(player)

    # Add a new row with all columns initialized to 0
    new_row = {col: 0 for col in player_df.columns}
    new_row['player'] = player  # Set the player's name
    player_df = pd.concat([player_df, pd.DataFrame([new_row])], ignore_index=True)
    
    try:
        player_id = next(x['id'] for x in statsapi.get('sports_players', {'season': end_year+1, 'gameType': 'W'})['people'] if x['fullName'] == player_str)
    except StopIteration:
        print(f"Player ID not found for {player_str}. Skipping.")

    for season in range(start_year, end_year+1):
        #player_df.loc[counter, 'season'] = season
        season_stats_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=season&season={season}&group=hitting"
        response = requests.get(season_stats_url)
        if response.status_code == 200:
            season_stats = response.json()
            if season_stats and 'stats' in season_stats and len(season_stats['stats']) > 0:
                for stat, value in season_stats['stats'][0]['splits'][0]['stat'].items():
                    current_stat = f"{season} {stat}"
                    try:
                        # Attempt to cast the value to float
                        player_df.loc[player_df['player'] == player, current_stat] = float(value)
                    except ValueError:
                        # If casting fails, assign NaN or handle the value appropriately
                        player_df.loc[player_df['player'] == player, current_stat] = float('nan')
            else:
                #print(f"No stats found for player {player} in season {season}.")            
                if player in player_df['player'].values:
                    player_df.loc[player_df['player'] == player, player_df.columns.difference(['player'])] = 0
                    
    # Check if all values for the current player's row are 0
    if (player_df.loc[player_df['player'] == player, :].drop(columns=['player']).eq(0).all(axis=None)):
        print(f"Dropping player {player_str} due to all zero values.")
        player_df.drop(player_df[player_df['player'] == player].index, inplace=True)
        counter -= 1
        raise ValueError(f"No stats exist for player {player_str} in season {season}. Terminating program.")


    # Fix unsupported types
    player_df.fillna(0, inplace=True)
    player_df.replace(['---', '-.--','.---'], 0, inplace=True)

    print("Player df head: ", player_df.head())

    model_input = player_df
    
    model_input.to_csv('model_input.csv', index=False)

    # Load the pre-trained model
    player_ops_model = load_model(model_path)

    # Ensure all columns in player_df are numeric
    player_df = player_df.apply(pd.to_numeric, errors='coerce')

    # Drop any rows or columns with NaN values (if necessary)
    player_df = player_df.dropna()

    # Convert to numpy array and ensure the correct data type
    model_input = np.array(player_df, dtype='float32').reshape(1, -1)

    # Debugging: Print the shape and data type of model_input
    print(f"Shape of model_input: {model_input.shape}")
    print(f"Data type of model_input: {model_input.dtype}")

    # Run the model to predict OPS
    predicted_ops = player_ops_model.predict(model_input)

    # Run the model to predict OPS
    #predicted_ops = player_ops_model.predict(model_input)[0][0]
    predicted_ops = player_ops_model.predict(model_input)

    return predicted_ops

if __name__ == "__main__":
    # Example usage
    player = "Jazz Chisholm Jr."
    model_path = 'player_ops_model_seasonal.h5'
    predicted_ops = predict_ops(player, model_path)
    print(f"Predicted OPS for {player}: {predicted_ops}")