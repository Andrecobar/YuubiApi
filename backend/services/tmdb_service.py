import requests
from config import config
from utils.helpers import clean_html
import sqlite3
from database import get_connection

class TMDBService:
    def __init__(self):
        self.api_key = config.TMDB_API_KEY
        self.base_url = config.TMDB_BASE_URL
        self.image_base_url = config.TMDB_IMAGE_BASE_URL
        self.language = config.LANGUAGE
    
    def search_movies(self, query, page=1):
        """Buscar películas en TMDB"""
        params = {
            'api_key': self.api_key,
            'language': self.language,
            'query': query,
            'page': page
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/search/movie",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('results', [])
        except Exception as e:
            print(f"Error buscando películas en TMDB: {e}")
            return []
    
    def search_series(self, query, page=1):
        """Buscar series en TMDB"""
        params = {
            'api_key': self.api_key,
            'language': self.language,
            'query': query,
            'page': page
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/search/tv",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('results', [])
        except Exception as e:
            print(f"Error buscando series en TMDB: {e}")
            return []
    
    def get_movie_details(self, tmdb_id):
        """Obtener detalles de una película"""
        params = {
            'api_key': self.api_key,
            'language': self.language
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/movie/{tmdb_id}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'tmdb_id': data.get('id'),
                'title': data.get('title'),
                'description': clean_html(data.get('overview', '')),
                'genre': ', '.join([g['name'] for g in data.get('genres', [])]),
                'rating': data.get('vote_average'),
                'duration': data.get('runtime'),
                'poster': f"{self.image_base_url}{data.get('poster_path')}" if data.get('poster_path') else None,
                'year': int(data.get('release_date', '2000')[:4])
            }
        except Exception as e:
            print(f"Error obteniendo detalles de película {tmdb_id}: {e}")
            return None
    
    def get_series_details(self, tmdb_id):
        """Obtener detalles de una serie"""
        params = {
            'api_key': self.api_key,
            'language': self.language
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/tv/{tmdb_id}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                'tmdb_id': data.get('id'),
                'title': data.get('name'),
                'description': clean_html(data.get('overview', '')),
                'genre': ', '.join([g['name'] for g in data.get('genres', [])]),
                'rating': data.get('vote_average'),
                'poster': f"{self.image_base_url}{data.get('poster_path')}" if data.get('poster_path') else None,
                'year': int(data.get('first_air_date', '2000')[:4]),
                'seasons': data.get('number_of_seasons', 1)
            }
        except Exception as e:
            print(f"Error obteniendo detalles de serie {tmdb_id}: {e}")
            return None
    
    def get_trending_movies(self, time_window='week'):
        """Obtener películas tendencia"""
        params = {
            'api_key': self.api_key,
            'language': self.language
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/trending/movie/{time_window}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('results', [])[:20]
        except Exception as e:
            print(f"Error obteniendo películas tendencia: {e}")
            return []
    
    def get_trending_series(self, time_window='week'):
        """Obtener series tendencia"""
        params = {
            'api_key': self.api_key,
            'language': self.language
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/trending/tv/{time_window}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('results', [])[:20]
        except Exception as e:
            print(f"Error obteniendo series tendencia: {e}")
            return []
    
    def get_popular_movies(self, page=1):
        """Obtener películas populares"""
        params = {
            'api_key': self.api_key,
            'language': self.language,
            'page': page
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/movie/popular",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('results', [])
        except Exception as e:
            print(f"Error obteniendo películas populares: {e}")
            return []
    
    def get_popular_series(self, page=1):
        """Obtener series populares"""
        params = {
            'api_key': self.api_key,
            'language': self.language,
            'page': page
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/tv/popular",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('results', [])
        except Exception as e:
            print(f"Error obteniendo series populares: {e}")
            return []

tmdb_service = TMDBService()
