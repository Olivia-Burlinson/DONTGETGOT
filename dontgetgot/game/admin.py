from django.contrib import admin
from .models import Player, Mission, PlayerMission

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'score', 'completed_missions_count', 'catches_count', 'joined_at', 'last_active']
    search_fields = ['name']
    readonly_fields = ['joined_at', 'last_active']

    def completed_missions_count(self, obj):
        return obj.completed_missions_count
    completed_missions_count.short_description = 'Completed'

    def catches_count(self, obj):
        return obj.catches_count
    catches_count.short_description = 'Catches'

@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ['text_preview', 'difficulty', 'points', 'is_daily', 'date', 'times_completed', 'times_caught']
    list_filter = ['difficulty', 'is_daily']
    search_fields = ['text']

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Mission Text'

@admin.register(PlayerMission)
class PlayerMissionAdmin(admin.ModelAdmin):
    list_display = ['player', 'mission_preview', 'status', 'assigned_at', 'completed_at']
    list_filter = ['status', 'assigned_at']
    search_fields = ['player__name', 'mission__text']

    def mission_preview(self, obj):
        return obj.mission.text[:40] + '...' if len(obj.mission.text) > 40 else obj.mission.text
    mission_preview.short_description = 'Mission'
