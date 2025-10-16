
SET NAMES utf8mb4;
SET time_zone = '+00:00';

CREATE DATABASE IF NOT EXISTS libros_circulares
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;
USE libros_circulares;


-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuario (
  id_usuario        BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nombre            VARCHAR(120) NOT NULL,
  email             VARCHAR(190) NOT NULL UNIQUE,
  password_hash     VARCHAR(255) NOT NULL,
  ciudad            VARCHAR(120),
  telefono          VARCHAR(40),
  fecha_registro    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  rol               ENUM('admin','usuario') NOT NULL DEFAULT 'usuario'
) ENGINE=InnoDB;


-- Tabla de libros
CREATE TABLE IF NOT EXISTS libro (
  id_libro               BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  titulo                 VARCHAR(250) NOT NULL,
  autor                  VARCHAR(250) NOT NULL,
  isbn                   VARCHAR(20) UNIQUE,
  genero                 VARCHAR(120),
  resumen                TEXT,
  anio_publicacion       YEAR,
  editorial              VARCHAR(150),
  paginas                INT UNSIGNED,
  idioma                 VARCHAR(80),
  estado_fisico          VARCHAR(100),
  id_propietario         BIGINT UNSIGNED NOT NULL,
  en_catalogo            TINYINT(1) NOT NULL DEFAULT 0,
  modalidad_publicacion  ENUM('visible','intercambio','venta') NOT NULL DEFAULT 'visible',
  precio_venta           DECIMAL(12,2) DEFAULT NULL,
  fecha_creacion         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_libro_propietario
    FOREIGN KEY (id_propietario) REFERENCES usuario(id_usuario)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT chk_precio_modalidad
    CHECK (
      (modalidad_publicacion <> 'venta' AND precio_venta IS NULL)
      OR (modalidad_publicacion = 'venta' AND precio_venta IS NOT NULL AND precio_venta > 0)
    )
) ENGINE=InnoDB;

CREATE INDEX idx_libro_propietario ON libro(id_propietario);
CREATE INDEX idx_libro_modalidad ON libro(modalidad_publicacion, en_catalogo);
CREATE FULLTEXT INDEX ftx_libro_busqueda ON libro(titulo, autor, genero, resumen);


-- Tabla de clubes de lectura
CREATE TABLE IF NOT EXISTS club_lectura (
  id_club          BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  nombre_club      VARCHAR(180) NOT NULL,
  descripcion      TEXT,
  fecha_inicio     DATE NOT NULL,
  fecha_fin        DATE DEFAULT NULL,
  estado           ENUM('activo','finalizado','suspendido') NOT NULL DEFAULT 'activo',
  id_libro         BIGINT UNSIGNED NOT NULL,
  id_administrador BIGINT UNSIGNED NOT NULL,
  max_miembros     INT UNSIGNED NOT NULL,
  CONSTRAINT fk_club_libro
    FOREIGN KEY (id_libro) REFERENCES libro(id_libro)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_club_admin
    FOREIGN KEY (id_administrador) REFERENCES usuario(id_usuario)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT chk_max_miembros CHECK (max_miembros > 0)
) ENGINE=InnoDB;

CREATE INDEX idx_club_libro ON club_lectura(id_libro);
CREATE INDEX idx_club_estado ON club_lectura(estado);


-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuario_club (
  id_usuario     BIGINT UNSIGNED NOT NULL,
  id_club        BIGINT UNSIGNED NOT NULL,
  fecha_union    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  estado_miembro ENUM('pendiente','aceptado','expulsado','retirado') NOT NULL DEFAULT 'pendiente',
  PRIMARY KEY (id_usuario, id_club),
  CONSTRAINT fk_uc_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_uc_club
    FOREIGN KEY (id_club) REFERENCES club_lectura(id_club)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_uc_estado ON usuario_club(estado_miembro);


-- Tabla de reseñas de libros
CREATE TABLE IF NOT EXISTS resena (
  id_resena          BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  contenido          TEXT NOT NULL,
  calificacion       TINYINT UNSIGNED NOT NULL,
  fecha_publicacion  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  id_usuario         BIGINT UNSIGNED NOT NULL,
  id_libro           BIGINT UNSIGNED NOT NULL,
  id_resena_padre    BIGINT UNSIGNED DEFAULT NULL,
  CONSTRAINT chk_calificacion CHECK (calificacion BETWEEN 1 AND 5),
  CONSTRAINT fk_resena_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_resena_libro
    FOREIGN KEY (id_libro) REFERENCES libro(id_libro)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_resena_padre
    FOREIGN KEY (id_resena_padre) REFERENCES resena(id_resena)
    ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX idx_resena_libro ON resena(id_libro);
CREATE INDEX idx_resena_usuario ON resena(id_usuario);


-- Tabla de órdenes de compra
CREATE TABLE IF NOT EXISTS orden_compra (
  id_orden        BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  precio_total    DECIMAL(12,2) NOT NULL CHECK (precio_total > 0),
  estado_orden    ENUM('pedido','pagado','cancelado','enviado','recibido') NOT NULL DEFAULT 'pedido',
  fecha_pedido    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_pago      DATETIME DEFAULT NULL,
  fecha_envio     DATETIME DEFAULT NULL,
  fecha_recepcion DATETIME DEFAULT NULL,
  direccion_envio VARCHAR(300) NOT NULL,
  metodo_pago     VARCHAR(60) NOT NULL,
  id_comprador    BIGINT UNSIGNED NOT NULL,
  id_libro        BIGINT UNSIGNED NOT NULL,
  CONSTRAINT fk_orden_comprador
    FOREIGN KEY (id_comprador) REFERENCES usuario(id_usuario)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_orden_libro
    FOREIGN KEY (id_libro) REFERENCES libro(id_libro)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_orden_comprador ON orden_compra(id_comprador);
CREATE INDEX idx_orden_estado ON orden_compra(estado_orden);
CREATE INDEX idx_orden_fechas ON orden_compra(fecha_pedido, fecha_pago, fecha_envio, fecha_recepcion);


-- Tabla de intercambios de libros
CREATE TABLE IF NOT EXISTS intercambio (
  id_intercambio       BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  estado_intercambio   ENUM('propuesto','aceptado','rechazado','completado') NOT NULL DEFAULT 'propuesto',
  fecha_propuesta      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  fecha_aceptacion     DATETIME DEFAULT NULL,
  fecha_intercambio    DATETIME DEFAULT NULL,
  mensaje_propuesta    TEXT,
  condiciones          TEXT,
  id_usuario_propone   BIGINT UNSIGNED NOT NULL,
  id_usuario_recibe    BIGINT UNSIGNED NOT NULL,
  id_libro_ofrecido    BIGINT UNSIGNED NOT NULL,
  id_libro_solicitado  BIGINT UNSIGNED NOT NULL,
  CONSTRAINT fk_itc_propone
    FOREIGN KEY (id_usuario_propone) REFERENCES usuario(id_usuario)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_itc_recibe
    FOREIGN KEY (id_usuario_recibe) REFERENCES usuario(id_usuario)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_itc_libro_ofrecido
    FOREIGN KEY (id_libro_ofrecido) REFERENCES libro(id_libro)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT fk_itc_libro_solicitado
    FOREIGN KEY (id_libro_solicitado) REFERENCES libro(id_libro)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE INDEX idx_itc_usuarios ON intercambio(id_usuario_propone, id_usuario_recibe);
CREATE INDEX idx_itc_libros   ON intercambio(id_libro_ofrecido, id_libro_solicitado);
CREATE INDEX idx_itc_estado   ON intercambio(estado_intercambio);



-- Relación de lectura de libros en clubes
CREATE TABLE IF NOT EXISTS leer_libros (
  id_usuario   BIGINT UNSIGNED NOT NULL,
  id_club      BIGINT UNSIGNED NOT NULL,
  id_libro     BIGINT UNSIGNED NOT NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin    DATE DEFAULT NULL,
  PRIMARY KEY (id_usuario, id_club, id_libro),
  CONSTRAINT fk_ll_membresia
    FOREIGN KEY (id_usuario, id_club) REFERENCES usuario_club(id_usuario, id_club)
    ON UPDATE CASCADE ON DELETE CASCADE,
  CONSTRAINT fk_ll_libro
    FOREIGN KEY (id_libro) REFERENCES libro(id_libro)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_ll_club_libro ON leer_libros(id_club, id_libro);
CREATE INDEX idx_ll_usuario_fecha ON leer_libros(id_usuario, fecha_inicio);

CREATE TABLE IF NOT EXISTS reunion (
  id_reunion    BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  id_club       BIGINT UNSIGNED NOT NULL,
  fecha_reunion DATETIME NOT NULL,
  tema          VARCHAR(255),
  descripcion   TEXT,
  lugar         VARCHAR(200),
  CONSTRAINT fk_reunion_club FOREIGN KEY (id_club) REFERENCES club_lectura(id_club)
    ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_reunion_club_fecha ON reunion(id_club, fecha_reunion);

CREATE OR REPLACE VIEW vw_catalogo_publico AS
SELECT
  l.id_libro, l.titulo, l.autor, l.genero, l.idioma,
  l.modalidad_publicacion, l.precio_venta, l.en_catalogo,
  u.id_usuario AS propietario_id, u.nombre AS propietario_nombre, u.ciudad
FROM libro l
JOIN usuario u ON u.id_usuario = l.id_propietario
WHERE l.en_catalogo = 1;

CREATE OR REPLACE VIEW vw_resenas_con_hilo AS
SELECT
  r.id_resena, r.id_libro, r.id_usuario, r.calificacion, r.fecha_publicacion,
  r.contenido,
  rp.id_resena AS id_resena_padre, rp.contenido AS contenido_padre
FROM resena r
LEFT JOIN resena rp ON rp.id_resena = r.id_resena_padre;


DELIMITER //
CREATE TRIGGER trg_libro_precio_modalidad_ins
BEFORE INSERT ON libro
FOR EACH ROW
BEGIN
  IF NEW.modalidad_publicacion <> 'venta' THEN
    SET NEW.precio_venta = NULL;
  END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER trg_libro_precio_modalidad_upd
BEFORE UPDATE ON libro
FOR EACH ROW
BEGIN
  IF NEW.modalidad_publicacion <> 'venta' THEN
    SET NEW.precio_venta = NULL;
  END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER trg_itc_validar_ins
BEFORE INSERT ON intercambio
FOR EACH ROW
BEGIN
  IF NEW.id_usuario_propone = NEW.id_usuario_recibe THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El proponente y el receptor deben ser distintos';
  END IF;
  IF NEW.id_libro_ofrecido = NEW.id_libro_solicitado THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El libro ofrecido y el solicitado deben ser distintos';
  END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER trg_itc_validar_upd
BEFORE UPDATE ON intercambio
FOR EACH ROW
BEGIN
  IF NEW.id_usuario_propone = NEW.id_usuario_recibe THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El proponente y el receptor deben ser distintos';
  END IF;
  IF NEW.id_libro_ofrecido = NEW.id_libro_solicitado THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'El libro ofrecido y el solicitado deben ser distintos';
  END IF;
END//
DELIMITER ;

select * from usuario;
ALTER TABLE usuario AUTO_INCREMENT = 1;
delete from usuario where id_usuario =1;

-- ===================================
INSERT INTO usuario (nombre, email, password_hash, ciudad, telefono, rol) VALUES
('Juan Pérez Admin', 'juan.admin@mail.com', 'pwhash1', 'Bogotá', '3101112233', 'admin'),
('Maria López', 'maria.lopez@mail.com', 'pwhash2', 'Medellín', '3004445566', 'usuario'),
('Carlos García', 'carlos.garcia@mail.com', 'pwhash3', 'Cali', '3207778899', 'usuario'),
('Ana Torres', 'ana.torres@mail.com', 'pwhash4', 'Barranquilla', '3010001122', 'usuario'),
('Pedro Sánchez', 'pedro.sanchez@mail.com', 'pwhash5', 'Cartagena', '3153334455', 'usuario');

-- 2. INSERTS para LIBRO (FK: id_propietario) (IDs 1 al 5)
-- =====================================
INSERT INTO libro (titulo, autor, isbn, genero, resumen, id_propietario, en_catalogo, modalidad_publicacion, precio_venta, anio_publicacion) VALUES
('Cien años de soledad', 'Gabriel García Márquez', '978-0307455295', 'Realismo Mágico', 'Una saga familiar épica en Macondo.', 1, 1, 'venta', 35.50, 1967),
('La sombra del viento', 'Carlos Ruiz Zafón', '978-8408083057', 'Misterio', 'Un joven descubre un libro maldito.', 2, 1, 'intercambio', NULL, 2001),
('1984', 'George Orwell', '978-0451524935', 'Distopía', 'El Gran Hermano te vigila.', 3, 0, 'visible', NULL, 1949),
('El amor en los tiempos del cólera', 'Gabriel García Márquez', '978-0307386766', 'Romance', 'Amor persistente a lo largo de décadas.', 4, 1, 'venta', 22.99, 1985),
('Ficciones', 'Jorge Luis Borges', '978-0307950920', 'Cuento', 'Colección de relatos metafísicos y fantásticos.', 5, 1, 'intercambio', NULL, 1944);

-- 3. INSERTS para CLUB_LECTURA (FK: id_libro, id_administrador) (IDs 1 al 5)
-- ===============================================
INSERT INTO club_lectura (nombre_club, descripcion, fecha_inicio, estado, id_libro, id_administrador, max_miembros) VALUES
('Gabo Eterno', 'Club dedicado a la obra de Gabriel García Márquez.', CURDATE(), 'activo', 1, 1, 15),
('Cazadores de Misterio', 'Club para lectores de thrillers y misterio.', CURDATE(), 'activo', 2, 2, 10),
('Visiones del Futuro', 'Análisis de obras distópicas y de ciencia ficción.', CURDATE(), 'suspendido', 3, 3, 20),
('Cali Romántica', 'Lecturas sobre el amor y las relaciones.', CURDATE() - INTERVAL 30 DAY, 'activo', 4, 4, 12),
('Los Metafísicos', 'Estudio de autores complejos como Borges.', CURDATE(), 'activo', 5, 5, 8);

-- 4. INSERTS para USUARIO_CLUB (FK: id_usuario, id_club)
-- ===========================================
INSERT INTO usuario_club (id_usuario, id_club, estado_miembro) VALUES
(1, 1, 'aceptado'), -- Juan se une a Gabo Eterno
(2, 1, 'aceptado'), -- Maria se une a Gabo Eterno
(3, 2, 'aceptado'), -- Carlos se une a Cazadores de Misterio
(4, 3, 'pendiente'), -- Ana solicita unirse a Visiones del Futuro
(5, 4, 'aceptado'); -- Pedro se une a Cali Romántica

-- 5. INSERTS para RESENA (FK: id_usuario, id_libro) (IDs 1 al 5)
-- ===================================
INSERT INTO resena (contenido, calificacion, id_usuario, id_libro, id_resena_padre) VALUES
('Una obra maestra atemporal. Imprescindible.', 5, 1, 1, NULL),
('Final inesperado, me mantuvo enganchado.', 4, 2, 2, NULL),
('Muy denso y oscuro, pero la crítica social es genial.', 3, 3, 3, NULL),
('Hermosa historia de amor, aunque algo lenta.', 4, 4, 4, NULL),
('Totalmente de acuerdo, la narración es sublime.', 5, 5, 1, 1); -- Respuesta a la Reseña 1

-- 6. INSERTS para ORDEN_COMPRA (FK: id_comprador, id_libro) (IDs 1 al 5)
-- ============================================
INSERT INTO orden_compra (precio_total, estado_orden, direccion_envio, metodo_pago, id_comprador, id_libro) VALUES
(35.50, 'pagado', 'Cra 10 # 5-20, Medellín', 'Tarjeta Crédito', 2, 1),
(22.99, 'pedido', 'Calle 50 # 33-10, Cali', 'Transferencia', 3, 4),
(35.50, 'enviado', 'Av. La Playa # 1-50, Barranquilla', 'PSE', 4, 1),
(22.99, 'recibido', 'Diagonal 20 # 10-05, Cartagena', 'Efectivo', 5, 4),
(22.99, 'cancelado', 'Av 15 # 80-20, Bogotá', 'Tarjeta Débito', 1, 4);

-- 7. INSERTS para INTERCAMBIO (FKs: id_usuario_*, id_libro_*) (IDs 1 al 5)
-- ============================================
INSERT INTO intercambio (id_usuario_propone, id_usuario_recibe, id_libro_ofrecido, id_libro_solicitado, estado_intercambio, mensaje_propuesta) VALUES
(1, 2, 3, 2, 'propuesto', 'Te ofrezco mi 1984 por tu Sombra del Viento.'), -- Prop 1 (visible por intercambio)
(3, 5, 1, 5, 'aceptado', 'Me encantaría leer Ficciones. Acepto el trato.'), -- Prop 2 (venta por intercambio)
(2, 3, 4, 3, 'rechazado', 'Lo siento, ya tengo ese libro.'), -- Prop 3
(4, 1, 5, 1, 'completado', 'Intercambio listo!'), -- Prop 4
(5, 4, 2, 4, 'propuesto', '¿Intercambias tu libro por el mío?'); -- Prop 5

-- 8. INSERTS para LEER_LIBROS (FK: id_usuario, id_club, id_libro)
-- ==========================================
INSERT INTO leer_libros (id_usuario, id_club, id_libro, fecha_inicio, fecha_fin) VALUES
(1, 1, 1, CURDATE() - INTERVAL 10 DAY, NULL), -- Juan (Club 1) lee Libro 1
(2, 1, 1, CURDATE() - INTERVAL 15 DAY, CURDATE() - INTERVAL 5 DAY), -- Maria (Club 1) terminó Libro 1
(3, 2, 2, CURDATE() - INTERVAL 20 DAY, NULL), -- Carlos (Club 2) lee Libro 2
(5, 4, 4, CURDATE() - INTERVAL 25 DAY, NULL), -- Pedro (Club 4) lee Libro 4
(2, 1, 4, CURDATE() - INTERVAL 3 DAY, NULL); -- Maria (Club 1) lee Libro 4

-- 9. INSERTS para REUNION (FK: id_club) (IDs 1 al 5)
-- =============================
INSERT INTO reunion (id_club, fecha_reunion, tema, lugar) VALUES
(1, NOW() + INTERVAL 7 DAY, 'Análisis de Aureliano Buendía', 'Cafetería Central'),
(1, NOW() + INTERVAL 21 DAY, 'Simbolismo del Mar', 'Zoom Call'),
(2, NOW() + INTERVAL 5 DAY, 'Revelación del Asesino', 'Biblioteca Pública'),
(4, NOW() + INTERVAL 10 DAY, 'Pasión y Tragedia', 'Parque Principal'),
(5, NOW() + INTERVAL 15 DAY, 'El Laberinto y el Tiempo', 'Salón Comunal');
