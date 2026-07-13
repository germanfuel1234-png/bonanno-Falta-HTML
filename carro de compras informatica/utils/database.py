import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="componentes.db"):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        """Inicializa las tablas de la base de datos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de componentes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS componentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL,
                precio REAL NOT NULL,
                stock INTEGER NOT NULL,
                imagen TEXT
            )
        ''')
        
        # Tabla de presupuestos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS presupuestos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_cliente TEXT NOT NULL,
                fecha TEXT NOT NULL,
                total REAL NOT NULL,
                estado TEXT DEFAULT 'Pendiente'
            )
        ''')
        
        # Tabla de items de presupuesto
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS presupuesto_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                presupuesto_id INTEGER NOT NULL,
                componente_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (presupuesto_id) REFERENCES presupuestos(id),
                FOREIGN KEY (componente_id) REFERENCES componentes(id)
            )
        ''')
        
        # Tabla de ventas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                presupuesto_id INTEGER,
                fecha TEXT NOT NULL,
                total REAL NOT NULL,
                FOREIGN KEY (presupuesto_id) REFERENCES presupuestos(id)
            )
        ''')
        
        conn.commit()
        
        # Verificar si hay datos, si no, insertar datos iniciales
        cursor.execute("SELECT COUNT(*) FROM componentes")
        if cursor.fetchone()[0] == 0:
            self.insertar_datos_iniciales(cursor)
            conn.commit()
        
        conn.close()
    
    def insertar_datos_iniciales(self, cursor):
        """Inserta los componentes iniciales"""
        componentes_iniciales = [
            ("Procesador Intel i7", "CPU", 350, 15, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS8PFVwghR2e6vAQkwa1uiMSWzmj8zry9pawQ&s"),
            ("Memoria RAM 16GB", "RAM", 80, 30, "https://mexx-img-2019.s3.amazonaws.com/40390_4.jpeg"),
            ("SSD 1TB", "Almacenamiento", 120, 25, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSifzA1siyBy6-sojLkf4UL15AyqMzGLG23dg&s"),
            ("Tarjeta Gráfica RTX 3070", "GPU", 550, 8, "https://http2.mlstatic.com/D_767790-MLU73886044251_012024-C.jpg"),
            ("Placa Base ASUS", "Motherboard", 180, 12, "https://gorilagames.com/img/Public/1019/11667-producto-motherboard-asus-rog-strix-z790-e-gaming-wifi-lga-1700-intel-goril.jpg"),
            ("Fuente 750W", "PSU", 90, 20, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS_mWOfgVmK4hivXa1VZL8RlbXQHO_lxNzpdg&s"),
            ("Gabinete ATX", "Case", 70, 18, "https://http2.mlstatic.com/D_NQ_NP_851678-MLU72146911510_102023-O.webp"),
            ("Monitor 27\"", "Periférico", 250, 10, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSJz04UPtDZn8zV_U_FdgwMI_nFSJ4vzsY9qQ&s"),
        ]
        
        cursor.executemany('''
            INSERT INTO componentes (nombre, tipo, precio, stock, imagen)
            VALUES (?, ?, ?, ?, ?)
        ''', componentes_iniciales)
    
    # ==================== COMPONENTES ====================
    
    def obtener_componentes(self):
        """Obtiene todos los componentes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM componentes")
        componentes = []
        for row in cursor.fetchall():
            componentes.append({
                "id": row[0],
                "nombre": row[1],
                "tipo": row[2],
                "precio": row[3],
                "stock": row[4],
                "imagen": row[5]
            })
        conn.close()
        return componentes
    
    def agregar_componente(self, nombre, tipo, precio, stock, imagen=""):
        """Agrega un nuevo componente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO componentes (nombre, tipo, precio, stock, imagen)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, tipo, precio, stock, imagen))
        conn.commit()
        componente_id = cursor.lastrowid
        conn.close()
        return componente_id
    
    def modificar_componente(self, id, nombre, tipo, precio, stock, imagen=""):
        """Modifica un componente existente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE componentes
            SET nombre=?, tipo=?, precio=?, stock=?, imagen=?
            WHERE id=?
        ''', (nombre, tipo, precio, stock, imagen, id))
        conn.commit()
        conn.close()
    
    def eliminar_componente(self, id):
        """Elimina un componente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM componentes WHERE id=?", (id,))
        conn.commit()
        conn.close()
    
    def actualizar_stock(self, componente_id, cantidad):
        """Actualiza el stock de un componente"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE componentes
            SET stock = stock - ?
            WHERE id = ?
        ''', (cantidad, componente_id))
        conn.commit()
        conn.close()
    
    # ==================== PRESUPUESTOS ====================
    
    def crear_presupuesto(self, nombre_cliente, items):
        """Crea un nuevo presupuesto con sus items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = sum(item['subtotal'] for item in items)
        
        # Insertar presupuesto
        cursor.execute('''
            INSERT INTO presupuestos (nombre_cliente, fecha, total, estado)
            VALUES (?, ?, ?, ?)
        ''', (nombre_cliente, fecha, total, 'Pendiente'))
        
        presupuesto_id = cursor.lastrowid
        
        # Insertar items del presupuesto
        for item in items:
            cursor.execute('''
                INSERT INTO presupuesto_items (presupuesto_id, componente_id, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            ''', (presupuesto_id, item['componente_id'], item['cantidad'], item['precio_unitario'], item['subtotal']))
        
        conn.commit()
        conn.close()
        return presupuesto_id
    
    def obtener_presupuestos(self):
        """Obtiene todos los presupuestos"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM presupuestos ORDER BY fecha DESC")
        presupuestos = []
        for row in cursor.fetchall():
            presupuestos.append({
                "id": row[0],
                "nombre_cliente": row[1],
                "fecha": row[2],
                "total": row[3],
                "estado": row[4]
            })
        conn.close()
        return presupuestos
    
    def obtener_items_presupuesto(self, presupuesto_id):
        """Obtiene los items de un presupuesto específico"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT pi.*, c.nombre, c.tipo
            FROM presupuesto_items pi
            JOIN componentes c ON pi.componente_id = c.id
            WHERE pi.presupuesto_id = ?
        ''', (presupuesto_id,))
        items = []
        for row in cursor.fetchall():
            items.append({
                "id": row[0],
                "presupuesto_id": row[1],
                "componente_id": row[2],
                "cantidad": row[3],
                "precio_unitario": row[4],
                "subtotal": row[5],
                "nombre_componente": row[6],
                "tipo_componente": row[7]
            })
        conn.close()
        return items
    
    def confirmar_presupuesto(self, presupuesto_id):
        """Confirma un presupuesto y crea una venta"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obtener datos del presupuesto
        cursor.execute("SELECT total FROM presupuestos WHERE id=?", (presupuesto_id,))
        resultado = cursor.fetchone()
        if not resultado:
            conn.close()
            return False
        
        total = resultado[0]
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Crear venta
        cursor.execute('''
            INSERT INTO ventas (presupuesto_id, fecha, total)
            VALUES (?, ?, ?)
        ''', (presupuesto_id, fecha, total))
        
        # Actualizar estado del presupuesto
        cursor.execute('''
            UPDATE presupuestos
            SET estado = 'Confirmado'
            WHERE id = ?
        ''', (presupuesto_id,))
        
        # Actualizar stock de componentes
        cursor.execute('''
            SELECT componente_id, cantidad
            FROM presupuesto_items
            WHERE presupuesto_id = ?
        ''', (presupuesto_id,))
        
        for componente_id, cantidad in cursor.fetchall():
            cursor.execute('''
                UPDATE componentes
                SET stock = stock - ?
                WHERE id = ?
            ''', (cantidad, componente_id))
        
        conn.commit()
        conn.close()
        return True
    
    def eliminar_presupuesto(self, presupuesto_id):
        """Elimina un presupuesto y sus items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM presupuesto_items WHERE presupuesto_id=?", (presupuesto_id,))
        cursor.execute("DELETE FROM presupuestos WHERE id=?", (presupuesto_id,))
        conn.commit()
        conn.close()
    
    # ==================== DASHBOARD ====================
    
    def obtener_estadisticas(self):
        """Obtiene estadísticas para el dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total de ventas
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM ventas")
        ventas_count, ventas_total = cursor.fetchone()
        
        # Presupuestos pendientes
        cursor.execute("SELECT COUNT(*) FROM presupuestos WHERE estado='Pendiente'")
        presupuestos_pendientes = cursor.fetchone()[0]
        
        # Componentes con bajo stock (menos de 10)
        cursor.execute("SELECT COUNT(*) FROM componentes WHERE stock < 10")
        bajo_stock = cursor.fetchone()[0]
        
        # Componente más vendido
        cursor.execute('''
            SELECT c.nombre, SUM(pi.cantidad) as total_vendido
            FROM presupuesto_items pi
            JOIN componentes c ON pi.componente_id = c.id
            JOIN presupuestos p ON pi.presupuesto_id = p.id
            WHERE p.estado = 'Confirmado'
            GROUP BY c.nombre
            ORDER BY total_vendido DESC
            LIMIT 1
        ''')
        mas_vendido = cursor.fetchone()
        
        conn.close()
        
        return {
            "ventas_count": ventas_count,
            "ventas_total": ventas_total,
            "presupuestos_pendientes": presupuestos_pendientes,
            "bajo_stock": bajo_stock,
            "mas_vendido": mas_vendido[0] if mas_vendido else "N/A"
        }
    
    def obtener_ventas_por_mes(self):
        """Obtiene las ventas agrupadas por mes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT strftime('%Y-%m', fecha) as mes, SUM(total) as total
            FROM ventas
            GROUP BY mes
            ORDER BY mes DESC
            LIMIT 12
        ''')
        ventas = []
        for row in cursor.fetchall():
            ventas.append({
                "mes": row[0],
                "total": row[1]
            })
        conn.close()
        return list(reversed(ventas))
    
    def obtener_componentes_bajo_stock(self):
        """Obtiene componentes con stock bajo"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT nombre, tipo, stock
            FROM componentes
            WHERE stock < 10
            ORDER BY stock ASC
        ''')
        componentes = []
        for row in cursor.fetchall():
            componentes.append({
                "nombre": row[0],
                "tipo": row[1],
                "stock": row[2]
            })
        conn.close()
        return componentes