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
from datetime import date  # Necesario para fechas


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
        user_id = int(user_id)
    except ValueError:
        print("ID inválido.")
        return

    updates = {}
    nombre = input("Nuevo Nombre (vacío para no cambiar): ")
    if nombre: updates['nombre'] = nombre
    ciudad = input("Nueva Ciudad (vacío para no cambiar): ")
    if ciudad: updates['ciudad'] = ciudad

    if not updates:
        print("No se proporcionaron campos para actualizar.")
        return

    filas = actualizar_usuario(user_id, **updates)
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
        user_id = int(user_id)
    except ValueError:
        print("ID inválido.")
        return

    confirmacion = input(f"¿Está seguro que desea eliminar el usuario ID '{user_id}'? (s/N): ").lower()
    if confirmacion == 's':
        filas = borrar_usuario(user_id)
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
        print("2. 🔎 Leer/Listar usuarios")
        print("3. ✏️ Actualizar usuario (por ID)")
        print("4. 🗑️ Borrar usuario (por ID)")
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
# CRUD LIBRO (Se mantiene la estructura para Crear/Leer)
# ----------------------------------------------------------------------

def menu_crud_libro():
    while True:
        print("\n=== CRUD TABLA LIBRO ===")
        print("1. ➕ Crear nuevo libro (Implementado)")
        print("2. 🔎 Leer/Listar libros (Implementado)")
        print("3. ✏️ Actualizar libro (No implementado)")
        print("4. 🗑️ Borrar libro (No implementado)")
        print("5. 🔙 Volver al menú principal")

        opcion = input("Seleccione una opción (1-5): ")

        if opcion == '1':
            # menu_crear_libro() # Llamar a la función implementada en el prompt anterior
            print("Función de crear libro no implementada en el menú.")
        elif opcion == '2':
            # menu_leer_libros() # Llamar a la función implementada en el prompt anterior
            print("Función de leer libro no implementada en el menú.")
        elif opcion == '3' or opcion == '4':
            print("❌ Función de Actualizar/Borrar no implementada para Libro en este menú.")
        elif opcion == '5':
            break
        else:
            print("Opción no válida.")


# ----------------------------------------------------------------------
# CRUD CLUB LECTURA (Se mantiene la estructura para Crear/Leer)
# ----------------------------------------------------------------------

def menu_crud_club():
    while True:
        print("\n=== CRUD TABLA CLUB_LECTURA ===")
        print("1. ➕ Crear nuevo club (Implementado)")
        print("2. 🔎 Leer/Listar clubes (Implementado)")
        print("3. 🔙 Volver al menú principal")

        opcion = input("Seleccione una opción (1-3): ")

        if opcion == '1':
            # menu_crear_club() # Llamar a la función implementada en el prompt anterior
            print("Función de crear club no implementada en el menú.")
        elif opcion == '2':
            clubes = leer_clubes()
            display_results(clubes, "Clubes de Lectura")
        elif opcion == '3':
            break
        else:
            print("Opción no válida.")


# ----------------------------------------------------------------------
# NUEVOS MENÚS (REUNION, USUARIO_CLUB, LEER_LIBROS)
# ----------------------------------------------------------------------

def menu_crud_reunion():
    """Menú para la tabla REUNION."""
    while True:
        print("\n=== GESTIÓN DE REUNIONES ===")
        print("1. 🔎 Listar todas las reuniones")
        print("2. 🔎 Buscar reuniones por ID de Club")
        print("3. ➕ Crear reunión (No implementado)")
        print("4. 🔙 Volver")

        opcion = input("Seleccione una opción (1-4): ")

        if opcion == '1':
            reuniones = leer_reuniones()
            display_results(reuniones, "Todas las Reuniones")
        elif opcion == '2':
            id_club = input("Ingrese el ID del Club para ver sus reuniones: ")
            try:
                reuniones = leer_reuniones(int(id_club))
                display_results(reuniones, f"Reuniones del Club ID {id_club}")
            except ValueError:
                print("ID de club inválido.")
        elif opcion == '3':
            print("❌ Función de Crear reunión no implementada en el menú.")
        elif opcion == '4':
            break
        else:
            print("Opción no válida.")


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
                afiliaciones = leer_usuarios_club(int(id_club))
                display_results(afiliaciones, f"Miembros del Club ID {id_club}")
            except ValueError:
                print("ID de club inválido.")
        elif opcion == '3':
            print("❌ Función de Afiliar miembro no implementada en el menú.")
        elif opcion == '4':
            break
        else:
            print("Opción no válida.")


def menu_crud_leer_libros():
    """Menú para la tabla LEER_LIBROS (Registros de Lectura)."""
    while True:
        print("\n=== GESTIÓN DE REGISTROS DE LECTURA ===")
        print("1. 🔎 Listar todos los registros de lectura")
        print("2. 🔎 Buscar registros por ID de Club")
        print("3. ➕ Crear registro de lectura (No implementado)")
        print("4. 🔙 Volver")

        opcion = input("Seleccione una opción (1-4): ")

        if opcion == '1':
            registros = leer_registros_lectura()
            display_results(registros, "Todos los Registros de Lectura")
        elif opcion == '2':
            id_club = input("Ingrese el ID del Club para ver sus registros de lectura: ")
            try:
                registros = leer_registros_lectura(int(id_club))
                display_results(registros, f"Registros de Lectura del Club ID {id_club}")
            except ValueError:
                print("ID de club inválido.")
        elif opcion == '3':
            print("❌ Función de Crear registro no implementada en el menú.")
        elif opcion == '4':
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
        print("📚 MENÚ PRINCIPAL - GESTOR DE CRUDS")
        print("==================================")
        print("Seleccione la tabla para gestionar:")
        print("1. 👤 Usuario (CRUD Completo)")
        print("2. 📖 Libro (CRUD Básico)")
        print("3. 🧑‍🤝‍🧑 Club Lectura (CRUD Básico)")
        print("--- Tablas relacionadas ---")
        print("4. 🤝 Intercambio (CRUD Básico)")
        print("5. ⭐ Reseña (CRUD Básico)")
        print("6. 📅 Reunión (Ver/Buscar)")
        print("7. 👥 Miembros de Club (Ver/Buscar)")
        print("8. 🔖 Registros de Lectura (Ver/Buscar)")
        print("9. 🚪 Salir")

        opcion = input("Opción (1-9): ")

        if opcion == '1':
            menu_crud_usuario()
        elif opcion == '2':
            menu_crud_libro()  # Necesita terminar de implementar CRUD
        elif opcion == '3':
            menu_crud_club()  # Necesita terminar de implementar CRUD
        elif opcion == '4':
            print("Función CRUD Intercambio no implementada.")
        elif opcion == '5':
            print("Función CRUD Reseña no implementada.")
        elif opcion == '6':
            menu_crud_reunion()
        elif opcion == '7':
            menu_crud_usuario_club()
        elif opcion == '8':
            menu_crud_leer_libros()
        elif opcion == '9':
            print("¡Gracias por usar el gestor de libros circulares! 👋")
            break
        else:
            print("Opción no válida. Intente de nuevo.")


if __name__ == "__main__":

    menu_principal()
