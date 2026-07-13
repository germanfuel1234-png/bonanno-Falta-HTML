from utils.database import Database

class stock_logic_function():
    db = Database()
    
    def cargar_componentes_stock():
        """Carga componentes desde la base de datos"""
        return stock_logic_function.db.obtener_componentes()
    
    def filtrar_componentes(nombre, tipo, componentes):
        """Filtra componentes por nombre y tipo"""
        nombre = nombre.lower()
        filtrados = []

        for comp in componentes:
            if nombre in comp["nombre"].lower() and (
                tipo == "Todos" or comp["tipo"] == tipo
            ):
                filtrados.append(comp)

        return filtrados
    
    def agregar_componente(nombre, tipo, precio, stock, imagen=""):
        """Agrega un nuevo componente a la base de datos"""
        return stock_logic_function.db.agregar_componente(nombre, tipo, precio, stock, imagen)
    
    def modificar_componente(id, nombre, tipo, precio, stock, imagen=""):
        """Modifica un componente existente"""
        stock_logic_function.db.modificar_componente(id, nombre, tipo, precio, stock, imagen)
    
    def eliminar_componente(id):
        """Elimina un componente"""
        stock_logic_function.db.eliminar_componente(id)
    
    def obtener_tipos_componentes():
        """Obtiene los tipos de componentes disponibles"""
        componentes = stock_logic_function.db.obtener_componentes()
        tipos = set([comp["tipo"] for comp in componentes])
        return ["Todos"] + sorted(list(tipos))