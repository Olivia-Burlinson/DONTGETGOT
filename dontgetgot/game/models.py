from django.db import models
from django.utils import timezone

class Game(models.Model):
    code = models.CharField(max_length=6, unique=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        ordering = ['-created_at']

class Player(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='players')
    name = models.CharField(max_length=50)
    score = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['game', 'name']
        ordering = ['-score', 'name']

    def __str__(self):
        return f"{self.name} in {self.game.code}"

class Mission(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    points = models.IntegerField()
    is_daily = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.text[:50]}..."

    class Meta:
        ordering = ['difficulty', 'points']

class PlayerMission(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('caught', 'Caught'),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='missions')
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    caught_by = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='catches')

    class Meta:
        unique_together = ['player', 'mission']
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.player.name} - {self.mission.text[:30]}"