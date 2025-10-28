# routes/movies.py - Sistema Híbrido Completo
from flask import Blueprint, jsonify, request
import requests
import os
from datetime import datetime, timedelta
from services.scrapers.zonahack import ZonaHackScraper
from services.scrapers.pelisplushd import PelisPlusHDScraper

movies_bp = Blueprint('movies', __name__)

# Configuración
TMDB_API_KEY = os.getenv('TMDB_API_KEY')
GIST_URL = os.getenv('GIST_DB_URL')  # URL raw de tu Gist

# Cache en memoria (se pierde al reiniciar pero eso está OK)
memory_cache = {}
gist_cache = {}
gist_cache_expiry = None

# === FUNCIONES AUXILIARES ===

def fetch_gist_db():
    """Obtiene y cachea el Gist DB"""
    global gist_cache, gist_cache_expiry
    
    if gist_cache and gist_cache_expiry and datetime.now() < gist_cache_expiry:
        return gist_cache
    
    try:
        response = requests.get(GIST_URL, timeout=10)
        response.raise_for_status()
        gist_cache = response.json()
        gist_cache_expiry = datetime.now() + timedelta(minutes=30)
        return gist_cache
    except Exception as e:
        print(f"Error fetching Gist: {e}")
        return {}

def check_availability_in_gist(tmdb_id):
    """Verifica si una película/serie está en el Gist"""
    gist_db = fetch_gist_db()
    return str(tmdb_id) in gist_db

def enrich_tmdb_results(tmdb_results):
    """Añade badge de disponibilidad a resultados de TMDB"""
    gist_db = fetch_gist_db()
    
    for item in tmdb_results:
        tmdb_id = str(item['tmdb_id'])
        item['has_links'] = tmdb_id in gist_db
        item['source'] = 'verified' if item['has_links'] else 'tmdb_only'
    
    return tmdb_results

def get_from_cache(cache_key):
    """Obtiene datos del cache en memoria"""
    if cache_key in memory_cache:
        cache_data = memory_cache[cache_key]
        if datetime.now() < cache_data['expires']:
            return cache_data['data']
        else:
            del memory_cache[cache_key]
    return None

def set_cache(cache_key, data, minutes=30):
    """Guarda datos en cache en memoria"""
    memory_cache[cache_key] = {
        'data': data,
        'expires': datetime.now() + timedelta(minutes=minutes)
    }

# === ENDPOINTS ===

@movies_bp.route('/api/home', methods=['GET'])
def get_home_data():
    """
    Endpoint principal para HOME screen
    Combina: Verificados (Gist) + Trending/Popular (TMDB)
    """
    if not TMDB_API_KEY:
        return jsonify({'error': 'TMDB_API_KEY no configurada'}), 500
    
    try:
        gist_db = fetch_gist_db()
        
        # 1. Películas verificadas (de tu Gist)
        verified_movies = []
        for tmdb_id, item in gist_db.items():
            if item.get('type') == 'movie':
                verified_movies.append({
                    'tmdb_id': int(tmdb_id),
                    'title': item['title'],
                    'poster': f"https://image.tmdb.org/t/p/w500{item.get('poster_path', '')}",
                    'has_links': True,
                    'source': 'verified'
                })
        
        # 2. Series verificadas (de tu Gist)
        verified_series = []
        for tmdb_id, item in gist_db.items():
            if item.get('type') == 'series':
                verified_series.append({
                    'tmdb_id': int(tmdb_id),
                    'title': item['title'],
                    'poster': f"https://image.tmdb.org/t/p/w500{item.get('poster_path', '')}",
                    'has_links': True,
                    'source': 'verified'
                })
        
        # 3. Trending (TMDB)
        trending_response = requests.get(
            'https://api.themoviedb.org/3/trending/all/week',
            params={'api_key': TMDB_API_KEY, 'language': 'es-ES'},
            timeout=10
        )
        trending_data = trending_response.json()
        trending_items = []
        
        for item in trending_data.get('results', [])[:20]:
            media_type = item.get('media_type')
            trending_items.append({
                'tmdb_id': item['id'],
                'title': item.get('title') or item.get('name'),
                'poster': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get('poster_path') else None,
                'type': 'movie' if media_type == 'movie' else 'series',
                'rating': item.get('vote_average'),
                'has_links': check_availability_in_gist(item['id']),
                'source': 'verified' if check_availability_in_gist(item['id']) else 'tmdb_only'
            })
        
        # 4. Películas populares (TMDB)
        movies_response = requests.get(
            'https://api.themoviedb.org/3/movie/popular',
            params={'api_key': TMDB_API_KEY, 'language': 'es-ES'},
            timeout=10
        )
        movies_data = movies_response.json()
        popular_movies = []
        
        for item in movies_data.get('results', [])[:20]:
            popular_movies.append({
                'tmdb_id': item['id'],
                'title': item['title'],
                'poster': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get('poster_path') else None,
                'year': item.get('release_date', '')[:4] if item.get('release_date') else None,
                'rating': item.get('vote_average'),
                'has_links': check_availability_in_gist(item['id']),
                'source': 'verified' if check_availability_in_gist(item['id']) else 'tmdb_only'
            })
        
        # 5. Series populares (TMDB)
        series_response = requests.get(
            'https://api.themoviedb.org/3/tv/popular',
            params={'api_key': TMDB_API_KEY, 'language': 'es-ES'},
            timeout=10
        )
        series_data = series_response.json()
        popular_series = []
        
        for item in series_data.get('results', [])[:20]:
            popular_series.append({
                'tmdb_id': item['id'],
                'title': item['name'],
                'poster': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get('poster_path') else None,
                'year': item.get('first_air_date', '')[:4] if item.get('first_air_date') else None,
                'rating': item.get('vote_average'),
                'has_links': check_availability_in_gist(item['id']),
                'source': 'verified' if check_availability_in_gist(item['id']) else 'tmdb_only'
            })
        
        return jsonify({
            'success': True,
            'verified_movies': verified_movies[:8],
            'verified_series': verified_series[:8],
            'trending': trending_items,
            'popular_movies': popular_movies,
            'popular_series': popular_series,
            'total_verified': len(verified_movies) + len(verified_series)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/api/search', methods=['GET'])
def search_content():
    """
    Busca películas/series en TMDB + indica disponibilidad
    """
    query = request.args.get('q', '')
    page = request.args.get('page', 1)
    content_type = request.args.get('type', 'multi')  # movie, tv, multi
    
    if not query:
        return jsonify({'error': 'Parámetro q es requerido'}), 400
    
    if not TMDB_API_KEY:
        return jsonify({'error': 'TMDB_API_KEY no configurada'}), 500
    
    try:
        # Determinar endpoint
        if content_type == 'movie':
            endpoint = 'search/movie'
        elif content_type == 'tv':
            endpoint = 'search/tv'
        else:
            endpoint = 'search/multi'
        
        response = requests.get(
            f'https://api.themoviedb.org/3/{endpoint}',
            params={
                'api_key': TMDB_API_KEY,
                'query': query,
                'language': 'es-ES',
                'page': page
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        # Formatear resultados
        results = []
        for item in data.get('results', []):
            # Filtrar solo películas y series
            media_type = item.get('media_type', content_type)
            if media_type not in ['movie', 'tv']:
                continue
            
            tmdb_id = item['id']
            results.append({
                'tmdb_id': tmdb_id,
                'title': item.get('title') or item.get('name'),
                'description': item.get('overview', ''),
                'year': (item.get('release_date') or item.get('first_air_date', ''))[:4],
                'rating': item.get('vote_average'),
                'poster': f"https://image.tmdb.org/t/p/w500{item['poster_path']}" if item.get('poster_path') else None,
                'type': 'movie' if media_type == 'movie' else 'series',
                'has_links': check_availability_in_gist(tmdb_id),
                'source': 'verified' if check_availability_in_gist(tmdb_id) else 'tmdb_only'
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'page': data.get('page'),
            'total_pages': data.get('total_pages'),
            'total_results': data.get('total_results')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/api/details/<int:tmdb_id>', methods=['GET'])
def get_content_details(tmdb_id):
    """
    Obtiene detalles completos de una película/serie
    """
    content_type = request.args.get('type', 'movie')  # movie o tv
    
    if not TMDB_API_KEY:
        return jsonify({'error': 'TMDB_API_KEY no configurada'}), 500
    
    try:
        endpoint = 'movie' if content_type == 'movie' else 'tv'
        response = requests.get(
            f'https://api.themoviedb.org/3/{endpoint}/{tmdb_id}',
            params={'api_key': TMDB_API_KEY, 'language': 'es-ES'},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        details = {
            'tmdb_id': tmdb_id,
            'title': data.get('title') or data.get('name'),
            'description': data.get('overview'),
            'poster': f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if data.get('poster_path') else None,
            'backdrop': f"https://image.tmdb.org/t/p/original{data['backdrop_path']}" if data.get('backdrop_path') else None,
            'rating': data.get('vote_average'),
            'year': (data.get('release_date') or data.get('first_air_date', ''))[:4],
            'genres': [g['name'] for g in data.get('genres', [])],
            'type': content_type,
            'has_links': check_availability_in_gist(tmdb_id)
        }
        
        # Datos específicos por tipo
        if content_type == 'movie':
            details['duration'] = data.get('runtime')
        else:
            details['seasons'] = data.get('number_of_seasons')
            details['episodes'] = data.get('number_of_episodes')
        
        return jsonify({
            'success': True,
            'details': details
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/api/links/<int:tmdb_id>', methods=['GET'])
def get_streaming_links(tmdb_id):
    """
    Obtiene enlaces de streaming para películas
    Estrategia: Gist (instantáneo) → Auto-scraping (5-10s) → Falla
    """
    auto_scrape = request.args.get('auto_scrape', 'true').lower() == 'true'
    
    # Verificar cache
    cache_key = f"links_{tmdb_id}"
    cached = get_from_cache(cache_key)
    if cached:
        cached['from_cache'] = True
        return jsonify(cached)
    
    start_time = datetime.now()
    
    try:
        gist_db = fetch_gist_db()
        movie_data = gist_db.get(str(tmdb_id))
        
        # Estrategia 1: Película en Gist (ZonaHack verificado)
        if movie_data and movie_data.get('listen_url'):
            scraper = ZonaHackScraper()
            result = scraper.extract_links(
                url=movie_data.get('zonahack_url', ''),
                listen_url=movie_data['listen_url']
            )
            
            if result['success']:
                response_data = {
                    'success': True,
                    'source': 'gist_zonahack',
                    'links': result['links'],
                    'total': len(result['links']),
                    'cache_time': (datetime.now() - start_time).total_seconds(),
                    'from_cache': False
                }
                set_cache(cache_key, response_data)
                return jsonify(response_data)
        
        # Estrategia 2: Auto-scraping de PelisPlusHD (si está habilitado)
        if auto_scrape:
            # Necesitamos construir la URL de PelisPlusHD
            # Para esto, necesitamos el título slug
            # Lo obtenemos de TMDB
            tmdb_response = requests.get(
                f'https://api.themoviedb.org/3/movie/{tmdb_id}',
                params={'api_key': TMDB_API_KEY},
                timeout=5
            )
            
            if tmdb_response.status_code == 200:
                tmdb_data = tmdb_response.json()
                title_slug = tmdb_data.get('title', '').lower().replace(' ', '-')
                pelisplus_url = f"https://ww4.pelisplushd.to/pelicula/{title_slug}"
                
                scraper = PelisPlusHDScraper()
                result = scraper.extract_links(pelisplus_url)
                
                if result['success']:
                    response_data = {
                        'success': True,
                        'source': 'auto_pelisplushd',
                        'links': result['links'],
                        'total': len(result['links']),
                        'cache_time': (datetime.now() - start_time).total_seconds(),
                        'from_cache': False,
                        'note': 'Scraped automatically, may not always work'
                    }
                    set_cache(cache_key, response_data, minutes=30)
                    return jsonify(response_data)
        
        # Estrategia 3: No disponible
        return jsonify({
            'success': False,
            'error': 'not_available',
            'tmdb_id': tmdb_id,
            'links': [],
            'total': 0,
            'suggestion': 'request_movie',
            'cache_time': (datetime.now() - start_time).total_seconds()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'tmdb_id': tmdb_id,
            'links': [],
            'total': 0
        }), 500


@movies_bp.route('/api/series/<int:tmdb_id>/season/<int:season>', methods=['GET'])
def get_series_season_episodes(tmdb_id, season):
    """
    Obtiene información de episodios de una temporada específica
    """
    if not TMDB_API_KEY:
        return jsonify({'error': 'TMDB_API_KEY no configurada'}), 500
    
    try:
        response = requests.get(
            f'https://api.themoviedb.org/3/tv/{tmdb_id}/season/{season}',
            params={'api_key': TMDB_API_KEY, 'language': 'es-ES'},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        episodes = []
        for ep in data.get('episodes', []):
            episodes.append({
                'episode_number': ep['episode_number'],
                'name': ep['name'],
                'overview': ep.get('overview'),
                'still_path': f"https://image.tmdb.org/t/p/w300{ep['still_path']}" if ep.get('still_path') else None,
                'air_date': ep.get('air_date')
            })
        
        # Verificar si tenemos enlaces para esta temporada
        gist_db = fetch_gist_db()
        series_data = gist_db.get(str(tmdb_id))
        has_links = False
        
        if series_data and series_data.get('seasons'):
            has_links = str(season) in series_data.get('seasons', {})
        
        return jsonify({
            'success': True,
            'tmdb_id': tmdb_id,
            'season': season,
            'episodes': episodes,
            'total_episodes': len(episodes),
            'has_links': has_links
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@movies_bp.route('/api/series/<int:tmdb_id>/links', methods=['GET'])
def get_series_episode_links(tmdb_id):
    """
    Obtiene enlaces de streaming para un episodio específico de una serie
    Query params: season, episode
    """
    season = request.args.get('season', type=int)
    episode = request.args.get('episode', type=int)
    
    if not season or not episode:
        return jsonify({'error': 'Parámetros season y episode son requeridos'}), 400
    
    # Verificar cache para toda la temporada
    cache_key = f"series_{tmdb_id}_s{season}"
    cached_season = get_from_cache(cache_key)
    
    if cached_season:
        # Buscar el episodio específico en el cache
        for ep in cached_season.get('episodes', []):
            if ep['episode'] == episode:
                return jsonify({
                    'success': True,
                    'source': cached_season['source'],
                    'episode': ep,
                    'from_cache': True
                })
    
    start_time = datetime.now()
    
    try:
        gist_db = fetch_gist_db()
        series_data = gist_db.get(str(tmdb_id))
        
        # Verificar si tenemos la temporada en el Gist
        if not series_data or not series_data.get('seasons'):
            return jsonify({
                'success': False,
                'error': 'series_not_available',
                'tmdb_id': tmdb_id,
                'season': season,
                'episode': episode,
                'suggestion': 'request_series'
            })
        
        season_data = series_data['seasons'].get(str(season))
        
        if not season_data or not season_data.get('listen_url'):
            return jsonify({
                'success': False,
                'error': 'season_not_available',
                'tmdb_id': tmdb_id,
                'season': season,
                'episode': episode,
                'suggestion': 'request_season'
            })
        
        # Hacer scraping de ZonaHack para TODA la temporada
        scraper = ZonaHackScraper()
        result = scraper.extract_links(
            url=season_data.get('zonahack_url', ''),
            listen_url=season_data['listen_url']
        )
        
        if not result['success']:
            return jsonify({
                'success': False,
                'error': 'scraping_failed',
                'details': result.get('error'),
                'tmdb_id': tmdb_id,
                'season': season,
                'episode': episode
            })
        
        # Organizar enlaces por episodio
        # ZonaHack devuelve enlaces con campo 'nombre' que incluye el episodio
        episodes_links = {}
        
        for link in result['links']:
            # Extraer número de episodio del nombre
            # Ejemplo: "Breaking Bad 1x01" o "Episodio 1"
            import re
            ep_match = re.search(r'(?:x|episodio\s*)(\d+)', link.get('nombre', ''), re.IGNORECASE)
            
            if ep_match:
                ep_num = int(ep_match.group(1))
            else:
                # Si no encuentra patrón, asumir orden secuencial
                ep_num = len(episodes_links) + 1
            
            if ep_num not in episodes_links:
                episodes_links[ep_num] = []
            
            episodes_links[ep_num].append({
                'server': link['server'],
                'url': link['url'],
                'language': link['language']
            })
        
        # Cachear TODA la temporada (smart caching)
        cache_data = {
            'source': 'gist_zonahack',
            'episodes': [
                {
                    'episode': ep_num,
                    'links': links,
                    'total': len(links)
                }
                for ep_num, links in episodes_links.items()
            ],
            'cache_time': (datetime.now() - start_time).total_seconds()
        }
        set_cache(cache_key, cache_data, minutes=30)
        
        # Devolver solo el episodio solicitado
        if episode in episodes_links:
            return jsonify({
                'success': True,
                'source': 'gist_zonahack',
                'tmdb_id': tmdb_id,
                'season': season,
                'episode': {
                    'episode': episode,
                    'links': episodes_links[episode],
                    'total': len(episodes_links[episode])
                },
                'all_episodes_cached': True,
                'cached_episodes': list(episodes_links.keys()),
                'cache_time': (datetime.now() - start_time).total_seconds(),
                'from_cache': False
            })
        else:
            return jsonify({
                'success': False,
                'error': 'episode_not_found',
                'tmdb_id': tmdb_id,
                'season': season,
                'episode': episode,
                'available_episodes': list(episodes_links.keys())
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'tmdb_id': tmdb_id,
            'season': season,
            'episode': episode
        }), 500


@movies_bp.route('/api/request', methods=['POST'])
def request_content():
    """
    Endpoint para que usuarios soliciten películas/series no disponibles
    Puedes conectarlo a un servicio como Formspree o EmailJS
    """
    data = request.get_json()
    
    tmdb_id = data.get('tmdb_id')
    title = data.get('title')
    content_type = data.get('type', 'movie')
    user_email = data.get('email')  # Opcional
    
    if not tmdb_id or not title:
        return jsonify({'error': 'tmdb_id y title son requeridos'}), 400
    
    # Aquí puedes implementar:
    # 1. Guardar en un archivo JSON de solicitudes
    # 2. Enviar email a ti mismo
    # 3. Enviar a un webhook de Discord/Telegram
    # 4. Guardar en una DB externa (Airtable, Google Sheets)
    
    # Por ahora, solo retornamos éxito
    # TODO: Implementar notificación real
    
    return jsonify({
        'success': True,
        'message': 'Solicitud recibida. Te notificaremos cuando esté disponible.',
        'tmdb_id': tmdb_id,
        'title': title,
        'type': content_type
    })


@movies_bp.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Estadísticas generales del contenido disponible
    """
    try:
        gist_db = fetch_gist_db()
        
        movies_count = sum(1 for item in gist_db.values() if item.get('type') == 'movie')
        series_count = sum(1 for item in gist_db.values() if item.get('type') == 'series')
        
        # Contar temporadas totales
        total_seasons = 0
        for item in gist_db.values():
            if item.get('type') == 'series' and item.get('seasons'):
                total_seasons += len(item['seasons'])
        
        return jsonify({
            'success': True,
            'stats': {
                'total_movies': movies_count,
                'total_series': series_count,
                'total_seasons': total_seasons,
                'total_content': movies_count + series_count,
                'last_updated': gist_cache_expiry.isoformat() if gist_cache_expiry else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500