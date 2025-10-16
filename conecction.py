import mysql.connector
from mysql.connector import Error
from typing import Optional

# --- Configuración de Conexión ---
DB_CONFIG = {
    'host': 'localhost',
    'database': 'libros_circulares',
    'user': 'root',
    'password': '1234'
}

def get_db_connection() -> Optional[mysql.connector.MySQLConnection]:
    """Establece y retorna el objeto de conexión a la base de datos."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
        return None
    except Error as e:

        print(f" Error al conectar a la base de datos MySQL: {e}")
        return None

