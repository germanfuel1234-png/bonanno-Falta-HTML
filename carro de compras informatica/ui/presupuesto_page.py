import flet as ft
from utils.database import Database

def presupuesto_view(page: ft.Page):
    db = Database()
    
    # Estado del carrito actual
    carrito = []
    
    def actualizar_vista():
        """Actualiza la vista del presupuesto"""
        page.update()
    
    def crear_presupuesto_view():
        """Vista para crear un nuevo presupuesto"""
        
        # Campos del formulario
        campo_cliente = ft.TextField(
            label="Nombre del cliente",
            width=300,
            autofocus=True
        )
        
        # Lista de componentes disponibles
        componentes_disponibles = db.obtener_componentes()
        
        # Dropdown para seleccionar componente
        selector_componente = ft.Dropdown(
            label="Seleccionar componente",
            width=220,
            options=[
                ft.DropdownOption(
                    key=str(c["id"]),
                    text=f"{c['nombre']} - ${c['precio']} (Stock: {c['stock']})"
                ) for c in componentes_disponibles if c["stock"] > 0
            ],
            enable_filter=True,
            editable=True
        )
        
        # Campo de cantidad
        campo_cantidad = ft.TextField(
            label="Cantidad",
            width=85,
            keyboard_type=ft.KeyboardType.NUMBER,
            value="1"
        )
        
        # Tabla del carrito
        tabla_carrito = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Componente", size=10)),
                ft.DataColumn(ft.Text("Cantidad", size=10)),
                ft.DataColumn(ft.Text("Precio U.", size=10)),
                ft.DataColumn(ft.Text("Subtotal", size=10)),
                ft.DataColumn(ft.Text("", size=12)),
            ],
            rows=[],
            border_radius=5,
            border=ft.Border(
                left=ft.BorderSide(1, "#EEEEEE"),
                top=ft.BorderSide(1, "#EEEEEE"),
                right=ft.BorderSide(1, "#EEEEEE"),
                bottom=ft.BorderSide(1, "#EEEEEE")
            ),
            horizontal_margin=5,
            vertical_lines=ft.BorderSide(1, "#EEEEEE"),
            horizontal_lines=ft.BorderSide(1, "#EEEEEE"),
            heading_row_height=35,
            data_row_min_height=40,
        )
        
        total_text = ft.Text("Total: $0.00", size=18, weight=ft.FontWeight.BOLD)
        
        def actualizar_total():
            """Actualiza el total del presupuesto"""
            total = sum(item['subtotal'] for item in carrito)
            total_text.value = f"Total: ${total:.2f}"
            page.update()
        
        def agregar_al_carrito(e):
            """Agrega un componente al carrito"""
            if not selector_componente.value:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Seleccione un componente"),
                    bgcolor=ft.Colors.RED_400
                )
                page.snack_bar.open = True
                page.update()
                return
            
            try:
                cantidad = int(campo_cantidad.value)
                if cantidad <= 0:
                    raise ValueError()
            except:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Cantidad inválida"),
                    bgcolor=ft.Colors.RED_400
                )
                page.snack_bar.open = True
                page.update()
                return
            
            componente_id = int(selector_componente.value)
            componente = next((c for c in componentes_disponibles if c["id"] == componente_id), None)
            
            if not componente:
                return
            
            if cantidad > componente["stock"]:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Stock insuficiente. Disponible: {componente['stock']}"),
                    bgcolor=ft.Colors.RED_400
                )
                page.snack_bar.open = True
                page.update()
                return
            
            # Verificar si ya está en el carrito
            existe = next((item for item in carrito if item["componente_id"] == componente_id), None)
            if existe:
                existe["cantidad"] += cantidad
                existe["subtotal"] = existe["cantidad"] * existe["precio_unitario"]
            else:
                carrito.append({
                    "componente_id": componente_id,
                    "nombre": componente["nombre"],
                    "cantidad": cantidad,
                    "precio_unitario": componente["precio"],
                    "subtotal": cantidad * componente["precio"]
                })
            
            actualizar_tabla_carrito()
            campo_cantidad.value = "1"
            page.update()

        
        def eliminar_del_carrito(componente_id):
            """Elimina un componente del carrito"""
            global carrito
            carrito = [item for item in carrito if item["componente_id"] != componente_id]
            actualizar_tabla_carrito()
        
        def actualizar_tabla_carrito():
            """Actualiza la tabla del carrito"""
            tabla_carrito.rows.clear()
            
            for item in carrito:
                fila = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["nombre"], size=12)),
                        ft.DataCell(ft.Text(str(item["cantidad"]), size=12)),
                        ft.DataCell(ft.Text(f"${item['precio_unitario']:.2f}", size=12)),
                        ft.DataCell(ft.Text(f"${item['subtotal']:.2f}", size=12)),
                        ft.DataCell(
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED_400,
                                icon_size=16,
                                on_click=lambda e, cid=item["componente_id"]: eliminar_del_carrito(cid)
                            )
                        ),
                    ]
                )
                tabla_carrito.rows.append(fila)
            
            actualizar_total()
            page.update()
        
        def guardar_presupuesto(e):
            """Guarda el presupuesto en la base de datos"""
            if not campo_cliente.value:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Ingrese el nombre del cliente"),
                    bgcolor=ft.Colors.RED_400
                )
                page.snack_bar.open = True
                page.update()
                return
            
            if not carrito:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("El carrito está vacío"),
                    bgcolor=ft.Colors.RED_400
                )
                page.snack_bar.open = True
                page.update()
                return
            
            try:
                presupuesto_id = db.crear_presupuesto(campo_cliente.value, carrito)
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Presupuesto #{presupuesto_id} creado exitosamente"),
                    bgcolor=ft.Colors.GREEN_400
                )
                page.snack_bar.open = True
                page.update()
                
                # Limpiar formulario
                campo_cliente.value = ""
                carrito.clear()
                actualizar_tabla_carrito()
                
                # Cambiar a la vista de lista
                contenedor_principal.content = lista_presupuestos_view()
                page.update()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error al crear presupuesto: {str(ex)}"),
                    bgcolor=ft.Colors.RED_400
                )
                page.snack_bar.open = True
                page.update()

        def volver_a_lista(e):
            """Vuelve a la lista de presupuestos"""
            contenedor_principal.content = lista_presupuestos_view()
            page.update()
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=volver_a_lista,
                            tooltip="Volver"
                        ),
                        ft.Text("Nuevo Presupuesto", size=20, weight=ft.FontWeight.BOLD)
                    ]),
                    campo_cliente,
                    ft.Divider(),
                    ft.Text("Agregar componentes:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        selector_componente,
                        campo_cantidad,
                    ], spacing=10),
                    ft.ElevatedButton(
                            "Agregar",
                            icon=ft.Icons.ADD,
                            on_click=agregar_al_carrito,
                            bgcolor=ft.Colors.BLUE_400,
                            color=ft.Colors.WHITE
                        ),
                    ft.Divider(),
                    ft.Text("Carrito:", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=tabla_carrito,
                        height=250,
                    ),
                    ft.Row([
                        total_text,
                    ], alignment=ft.MainAxisAlignment.END),
                    ft.Row([
                        ft.ElevatedButton(
                            "Cancelar",
                            on_click=volver_a_lista,
                            bgcolor=ft.Colors.RED_400,
                            color=ft.Colors.WHITE
                        ),
                        ft.ElevatedButton(
                            "Guardar Presupuesto",
                            icon=ft.Icons.SAVE,
                            on_click=guardar_presupuesto,
                            bgcolor=ft.Colors.GREEN_400,
                            color=ft.Colors.WHITE
                        )
                    ], alignment=ft.MainAxisAlignment.END, spacing=10)
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=10
            ),
            padding=10,
            expand=True
        )
    
    def lista_presupuestos_view():
        """Vista de lista de presupuestos"""
        
        presupuestos = db.obtener_presupuestos()
        
        def ver_detalle_presupuesto(presupuesto_id):
            """Muestra el detalle de un presupuesto"""
            presupuesto = next((p for p in presupuestos if p["id"] == presupuesto_id), None)
            if not presupuesto:
                return
            
            items = db.obtener_items_presupuesto(presupuesto_id)
            
            tabla_items = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Componente", size=11)),
                    ft.DataColumn(ft.Text("Cant.", size=11)),
                    ft.DataColumn(ft.Text("P.Unit.", size=11)),
                    ft.DataColumn(ft.Text("Subtotal", size=11)),
                ],
                rows=[],
                border_radius=5,
                border=ft.Border(
                    left=ft.BorderSide(1, "#EEEEEE"),
                    top=ft.BorderSide(1, "#EEEEEE"),
                    right=ft.BorderSide(1, "#EEEEEE"),
                    bottom=ft.BorderSide(1, "#EEEEEE")
                ),
            )
            
            for item in items:
                tabla_items.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item["nombre_componente"], size=11)),
                        ft.DataCell(ft.Text(str(item["cantidad"]), size=11)),
                        ft.DataCell(ft.Text(f"${item['precio_unitario']:.2f}", size=11)),
                        ft.DataCell(ft.Text(f"${item['subtotal']:.2f}", size=11)),
                    ])
                )
            
            def cerrar_dialogo(e):
                dialogo.open = False
                page.update()
                        
            def confirmar_presupuesto_dialogo(e):
                if db.confirmar_presupuesto(presupuesto_id):
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Presupuesto confirmado y venta registrada"),
                        bgcolor=ft.Colors.GREEN_400
                    )
                    page.snack_bar.open = True
                    page.update()
                    
                    dialogo.open = False
                    contenedor_principal.content = lista_presupuestos_view()
                    page.update()
                else:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Error al confirmar presupuesto"),
                        bgcolor=ft.Colors.RED_400
                    )
                    page.snack_bar.open = True
                    page.update()

            dialogo = ft.AlertDialog(
                title=ft.Text(f"Presupuesto #{presupuesto['id']} - {presupuesto['nombre_cliente']}"),
                content=ft.Column([
                    ft.Text(f"Fecha: {presupuesto['fecha']}", size=12),
                    ft.Text(f"Estado: {presupuesto['estado']}", size=12, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    tabla_items,
                    ft.Divider(),
                    ft.Text(f"Total: ${presupuesto['total']:.2f}", size=16, weight=ft.FontWeight.BOLD),
                ], spacing=10, width=400, height=400, scroll=ft.ScrollMode.AUTO),
                actions=[
                    ft.TextButton("Cerrar", on_click=cerrar_dialogo),
                    ft.ElevatedButton(
                        "Confirmar Venta",
                        on_click=confirmar_presupuesto_dialogo,
                        bgcolor=ft.Colors.GREEN_400,
                        color=ft.Colors.WHITE,
                        disabled=presupuesto['estado'] == 'Confirmado'
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            page.overlay.append(dialogo)
            dialogo.open = True
            page.update()
        
        def eliminar_presupuesto_dialogo(presupuesto_id):
            """Elimina un presupuesto"""
            def confirmar_eliminar(e):
                db.eliminar_presupuesto(presupuesto_id)
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Presupuesto eliminado"),
                    bgcolor=ft.Colors.ORANGE_400
                )
                page.snack_bar.open = True
                page.update()
                
                dialogo.open = False
                contenedor_principal.content = lista_presupuestos_view()
                page.update()
            
            def cancelar_eliminar(e):
                dialogo.open = False
                page.update()
            
            dialogo = ft.AlertDialog(
                title=ft.Text("Confirmar eliminación"),
                content=ft.Text("¿Está seguro que desea eliminar este presupuesto?"),
                actions=[
                    ft.TextButton("Cancelar", on_click=cancelar_eliminar),
                    ft.ElevatedButton(
                        "Eliminar",
                        on_click=confirmar_eliminar,
                        bgcolor=ft.Colors.RED_400,
                        color=ft.Colors.WHITE
                    )
                ],
            )
            
            page.overlay.append(dialogo)
            dialogo.open = True
            page.update()

        
        def ir_a_nuevo_presupuesto(e):
            """Va a la vista de crear presupuesto"""
            contenedor_principal.content = crear_presupuesto_view()
            page.update()
        
        # Lista de presupuestos
        lista_presupuestos = ft.ListView(
            spacing=10,
            padding=10,
            expand=True
        )
        
        if not presupuestos:
            lista_presupuestos.controls.append(
                ft.Container(
                    content=ft.Text("No hay presupuestos creados", size=16, color=ft.Colors.GREY_600),
                    alignment=ft.Alignment(0, 0),
                    padding=20
                )
            )
        else:
            for p in presupuestos:
                estado_color = ft.Colors.GREEN_400 if p["estado"] == "Confirmado" else ft.Colors.ORANGE_400
                
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"#{p['id']} - {p['nombre_cliente']}", size=14, weight=ft.FontWeight.BOLD),
                                ft.Container(
                                    content=ft.Text(p["estado"], size=11, color=ft.Colors.WHITE),
                                    bgcolor=estado_color,
                                    padding=5,
                                    border_radius=5
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(f"Fecha: {p['fecha']}", size=11, color=ft.Colors.GREY_700),
                            ft.Text(f"Total: ${p['total']:.2f}", size=13, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                ft.TextButton("Ver Detalle", on_click=lambda e, pid=p["id"]: ver_detalle_presupuesto(pid)),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=ft.Colors.RED_400,
                                    icon_size=18,
                                    on_click=lambda e, pid=p["id"]: eliminar_presupuesto_dialogo(pid)
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                        ], spacing=5),
                        padding=15
                    )
                )
                lista_presupuestos.controls.append(card)
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Presupuestos", size=20, weight=ft.FontWeight.BOLD),
                    ft.ElevatedButton(
                        "Nuevo Presupuesto",
                        icon=ft.Icons.ADD,
                        on_click=ir_a_nuevo_presupuesto,
                        bgcolor=ft.Colors.BLUE_400,
                        color=ft.Colors.WHITE
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                lista_presupuestos
            ], spacing=10),
            padding=10,
            expand=True
        )
    
    # Contenedor principal que cambiará entre vistas
    contenedor_principal = ft.Container(
        content=lista_presupuestos_view(),
        expand=True
    )
    
    return contenedor_principal