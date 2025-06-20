-- Tabla de Autores
CREATE TABLE autores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL UNIQUE,
    biografia TEXT,
    fecha_nacimiento DATE,
    pais VARCHAR(100)
);

-- Tabla de Géneros
CREATE TABLE generos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE
);

-- Tabla de Mangas
CREATE TABLE mangas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    titulo_alternativo VARCHAR(255),
    sinopsis TEXT,
    estado ENUM('En curso', 'Finalizado', 'Pausado', 'Cancelado') NOT NULL DEFAULT 'En curso',
    fecha_publicacion DATE,
    editorial VARCHAR(255),
    calificacion DECIMAL(3, 2) DEFAULT 0.00, -- e.g., 8.50
    portada_url VARCHAR(2048), -- URL a la imagen de la portada
    autor_id INT, -- FK al autor principal (puedes expandir si hay múltiples autores/artistas)
    FOREIGN KEY (autor_id) REFERENCES autores(id) ON DELETE SET NULL
);

-- Tabla de Unión para Manga y Género (muchos a muchos)
CREATE TABLE manga_genero (
    manga_id INT NOT NULL,
    genero_id INT NOT NULL,
    PRIMARY KEY (manga_id, genero_id),
    FOREIGN KEY (manga_id) REFERENCES mangas(id) ON DELETE CASCADE,
    FOREIGN KEY (genero_id) REFERENCES generos(id) ON DELETE CASCADE
);
