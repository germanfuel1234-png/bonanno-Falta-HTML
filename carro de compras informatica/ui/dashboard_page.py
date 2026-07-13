import flet as ft
from utils.database import Database

def dashboard_view(page: ft.Page):
    db = Database()
    
    # Obtener estadísticas
    stats = db.obtener_estadisticas()
    ventas_por_mes = db.obtener_ventas_por_mes()
    bajo_stock = db.obtener_componentes_bajo_stock()
    
    # Tarjetas de estadísticas
    def crear_tarjeta_stat(titulo, valor, icono, color):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icono, size=30, color=color),
                        ft.Column([
                            ft.Text(titulo, size=11, color=ft.Colors.GREY_600),
                            ft.Text(str(valor), size=18, weight=ft.FontWeight.BOLD),
                        ], spacing=0)
                    ], spacing=10)
                ], spacing=5),
                padding=15,
                width=170
            )
        )
    
    # Tarjetas principales
    tarjetas_stats = ft.Row([
        crear_tarjeta_stat(
            "Total Ventas",
            f"${stats['ventas_total']:.2f}",
            ft.Icons.ATTACH_MONEY,
            ft.Colors.GREEN_400
        ),
        crear_tarjeta_stat(
            "Ventas Realizadas",
            stats['ventas_count'],
            ft.Icons.SHOPPING_CART,
            ft.Colors.BLUE_400
        ),
    ], spacing=10, wrap=True)
    
    tarjetas_stats2 = ft.Row([
        crear_tarjeta_stat(
            "Presupuestos Pendientes",
            stats['presupuestos_pendientes'],
            ft.Icons.PENDING_ACTIONS,
            ft.Colors.ORANGE_400
        ),
        crear_tarjeta_stat(
            "Bajo Stock",
            stats['bajo_stock'],
            ft.Icons.WARNING,
            ft.Colors.RED_400
        ),
    ], spacing=10, wrap=True)
    
    # Componente más vendido
    mas_vendido_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.STAR, size=25, color=ft.Colors.AMBER_400),
                    ft.Text("Componente Más Vendido", size=13, weight=ft.FontWeight.BOLD)
                ]),
                ft.Text(
                    stats['mas_vendido'],
                    size=14,
                    color=ft.Colors.BLUE_700,
                    weight=ft.FontWeight.BOLD
                )
            ], spacing=10),
            padding=15,
            width=350
        )
    )
    
    # Gráfico de ventas por mes (simulado con barras)
    def crear_barra_grafico(mes, total, max_total):
        porcentaje = (total / max_total * 100) if max_total > 0 else 0
        altura = max(porcentaje * 1.5, 5)  # Altura mínima de 5
        
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    bgcolor=ft.Colors.BLUE_400,
                    height=altura,
                    width=30,
                    border_radius=5,
                    tooltip=f"${total:.2f}"
                ),
                ft.Text(mes[-2:], size=9, color=ft.Colors.GREY_600)  # Solo el mes
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            alignment=ft.Alignment(0, 1)
        )
    
    # Crear gráfico de barras
    max_venta = max([v['total'] for v in ventas_por_mes]) if ventas_por_mes else 1
    
    grafico_ventas = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Ventas por Mes", size=14, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Row([
                        crear_barra_grafico(v['mes'], v['total'], max_venta)
                        for v in ventas_por_mes
                    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                    height=180,
                    alignment=ft.Alignment(0, 1)
                ) if ventas_por_mes else ft.Container(
                    content=ft.Text("No hay datos de ventas", color=ft.Colors.GREY_600),
                    alignment=ft.Alignment(0, 0),
                    height=180
                )
            ], spacing=10),
            padding=15,
            width=350
        )
    )
    
    # Lista de componentes con bajo stock
    lista_bajo_stock = ft.ListView(
        spacing=5,
        padding=5,
        height=200
    )
    
    if bajo_stock:
        for comp in bajo_stock:
            stock_color = ft.Colors.RED_400 if comp['stock'] < 5 else ft.Colors.ORANGE_400
            
            lista_bajo_stock.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(comp['nombre'], size=12, weight=ft.FontWeight.BOLD),
                            ft.Text(comp['tipo'], size=10, color=ft.Colors.GREY_600)
                        ], spacing=2, expand=True),
                        ft.Container(
                            content=ft.Text(f"Stock: {comp['stock']}", size=11, color=ft.Colors.WHITE),
                            bgcolor=stock_color,
                            padding=5,
                            border_radius=5
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10,
                    border=ft.Border(
                        left=ft.BorderSide(1, ft.Colors.GREY_300),
                        top=ft.BorderSide(1, ft.Colors.GREY_300),
                        right=ft.BorderSide(1, ft.Colors.GREY_300),
                        bottom=ft.BorderSide(1, ft.Colors.GREY_300)
                    ),
                    border_radius=5
                )
            )
    else:
        lista_bajo_stock.controls.append(
            ft.Container(
                content=ft.Text("Todos los componentes tienen stock suficiente", size=12, color=ft.Colors.GREEN_600),
                alignment=ft.MainAxisAlignment.CENTER,
                padding=20
            )
        )
    
    bajo_stock_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INVENTORY_2, size=25, color=ft.Colors.RED_400),
                    ft.Text("Componentes con Bajo Stock", size=13, weight=ft.FontWeight.BOLD)
                ]),
                lista_bajo_stock
            ], spacing=10),
            padding=15,
            width=350
        )
    )
    
        # Botón de actualizar
    def actualizar_dashboard(e):
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Dashboard actualizado"),
            bgcolor=ft.Colors.GREEN_400
        )
        page.snack_bar.open = True
        page.update()

        # Recargar la vista
        contenedor_principal = dashboard_view(page)
        page.controls[-2] = contenedor_principal  # Reemplazar el contenedor actual
        page.update()

    
    boton_actualizar = ft.FloatingActionButton(
        icon=ft.Icons.REFRESH,
        on_click=actualizar_dashboard,
        bgcolor=ft.Colors.BLUE_400,
        tooltip="Actualizar Dashboard"
    )
    
    # Contenedor principal del dashboard
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("📊 Dashboard", size=22, weight=ft.FontWeight.BOLD),
            ]),
            ft.Divider(),
            tarjetas_stats,
            tarjetas_stats2,
            mas_vendido_card,
            grafico_ventas,
            bajo_stock_card,
            ft.Container(
                content=boton_actualizar,
                alignment=ft.Alignment(1, 1),
                padding=10
            )
        ], spacing=15, scroll=ft.ScrollMode.AUTO),
        padding=15,
        expand=True
    )