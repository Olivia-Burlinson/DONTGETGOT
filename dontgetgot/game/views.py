
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import date
import json
import random
from .models import Game, Player, Mission, PlayerMission

def get_json_body(request):
    """Helper to parse JSON request body"""
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return {}

# Game Views
@csrf_exempt
@require_http_methods(["POST"])
def create_game(request):
    data = get_json_body(request)
    name = data.get('name', 'Untitled Game')

    code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    while Game.objects.filter(code=code).exists():
        code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))

    game = Game.objects.create(code=code, name=name)

    return JsonResponse({
        'success': True,
        'game': {
            'id': game.id,
            'code': game.code,
            'name': game.name,
            'created_at': game.created_at.isoformat(),
        }
    }, status=201)

@require_http_methods(["GET"])
def get_game(request, code):
    try:
        game = Game.objects.get(code=code.upper())
        players = game.players.all()

        return JsonResponse({
            'success': True,
            'game': {
                'id': game.id,
                'code': game.code,
                'name': game.name,
                'created_at': game.created_at.isoformat(),
                'is_active': game.is_active,
                'players': [{'id': p.id, 'name': p.name, 'score': p.score} for p in players]
            }
        })
    except Game.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Game not found'}, status=404)

# Player Views
@csrf_exempt
@require_http_methods(["POST"])
def join_game(request):
    data = get_json_body(request)
    game_code = data.get('game_code', '').upper()
    player_name = data.get('name', '')

    if not game_code or not player_name:
        return JsonResponse({'success': False, 'error': 'game_code and name required'}, status=400)

    try:
        game = Game.objects.get(code=game_code, is_active=True)
        player, created = Player.objects.get_or_create(game=game, name=player_name)

        return JsonResponse({
            'success': True,
            'player': {
                'id': player.id,
                'name': player.name,
                'score': player.score,
                'game_code': game.code
            }
        }, status=201 if created else 200)
    except Game.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Game not found'}, status=404)

@require_http_methods(["GET"])
def get_player(request, player_id):
    try:
        player = Player.objects.select_related('game').get(id=player_id)
        missions = player.missions.select_related('mission').all()

        return JsonResponse({
            'success': True,
            'player': {
                'id': player.id,
                'name': player.name,
                'score': player.score,
                'game': {'code': player.game.code, 'name': player.game.name},
                'missions': [{
                    'id': pm.id,
                    'text': pm.mission.text,
                    'difficulty': pm.mission.difficulty,
                    'points': pm.mission.points,
                    'status': pm.status,
                    'is_daily': pm.mission.is_daily
                } for pm in missions]
            }
        })
    except Player.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Player not found'}, status=404)

# Mission Views
@csrf_exempt
@require_http_methods(["POST"])
def assign_missions(request, player_id):
    try:
        player = Player.objects.get(id=player_id)
        data = get_json_body(request)
        count = data.get('count', 3)

        available = Mission.objects.filter(is_daily=False).exclude(playermission__player=player)
        daily = Mission.objects.filter(is_daily=True, date=date.today()).first()

        missions = list(available.order_by('?')[:count])
        if daily:
            missions.append(daily)

        assigned = []
        for mission in missions:
            pm, created = PlayerMission.objects.get_or_create(player=player, mission=mission)
            if created:
                assigned.append(pm)

        return JsonResponse({
            'success': True,
            'assigned_count': len(assigned),
            'missions': [{'id': pm.id, 'text': pm.mission.text, 'points': pm.mission.points} for pm in assigned]
        })
    except Player.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Player not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def complete_mission(request, mission_id):
    try:
        pm = PlayerMission.objects.select_related('player', 'mission').get(id=mission_id)

        if pm.status != 'active':
            return JsonResponse({'success': False, 'error': f'Mission is {pm.status}'}, status=400)

        pm.status = 'completed'
        pm.completed_at = timezone.now()
        pm.save()

        pm.player.score += pm.mission.points
        pm.player.save()

        return JsonResponse({
            'success': True,
            'points_earned': pm.mission.points,
            'new_score': pm.player.score
        })
    except PlayerMission.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Mission not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def catch_player(request):
    data = get_json_body(request)
    catcher_id = data.get('catcher_id')
    caught_name = data.get('caught_player_name')
    mission_hint = data.get('mission_hint', '')

    try:
        catcher = Player.objects.get(id=catcher_id)
        caught_player = Player.objects.get(game=catcher.game, name=caught_name)

        pm = PlayerMission.objects.filter(
            player=caught_player,
            status='active',
            mission__text__icontains=mission_hint
        ).first()

        if not pm:
            return JsonResponse({'success': False, 'error': 'No matching mission'}, status=404)

        pm.status = 'caught'
        pm.caught_by = catcher
        pm.save()

        points = pm.mission.points // 2
        catcher.score += points
        catcher.save()

        return JsonResponse({
            'success': True,
            'points_earned': points,
            'catcher_new_score': catcher.score
        })
    except Player.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Player not found'}, status=404)

@require_http_methods(["GET"])
def get_leaderboard(request, code):
    try:
        game = Game.objects.get(code=code.upper())
        players = game.players.order_by('-score', 'name')

        return JsonResponse({
            'success': True,
            'leaderboard': [{
                'rank': idx + 1,
                'name': p.name,
                'score': p.score
            } for idx, p in enumerate(players)]
        })
    except Game.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Game not found'}, status=404)
