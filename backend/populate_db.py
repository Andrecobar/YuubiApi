from services.tmdb_service import tmdb_service
from database import get_connection
import sqlite3

def populate_database():
    """Agregar contenido inicial a la BD"""
    
    # Lista de películas populares para buscar
    movies_to_add = [
        'Inception',
        'The Dark Knight',
        'Interstellar',
        'Pulp Fiction',
        'The Matrix',
        'Forrest Gump',
        'Titanic',
        'Avatar',
        'The Avengers',
        'Fight Club',
    ]
    
    # Lista de series populares
    series_to_add = [
        'Breaking Bad',
        'Game of Thrones',
        'The Office',
        'Stranger Things',
        'The Crown',
        'Chernobyl',
        'The Mandalorian',
        'Westworld',
        'True Detective',
        'The Sopranos',
    ]
    
    conn = get_connection()
    cursor = conn.cursor()
    
    print("Agregando películas...")
    for movie_query in movies_to_add:
        try:
            results = tmdb_service.search_movies(movie_query)
            if results:
                details = tmdb_service.get_movie_details(results[0]['id'])
                if details:
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
                    print(f"  ✅ {details['title']}")
        except Exception as e:
            print(f"  ❌ {movie_query}: {e}")
    
    print("\nAgregando series...")
    for series_query in series_to_add:
        try:
            results = tmdb_service.search_series(series_query)
            if results:
                details = tmdb_service.get_series_details(results[0]['id'])
                if details:
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
                    print(f"  ✅ {details['title']}")
        except Exception as e:
            print(f"  ❌ {series_query}: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Base de datos poblada")

if __name__ == '__main__':
    populate_database()
