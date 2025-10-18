from flask import jsonify, request
from routes import admin_bp
from database import get_connection
from services.tmdb_service import tmdb_service
from services.scraper_service import scraper_service
import sqlite3

@admin_bp.route('/admin/add-movie', methods=['POST'])
def add_movie():
    """Agregar película manualmente"""
    data = request.get_json()
    
    required_fields = ['title', 'tmdb_id', 'description', 'genre', 'rating', 'year']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO movies (tmdb_id, title, description, genre, rating, duration, poster, year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['tmdb_id'],
            data['title'],
            data['description'],
            data['genre'],
            data['rating'],
            data.get('duration', 0),
            data.get('poster'),
            data['year']
        ))
        
        movie_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Película agregada', 'movie_id': movie_id}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Película ya existe'}), 409
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/add-series', methods=['POST'])
def add_series():
    """Agregar serie manualmente"""
    data = request.get_json()
    
    required_fields = ['title', 'tmdb_id', 'description', 'genre', 'rating', 'year']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO series (tmdb_id, title, description, genre, rating, poster, year, seasons)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['tmdb_id'],
            data['title'],
            data['description'],
            data['genre'],
            data['rating'],
            data.get('poster'),
            data['year'],
            data.get('seasons', 1)
        ))
        
        series_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Serie agregada', 'series_id': series_id}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Serie ya existe'}), 409
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/add-link', methods=['POST'])
def add_link():
    """Agregar link manualmente"""
    data = request.get_json()
    
    required = ['content_id', 'content_type', 'url', 'source']
    if not all(field in data for field in required):
        return jsonify({'error': 'Faltan campos requeridos'}), 400
    
    if data['content_type'] not in ['movie', 'series']:
        return jsonify({'error': 'content_type debe ser movie o series'}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO links (content_id, content_type, url, source, season, episode, status)
            VALUES (?, ?, ?, ?, ?, ?, 'active')
        ''', (
            data['content_id'],
            data['content_type'],
            data['url'],
            data['source'],
            data.get('season'),
            data.get('episode')
        ))
        
        link_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Link agregado', 'link_id': link_id}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/scrape-and-add', methods=['POST'])
def scrape_and_add():
    """Scrappear y agregar contenido automáticamente"""
    data = request.get_json()
    query = data.get('query')
    content_type = data.get('type', 'movie')  # 'movie' o 'series'
    
    if not query:
        return jsonify({'error': 'Query requerido'}), 400
    
    try:
        # Paso 1: Obtener detalles de TMDB
        if content_type == 'movie':
            tmdb_results = tmdb_service.search_movies(query)
            if tmdb_results:
                details = tmdb_service.get_movie_details(tmdb_results[0]['id'])
        else:
            tmdb_results = tmdb_service.search_series(query)
            if tmdb_results:
                details = tmdb_service.get_series_details(tmdb_results[0]['id'])
        
        if not tmdb_results or not details:
            return jsonify({'error': 'No encontrado en TMDB'}), 404
        
        # Paso 2: Guardar en BD
        conn = get_connection()
        cursor = conn.cursor()
        
        if content_type == 'movie':
            cursor.execute('''
                INSERT OR IGNORE INTO movies 
                (tmdb_id, title, description, genre, rating, duration, poster, year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                details['tmdb_id'],
                details['title'],
                details['description'],
                details['genre'],
                details['rating'],
                details['duration'],
                details['poster'],
                details['year']
            ))
            content_id = cursor.lastrowid
        else:
            cursor.execute('''
                INSERT OR IGNORE INTO series 
                (tmdb_id, title, description, genre, rating, poster, year, seasons)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                details['tmdb_id'],
                details['title'],
                details['description'],
                details['genre'],
                details['rating'],
                details['poster'],
                details['year'],
                details['seasons']
            ))
            content_id = cursor.lastrowid
        
        conn.commit()
        
        # Paso 3: Scrappear links
        scraped_links = scraper_service.get_all_sources(query)
        
        for link_data in scraped_links:
            cursor.execute('''
                INSERT INTO links (content_id, content_type, url, source, status)
                VALUES (?, ?, ?, ?, 'active')
            ''', (content_id, content_type, link_data['url'], link_data['source']))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Contenido agregado',
            'content_id': content_id,
            'links_found': len(scraped_links)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/get-stats', methods=['GET'])
def get_stats():
    """Obtener estadísticas de la BD"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM movies')
    total_movies = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM series')
    total_series = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM links WHERE status = "active"')
    active_links = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM links WHERE status = "broken"')
    broken_links = cursor.fetchone()['count']
    
    conn.close()
    
    return jsonify({
        'total_movies': total_movies,
        'total_series': total_series,
        'active_links': active_links,
        'broken_links': broken_links,
        'total_content': total_movies + total_series
    })

@admin_bp.route('/admin/delete-link/<int:link_id>', methods=['DELETE'])
def delete_link(link_id):
    """Eliminar un link"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM links WHERE id = ?', (link_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Link eliminado'})

@admin_bp.route('/admin/update-link-status/<int:link_id>', methods=['PUT'])
def update_link_status(link_id):
    """Actualizar estado de un link"""
    data = request.get_json()
    status = data.get('status')  # 'active' o 'broken'
    
    if status not in ['active', 'broken']:
        return jsonify({'error': 'Estado inválido'}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE links SET status = ?, checked_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (status, link_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Link actualizado'})
