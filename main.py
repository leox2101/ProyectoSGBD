# main.py
from cruds import (
    crear_usuario, leer_usuarios, actualizar_usuario, borrar_usuario,
    crear_libro, leer_libros, actualizar_libro, borrar_libro,
    crear_club, leer_clubes, actualizar_club, borrar_club,
    crear_usuario_club, leer_usuarios_club,
    crear_resena, leer_resenas,
    crear_orden, leer_ordenes,
    crear_intercambio, leer_intercambios,
    crear_leer_libros, leer_registros_lectura,
    crear_reunion, leer_reuniones,
    execute_query,
)
from conecction import get_db_connection
from datetime import date 


# ----------------------------------------------------------------------
# UTILITY FUNCTIONS (Se asume que la mayoría de los CRUDs no están completos)
# ----------------------------------------------------------------------

def display_results(items: list, title: str):
    """Función genérica para mostrar resultados en formato tabular."""
    if not items:
        print(f"No se encontraron registros para {title}.")
        return

    print(f"\n--- Resultados: {title} ({len(items)} registros) ---")

    # Obtener encabezados (claves del primer diccionario)
    headers = list(items[0].keys())

    # Definir anchos de columna fijos o basados en el contenido
    widths = {h: max(len(h), max(len(str(item.get(h, ''))[:30]) for item in items)) + 2 for h in headers}

    # Imprimir encabezados
    header_line = " | ".join(h.ljust(widths.get(h, len(h))) for h in headers)
    print(header_line)
    print("-" * len(header_line))

    # Imprimir filas
    for item in items:
        row = " | ".join(str(item.get(h, 'N/A')).ljust(widths.get(h, len(h))) for h in headers)
        print(row)
    print("-" * len(header_line))



# ----------------------------------------------------------------------
# CONSULTAS Y REPORTES - ENTREGA 3
# ----------------------------------------------------------------------

def consulta_1_miembros_por_club():
    print("\n[Consulta 1] Miembros de un club específico")
    id_club = input("Ingrese el ID del club: ").strip()
    if not id_club.isdigit():
        print("ID de club inválido.")
        return

    rows = execute_query("""
        SELECT c.id_club,
               c.nombre_club,
               u.id_usuario,
               u.nombre,
               u.email
        FROM usuario_club uc
        JOIN usuario u      ON uc.id_usuario = u.id_usuario
        JOIN club_lectura c ON uc.id_club    = c.id_club
        WHERE uc.estado_miembro = 'aceptado'
          AND c.id_club = %s;
    """, (int(id_club),), commit=False)
    display_results(rows, f"Miembros del club {id_club}")


def consulta_2_clubes_y_total_miembros():
    print("\n[Consulta 2] Clubs de lectura y total de miembros aceptados")
    rows = execute_query("""
        SELECT c.id_club,
               c.nombre_club,
               COUNT(CASE WHEN uc.estado_miembro = 'aceptado' THEN 1 END) AS total_miembros_aceptados
        FROM club_lectura c
        LEFT JOIN usuario_club uc ON c.id_club = uc.id_club
        GROUP BY c.id_club, c.nombre_club
        ORDER BY total_miembros_aceptados DESC;
    """, commit=False)
    display_results(rows, "Clubs y total de miembros aceptados")


def consulta_3_buscar_libros_propietario():
    print("\n[Consulta 3] Buscar libros por título o autor y mostrar propietario")
    termino = input("Ingrese parte del título o autor a buscar: ").strip()
    like = f"%{termino}%"
    rows = execute_query("""
        SELECT l.id_libro,
               l.titulo,
               l.autor,
               l.genero,
               u.nombre  AS propietario,
               u.email   AS email_propietario
        FROM libro l
        JOIN usuario u ON l.id_propietario = u.id_usuario
        WHERE l.titulo LIKE %s
           OR l.autor  LIKE %s;
    """, (like, like), commit=False)
    display_results(rows, f"Libros que coinciden con '{termino}'")


def consulta_4_buscar_usuarios_por_ciudad_y_club():
    print("\n[Consulta 4] Buscar usuarios por ciudad y club")
    ciudad = input("Ciudad (ej. Medellín): ").strip()
    filtro_club = input("Parte del nombre del club (o vacío para todos): ").strip()
    params = [ciudad]
    extra = ""
    if filtro_club:
        extra = "AND (c.nombre_club LIKE %s OR c.nombre_club IS NULL)"
        params.append(f"%{filtro_club}%")

    query = f"""
        SELECT DISTINCT u.id_usuario,
               u.nombre,
               u.email,
               u.ciudad,
               c.nombre_club
        FROM usuario u
        LEFT JOIN usuario_club uc ON u.id_usuario = uc.id_usuario
        LEFT JOIN club_lectura c  ON uc.id_club    = c.id_club
        WHERE u.ciudad = %s
        {extra}
        ORDER BY u.nombre;
    """
    rows = execute_query(query, tuple(params), commit=False)
    display_results(rows, f"Usuarios en {ciudad}")


def consulta_5_ordenes_por_ciudad_y_mes():
    print("\n[Consulta 5] Indicador de órdenes y ventas por ciudad y mes")
    rows = execute_query("""
        SELECT u.ciudad,
               YEAR(oc.fecha_pago)  AS anio,
               MONTH(oc.fecha_pago) AS mes,
               COUNT(oc.id_orden)   AS total_ordenes,
               SUM(oc.precio_total) AS total_vendido
        FROM orden_compra oc
        JOIN usuario u ON oc.id_comprador = u.id_usuario
        WHERE oc.estado_orden IN ('pagado','enviado','recibido')
        GROUP BY u.ciudad, YEAR(oc.fecha_pago), MONTH(oc.fecha_pago)
        ORDER BY u.ciudad, anio, mes;
    """, commit=False)
    display_results(rows, "Órdenes por ciudad y mes")


def consulta_6_ventas_por_libro():
    print("\n[Consulta 6] Libros vendidos y total de ingresos por libro")
    rows = execute_query("""
        SELECT l.id_libro,
               l.titulo,
               COUNT(oc.id_orden)                 AS veces_vendido,
               COALESCE(SUM(oc.precio_total), 0)  AS total_ingresos
        FROM libro l
        LEFT JOIN orden_compra oc
               ON l.id_libro = oc.id_libro
              AND oc.estado_orden IN ('pagado','enviado','recibido')
        GROUP BY l.id_libro, l.titulo
        ORDER BY veces_vendido DESC;
    """, commit=False)
    display_results(rows, "Ventas por libro")


def consulta_7_detalle_intercambios():
    print("\n[Consulta 7] Detalle de intercambios entre usuarios")
    rows = execute_query("""
        SELECT i.id_intercambio,
               u1.nombre AS usuario_propone,
               u2.nombre AS usuario_recibe,
               l1.titulo AS libro_ofrecido,
               l2.titulo AS libro_solicitado,
               i.estado_intercambio,
               i.fecha_propuesta
        FROM intercambio i
        JOIN usuario u1 ON i.id_usuario_propone  = u1.id_usuario
        JOIN usuario u2 ON i.id_usuario_recibe   = u2.id_usuario
        JOIN libro   l1 ON i.id_libro_ofrecido   = l1.id_libro
        JOIN libro   l2 ON i.id_libro_solicitado = l2.id_libro;
    """, commit=False)
    display_results(rows, "Intercambios entre usuarios")


def consulta_8_intercambios_completados_por_usuario():
    print("\n[Consulta 8] Intercambios completados por usuario que propone")
    rows = execute_query("""
        SELECT u.id_usuario,
               u.nombre,
               COUNT(i.id_intercambio) AS intercambios_completados
        FROM usuario u
        JOIN intercambio i ON u.id_usuario = i.id_usuario_propone
        WHERE i.estado_intercambio = 'completado'
        GROUP BY u.id_usuario, u.nombre
        ORDER BY intercambios_completados DESC;
    """, commit=False)
    display_results(rows, "Intercambios completados por usuario")


def consulta_9_promedio_calificacion_por_libro():
    print("\n[Consulta 9] Promedio de calificación por libro (>= 4)")
    rows = execute_query("""
        SELECT l.id_libro,
               l.titulo,
               ROUND(AVG(r.calificacion), 2) AS promedio_calificacion,
               COUNT(r.id_resena)            AS total_resenas
        FROM libro l
        JOIN resena r ON l.id_libro = r.id_libro
        GROUP BY l.id_libro, l.titulo
        HAVING promedio_calificacion >= 4
        ORDER BY promedio_calificacion DESC;
    """, commit=False)
    display_results(rows, "Promedio de calificación por libro")


def consulta_10_promedio_calificacion_por_usuario():
    print("\n[Consulta 10] Promedio de calificación dada por usuario")
    rows = execute_query("""
        SELECT u.id_usuario,
               u.nombre,
               ROUND(AVG(r.calificacion), 2) AS promedio_calificaciones_dadas,
               COUNT(r.id_resena)            AS total_resenas
        FROM usuario u
        JOIN resena r ON u.id_usuario = r.id_usuario
        GROUP BY u.id_usuario, u.nombre
        ORDER BY promedio_calificaciones_dadas DESC;
    """, commit=False)
    display_results(rows, "Promedio de calificación dada por usuario")


def consulta_11_proximas_reuniones():
    print("\n[Consulta 11] Próximas reuniones por club")
    rows = execute_query("""
        SELECT c.id_club,
               c.nombre_club,
               r.fecha_reunion,
               r.tema,
               r.lugar
        FROM reunion r
        JOIN club_lectura c ON r.id_club = c.id_club
        WHERE r.fecha_reunion >= NOW()
        ORDER BY r.fecha_reunion;
    """, commit=False)
    display_results(rows, "Próximas reuniones")


def consulta_12_libros_en_lectura_por_club():
    print("\n[Consulta 12] Libros en lectura actual por club")
    rows = execute_query("""
        SELECT c.id_club,
               c.nombre_club,
               COUNT(ll.id_libro) AS libros_en_lectura_actual
        FROM club_lectura c
        LEFT JOIN leer_libros ll
               ON c.id_club = ll.id_club
              AND ll.fecha_fin IS NULL
        GROUP BY c.id_club, c.nombre_club
        ORDER BY libros_en_lectura_actual DESC;
    """, commit=False)
    display_results(rows, "Libros en lectura actual por club")


def consulta_13_clubes_por_usuario():
    print("\n[Consulta 13] Número de clubes en los que participa cada usuario")
    rows = execute_query("""
        SELECT u.id_usuario,
               u.nombre,
               COUNT(CASE WHEN uc.estado_miembro = 'aceptado' THEN 1 END) AS clubes_aceptados
        FROM usuario u
        LEFT JOIN usuario_club uc ON u.id_usuario = uc.id_usuario
        GROUP BY u.id_usuario, u.nombre
        ORDER BY clubes_aceptados DESC;
    """, commit=False)
    display_results(rows, "Clubes por usuario")


def consulta_14_libros_clubes_y_lectores():
    print("\n[Consulta 14] Libros con clubes asociados y número de lectores actuales")
    rows = execute_query("""
        SELECT l.id_libro,
               l.titulo,
               COUNT(DISTINCT c.id_club)     AS num_clubes_asociados,
               COUNT(DISTINCT ll.id_usuario) AS num_lectores_activos
        FROM libro l
        JOIN club_lectura c ON l.id_libro = c.id_libro
        LEFT JOIN leer_libros ll
               ON l.id_libro = ll.id_libro
              AND ll.fecha_fin IS NULL
        GROUP BY l.id_libro, l.titulo
        ORDER BY num_lectores_activos DESC;
    """, commit=False)
    display_results(rows, "Libros, clubes y lectores activos")


def consulta_15_usuarios_con_club_sin_compras():
    print("\n[Consulta 15] Usuarios con clubes aceptados pero sin compras")
    rows = execute_query("""
        SELECT DISTINCT u.id_usuario,
               u.nombre,
               u.email,
               u.ciudad
        FROM usuario u
        JOIN usuario_club uc
               ON u.id_usuario = uc.id_usuario
              AND uc.estado_miembro = 'aceptado'
        LEFT JOIN orden_compra oc
               ON u.id_usuario = oc.id_comprador
        WHERE oc.id_orden IS NULL
        ORDER BY u.nombre;
    """, commit=False)
    display_results(rows, "Usuarios con clubes pero sin compras")


def menu_consultas():
    """Menú de consultas y reportes (Entrega 3)."""
    while True:
        print("\n=== CONSULTAS Y REPORTES (ENTREGA 3) ===")
        print("1. Miembros de un club (nombres y emails)")
        print("2. Clubs de lectura y total de miembros aceptados")
        print("3. Buscar libros por título/autor y propietario")
        print("4. Buscar usuarios por ciudad y club")
        print("5. Indicador: órdenes y ventas por ciudad y mes")
        print("6. Indicador: ventas por libro")
        print("7. Detalle de intercambios entre usuarios")
        print("8. Indicador: intercambios completados por usuario")
        print("9. Promedio de calificación por libro (>= 4)")
        print("10. Promedio de calificación dada por usuario")
        print("11. Próximas reuniones por club")
        print("12. Libros en lectura actual por club")
        print("13. Número de clubes por usuario")
        print("14. Libros con clubes asociados y lectores activos")
        print("15. Usuarios con clubes pero sin compras")
        print("16. 🔙 Volver al menú principal")

        opcion = input("Opción (1-16): ").strip()

        if   opcion == '1':  consulta_1_miembros_por_club()
        elif opcion == '2':  consulta_2_clubes_y_total_miembros()
        elif opcion == '3':  consulta_3_buscar_libros_propietario()
        elif opcion == '4':  consulta_4_buscar_usuarios_por_ciudad_y_club()
        elif opcion == '5':  consulta_5_ordenes_por_ciudad_y_mes()
        elif opcion == '6':  consulta_6_ventas_por_libro()
        elif opcion == '7':  consulta_7_detalle_intercambios()
        elif opcion == '8':  consulta_8_intercambios_completados_por_usuario()
        elif opcion == '9':  consulta_9_promedio_calificacion_por_libro()
        elif opcion == '10': consulta_10_promedio_calificacion_por_usuario()
        elif opcion == '11': consulta_11_proximas_reuniones()
        elif opcion == '12': consulta_12_libros_en_lectura_por_club()
        elif opcion == '13': consulta_13_clubes_por_usuario()
        elif opcion == '14': consulta_14_libros_clubes_y_lectores()
        elif opcion == '15': consulta_15_usuarios_con_club_sin_compras()
        elif opcion == '16':
            break
        else:
            print("Opción no válida. Intente de nuevo.")


# ----------------------------------------------------------------------
# CRUD USUARIO (Se mantiene como ejemplo completo)
# ----------------------------------------------------------------------

def menu_crear_usuario():
    print("\n--- CREAR NUEVO USUARIO ---")
    nombre = input("Nombre completo (requerido): ")
    email = input("Email (requerido, debe ser único): ")
    password_hash = input("Contraseña (hash simple): ")
    ciudad = input("Ciudad (opcional): ")
    telefono = input("Teléfono (opcional): ")

    user_id = crear_usuario(nombre, email, password_hash, ciudad, telefono)
    if user_id and user_id != -1:
        print(f"Resultado: Usuario creado con ID: {user_id}")
    elif user_id == -1:
        print("Resultado: Falló la creación (ver error de DB arriba).")


def menu_leer_usuarios():
    while True:
        print("\n--- LEER USUARIOS ---")
        print("1. 🔎 Listar todos los usuarios")
        print("2. 📧 Buscar por Email")
        print("3. 🔢 Buscar por ID")
        print("4. 🔙 Volver")

        opcion_leer = input("Seleccione una opción (1-4): ")

        if opcion_leer == '1':
            usuarios = leer_usuarios()
            display_results(usuarios, "Usuarios")
            break
        elif opcion_leer == '2':
            valor = input("Ingrese el email del usuario: ")
            usuarios = leer_usuarios(campo='email', valor=valor)
            display_results(usuarios, f"Usuario con Email '{valor}'")
            break
        elif opcion_leer == '3':
            valor = input("Ingrese el ID del usuario: ")
            usuarios = leer_usuarios(campo='id_usuario', valor=valor)
            display_results(usuarios, f"Usuario con ID '{valor}'")
            break
        elif opcion_leer == '4':
            return
        else:
            print("Opción no válida.")


def menu_actualizar_usuario():
    print("\n--- ACTUALIZAR USUARIO ---")
    user_id = input("Ingrese el ID del usuario a actualizar: ")
    try:
        user_id_int = int(user_id)
    except ValueError:
        print("ID inválido.")
        return

    print("Deje en blanco los campos que NO desea modificar.")
    nuevo_email = input("Nuevo email (o Enter para omitir): ")
    nueva_ciudad = input("Nueva ciudad (o Enter para omitir): ")
    nuevo_telefono = input("Nuevo teléfono (o Enter para omitir): ")

    updates = {}
    if nuevo_email:
        updates["email"] = nuevo_email
    if nueva_ciudad:
        updates["ciudad"] = nueva_ciudad
    if nuevo_telefono:
        updates["telefono"] = nuevo_telefono

    if not updates:
        print("No se ingresaron cambios. Operación cancelada.")
        return

    filas = actualizar_usuario(user_id_int, **updates)
    if filas > 0:
        print(f"✅ Usuario ID {user_id} actualizado.")
    elif filas == 0:
        print(f"✏️ No se encontró el usuario ID {user_id} o no hubo cambios.")
    else:
        print("❌ Error al actualizar.")


def menu_borrar_usuario():
    print("\n--- BORRAR USUARIO ---")
    user_id = input("Ingrese el ID del usuario a ELIMINAR: ")
    try:
        user_id_int = int(user_id)
    except ValueError:
        print("ID inválido.")
        return

    confirmacion = input(f"¿Está seguro que desea eliminar el usuario ID '{user_id}'? (s/N): ").lower()
    if confirmacion == 's':
        filas = borrar_usuario(user_id_int)
        if filas > 0:
            print(f"🗑️ Usuario ID {user_id} eliminado.")
        elif filas == 0:
            print(f"🗑️ No se encontró el usuario ID {user_id}.")
        else:
            print("❌ Error al borrar.")
    else:
        print("Operación cancelada.")


def menu_crud_usuario():
    while True:
        print("\n=== CRUD TABLA USUARIO ===")
        print("1. ➕ Crear nuevo usuario")
        print("2. 🔎 Leer/Buscar usuarios")
        print("3. ✏️ Actualizar usuario")
        print("4. 🗑️ Borrar usuario")
        print("5. 🔙 Volver al menú principal")

        opcion = input("Seleccione una opción (1-5): ")

        if opcion == '1':
            menu_crear_usuario()
        elif opcion == '2':
            menu_leer_usuarios()
        elif opcion == '3':
            menu_actualizar_usuario()
        elif opcion == '4':
            menu_borrar_usuario()
        elif opcion == '5':
            break
        else:
            print("Opción no válida.")


# ----------------------------------------------------------------------
# CRUD LIBRO (estructura básica, sin implementar todo)
# ----------------------------------------------------------------------

def menu_crud_libro():
    while True:
        print("\n=== CRUD TABLA LIBRO ===")
        print("1. ➕ Crear nuevo libro (No implementado)")
        print("2. 🔎 Leer/Listar libros (No implementado)")
        print("3. ✏️ Actualizar libro (No implementado)")
        print("4. 🗑️ Borrar libro (No implementado)")
        print("5. 🔙 Volver al menú principal")

        opcion = input("Seleccione una opción (1-5): ")

        if opcion == '1':
            print("Función de crear libro no implementada en el menú.")
        elif opcion == '2':
            print("Función de leer libro no implementada en el menú.")
        elif opcion == '3' or opcion == '4':
            print("❌ Función de Actualizar/Borrar no implementada para Libro en este menú.")
        elif opcion == '5':
            break
        else:
            print("Opción no válida.")


# ----------------------------------------------------------------------
# CRUD CLUB LECTURA (estructura básica)
# ----------------------------------------------------------------------

def menu_crud_club():
    while True:
        print("\n=== CRUD TABLA CLUB_LECTURA ===")
        print("1. ➕ Crear nuevo club (No implementado)")
        print("2. 🔎 Leer/Listar clubes (No implementado)")
        print("3. 🔙 Volver al menú principal")

        opcion = input("Seleccione una opción (1-3): ")

        if opcion == '1':
            print("Función de crear club no implementada en este menú.")
        elif opcion == '2':
            print("Función de leer clubes no implementada en este menú.")
        elif opcion == '3':
            break
        else:
            print("Opción no válida.")


# ----------------------------------------------------------------------
# CRUD REUNIÓN (solo lectura/búsqueda)
# ----------------------------------------------------------------------

def menu_crud_reunion():
    while True:
        print("\n=== GESTIÓN DE REUNIONES ===")
        print("1. 🔎 Listar todas las reuniones")
        print("2. 🔎 Buscar reuniones por ID de Club")
        print("3. ➕ Crear reunión (No implementado)")
        print("4. 🔙 Volver")

        opcion = input("Seleccione una opción (1-4): ")

        if opcion == '1':
            reuniones = leer_reuniones()
            display_results(reuniones, "Reuniones")
        elif opcion == '2':
            id_club = input("Ingrese el ID del Club para ver sus reuniones: ")
            try:
                id_club_int = int(id_club)
                reuniones = leer_reuniones(id_club_int)
                display_results(reuniones, f"Reuniones del Club ID {id_club}")
            except ValueError:
                print("ID de club inválido.")
        elif opcion == '3':
            print("❌ Función de Crear reunión no implementada en el menú.")
        elif opcion == '4':
            break
        else:
            print("Opción no válida.")


# ----------------------------------------------------------------------
# CRUD USUARIO_CLUB (miembros de clubes)
# ----------------------------------------------------------------------

def menu_crud_usuario_club():
    """Menú para la tabla USUARIO_CLUB (Miembros de Clubes)."""
    while True:
        print("\n=== GESTIÓN DE MIEMBROS DE CLUB ===")
        print("1. 🔎 Listar todas las afiliaciones")
        print("2. 🔎 Buscar miembros por ID de Club")
        print("3. ➕ Afiliar usuario a club (No implementado)")
        print("4. 🔙 Volver")

        opcion = input("Seleccione una opción (1-4): ")

        if opcion == '1':
            afiliaciones = leer_usuarios_club()
            display_results(afiliaciones, "Afiliaciones a Clubes")
        elif opcion == '2':
            id_club = input("Ingrese el ID del Club para ver sus miembros: ")
            try:
                id_club_int = int(id_club)
                afiliaciones = leer_usuarios_club(id_club_int)
                display_results(afiliaciones, f"Miembros del Club ID {id_club}")
            except ValueError:
                print("ID de club inválido.")
        elif opcion == '3':
            print("❌ Función de Afiliar miembro no implementada en el menú.")
        elif opcion == '4':
            break
        else:
            print("Opción no válida.")


# ----------------------------------------------------------------------
# CRUD LEER_LIBROS (registros de lectura)
# ----------------------------------------------------------------------

def menu_crud_leer_libros():
    """Menú para la tabla LEER_LIBROS (Registros de Lectura)."""
    while True:
        print("\n=== GESTIÓN DE REGISTROS DE LECTURA ===")
        print("1. 🔎 Listar todos los registros de lectura")
        print("2. 🔎 Buscar registros por ID de Club")
        print("3. 🔙 Volver")

        opcion = input("Seleccione una opción (1-3): ")

        if opcion == '1':
            registros = leer_registros_lectura()
            display_results(registros, "Registros de Lectura")
        elif opcion == '2':
            id_club = input("Ingrese el ID del Club: ")
            try:
                id_club_int = int(id_club)
                registros = leer_registros_lectura(id_club_int)
                display_results(registros, f"Registros de lectura del Club ID {id_club}")
            except ValueError:
                print("ID de club inválido.")
        elif opcion == '3':
            break
        else:
            print("Opción no válida.")


# ----------------------------------------------------------------------
# MENÚ PRINCIPAL
# ----------------------------------------------------------------------

def menu_principal():
    conn_check = get_db_connection()
    if not conn_check:
        print("\n🛑 **ERROR CRÍTICO:** No se pudo conectar a la base de datos. Revise 'connection.py'.")
        return
    conn_check.close()

    while True:
        print("\n==================================")
        print("📚 MENÚ PRINCIPAL - GESTOR DEL SISTEMA")
        print("==================================")
        print("Seleccione la opción:")
        print("1. 👤 Usuario (CRUD Completo)")
        print("2. 📖 Libro (CRUD Básico)")
        print("3. 🧑‍🤝‍🧑 Club Lectura (CRUD Básico)")
        print("--- Tablas relacionadas ---")
        print("4. 🤝 Intercambio (CRUD Básico)")
        print("5. ⭐ Reseña (CRUD Básico)")
        print("6. 📅 Reunión (Ver/Buscar)")
        print("7. 👥 Miembros de Club (Ver/Buscar)")
        print("8. 🔖 Registros de Lectura (Ver/Buscar)")
        print("9. 📊 Consultas y Reportes (Entrega 3)")
        print("10. 🚪 Salir")

        opcion = input("Opción (1-10): ").strip()

        if opcion == '1':
            menu_crud_usuario()
        elif opcion == '2':
            menu_crud_libro()  # CRUD parcial
        elif opcion == '3':
            menu_crud_club()  # CRUD parcial
        elif opcion == '4':
            print("Función CRUD Intercambio no implementada en el menú.")
        elif opcion == '5':
            print("Función CRUD Reseña no implementada en el menú.")
        elif opcion == '6':
            menu_crud_reunion()
        elif opcion == '7':
            menu_crud_usuario_club()
        elif opcion == '8':
            menu_crud_leer_libros()
        elif opcion == '9':
            menu_consultas()
        elif opcion == '10':
            print("¡Gracias por usar el gestor de libros circulares! 👋")
            break
        else:
            print("Opción no válida. Intente de nuevo.")


if __name__ == "__main__":
    menu_principal()
