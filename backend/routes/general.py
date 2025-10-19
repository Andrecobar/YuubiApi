from flask import jsonify, request
from flask import Blueprint
from database import get_connection
from services.tmdb_service import tmdb_service

general_bp = Blueprint('general', __name__)

@general_bp.route('/', methods=['GET'])
def index():
    """Endpoint raíz de la API"""
    return jsonify({
        'message': 'Netflix Personal API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'movies': '/api/movies',
            'series': '/api/series',
            'search': '/api/search?q=title',
            'trending_movies': '/api/movies/trending',
            'trending_series': '/api/series/trending',
            'popular_movies': '/api/movies/popular',
            'popular_series': '/api/series/popular',
            'admin': '/api/admin/*'
        }
    })

@general_bp.route('/search', methods=['GET'])
def search():
    """Buscar películas o series"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify({'error': 'Búsqueda muy corta'}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Buscar en películas
    cursor.execute('''
        SELECT * FROM movies WHERE title LIKE ? OR description LIKE ?
        LIMIT 10
    ''', (f'%{query}%', f'%{query}%'))
    movies = [dict(row) for row in cursor.fetchall()]
    
    # Buscar en series
    cursor.execute('''
        SELECT * FROM series WHERE title LIKE ? OR description LIKE ?
        LIMIT 10
    ''', (f'%{query}%', f'%{query}%'))
    series = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'movies': movies,
        'series': series,
        'total': len(movies) + len(series)
    })

@general_bp.route('/trending', methods=['GET'])
def trending():
    """Obtener tendencias de películas y series"""
    trending_movies = tmdb_service.get_trending_movies('week')
    trending_series = tmdb_service.get_trending_series('week')
    
    movies_list = []
    for item in trending_movies[:10]:
        details = tmdb_service.get_movie_details(item['id'])
        if details:
            movies_list.append(details)
    
    series_list = []
    for item in trending_series[:10]:
        details = tmdb_service.get_series_details(item['id'])
        if details:
            series_list.append(details)
    
    return jsonify({
        'trending_movies': movies_list,
        'trending_series': series_list
    })

@general_bp.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'healthy'})
