import sqlite3
import pandas as pd

def csv_to_table():

    # Load the CSV into a DataFrame
    df = pd.read_csv('combined_player_data_ops_seasonal.csv')
    
    # Drop the 'predicted_ops' column from the DataFrame
    if '2024 OPS' in df.columns:
        df = df.drop(columns=['2024 OPS'])

    # Connect to the SQLite database (or create it)
    conn = sqlite3.connect('leadoffAI.db')

    # Write the DataFrame to a new SQLite table
    df.to_sql('player_stats_table', conn, if_exists='replace', index=False)

    # Optional: read back the data
    result = pd.read_sql('SELECT * FROM player_stats_table', conn)
    print(result.head())

    # Close the connection
    conn.close()


if __name__ == "__main__":
    csv_to_table()