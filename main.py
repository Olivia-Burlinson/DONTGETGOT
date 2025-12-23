from nicegui import ui

# Global page styling
ui.add_head_html("""
<style>
    body {
        background-color: #f4f4f4;
        font-family: 'Inter', sans-serif;
    }
</style>
""")

# ---------- Top Navigation ----------
with ui.row().classes("items-center justify-between").style(
    "width: 100%; background-color: #222; padding: 12px 24px;"
):
    ui.label("🎯 Don't Get Got").style(
        "font-size: 22px; font-weight: 700; color: white;"
    )

    with ui.row().classes("gap-3"):
        ui.button("Sign Up").props("flat").style("color: white;")
        ui.button("Login").props("outline").style(
            "color: white; border-color: white;"
        )

# ---------- Main Layout ----------
with ui.row().style("width: 100%; padding: 20px; gap: 20px;"):

    # ----- Left Sidebar -----
    with ui.column().style(
        """
        width: 220px;
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        gap: 12px;
        """
    ):
        ui.label("Menu").style("font-weight: 600; font-size: 16px;")
        for i in range(1, 7):
            ui.button(f"Menu {i}").props("flat").style(
                "justify-content: flex-start;"
            )

    # ----- Main Challenge Area -----
    with ui.column().style(
        """
        flex: 1;
        background-color: white;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        align-items: center;
        """
    ):
        ui.label("Active Challenge").style(
            "font-size: 20px; font-weight: 600; margin-bottom: 10px;"
        )

        with ui.card().tight().style(
            """
            width: 420px;
            border-radius: 16px;
            overflow: hidden;
            """
        ):
            ui.image("https://picsum.photos/640/360")

            with ui.card_section().style("text-align: center; padding: 20px;"):
                ui.label("Challenge Incoming").style(
                    "font-size: 24px; font-weight: 700;"
                )
                ui.label("Do some QA before time runs out ⏱️").style(
                    "font-size: 14px; color: #666; margin-bottom: 20px;"
                )

                with ui.row().classes("justify-center gap-4"):
                    ui.button("Accept").style(
                        """
                        background-color: #22c55e;
                        color: white;
                        width: 120px;
                        """
                    )
                    ui.button("Decline").style(
                        """
                        background-color: #ef4444;
                        color: white;
                        width: 120px;
                        """
                    )

ui.run()
