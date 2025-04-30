from django.urls import path
from . import views

urlpatterns = [
    path('', views.player_stats_explorer, name='player_stats_explorer'),
    path('api/search-player/', views.search_player_api, name='search_player_api'),
]