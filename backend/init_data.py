from database import get_connection
from services.tmdb_service import tmdb_service

def init_with_data():
    """Inicializar BD con datos si está vacía"""
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM movies")
    total = cursor.fetchone()['count']
    
    if total > 0:
        print(f"✅ BD ya tiene {total} películas")
        conn.close()
        return
    
    print("📥 BD vacía, cargando datos iniciales...")
    
    movies = [
        'Inception',
        'The Dark Knight',
        'Interstellar',
        'The Matrix',
        'Forrest Gump',
        'Titanic',
        'Avatar',
        'Pulp Fiction',
        'Fight Club',
        'The Avengers',
    ]
    
    series = [
        'Breaking Bad',
        'Game of Thrones',
        'Stranger Things',
        'The Office',
        'The Crown',
    ]
    
    # Agregar películas
    for query in movies:
        try:
            results = tmdb_service.search_movies(query)
            if results:
                details = tmdb_service.get_movie_details(results[0]['id'])
                if details:
                    cursor.execute('''
                        INSERT INTO movies 
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
            print(f"  ⚠️ {query}: {str(e)[:50]}")
    
    # Agregar series
    for query in series:
        try:
            results = tmdb_service.search_series(query)
            if results:
                details = tmdb_service.get_series_details(results[0]['id'])
                if details:
                    cursor.execute('''
                        INSERT INTO series 
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
            print(f"  ⚠️ {query}: {str(e)[:50]}")
    
    conn.commit()
    conn.close()
    print("✅ Datos iniciales cargados")
