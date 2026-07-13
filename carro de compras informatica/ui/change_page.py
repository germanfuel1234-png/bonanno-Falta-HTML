import flet as ft
import ui.stock_page as stock
import ui.presupuesto_page as presupuesto
import ui.dashboard_page as dashboard

def main(page: ft.Page):
    page.title = "Gestor de Componentes"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.width = 400
    page.window.height = 700

    # Contenedor dinámico para la vista actual
    current_view = ft.Container(content=stock.stock_view(page), expand=True)

    # Función para cambiar de pestaña
    def change_view(e):
        selected_index = nav_bar.selected_index
        if selected_index == 0:
            current_view.content = stock.stock_view(page)
        elif selected_index == 1:
            current_view.content = presupuesto.presupuesto_view(page)
        elif selected_index == 2:
            current_view.content = dashboard.dashboard_view(page)
        page.update()

    # Barra inferior de navegación
    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.STORAGE, label="Stock"),
            ft.NavigationBarDestination(icon=ft.Icons.CALCULATE, label="Presupuesto"),
            ft.NavigationBarDestination(icon=ft.Icons.INSIGHTS, label="Dashboard")
        ],
        selected_index=0,
        on_change=change_view
    )

    # Agregamos los elementos a la página
    page.add(
        current_view,
        nav_bar
    )