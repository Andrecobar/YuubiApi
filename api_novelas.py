from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('novelas.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            imagen_portada TEXT,
            anio INTEGER,
            genero TEXT
        )
    ''')
    
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS peliculas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            imagen_portada TEXT,
            anio INTEGER,
            genero TEXT,
            url_video TEXT,
            duracion INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def inicio():
    return jsonify({
        'mensaje': '🎬 API de Novelas funcionando',
        'version': '1.0',
        'endpoints': {
            'series': '/api/series',
            'serie_detalle': '/api/series/<id>',
            'episodios': '/api/series/<id>/episodios',
            'peliculas': '/api/peliculas',
            'buscar': '/api/buscar?q=nombre'
        }
    })

@app.route('/api/series', methods=['GET'])
def obtener_series():
    conn = sqlite3.connect('novelas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM series')
    series = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(series)

@app.route('/api/series/<int:serie_id>', methods=['GET'])
def obtener_serie_detalle(serie_id):
    conn = sqlite3.connect('novelas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM series WHERE id = ?', (serie_id,))
    serie = cursor.fetchone()
    conn.close()
    
    if serie:
        return jsonify(dict(serie))
    else:
        return jsonify({'error': 'Serie no encontrada'}), 404

@app.route('/api/series/<int:serie_id>/episodios', methods=['GET'])
def obtener_episodios(serie_id):
    conn = sqlite3.connect('novelas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM episodios 
        WHERE serie_id = ? 
        ORDER BY numero_episodio ASC
    ''', (serie_id,))
    episodios = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(episodios)

@app.route('/api/peliculas', methods=['GET'])
def obtener_peliculas():
    conn = sqlite3.connect('novelas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM peliculas')
    peliculas = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(peliculas)

@app.route('/api/buscar', methods=['GET'])
def buscar():
    query = request.args.get('q', '')
    conn = sqlite3.connect('novelas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 'serie' as tipo, * FROM series 
        WHERE titulo LIKE ?
    ''', (f'%{query}%',))
    series = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute('''
        SELECT 'pelicula' as tipo, * FROM peliculas 
        WHERE titulo LIKE ?
    ''', (f'%{query}%',))
    peliculas = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return jsonify({
        'series': series,
        'peliculas': peliculas,
        'total': len(series) + len(peliculas)
    })

@app.route('/api/series', methods=['POST'])
def agregar_serie():
    datos = request.get_json()
    conn = sqlite3.connect('novelas.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO series (titulo, descripcion, imagen_portada, anio, genero)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        datos.get('titulo'),
        datos.get('descripcion'),
        datos.get('imagen_portada'),
        datos.get('anio'),
        datos.get('genero')
    ))
    conn.commit()
    serie_id = cursor.lastrowid
    conn.close()
    return jsonify({'mensaje': 'Serie agregada', 'id': serie_id}), 201

@app.route('/api/episodios', methods=['POST'])
def agregar_episodio():
    datos = request.get_json()
    conn = sqlite3.connect('novelas.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO episodios (serie_id, numero_episodio, titulo, url_video, duracion)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        datos.get('serie_id'),
        datos.get('numero_episodio'),
        datos.get('titulo'),
        datos.get('url_video'),
        datos.get('duracion')
    ))
    conn.commit()
    episodio_id = cursor.lastrowid
    conn.close()
    return jsonify({'mensaje': 'Episodio agregado', 'id': episodio_id}), 201

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
