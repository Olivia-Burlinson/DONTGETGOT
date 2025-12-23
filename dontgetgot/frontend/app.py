from nicegui import ui
import requests

API_URL = 'http://localhost:8000/api'

class GameState:
    def __init__(self):
        self.current_player = None

state = GameState()

@ui.page('/')
def main_page():
    ui.label('🎯 Don\'t Get Got!').classes('text-4xl font-bold mb-4')

    with ui.card().classes('w-96 p-6'):
        ui.label('Create New Game').classes('text-2xl mb-4')
        game_name = ui.input('Game Name').classes('w-full')

        def create():
            r = requests.post(f'{API_URL}/games/create/', json={'name': game_name.value})
            data = r.json()
            if data['success']:
                ui.notify(f"Game created! Code: {data['game']['code']}")
                ui.navigate.to(f"/game/{data['game']['code']}")

        ui.button('Create', on_click=create).classes('w-full')

    with ui.card().classes('w-96 p-6 mt-4'):
        ui.label('Join Game').classes('text-2xl mb-4')
        code = ui.input('Game Code').classes('w-full')
        name = ui.input('Your Name').classes('w-full')

        def join():
            r = requests.post(f'{API_URL}/players/join/',
                              json={'game_code': code.value, 'name': name.value})
            data = r.json()
            if data['success']:
                state.current_player = data['player']
                ui.navigate.to(f"/play/{data['player']['id']}")

        ui.button('Join', on_click=join).classes('w-full')

@ui.page('/game/{code}')
def game_lobby(code: str):
    r = requests.get(f'{API_URL}/games/{code}/')
    data = r.json()

    if not data['success']:
        ui.label('Game not found')
        return

    game = data['game']
    ui.label(f"🎮 {game['name']}").classes('text-3xl mb-2')
    ui.label(f"Code: {game['code']}").classes('text-xl text-blue-600')

    with ui.column():
        for player in game['players']:
            ui.label(f"👤 {player['name']} - {player['score']} pts")

@ui.page('/play/{player_id}')
def play_game(player_id: int):
    r = requests.get(f'{API_URL}/players/{player_id}/')
    data = r.json()

    if not data['success']:
        ui.label('Player not found')
        return

    player = data['player']
    ui.label(f"👤 {player['name']}").classes('text-3xl')
    ui.label(f"Score: {player['score']}").classes('text-xl')

    with ui.column():
        if not player['missions']:
            def assign():
                requests.post(f"{API_URL}/players/{player_id}/missions/assign/")
                ui.navigate.reload()
            ui.button('Get Missions', on_click=assign)
        else:
            for m in player['missions']:
                with ui.card():
                    ui.label(f"{m['text']} ({m['points']} pts)")
                    if m['status'] == 'active':
                        def complete(mid=m['id']):
                            requests.post(f"{API_URL}/missions/{mid}/complete/")
                            ui.navigate.reload()
                        ui.button('Complete', on_click=complete)

if __name__ == '__main__':
    ui.run(port=8080)