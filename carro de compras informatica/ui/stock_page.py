import flet as ft
from utils.stock_logic import stock_logic_function as stock_logic
from const.constantes import tipos_componentes

def stock_view(page: ft.Page):
    
    componente_seleccionado = {"id": None}
    
    def pop_up_agregar_componente(e):
        def cerrar_dialogo(e):
            dialogo.open = False
            page.update()
        
        def guardar_componente(e):
            # Validaciones
            if not campo_nombre.value:
                page.show_snack_bar(ft.SnackBar(content=ft.Text("Ingrese el nombre del componente"), bgcolor=ft.Colors.RED_400))
                return
            
            if not campo_tipo.value:
                page.show_snack_bar(ft.SnackBar(content=ft.Text("Seleccione el tipo de componente"), bgcolor=ft.Colors.RED_400))
                return
            
            try:
                precio = float(campo_precio.value)
                stock = int(campo_stock.value)
                
                if precio <= 0 or stock < 0:
                    raise ValueError()
            except:
                page.show_snack_bar(ft.SnackBar(content=ft.Text("Precio y stock deben ser números válidos"), bgcolor=ft.Colors.RED_400))
                return
            
            # Guardar en la base de datos
            stock_logic.agregar_componente(
                campo_nombre.value,
                campo_tipo.value,
                precio,
                stock,
                campo_imagen.value or ""
            )
            
            page.show_snack_bar(ft.SnackBar(content=ft.Text("Componente agregado exitosamente"), bgcolor=ft.Colors.GREEN_400))
            dialogo.open = False
            actualizar_filtro()
            page.update()
        
        campo_nombre = ft.TextField(label="Nombre del componente", autofocus=True)
        campo_tipo = ft.Dropdown(
            label="Tipo",
            options=[ft.DropdownOption(t) for t in tipos_componentes if t != "Todos"]
        )
        campo_precio = ft.TextField(label="Precio", keyboard_type=ft.KeyboardType.NUMBER)
        campo_stock = ft.TextField(label="Stock", keyboard_type=ft.KeyboardType.NUMBER)
        campo_imagen = ft.TextField(label="URL de Imagen (opcional)", keyboard_type=ft.KeyboardType.URL)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("Agregar nuevo componente"),
            content=ft.Column([
                campo_nombre,
                campo_tipo,
                campo_precio,
                campo_stock,
                campo_imagen
            ], spacing=10, width=400, height=300, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.ElevatedButton("Cancelar", on_click=cerrar_dialogo),
                ft.ElevatedButton("Guardar", on_click=guardar_componente, bgcolor="#6750A4", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()
    
    def pop_up_eliminar_componente(e):
        if componente_seleccionado["id"] is None:
            page.show_snack_bar(ft.SnackBar(content=ft.Text("Seleccione un componente haciendo clic en una fila"), bgcolor=ft.Colors.ORANGE_400))
            return
        
        def confirmar_eliminar(e):
            stock_logic.eliminar_componente(componente_seleccionado["id"])
            page.show_snack_bar(ft.SnackBar(content=ft.Text("Componente eliminado"), bgcolor=ft.Colors.GREEN_400))
            componente_seleccionado["id"] = None
            dialogo.open = False
            actualizar_filtro()
            page.update()
        
        def cancelar_eliminar(e):
            dialogo.open = False
            page.update()
        
        dialogo = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text("¿Está seguro que desea eliminar este componente?"),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar_eliminar),
                ft.ElevatedButton("Eliminar", on_click=confirmar_eliminar, bgcolor=ft.Colors.RED_400, color="white")
            ],
        )
        
        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()
    
    def pop_up_modificar_componente(e):
        if componente_seleccionado["id"] is None:
            page.show_snack_bar(ft.SnackBar(content=ft.Text("Seleccione un componente haciendo clic en una fila"), bgcolor=ft.Colors.ORANGE_400))
            return
        
        # Buscar el componente seleccionado
        componentes = stock_logic.cargar_componentes_stock()
        comp = next((c for c in componentes if c["id"] == componente_seleccionado["id"]), None)
        
        if not comp:
            return
        
        def cerrar_dialogo(e):
            dialogo.open = False
            page.update()
        
        def guardar_cambios(e):
            # Validaciones
            if not campo_nombre.value:
                page.show_snack_bar(ft.SnackBar(content=ft.Text("Ingrese el nombre del componente"), bgcolor=ft.Colors.RED_400))
                return
            
            if not campo_tipo.value:
                page.show_snack_bar(ft.SnackBar(content=ft.Text("Seleccione el tipo de componente"), bgcolor=ft.Colors.RED_400))
                return
            
            try:
                precio = float(campo_precio.value)
                stock = int(campo_stock.value)
                
                if precio <= 0 or stock < 0:
                    raise ValueError()
            except:
                page.show_snack_bar(ft.SnackBar(content=ft.Text("Precio y stock deben ser números válidos"), bgcolor=ft.Colors.RED_400))
                return
            
            # Modificar en la base de datos
            stock_logic.modificar_componente(
                componente_seleccionado["id"],
                campo_nombre.value,
                campo_tipo.value,
                precio,
                stock,
                campo_imagen.value or ""
            )
            
            page.show_snack_bar(ft.SnackBar(content=ft.Text("Componente modificado exitosamente"), bgcolor=ft.Colors.GREEN_400))
            componente_seleccionado["id"] = None
            dialogo.open = False
            actualizar_filtro()
            page.update()
        
        campo_nombre = ft.TextField(label="Nombre del componente", value=comp["nombre"], autofocus=True)
        campo_tipo = ft.Dropdown(
            label="Tipo",
            options=[ft.DropdownOption(t) for t in tipos_componentes if t != "Todos"],
            value=comp["tipo"]
        )
        campo_precio = ft.TextField(label="Precio", value=str(comp["precio"]), keyboard_type=ft.KeyboardType.NUMBER)
        campo_stock = ft.TextField(label="Stock", value=str(comp["stock"]), keyboard_type=ft.KeyboardType.NUMBER)
        campo_imagen = ft.TextField(label="URL de Imagen (opcional)", value=comp.get("imagen", ""), keyboard_type=ft.KeyboardType.URL)
        
        dialogo = ft.AlertDialog(
            title=ft.Text("Modificar componente"),
            content=ft.Column([
                campo_nombre,
                campo_tipo,
                campo_precio,
                campo_stock,
                campo_imagen
            ], spacing=10, width=400, height=300, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.ElevatedButton("Cancelar", on_click=cerrar_dialogo),
                ft.ElevatedButton("Guardar", on_click=guardar_cambios, bgcolor="#6750A4", color="white"),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()
    
    def ver_imagen_grande(imagen, nombre):
        if not imagen:
            page.show_snack_bar(ft.SnackBar(content=ft.Text("Este componente no tiene imagen"), bgcolor=ft.Colors.ORANGE_400))
            return
        dialogo = ft.AlertDialog(
            title=ft.Text("Imagen de " + nombre),
            content=ft.Image(src=imagen, width=400, height=400, fit=ft.ImageFit.CONTAIN),
            actions=[ft.TextButton("Cerrar", on_click=lambda e: cerrar_dialogo(dialogo))],
        )
        page.overlay.append(dialogo)
        dialogo.open = True
        page.update()

    def cerrar_dialogo(dialogo):
        dialogo.open = False
        page.update()
    
    def componentes():
        font_size = 12
        componentes_lista = stock_logic.cargar_componentes_stock()
    
        Campo_busqueda = ft.TextField(
            label="Buscar",
            prefix_icon=ft.Icons.SEARCH,
            expand=True
            # on_change eliminado por incompatibilidad
        )
        
        selector_tipo = ft.Dropdown(
            label="Filtrar por tipo",
            options=[ft.DropdownOption(t) for t in tipos_componentes],
            value="Todos",
            expand=True,
            on_change=lambda e: actualizar_filtro()
        )

        def actualizar_filtro():
            texto = Campo_busqueda.value or ""
            tipo = selector_tipo.value
            componentes_actualizados = stock_logic.cargar_componentes_stock()
            nuevos = stock_logic.filtrar_componentes(texto, tipo, componentes_actualizados)
            
            tabla_stock.rows.clear()
            cargar_tabla(nuevos)
            page.update()
        
        def seleccionar_fila(e, comp_id):
            componente_seleccionado["id"] = comp_id
            # Resaltar la fila seleccionada
            for row in tabla_stock.rows:
                row.selected = False
            e.control.selected = True
            page.update()
        
        def cargar_tabla(componentes_lista=componentes_lista):
            tabla_stock.rows.clear()
            
            for c in componentes_lista:
                # Crear contenedor con imagen en miniatura
                if c.get("imagen"):
                    imagen_componente = ft.Container(
                        content=ft.Image(
                            src=c["imagen"],
                            width=40,
                            height=40,
                            fit=ft.ImageFit.COVER,
                            border_radius=5
                        ),
                        on_click=lambda e, src=c["imagen"], nombre=c["nombre"]: ver_imagen_grande(src, nombre),
                        tooltip="Click para ampliar",
                        ink=True
                    )
                else:
                    imagen_componente = ft.Container(
                        content=ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED, size=20, color=ft.Colors.GREY_400),
                        tooltip="Sin imagen"
                    )
                
                fila = ft.DataRow(
                    on_select_changed=lambda e, cid=c["id"]: seleccionar_fila(e, cid),
                    cells=[
                        ft.DataCell(ft.Text(c["nombre"], size=font_size)),
                        ft.DataCell(ft.Text(c["tipo"], size=font_size)),
                        ft.DataCell(ft.Text(str(c["precio"]) + "$", size=font_size)),
                        ft.DataCell(ft.Text(str(c["stock"]), size=font_size)),
                        ft.DataCell(imagen_componente),
                    ]
                )
                tabla_stock.rows.append(fila)
            
            page.update()
        
        tabla_stock = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Nombre", size=font_size)),
                ft.DataColumn(ft.Text("Tipo", size=font_size)),
                ft.DataColumn(ft.Text("Precio", size=font_size)),
                ft.DataColumn(ft.Text("Stock", size=font_size)),
                ft.DataColumn(ft.Text("Imagen", size=font_size)),
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
            data_row_min_height=50,
            data_row_max_height=80,
            column_spacing=0,
            expand=True,
        )
        cargar_tabla()
        
        lv = ft.ListView(
            expand=1,
            spacing=10,
            padding=5,
        )
        lv.controls.append(tabla_stock)
        
        boton_agregar = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            tooltip="Agregar",
            foreground_color=ft.Colors.BLUE_300,
            on_click=pop_up_agregar_componente,
            scale=0.8
        )

        boton_eliminar = ft.FloatingActionButton(
            icon=ft.Icons.DELETE,
            foreground_color=ft.Colors.RED_300,
            tooltip="Eliminar",
            on_click=pop_up_eliminar_componente,
            scale=0.8
        )

        boton_modificar = ft.FloatingActionButton(
            icon=ft.Icons.EDIT,
            foreground_color=ft.Colors.YELLOW_300,
            tooltip="Modificar",
            on_click=pop_up_modificar_componente,
            scale=0.8
        )
        
        return ft.Container(
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[Campo_busqueda, selector_tipo],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10
                    ),
                    ft.Stack(
                        controls=[
                            lv,
                            ft.Container(
                                ft.Row(
                                    controls=[boton_agregar, boton_eliminar, boton_modificar],
                                    alignment=ft.Alignment(0, 0)
                                ),
                                right=0,
                                bottom=0
                            )
                        ],
                        alignment=ft.Alignment(-1, -1),
                        expand=True,
                    )
                ],
            )
        )
    
    return componentes()