import statsapi
import pandas as pd
import requests

def get_player_training_data():
    players = []
    try:
        all_players = statsapi.get('sports_players', {'season': 2022, 'gameType': 'W'})['people']
        players = [player['fullName'] for player in all_players[:1000]]
    except Exception as e:
        print(f"Error retrieving player list: {e}")

    data = {
        'player': ['Chase "Silver Fox" Utley, 2B (2003-2018)'],
        'gamesPlayed': [1937],
        'groundOuts': [1734],
        'airOuts': [2123],
        'runs': [1103],
        'doubles': [411],
        'triples': [58],
        'homeRuns': [259],
        'strikeOuts': [1193],
        'baseOnBalls': [724],
        'intentionalWalks': [62],
        'hits': [1885],
        'hitByPitch': [204],
        'avg': [.275],
        'atBats': [6857],
        'obp': [.358],
        'slg': [.465],
        'ops': [.823],
        'caughtStealing': [22],
        'stolenBases': [154],
        'stolenBasePercentage': [.875],
        'groundIntoDoublePlay': [93],
        'numberOfPitches': [30993],
        'plateAppearances': [7863],
        'totalBases': [3189],
        'rbi': [1025],
        'leftOnBase': [2790],
        'sacBunts': [6],
        'sacFlies': [72],
        'babip': [.297],
        'groundOutsToAirouts': [0.82],
        'catchersInterference': [0],
        'atBatsPerHomeRun': [26.48]
    }

    df = pd.DataFrame(data)
    counter = 0

    for player in players:
        try:
            counter += 1
            player_id = next(x['id'] for x in statsapi.get('sports_players', {'season': 2022, 'gameType': 'W'})['people'] if x['fullName'] == player)
            career_stats = statsapi.player_stats(player_id, 'hitting', 'career')
            #season_stats = statsapi.player_stats(player_id, 'hitting', 'season', season=2024)
            season_stats_url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=season&season=2024&group=hitting"
            response = requests.get(season_stats_url)
            if response.status_code == 200:
                season_stats = response.json()
            else:
                season_stats = {}
                print(f"Failed to retrieve season stats for {player}. HTTP Status Code: {response.status_code}")
            #print("Career stats: ", career_stats)
            #print("Season stats: ", season_stats)
            stats_dict = {'player': player}
            career_stats = {stat.split(': ')[0]: stat.split(': ')[1] for stat in career_stats.split('\n') if ': ' in stat}
            stats_dict.update(career_stats)
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
    df.fillna(0, inplace=True)
    df.replace(['---', '-.--','.---'], 0, inplace=True)

    df.to_csv('/Users/zach/Projects/leadoffAI/statload_test.csv', index=False)


if __name__ == "__main__":
    get_player_training_data()
    print("Player data loaded successfully.")
