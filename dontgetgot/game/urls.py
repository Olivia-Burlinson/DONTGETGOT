from django.urls import path
from . import views

app_name = 'game'

urlpatterns = [
    # Games
    path('games/create/', views.create_game, name='create_game'),
    path('games/<str:code>/', views.get_game, name='get_game'),
    path('games/<str:code>/leaderboard/', views.get_leaderboard, name='leaderboard'),

    # Players
    path('players/join/', views.join_game, name='join_game'),
    path('players/<int:player_id>/', views.get_player, name='get_player'),
    path('players/<int:player_id>/missions/assign/', views.assign_missions, name='assign_missions'),
    path('players/catch/', views.catch_player, name='catch_player'),

    # Missions
    path('missions/<int:mission_id>/complete/', views.complete_mission, name='complete_mission'),
]