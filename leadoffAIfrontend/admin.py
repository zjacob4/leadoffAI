from django.contrib import admin
from .models import Player, PredictedStats, HistoricalStats

class PredictedStatsInline(admin.StackedInline):
    model = PredictedStats
    can_delete = False
    verbose_name_plural = 'Predicted Stats'

class HistoricalStatsInline(admin.TabularInline):
    model = HistoricalStats
    extra = 1
    verbose_name_plural = 'Historical Stats'

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [PredictedStatsInline, HistoricalStatsInline]

@admin.register(PredictedStats)
class PredictedStatsAdmin(admin.ModelAdmin):
    list_display = ('player', 'year', 'points', 'assists', 'rebounds', 'steals', 'blocks')
    list_filter = ('year',)
    search_fields = ('player__name',)

@admin.register(HistoricalStats)
class HistoricalStatsAdmin(admin.ModelAdmin):
    list_display = ('player', 'year', 'points', 'assists', 'rebounds')
    list_filter = ('year',)
    search_fields = ('player__name',)