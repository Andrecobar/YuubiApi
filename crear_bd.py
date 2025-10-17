import sqlite3

conn = sqlite3.connect('novelas.db')
cursor = conn.cursor()

# Crear tabla de series CON las nuevas columnas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS series (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descripcion TEXT,
        imagen_portada TEXT,
        anio INTEGER,
        genero TEXT,
        puntuacion REAL,
        reparto TEXT
    )
''')

# Tabla de episodios
cursor.execute('''
    CREATE TABLE IF NOT EXISTS episodios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        serie_id INTEGER,
        numero_episodio INTEGER,
        titulo TEXT,
        url_video TEXT,
        duracion INTEGER,
        FOREIGN KEY (serie_id) REFERENCES series (id)
    )
''')

# Tabla de películas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS peliculas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descripcion TEXT,
        imagen_portada TEXT,
        anio INTEGER,
        genero TEXT,
        url_video TEXT,
        duracion INTEGER,
        puntuacion REAL,
        reparto TEXT
    )
''')

conn.commit()
conn.close()

print("✅ Base de datos creada correctamente")
