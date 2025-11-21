-- CONSULTAS DEL PROYECTO (Entrega 3)

USE libros_circulares;

-- 1. Miembros de un club
SELECT c.id_club, c.nombre_club, u.id_usuario, u.nombre, u.email
FROM usuario_club uc
JOIN usuario u ON uc.id_usuario = u.id_usuario
JOIN club_lectura c ON uc.id_club = c.id_club
WHERE uc.estado_miembro = 'aceptado';

-- 2. Total de miembros por club
SELECT c.id_club, c.nombre_club,
       COUNT(CASE WHEN uc.estado_miembro = 'aceptado' THEN 1 END) AS total_miembros
FROM club_lectura c
LEFT JOIN usuario_club uc ON c.id_club = uc.id_club
GROUP BY c.id_club, c.nombre_club;

-- 3. Buscar libros por título o autor
SELECT l.id_libro, l.titulo, l.autor, u.nombre AS propietario
FROM libro l
JOIN usuario u ON l.id_propietario = u.id_usuario
WHERE l.titulo LIKE '%a%' OR l.autor LIKE '%a%';

-- 4. Usuarios por ciudad y club
SELECT u.id_usuario, u.nombre, u.email, u.ciudad, c.nombre_club
FROM usuario u
LEFT JOIN usuario_club uc ON u.id_usuario = uc.id_usuario
LEFT JOIN club_lectura c ON uc.id_club = c.id_club
WHERE u.ciudad = 'Medellín';

-- 5. Órdenes por ciudad y mes
SELECT u.ciudad,
       YEAR(oc.fecha_pago) AS anio,
       MONTH(oc.fecha_pago) AS mes,
       COUNT(oc.id_orden) AS total_ordenes
FROM orden_compra oc
JOIN usuario u ON oc.id_comprador = u.id_usuario
GROUP BY u.ciudad, anio, mes;

-- 6. Ventas por libro
SELECT l.id_libro, l.titulo,
       COUNT(oc.id_orden) AS veces_vendido
FROM libro l
LEFT JOIN orden_compra oc ON l.id_libro = oc.id_libro
GROUP BY l.id_libro, l.titulo;

-- 7. Detalle de intercambios
SELECT i.id_intercambio, u1.nombre AS propone, u2.nombre AS recibe,
       l1.titulo AS libro_ofrecido, l2.titulo AS libro_solicitado
FROM intercambio i
JOIN usuario u1 ON i.id_usuario_propone = u1.id_usuario
JOIN usuario u2 ON i.id_usuario_recibe = u2.id_usuario
JOIN libro l1 ON i.id_libro_ofrecido = l1.id_libro
JOIN libro l2 ON i.id_libro_solicitado = l2.id_libro;

-- 8. Intercambios completados por usuario
SELECT u.id_usuario, u.nombre,
       COUNT(i.id_intercambio) AS completados
FROM usuario u
JOIN intercambio i ON u.id_usuario = i.id_usuario_propone
WHERE i.estado_intercambio = 'completado'
GROUP BY u.id_usuario, u.nombre;

-- 9. Promedio de calificación por libro
SELECT l.id_libro, l.titulo,
       ROUND(AVG(r.calificacion),2) AS promedio
FROM libro l
JOIN resena r ON l.id_libro = r.id_libro
GROUP BY l.id_libro, l.titulo;

-- 10. Promedio de calificación por usuario
SELECT u.id_usuario, u.nombre,
       ROUND(AVG(r.calificacion),2) AS promedio
FROM usuario u
JOIN resena r ON u.id_usuario = r.id_usuario
GROUP BY u.id_usuario, u.nombre;

-- 11. Próximas reuniones
SELECT c.nombre_club, r.fecha_reunion, r.tema, r.lugar
FROM reunion r
JOIN club_lectura c ON r.id_club = c.id_club
WHERE r.fecha_reunion >= NOW();

-- 12. Libros en lectura actual
SELECT c.nombre_club, COUNT(ll.id_libro) AS leyendo
FROM club_lectura c
LEFT JOIN leer_libros ll ON c.id_club = ll.id_club AND ll.fecha_fin IS NULL
GROUP BY c.id_club, c.nombre_club;

-- 13. Total de clubes por usuario
SELECT u.id_usuario, u.nombre,
       COUNT(uc.id_club) AS clubes
FROM usuario u
LEFT JOIN usuario_club uc ON u.id_usuario = uc.id_usuario AND uc.estado_miembro='aceptado'
GROUP BY u.id_usuario, u.nombre;

-- 14. Libros con clubes y lectores activos
SELECT l.id_libro, l.titulo,
       COUNT(DISTINCT c.id_club) AS clubes,
       COUNT(DISTINCT ll.id_usuario) AS lectores
FROM libro l
JOIN club_lectura c ON l.id_libro = c.id_libro
LEFT JOIN leer_libros ll ON l.id_libro = ll.id_libro AND ll.fecha_fin IS NULL
GROUP BY l.id_libro, l.titulo;

-- 15. Usuarios con clubes pero sin compras
SELECT DISTINCT u.id_usuario, u.nombre, u.email
FROM usuario u
JOIN usuario_club uc ON u.id_usuario = uc.id_usuario AND uc.estado_miembro='aceptado'
LEFT JOIN orden_compra oc ON u.id_usuario = oc.id_comprador
WHERE oc.id_orden IS NULL;
