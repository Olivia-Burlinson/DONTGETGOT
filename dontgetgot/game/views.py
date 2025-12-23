from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Q
from datetime import date
import json
from .models import Player, Mission, PlayerMission

def get_json_body(request):
    """Helper to parse JSON request body"""
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return {}

# Player Views
@csrf_exempt
@require_http_methods(["POST"])
def create_player(request):
    """Create or get a player (global game)"""
    data = get_json_body(request)
    player_name = data.get('name', '')

    if not player_name:
        return JsonResponse({'success': False, 'error': 'name is required'}, status=400)

    player, created = Player.objects.get_or_create(name=player_name)

    return JsonResponse({
        'success': True,
        'player': {
            'id': player.id,
            'name': player.name,
            'score': player.score,
            'joined_at': player.joined_at.isoformat()
        },
        'created': created
    }, status=201 if created else 200)

@require_http_methods(["GET"])
def get_player(request, player_id):
    """Get player details including missions"""
    try:
        player = Player.objects.get(id=player_id)
        missions = player.missions.select_related('mission').all()

        return JsonResponse({
            'success': True,
            'player': {
                'id': player.id,
                'name': player.name,
                'score': player.score,
                'missions': [{
                    'id': pm.id,
                    'text': pm.mission.text,
                    'difficulty': pm.mission.difficulty,
                    'points': pm.mission.points,
                    'status': pm.status,
                    'is_daily': pm.mission.is_daily,
                    'assigned_at': pm.assigned_at.isoformat(),
                    'completed_at': pm.completed_at.isoformat() if pm.completed_at else None,
                    'caught_by': pm.caught_by.name if pm.caught_by else None
                } for pm in missions],
                'stats': {
                    'completed': player.completed_missions_count,
                    'caught': player.caught_missions_count,
                    'active': player.active_missions_count,
                    'catches': player.catches_count
                }
            }
        })
    except Player.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Player not found'}, status=404)

@require_http_methods(["GET"])
def get_leaderboard(request):
    """Get global leaderboard with detailed stats"""
    players = Player.objects.annotate(
        completed_count=Count('missions', filter=Q(missions__status='completed')),
        caught_count=Count('missions', filter=Q(missions__status='caught')),
        catches_made=Count('catches')
    ).order_by('-score', 'name')[:50]  # Top 50 players

    return JsonResponse({
        'success': True,
        'leaderboard': [{
            'rank': idx + 1,
            'id': p.id,
            'name': p.name,
            'score': p.score,
            'completed': p.completed_count,
            'caught': p.caught_count,
            'catches': p.catches_made,
            'last_active': p.last_active.isoformat()
        } for idx, p in enumerate(players)],
        'total_players': Player.objects.count()
    })

@require_http_methods(["GET"])
def get_player_rank(request, player_id):
    """Get a specific player's rank"""
    try:
        player = Player.objects.get(id=player_id)
        rank = Player.objects.filter(
            Q(score__gt=player.score) |
            Q(score=player.score, name__lt=player.name)
        ).count() + 1

        return JsonResponse({
            'success': True,
            'player': player.name,
            'rank': rank,
            'score': player.score,
            'total_players': Player.objects.count()
        })
    except Player.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Player not found'}, status=404)

# Mission Views
@csrf_exempt
@require_http_methods(["POST"])
def assign_missions(request, player_id):
    """Assign missions to a player"""
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
            'missions': [{
                'id': pm.id,
                'text': pm.mission.text,
                'points': pm.mission.points,
                'difficulty': pm.mission.difficulty
            } for pm in assigned]
        })
    except Player.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Player not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def complete_mission(request, mission_id):
    """Mark a mission as completed"""
    try:
        pm = PlayerMission.objects.select_related('player', 'mission').get(id=mission_id)

        if pm.status != 'active':
            return JsonResponse({'success': False, 'error': f'Mission is {pm.status}'}, status=400)

        pm.status = 'completed'
        pm.completed_at = timezone.now()
        pm.save()

        pm.player.score += pm.mission.points
        pm.player.save()

        pm.mission.times_completed += 1
        pm.mission.save()

        return JsonResponse({
            'success': True,
            'message': f'Mission completed! +{pm.mission.points} points',
            'points_earned': pm.mission.points,
            'new_score': pm.player.score
        })
    except PlayerMission.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Mission not found'}, status=404)

@csrf_exempt
@require_http_methods(["POST"])
def catch_player(request):
    """Catch another player attempting their mission"""
    data = get_json_body(request)
    catcher_id = data.get('catcher_id')
    caught_name = data.get('caught_player_name')
    mission_hint = data.get('mission_hint', '')

    if not all([catcher_id, caught_name]):
        return JsonResponse({
            'success': False,
            'error': 'catcher_id and caught_player_name required'
        }, status=400)

    try:
        catcher = Player.objects.get(id=catcher_id)
        caught_player = Player.objects.get(name=caught_name)

        if catcher.id == caught_player.id:
            return JsonResponse({'success': False, 'error': 'Cannot catch yourself'}, status=400)

        pm = PlayerMission.objects.filter(
            player=caught_player,
            status='active',
            mission__text__icontains=mission_hint
        ).first()

        if not pm:
            return JsonResponse({'success': False, 'error': 'No matching mission found'}, status=404)

        pm.status = 'caught'
        pm.caught_by = catcher
        pm.save()

        points = pm.mission.points // 2
        catcher.score += points
        catcher.save()

        pm.mission.times_caught += 1
        pm.mission.save()

        return JsonResponse({
            'success': True,
            'message': f'Caught {caught_name}! +{points} points',
            'points_earned': points,
            'catcher_new_score': catcher.score,
            'caught_mission': pm.mission.text
        })
    except Player.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Player not found'}, status=404)

@require_http_methods(["GET"])
def get_mission_stats(request):
    """Get statistics about missions"""
    missions = Mission.objects.all()

    return JsonResponse({
        'success': True,
        'stats': {
            'total_missions': missions.count(),
            'total_completions': sum(m.times_completed for m in missions),
            'total_catches': sum(m.times_caught for m in missions),
            'most_completed': [{
                'text': m.text,
                'completions': m.times_completed
            } for m in missions.order_by('-times_completed')[:5]],
            'most_caught': [{
                'text': m.text,
                'catches': m.times_caught
            } for m in missions.order_by('-times_caught')[:5]]
        }
    })
