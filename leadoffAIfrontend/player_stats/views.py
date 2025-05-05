from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
import random
import hashlib

from .models import Player, PredictedStats, HistoricalStats
from .forms import PlayerSearchForm

def player_stats_explorer(request):
    form = PlayerSearchForm(request.GET or None)
    selected_player = None
    predicted_stats = {}
    historical_stats = []
    error = None

    if form.is_valid() and 'search_query' in request.GET and request.GET.get('search_query'):
        search_query = form.cleaned_data['search_query']
        print(f"Search query: {search_query}")

        # Try to find the player in the database
        try:
            player = Player.objects.filter(name__icontains=search_query).first()

            if player:
                selected_player = player.name

                # Get predicted stats
                try:
                    stats = player.predicted_stats
                    predicted_stats = stats.as_dict()
                except PredictedStats.DoesNotExist:
                    # Create mock predicted stats if not found
                    predicted_stats = {
                        'points': 23.7 + random.random() * 5,
                        'assists': 5.8 + random.random() * 2,
                        'rebounds': 4.5 + random.random() * 3,
                        'steals': 1.2 + random.random() * 0.8,
                        'blocks': 0.7 + random.random() * 0.6,
                    }

                # Get historical stats
                # Convert player name to numeric ID
                # Use a hash function to generate a numeric representation
                hash_object = hashlib.md5(player.name.encode())  # MD5 hash
                hash_value = int(hash_object.hexdigest(), 16)  # Convert hash to an integer
                player_id = hash_value % 1e6  # Reduce the size of the number to avoid overflow
                #player_id = hash_value % 1_000_000  # Use an integer divisor

                #player_historical_stats = player_id.historical_stats.all()
                player_historical_stats = player.historical_stats.all()
                print("Player historical stats:", player_historical_stats)

                if player_historical_stats:
                    historical_stats = player_historical_stats
                else:
                    # Create mock historical stats if not found
                    historical_stats = [
                        {
                            'year': '2023',
                            'points': 22.3 + random.random() * 4,
                            'assists': 5.5 + random.random() * 1.5,
                            'rebounds': 4.2 + random.random() * 2,
                        },
                        {
                            'year': '2022',
                            'points': 21.1 + random.random() * 3,
                            'assists': 5.0 + random.random() * 1.2,
                            'rebounds': 4.0 + random.random() * 1.5,
                        },
                        {
                            'year': '2021',
                            'points': 19.8 + random.random() * 2.5,
                            'assists': 4.7 + random.random() * 1,
                            'rebounds': 3.8 + random.random() * 1.2,
                        },
                    ]
            else:
                # Create mock data for demonstration
                selected_player = search_query
                predicted_stats = {
                    'points': 23.7 + random.random() * 5,
                    'assists': 5.8 + random.random() * 2,
                    'rebounds': 4.5 + random.random() * 3,
                    'steals': 1.2 + random.random() * 0.8,
                    'blocks': 0.7 + random.random() * 0.6,
                }
                historical_stats = [
                    {
                        'year': '2023',
                        'points': 22.3 + random.random() * 4,
                        'assists': 5.5 + random.random() * 1.5,
                        'rebounds': 4.2 + random.random() * 2,
                    },
                    {
                        'year': '2022',
                        'points': 21.1 + random.random() * 3,
                        'assists': 5.0 + random.random() * 1.2,
                        'rebounds': 4.0 + random.random() * 1.5,
                    },
                    {
                        'year': '2021',
                        'points': 19.8 + random.random() * 2.5,
                        'assists': 4.7 + random.random() * 1,
                        'rebounds': 3.8 + random.random() * 1.2,
                    },
                ]
        except Exception as e:
            error = f"An error occurred: {str(e)}"
    else:
        # Default data for initial page load
        predicted_stats = {
            'OPS': 25.4,
            'K': 6.2,
            'AB': 5.1,
        }
        
        historical_stats = [
            {
                'year': '2023',
                'OPS': 24.1,
                'K': 5.8,
                'AB': 4.9,
            },
            {
                'year': '2022',
                'OPS': 22.3,
                'K': 5.2,
                'AB': 4.5,
            },
            {
                'year': '2021',
                'OPS': 20.8,
                'K': 4.9,
                'AB': 4.2,
            },
        ]

    context = {
        'form': form,
        'selected_player': selected_player,
        'predicted_stats': predicted_stats,
        'historical_stats': historical_stats,
        'error': error,
    }

    return render(request, 'player_stats_explorer.html', context)

def search_player_api(request):
    """API endpoint for searching players"""
    search_query = request.GET.get('q', '')
    if not search_query:
        return JsonResponse({'error': 'No search query provided'}, status=400)

    players = Player.objects.filter(name__icontains=search_query)[:10]
    results = [{'id': player.id, 'name': player.name} for player in players]

    return JsonResponse({'results': results})