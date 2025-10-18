from flask import jsonify, request
from routes import series_bp
from database import get_connection
from services.tmdb_service import tmdb_service

@series_bp.route('/series', methods=['GET'])
def get_all_series():
    """Obtener todas las series"""
    page = request.args.get('page', 1, type=int)
    limit = 20
    offset = (page - 1) * limit
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, GROUP_CONCAT(l.url, '||') as links
        FROM series s
        LEFT JOIN links l ON s.id = l.content_id AND l.content_type = 'series'
        GROUP BY s.id
        LIMIT ? OFFSET ?
    ''', (limit, offset))
    
    series_list = []
    for row in cursor.fetchall():
        series_list.append(dict(row))
    
    cursor.execute('SELECT COUNT(*) as total FROM series')
    total = cursor.fetchone()['total']
    
    conn.close()
    
    return jsonify({
        'series': series_list,
        'total': total,
        'page': page,
        'per_page': limit
    })

@series_bp.route('/series/<int:series_id>', methods=['GET'])
def get_series(series_id):
    """Obtener detalles de una serie"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, GROUP_CONCAT(l.url, '||') as links
        FROM series s
        LEFT JOIN links l ON s.id = l.content_id AND l.content_type = 'series'
        WHERE s.id = ?
        GROUP BY s.id
    ''', (series_id,))
    
    series = cursor.fetchone()
    conn.close()
    
    if not series:
        return jsonify({'error': 'Serie no encontrada'}), 404
    
    return jsonify(dict(series))

@series_bp.route('/series/search', methods=['GET'])
def search_series():
    """Buscar series por título"""
    query = request.args.get('q', '')
    
    if len(query) < 2:
        return jsonify({'error': 'Búsqueda muy corta'}), 400
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM series
        WHERE title LIKE ? OR description LIKE ?
        LIMIT 20
    ''', (f'%{query}%', f'%{query}%'))
    
    series_list = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(series_list)

@series_bp.route('/series/trending', methods=['GET'])
def get_trending_series():
    """Obtener series tendencia"""
    results = tmdb_service.get_trending_series('week')
    
    series_list = []
    for item in results:
        series_details = tmdb_service.get_series_details(item['id'])
        if series_details:
            series_list.append(series_details)
    
    return jsonify(series_list)

@series_bp.route('/series/popular', methods=['GET'])
def get_popular_series():
    """Obtener series más populares"""
    results = tmdb_service.get_popular_series()
    
    series_list = []
    for item in results:
        series_details = tmdb_service.get_series_details(item['id'])
        if series_details:
            series_list.append(series_details)
    
    return jsonify(series_list)
