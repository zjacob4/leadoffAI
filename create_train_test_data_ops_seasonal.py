import statsapi
import pandas as pd
import requests
import pandas as pd
from sklearn.model_selection import train_test_split
import hashlib

# Load the dataset
file_path = 'statload_test.csv'

def get_player_training_data_ops():
    players = []
    try:
        all_players = statsapi.get('sports_players', {'season': 2022, 'gameType': 'W'})['people']
        players = [player['fullName'] for player in all_players[:100]]
    except Exception as e:
        print(f"Error retrieving player list: {e}")

    data = {}

    df = pd.DataFrame(data)
    counter = 0

    for player in players:
        try:
            counter += 1
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
                stats_dict['2024 OPS'] = ops
            else:
                stats_dict['2024 OPS'] = 0

            print("Player ", counter, " out of 1000")

            df = pd.concat([df, pd.DataFrame([stats_dict])], ignore_index=True)
        except StopIteration:
            print(f"Player {player} not found in the 2022 season.")
        except Exception as e:
            print(f"Error retrieving stats for {player}: {e}")


    print(df.head())

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

    df.to_csv('/Users/zach/Projects/leadoffAI/statload_test_seasonal.csv', index=False)
    return df


def get_player_training_data(data, expected_value_column):

    # Check if '2024 OPS' column exists
    if expected_value_column not in data.columns:
        raise ValueError("The dataset does not contain a ", expected_value_column, " column.")

    # Define features (X) and target (y)
    X = data.drop(columns=['2024 OPS'])
    y = data['2024 OPS']

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
    expected_value_column = '2024 OPS'

    # Get player training data with train/test split
    X_train, X_test, y_train, y_test = get_player_training_data(df, expected_value_column)

    # Save the training and testing data to CSV files
    save_data_to_csv(X_train, '/Users/zach/Projects/leadoffAI/X_train_seasonal.csv')
    save_data_to_csv(X_test, '/Users/zach/Projects/leadoffAI/X_test_seasonal.csv')
    save_data_to_csv(y_train, '/Users/zach/Projects/leadoffAI/y_train_seasonal.csv')
    save_data_to_csv(y_test, '/Users/zach/Projects/leadoffAI/y_test_seasonal.csv')
