from nicegui import ui



with ui.row().classes("col-span-full").style("width: 100%; background-color: yellow; padding: 10px 0px;"):
    ui.label("Don't Get Got").style("font-size: 20px; grid-column-start: 1; margin-left: 20px;")
    ui.space().style("grid-column: 2/13")
    ui.button('Sign Up', on_click=lambda: ui.notify('button was pressed')).style("grid-column-start: 15; margin-right: 20px;")
    ui.button('Login', on_click=lambda: ui.notify('button was pressed')).style("grid-column-start: 16; margin-right: 20px;")

with ui.row().style("width: 100%; height: 100%"):  

    # Left Menu
    with ui.column().style("justify-content: space-evenly; grid-gap: 20px; background-color: yellow; padding: 10px 50px; grid-column: 1 / span 1; align-items: stretch; height: 500px"):
        ui.label("Menu 1")
        ui.label("Menu 2")
        ui.label("Menu 3")
        ui.label("Menu 4")
        ui.label("Menu 5")
        ui.label("Menu 6")

    # Middle Section
    with ui.column().style("height: 500px; width: 75%; justify-content: center; grid-gap: 20px; background-color: yellow; padding: 10px 50px; grid-column: 2 / span 8;"):
        with ui.card().tight().style("margin: 20px auto; grid-row: 2 / span 4; width: 500px; height: 500px;"):
            ui.image('https://picsum.photos/640/360')
            with ui.card_section().style("margin: auto;"):
                ui.label('Challenge').style("text-align: center; font-size: 30px; justify-items: center; align-content: center;")
                ui.label('do some qa').style("text-align: center; font-size: 15px; justify-items: center; align-content: center;")

ui.run()

