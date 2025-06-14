from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class PredictedStats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='predicted_stats')
    OPS = models.FloatField(default=0)
    K = models.FloatField(default=0)
    AB = models.FloatField(default=0)

    def __str__(self):
        return f"{self.player.name}'s Predicted Stats for {self.year}"

    def as_dict(self):
        return {
            'OPS': self.points,
            'K': self.assists,
            'AB': self.rebounds
        }

class HistoricalStats(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='historical_stats')
    year = models.CharField(max_length=4)
    OPS = models.FloatField(default=0)
    K = models.FloatField(default=0)
    AB = models.FloatField(default=0)

    class Meta:
        ordering = ['-year']

    def __str__(self):
        return f"{self.player.name}'s Stats for {self.year}"