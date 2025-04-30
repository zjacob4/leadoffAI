"""
URL configuration for player_stats_project project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('player_stats.urls')),  # Include the player_stats app URLs
]