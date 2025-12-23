from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    # Players
    path('players/create/', views.create_player, name='create_player'),
    path('players/<int:player_id>/', views.get_player, name='get_player'),
    path('players/<int:player_id>/rank/', views.get_player_rank, name='player_rank'),
    path('players/<int:player_id>/missions/assign/', views.assign_missions, name='assign_missions'),
    path('players/catch/', views.catch_player, name='catch_player'),

    # Leaderboard
    path('leaderboard/', views.get_leaderboard, name='leaderboard'),

    # Missions
    path('missions/<int:mission_id>/complete/', views.complete_mission, name='complete_mission'),
    path('missions/stats/', views.get_mission_stats, name='mission_stats'),
]