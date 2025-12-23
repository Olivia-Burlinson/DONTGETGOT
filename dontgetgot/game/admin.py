
from django.contrib import admin
from .models import Game, Player, Mission, PlayerMission

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at', 'is_active', 'player_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['code', 'name']

    def player_count(self, obj):
        return obj.players.count()
    player_count.short_description = 'Players'

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'game', 'score', 'joined_at']
    list_filter = ['game', 'joined_at']
    search_fields = ['name', 'game__code']

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ['text_preview', 'difficulty', 'points', 'is_daily', 'date']
    list_filter = ['difficulty', 'is_daily']
    search_fields = ['text']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Mission Text'

@admin.register(PlayerMission)
class PlayerMissionAdmin(admin.ModelAdmin):
    list_display = ['player', 'mission_preview', 'status', 'assigned_at']
    list_filter = ['status', 'assigned_at']
    search_fields = ['player__name', 'mission__text']

    def mission_preview(self, obj):
        return obj.mission.text[:40] + '...' if len(obj.mission.text) > 40 else obj.mission.text
    mission_preview.short_description = 'Mission'