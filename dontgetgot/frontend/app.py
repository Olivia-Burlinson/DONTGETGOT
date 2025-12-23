from nicegui import ui
import requests
from datetime import datetime

API_URL = 'http://localhost:8080/api'

class GameState:
    def __init__(self):
        self.current_player = None

state = GameState()

def format_time_ago(iso_string):
    """Format timestamp to relative time"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        diff = datetime.now(dt.tzinfo) - dt

        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "just now"
    except:
        return ""

@ui.page('/')
def main_page():
    ui.colors(primary='#6366f1')

    with ui.column().classes('w-full items-center p-8'):
        ui.label('🎯 Don\'t Get Got!').classes('text-5xl font-bold mb-2')
        ui.label('Global Social Deduction Game').classes('text-xl text-gray-600 mb-8')

        with ui.card().classes('w-96 p-6'):
            ui.label('Enter Your Name').classes('text-2xl mb-4')
            name_input = ui.input('Player Name', placeholder='Enter your name').classes('w-full mb-4')

            def join_game():
                if name_input.value:
                    r = requests.post(f'{API_URL}/players/create/', json={'name': name_input.value})
                    data = r.json()
                    if data['success']:
                        state.current_player = data['player']
                        ui.notify(f"Welcome, {data['player']['name']}!" if data['created'] else f"Welcome back, {data['player']['name']}!")
                        ui.navigate.to(f"/play/{data['player']['id']}")
                    else:
                        ui.notify(data['error'], type='negative')

            ui.button('Join Game', on_click=join_game).classes('w-full')

        ui.button('View Leaderboard 🏆', on_click=lambda: ui.navigate.to('/leaderboard')).classes('mt-4')

@ui.page('/play/{player_id}')
def play_game(player_id: int):
    ui.colors(primary='#6366f1')

    missions_container = ui.column().classes('w-full')
    stats_container = ui.row().classes('w-full gap-4 mb-6')

    def refresh():
        r = requests.get(f'{API_URL}/players/{player_id}/')
        data = r.json()

        if not data['success']:
            ui.notify('Player not found', type='negative')
            return

        player = data['player']
        state.current_player = player

        # Update stats
        stats_container.clear()
        with stats_container:
            with ui.card().classes('flex-1 p-4'):
                ui.label('Score').classes('text-sm text-gray-600')
                ui.label(str(player['score'])).classes('text-3xl font-bold text-green-600')
            with ui.card().classes('flex-1 p-4'):
                ui.label('Completed').classes('text-sm text-gray-600')
                ui.label(str(player['stats']['completed'])).classes('text-3xl font-bold text-blue-600')
            with ui.card().classes('flex-1 p-4'):
                ui.label('Catches').classes('text-sm text-gray-600')
                ui.label(str(player['stats']['catches'])).classes('text-3xl font-bold text-purple-600')

        # Update missions
        missions_container.clear()
        with missions_container:
            ui.label('🎯 Your Missions').classes('text-3xl font-bold mb-4')

            if not player['missions']:
                ui.label('No missions assigned yet!').classes('text-gray-600 mb-4')
                ui.button('Get Missions', on_click=lambda: [assign_missions(), refresh()]).classes('mb-4')
            else:
                active = [m for m in player['missions'] if m['status'] == 'active']
                completed = [m for m in player['missions'] if m['status'] == 'completed']
                caught = [m for m in player['missions'] if m['status'] == 'caught']

                if active:
                    ui.label('Active Missions').classes('text-xl font-bold mb-2 mt-4')
                    for m in active:
                        with ui.card().classes('w-full max-w-2xl p-4 mb-3 border-l-4 border-blue-500'):
                            with ui.row().classes('w-full items-center justify-between'):
                                with ui.column().classes('flex-1'):
                                    ui.label(m['text']).classes('font-bold text-lg')
                                    ui.label(f"🎖️ {m['points']} pts • {m['difficulty'].title()} {'• 🌟 Daily' if m['is_daily'] else ''}").classes('text-sm text-gray-600')
                                ui.button('✅ Complete', on_click=lambda mid=m['id']: [complete_mission(mid), refresh()]).props('flat color=positive')

                if completed:
                    ui.label('Completed Missions').classes('text-xl font-bold mb-2 mt-6')
                    for m in completed:
                        with ui.card().classes('w-full max-w-2xl p-4 mb-2 bg-green-50'):
                            ui.label(f"✅ {m['text']}").classes('text-green-800')
                            ui.label(f"Completed {format_time_ago(m['completed_at'])} • +{m['points']} pts").classes('text-sm text-green-600')

                if caught:
                    ui.label('Caught Missions').classes('text-xl font-bold mb-2 mt-6')
                    for m in caught:
                        with ui.card().classes('w-full max-w-2xl p-4 mb-2 bg-red-50'):
                            ui.label(f"❌ {m['text']}").classes('text-red-800')
                            ui.label(f"Caught by {m['caught_by']}").classes('text-sm text-red-600')

    def assign_missions():
        requests.post(f"{API_URL}/players/{player_id}/missions/assign/")
        ui.notify('New missions assigned!', type='positive')

    def complete_mission(mid):
        r = requests.post(f"{API_URL}/missions/{mid}/complete/")
        data = r.json()
        if data['success']:
            ui.notify(data['message'], type='positive')

    with ui.column().classes('w-full items-center p-8'):
        with ui.row().classes('w-full max-w-4xl justify-between mb-6'):
            with ui.column():
                ui.label('').bind_text_from(state.current_player, 'name', backward=lambda n: f"👤 {n}").classes('text-3xl font-bold')
            with ui.row().classes('gap-2'):
                ui.button('🏆 Leaderboard', on_click=lambda: ui.navigate.to('/leaderboard')).props('flat')
                ui.button('🔄 Refresh', on_click=refresh).props('flat')

        with ui.column().classes('w-full max-w-4xl'):
            stats_container
            missions_container

            with ui.card().classes('w-full p-6 mt-6'):
                ui.label('🚨 Catch Someone!').classes('text-2xl font-bold mb-4')
                with ui.row().classes('w-full gap-2'):
                    catch_name = ui.input('Player Name', placeholder='Who did you catch?').classes('flex-1')
                    catch_mission = ui.input('Mission Hint', placeholder='What were they doing?').classes('flex-1')

                def attempt_catch():
                    if catch_name.value and catch_mission.value:
                        r = requests.post(f"{API_URL}/players/catch/", json={
                            'catcher_id': player_id,
                            'caught_player_name': catch_name.value,
                            'mission_hint': catch_mission.value
                        })
                        data = r.json()
                        ui.notify(data.get('message', data.get('error')), type='positive' if data['success'] else 'negative')
                        if data['success']:
                            catch_name.value = ''
                            catch_mission.value = ''
                            refresh()

                ui.button('Report Catch!', on_click=attempt_catch).classes('w-full')

    refresh()

@ui.page('/leaderboard')
def leaderboard_page():
    ui.colors(primary='#6366f1')

    leaderboard_container = ui.column().classes('w-full')

    def load_leaderboard():
        r = requests.get(f'{API_URL}/leaderboard/')
        data = r.json()
        leaderboard_container.clear()
        with leaderboard_container:
            ui.label('🏆 Global Leaderboard').classes('text-4xl font-bold mb-2')
            ui.label(f"Total Players: {data['total_players']}").classes('text-gray-600 mb-6')

            for entry in data['leaderboard']:
                medal = '🥇' if entry['rank'] == 1 else '🥈' if entry['rank'] == 2 else '🥉' if entry['rank'] == 3 else f"#{entry['rank']}"

                with ui.card().classes('w-full max-w-3xl p-4 mb-2'):
                    with ui.row().classes('w-full items-center gap-4'):
                        ui.label(medal).classes('text-3xl font-bold w-16')
                        with ui.column().classes('flex-1'):
                            ui.label(entry['name']).classes('text-xl font-bold')
                            ui.label(f"{entry['completed']} completed • {entry['catches']} catches • Active {format_time_ago(entry['last_active'])}").classes('text-sm text-gray-600')
                        ui.label(f"{entry['score']} pts").classes('text-2xl font-bold text-green-600')

        with ui.column().classes('w-full items-center p-8'):
            with ui.row().classes('w-full max-w-3xl justify-between mb-6'):
                ui.label('')
                with ui.row().classes('gap-2'):
                    ui.button('🏠 Home', on_click=lambda: ui.navigate.to('/')).props('flat')
                    ui.button('🔄 Refresh', on_click=load_leaderboard).props('flat')

            leaderboard_container

        load_leaderboard()

ui.run(port=8080, title="Don't Get Got!")