from django.db import models
from django.utils import timezone

class Player(models.Model):
    name = models.CharField(max_length=50, unique=True)
    score = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-score', 'name']

    def __str__(self):
        return f"{self.name} ({self.score} pts)"

    @property
    def completed_missions_count(self):
        return self.missions.filter(status='completed').count()

    @property
    def caught_missions_count(self):
        return self.missions.filter(status='caught').count()

    @property
    def active_missions_count(self):
        return self.missions.filter(status='active').count()

    @property
    def catches_count(self):
        return self.catches.count()

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
    times_completed = models.IntegerField(default=0)
    times_caught = models.IntegerField(default=0)

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
