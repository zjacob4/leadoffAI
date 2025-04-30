from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class PredictedStats(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE, related_name='predicted_stats')
    points = models.FloatField(default=0)
    assists = models.FloatField(default=0)
    rebounds = models.FloatField(default=0)
    steals = models.FloatField(default=0)
    blocks = models.FloatField(default=0)
    year = models.CharField(max_length=4, default="2024")

    def __str__(self):
        return f"{self.player.name}'s Predicted Stats for {self.year}"

    def as_dict(self):
        return {
            'points': self.points,
            'assists': self.assists,
            'rebounds': self.rebounds,
            'steals': self.steals,
            'blocks': self.blocks
        }

class HistoricalStats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='historical_stats')
    year = models.CharField(max_length=4)
    points = models.FloatField(default=0)
    assists = models.FloatField(default=0)
    rebounds = models.FloatField(default=0)

    class Meta:
        ordering = ['-year']

    def __str__(self):
        return f"{self.player.name}'s Stats for {self.year}"