# cruds.py
import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, Any, List, Tuple
from conecction import get_db_connection


# ----------------------------------------------------------------------
# UTILITY FUNCTIONS
# ----------------------------------------------------------------------

def execute_query(query: str, params: Tuple = None, commit: bool = False, fetch_one: bool = False) -> Any:
    """Función genérica para ejecutar consultas."""
    conn = get_db_connection()
    if not conn: return None

    result = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)

        if commit:
            conn.commit()
            result = cursor.lastrowid if 'INSERT' in query.upper() else cursor.rowcount
        elif fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()

    except Error as e:
        print(f"❌ Error DB en ejecución: {e}")
        if commit: conn.rollback()
        result = -1 if commit else []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    return result


# ----------------------------------------------------------------------
# 1. CRUD USUARIO
# ----------------------------------------------------------------------

def crear_usuario(nombre, email, password_hash, ciudad, telefono, rol='usuario') -> Optional[int]:
    query = """INSERT INTO usuario (nombre, email, password_hash, ciudad, telefono, rol)
               VALUES (%s, %s, %s, %s, %s, %s)"""
    return execute_query(query, (nombre, email, password_hash, ciudad, telefono, rol), commit=True)


def leer_usuarios(campo: str = None, valor: str = None) -> List[Dict[str, Any]]:
    if campo and valor:
        query = f"SELECT * FROM usuario WHERE {campo} = %s"
        return execute_query(query, (valor,), commit=False)
    else:
        return execute_query("SELECT * FROM usuario", commit=False)


def actualizar_usuario(user_id, **kwargs) -> int:
    set_clauses = [f"{k} = %s" for k in kwargs.keys()]
    values = list(kwargs.values())
    if not set_clauses: return 0

    query = f"UPDATE usuario SET {', '.join(set_clauses)} WHERE id_usuario = %s"
    params = tuple(values + [user_id])
    return execute_query(query, params, commit=True)


def borrar_usuario(user_id: int) -> int:
    return execute_query("DELETE FROM usuario WHERE id_usuario = %s", (user_id,), commit=True)


# ----------------------------------------------------------------------
# 2. CRUD LIBRO
# ----------------------------------------------------------------------

def crear_libro(titulo, autor, id_propietario, isbn=None, genero=None, resumen=None, anio_publicacion=None,
                editorial=None, paginas=None, idioma=None, estado_fisico=None, en_catalogo=0,
                modalidad_publicacion='visible', precio_venta=None) -> Optional[int]:
    query = """INSERT INTO libro (titulo, autor, id_propietario, isbn, genero, resumen, anio_publicacion, editorial, paginas, idioma, estado_fisico, en_catalogo, modalidad_publicacion, precio_venta)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    params = (titulo, autor, id_propietario, isbn, genero, resumen, anio_publicacion, editorial, paginas, idioma,
              estado_fisico, en_catalogo, modalidad_publicacion, precio_venta)
    return execute_query(query, params, commit=True)


def leer_libros(campo: str = None, valor: str = None) -> List[Dict[str, Any]]:
    if campo and valor:
        query = f"SELECT * FROM libro WHERE {campo} = %s"
        return execute_query(query, (valor,), commit=False)
    else:
        return execute_query("SELECT * FROM libro", commit=False)


def actualizar_libro(id_libro: int, **kwargs) -> int:
    set_clauses = [f"{k} = %s" for k in kwargs.keys()]
    values = list(kwargs.values())
    if not set_clauses: return 0

    query = f"UPDATE libro SET {', '.join(set_clauses)} WHERE id_libro = %s"
    params = tuple(values + [id_libro])
    return execute_query(query, params, commit=True)


def borrar_libro(id_libro: int) -> int:
    return execute_query("DELETE FROM libro WHERE id_libro = %s", (id_libro,), commit=True)


# ----------------------------------------------------------------------
# 3. CRUD CLUB_LECTURA
# ----------------------------------------------------------------------

# ======================================================================
# 3. CRUD CLUB_LECTURA
# ======================================================================

def crear_club(nombre_club, fecha_inicio, id_libro, id_administrador, max_miembros, descripcion=None, fecha_fin=None,
               estado='activo') -> Optional[int]:
    query = """INSERT INTO club_lectura (nombre_club, descripcion, fecha_inicio, fecha_fin, estado, id_libro, id_administrador, max_miembros)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
    params = (nombre_club, descripcion, fecha_inicio, fecha_fin, estado, id_libro, id_administrador, max_miembros)
    return execute_query(query, params, commit=True)


def leer_clubes(campo: str = None, valor: str = None) -> List[Dict[str, Any]]:
    if campo and valor:
        query = f"SELECT * FROM club_lectura WHERE {campo} = %s"
        return execute_query(query, (valor,), commit=False)
    else:
        return execute_query("SELECT * FROM club_lectura", commit=False)



def actualizar_club(id_club: int, **kwargs) -> int:
    """Actualiza campos de un club por su ID."""
    set_clauses = [f"{k} = %s" for k in kwargs.keys()]
    values = list(kwargs.values())
    if not set_clauses: return 0

    query = f"UPDATE club_lectura SET {', '.join(set_clauses)} WHERE id_club = %s"
    params = tuple(values + [id_club])
    return execute_query(query, params, commit=True)



def borrar_club(id_club: int) -> int:
    """Borra un club por su ID."""
    return execute_query("DELETE FROM club_lectura WHERE id_club = %s", (id_club,), commit=True)


# ----------------------------------------------------------------------
# 4. CRUD USUARIO_CLUB
# ----------------------------------------------------------------------

def crear_usuario_club(id_usuario, id_club, estado_miembro='pendiente') -> Optional[int]:
    query = """INSERT INTO usuario_club (id_usuario, id_club, estado_miembro)
               VALUES (%s, %s, %s)"""
    # Nota: Esta tabla no tiene un auto_increment, lastrowid puede no ser útil.
    return execute_query(query, (id_usuario, id_club, estado_miembro), commit=True)


def leer_usuarios_club(id_club: Optional[int] = None) -> List[Dict[str, Any]]:
    if id_club:
        return execute_query("SELECT * FROM usuario_club WHERE id_club = %s", (id_club,), commit=False)
    else:
        return execute_query("SELECT * FROM usuario_club", commit=False)


# (Implementaciones de Actualizar/Borrar usuario_club serían similares)


# ----------------------------------------------------------------------
# 5. CRUD RESENA
# ----------------------------------------------------------------------

def crear_resena(contenido, calificacion, id_usuario, id_libro, id_resena_padre=None) -> Optional[int]:
    query = """INSERT INTO resena (contenido, calificacion, id_usuario, id_libro, id_resena_padre)
               VALUES (%s, %s, %s, %s, %s)"""
    return execute_query(query, (contenido, calificacion, id_usuario, id_libro, id_resena_padre), commit=True)


def leer_resenas(id_libro: Optional[int] = None) -> List[Dict[str, Any]]:
    if id_libro:
        return execute_query("SELECT * FROM resena WHERE id_libro = %s", (id_libro,), commit=False)
    else:
        return execute_query("SELECT * FROM resena", commit=False)


# (Implementaciones de Actualizar/Borrar resena serían similares)


# ----------------------------------------------------------------------
# 6. CRUD ORDEN_COMPRA
# ----------------------------------------------------------------------

def crear_orden(precio_total, direccion_envio, metodo_pago, id_comprador, id_libro, estado_orden='pedido') -> Optional[
    int]:
    query = """INSERT INTO orden_compra (precio_total, estado_orden, direccion_envio, metodo_pago, id_comprador, id_libro)
               VALUES (%s, %s, %s, %s, %s, %s)"""
    return execute_query(query, (precio_total, estado_orden, direccion_envio, metodo_pago, id_comprador, id_libro),
                         commit=True)


def leer_ordenes(id_comprador: Optional[int] = None) -> List[Dict[str, Any]]:
    if id_comprador:
        return execute_query("SELECT * FROM orden_compra WHERE id_comprador = %s", (id_comprador,), commit=False)
    else:
        return execute_query("SELECT * FROM orden_compra", commit=False)


# (Implementaciones de Actualizar/Borrar orden_compra serían similares)


# ----------------------------------------------------------------------
# 7. CRUD INTERCAMBIO
# ----------------------------------------------------------------------

def crear_intercambio(id_usuario_propone, id_usuario_recibe, id_libro_ofrecido, id_libro_solicitado,
                      estado_intercambio='propuesto', mensaje_propuesta=None, condiciones=None) -> Optional[int]:
    query = """INSERT INTO intercambio (estado_intercambio, mensaje_propuesta, condiciones, id_usuario_propone, id_usuario_recibe, id_libro_ofrecido, id_libro_solicitado)
               VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    params = (estado_intercambio, mensaje_propuesta, condiciones, id_usuario_propone, id_usuario_recibe,
              id_libro_ofrecido, id_libro_solicitado)
    return execute_query(query, params, commit=True)


def leer_intercambios(id_usuario: Optional[int] = None) -> List[Dict[str, Any]]:
    if id_usuario:
        query = "SELECT * FROM intercambio WHERE id_usuario_propone = %s OR id_usuario_recibe = %s"
        return execute_query(query, (id_usuario, id_usuario), commit=False)
    else:
        return execute_query("SELECT * FROM intercambio", commit=False)


# (Implementaciones de Actualizar/Borrar intercambio serían similares)


# ----------------------------------------------------------------------
# 8. CRUD LEER_LIBROS
# ----------------------------------------------------------------------

def crear_leer_libros(id_usuario, id_club, id_libro, fecha_inicio, fecha_fin=None) -> int:
    query = """INSERT INTO leer_libros (id_usuario, id_club, id_libro, fecha_inicio, fecha_fin)
               VALUES (%s, %s, %s, %s, %s)"""
    return execute_query(query, (id_usuario, id_club, id_libro, fecha_inicio, fecha_fin), commit=True)


def leer_registros_lectura(id_club: Optional[int] = None) -> List[Dict[str, Any]]:
    if id_club:
        return execute_query("SELECT * FROM leer_libros WHERE id_club = %s", (id_club,), commit=False)
    else:
        return execute_query("SELECT * FROM leer_libros", commit=False)


# (Implementaciones de Actualizar/Borrar leer_libros serían similares)


# ----------------------------------------------------------------------
# 9. CRUD REUNION
# ----------------------------------------------------------------------

def crear_reunion(id_club, fecha_reunion, tema, descripcion=None, lugar=None) -> Optional[int]:
    query = """INSERT INTO reunion (id_club, fecha_reunion, tema, descripcion, lugar)
               VALUES (%s, %s, %s, %s, %s)"""
    return execute_query(query, (id_club, fecha_reunion, tema, descripcion, lugar), commit=True)


def leer_reuniones(id_club: Optional[int] = None) -> List[Dict[str, Any]]:
    if id_club:
        return execute_query("SELECT * FROM reunion WHERE id_club = %s", (id_club,), commit=False)
    else:
        return execute_query("SELECT * FROM reunion", commit=False)

# (Implementaciones de Actualizar/Borrar reunion serían similares)