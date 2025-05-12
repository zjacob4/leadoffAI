import statsapi
import pandas as pd
import requests
import pandas as pd
from sklearn.model_selection import train_test_split
import hashlib
import numpy as np

# Load the dataset
file_path = 'statload_test.csv'
num_players = 10
start_year = 2013
end_year = 2023


def get_player_training_data_ops():
    players = []
    try:
        all_players = statsapi.get('sports_players', {'season': end_year+1, 'gameType': 'W'})['people']
        players = [player['fullName'] for player in all_players[:num_players]]
    except Exception as e:
        print(f"Error retrieving player list: {e}")

    data = {}

    df = pd.DataFrame(data)
    counter = -1

    # Create a num_player row by 33 column DataFrame with all zeros
    #player_df = pd.DataFrame(np.zeros((num_players, ((32*(end_year-start_year))+1))))
    
    player_df_col = []
    player_df_stats = ['gamesPlayed','groundOuts','airOuts','runs','doubles','triples','homeRuns','strikeOuts','baseOnBalls','intentionalWalks','hits','hitByPitch','avg','atBats','obp','slg','ops','caughtStealing','stolenBases','stolenBasePercentage','groundIntoDoublePlay','numberOfPitches','plateAppearances','totalBases','rbi','leftOnBase','sacBunts','sacFlies','babip','groundOutsToAirouts','catchersInterference','atBatsPerHomeRun']

    # Create column names for the player_df DataFrame
    for season_col in range(start_year, end_year+1):
        for stat in player_df_stats:
            player_df_col.append(f"{season_col} {stat}")
    player_df_col.append('player')

    # Add column for y value, since training
    player_df_col.append(f"{end_year} OPS")

    # Create an empty DataFrame with the correct columns
    player_df = pd.DataFrame(columns=player_df_col)

    # Assign the column names to the DataFrame
    player_df.columns = player_df_col
            

    for player in players:
        try:
            counter += 1

            # Add a new row for the current player
            player_df = pd.concat([player_df, pd.DataFrame([{col: 0 for col in player_df.columns}])], ignore_index=True)
            player_df.loc[player_df.index[-1], 'player'] = player
            
            try:
                player_id = next(x['id'] for x in statsapi.get('sports_players', {'season': end_year+1, 'gameType': 'W'})['people'] if x['fullName'] == player)
                print(f"Player ID found for {player}")
            except StopIteration:
                print(f"Player ID not found for {player}. Skipping.")
                continue

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
                        player_df.loc[player_df['player'] == player, player_df_col] = 0

            # Get 2024 OPS for player, expected value
            season_stats_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=season&season=2024&group=hitting"
            response = requests.get(season_stats_url)
            if response.status_code == 200:
                season_stats = response.json()
            else:
                season_stats = {}
                print(f"Failed to retrieve season stats for {player}. HTTP Status Code: {response.status_code}")
            if season_stats and 'stats' in season_stats and len(season_stats['stats']) > 0:
                ops = season_stats['stats'][0]['splits'][0]['stat'].get('ops', 0)
                player_df.loc[player_df['player'] == player,f"{end_year} OPS"] = ops
            else:
                player_df.loc[player_df['player'] == player,f"{end_year} OPS"] = 0

            print("Player ", counter+1, " out of ", num_players, " : ", player)

            #df = pd.concat([df, pd.DataFrame([stats_dict])], ignore_index=True)
        except StopIteration:
            print(f"Player {player} not found in the {end_year} season.")
        except Exception as e:
            print(f"Error retrieving stats for {player}: {e}")


    # Fix unsupported types
    player_df.fillna(0, inplace=True)
    player_df.replace(['---', '-.--','.---'], 0, inplace=True)

    print("Player df head: ", player_df.head())

    # Convert 'player' column into a numeric representation using hashing
    def convert_player_to_numeric(player_name):
        # Use a hash function to generate a numeric representation
        hash_object = hashlib.md5(player_name.encode())  # MD5 hash
        hash_value = int(hash_object.hexdigest(), 16)  # Convert hash to an integer
        return hash_value % 1e6  # Reduce the size of the number to avoid overflow

    player_df['player'] = player_df['player'].astype(str)  # Ensure player names are strings
    player_df['player_numeric'] = player_df['player'].apply(convert_player_to_numeric).astype('float32')

    # Drop the original 'player' column
    player_df.drop(columns=['player'], inplace=True)

    player_df.to_csv('/Users/zach/Projects/leadoffAI/statload_test_seasonal.csv', index=False)
    return player_df


def get_player_training_data(data, expected_value_column):

    # Check if '2024 OPS' column exists
    if expected_value_column not in data.columns:
        raise ValueError("The dataset does not contain a ", expected_value_column, " column.")

    # Define features (X) and target (y)
    X = data.drop(columns=[f"{end_year} OPS"])
    y = data[f"{end_year} OPS"]

    # Split the data into 80/20 train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Data split and saved successfully.")

    return X_train, X_test, y_train, y_test


def save_data_to_csv(df, file_path):
    """
    Save the DataFrame to a CSV file.
    """
    try:
        df.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")


if __name__ == "__main__":
    # Get player training data
    df = get_player_training_data_ops()

    # Save the DataFrame to a CSV file
    save_data_to_csv(df, '/Users/zach/Projects/leadoffAI/combined_player_data_ops_seasonal.csv')

    # Define expected value column
    expected_value_column = f"{end_year} OPS"

    # Get player training data with train/test split
    X_train, X_test, y_train, y_test = get_player_training_data(df, expected_value_column)

    # Save the training and testing data to CSV files
    save_data_to_csv(X_train, '/Users/zach/Projects/leadoffAI/X_train_seasonal.csv')
    save_data_to_csv(X_test, '/Users/zach/Projects/leadoffAI/X_test_seasonal.csv')
    save_data_to_csv(y_train, '/Users/zach/Projects/leadoffAI/y_train_seasonal.csv')
    save_data_to_csv(y_test, '/Users/zach/Projects/leadoffAI/y_test_seasonal.csv')
