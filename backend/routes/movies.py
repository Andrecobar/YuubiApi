from flask import jsonify, request
from routes import movies_bp
from database import get_connection
from services.tmdb_service import tmdb_service
from services.scraper_service import scraper_service
import sqlite3

@movies_bp.route('/movies', methods=['GET'])
def get_all_movies():
    """Obtener todas las películas"""
    page = request.args.get('page', 1, type=int)
    limit = 20
    offset = (page - 1) * limit
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.*, GROUP_CONCAT(l.url, '||') as links
        FROM movies m
        LEFT JOIN links l ON m.id = l.content_id AND l.content_type = 'movie'
        GROUP BY m.id
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    
    movies = []
    for row in cursor.fetchall():
        movies.append(dict(row))
    
    cursor.execute('SELECT COUNT(*) as total FROM movies')
    total = cursor.fetchone()['total']
    
    conn.close()
    
    return jsonify({
        'movies': movies,
        'total': total,
        'page': page,
        'per_page': limit
    })

@movies_bp.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Obtener detalles de una película"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT m.*, GROUP_CONCAT(l.url, '||') as links
        FROM movies m
        LEFT JOIN links l ON m.id = l.content_id AND l.content_type = 'movie'
        WHERE m.id = ?
        GROUP BY m.id
    ''', (movie_id,))
    
    movie = cursor.fetchone()
    conn.close()
    
    if not movie:
        return jsonify({'error': 'Película no encontrada'}), 404
    
    return jsonify(dict(movie))

@movies_bp.route('/movies/search', methods=['GET'])
def search_movies():
    """Buscar películas por título"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify({'error': 'Búsqueda muy corta'}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM movies
        WHERE title LIKE ? OR description LIKE ?
        LIMIT 20
    ''', (f'%{query}%', f'%{query}%'))
    
    movies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(movies)

@movies_bp.route('/movies/trending', methods=['GET'])
def get_trending_movies():
    """Obtener películas tendencia"""
    results = tmdb_service.get_trending_movies('week')
    
    movies = []
    for item in results:
        movie_details = tmdb_service.get_movie_details(item['id'])
        if movie_details:
            movies.append(movie_details)
    
    return jsonify(movies)

@movies_bp.route('/movies/popular', methods=['GET'])
def get_popular_movies():
    """Obtener películas más populares"""
    results = tmdb_service.get_popular_movies()
    
    movies = []
    for item in results:
        movie_details = tmdb_service.get_movie_details(item['id'])
        if movie_details:
            movies.append(movie_details)
    
    return jsonify(movies)
