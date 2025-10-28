#!/usr/bin/env python3
"""
Script para actualizar tu Gist DB fácilmente
Uso: python update_gist.py
"""

import requests
import json
import os
from datetime import datetime

# Configuración
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # Tu Personal Access Token de GitHub
GIST_ID = os.getenv('GIST_ID')  # ID de tu Gist (aparece en la URL)
TMDB_API_KEY = os.getenv('TMDB_API_KEY')  # Para obtener metadata

def get_gist_content():
    """Obtiene el contenido actual del Gist"""
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(f'https://api.github.com/gists/{GIST_ID}', headers=headers)
    response.raise_for_status()
    
    gist_data = response.json()
    filename = list(gist_data['files'].keys())[0]
    content = gist_data['files'][filename]['content']
    
    return json.loads(content), filename

def update_gist_content(content, filename='movies.json'):
    """Actualiza el contenido del Gist"""
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    
    payload = {
        'files': {
            filename: {
                'content': json.dumps(content, indent=2, ensure_ascii=False)
            }
        }
    }
    
    response = requests.patch(
        f'https://api.github.com/gists/{GIST_ID}',
        headers=headers,
        json=payload
    )
    response.raise_for_status()
    return response.json()

def get_tmdb_movie_info(tmdb_id):
    """Obtiene información de una película desde TMDB"""
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{tmdb_id}',
        params={'api_key': TMDB_API_KEY, 'language': 'es-ES'}
    )
    response.raise_for_status()
    return response.json()

def get_tmdb_series_info(tmdb_id):
    """Obtiene información de una serie desde TMDB"""
    response = requests.get(
        f'https://api.themoviedb.org/3/tv/{tmdb_id}',
        params={'api_key': TMDB_API_KEY, 'language': 'es-ES'}
    )
    response.raise_for_status()
    return response.json()

def add_movie():
    """Modo interactivo para agregar una película"""
    print("\n" + "="*60)
    print("🎬 AGREGAR PELÍCULA")
    print("="*60)
    
    # Paso 1: Buscar en TMDB
    query = input("\n🔍 Buscar película en TMDB: ").strip()
    
    search_response = requests.get(
        'https://api.themoviedb.org/3/search/movie',
        params={'api_key': TMDB_API_KEY, 'query': query, 'language': 'es-ES'}
    )
    results = search_response.json().get('results', [])[:5]
    
    if not results:
        print("❌ No se encontraron resultados")
        return
    
    print("\nResultados:")
    for i, movie in enumerate(results, 1):
        year = movie.get('release_date', '')[:4] if movie.get('release_date') else 'N/A'
        print(f"{i}. {movie['title']} ({year}) - ID: {movie['id']}")
    
    choice = int(input("\nSelecciona una opción (1-5): ")) - 1
    selected_movie = results[choice]
    tmdb_id = selected_movie['id']
    
    # Paso 2: Obtener detalles completos
    movie_info = get_tmdb_movie_info(tmdb_id)
    
    print(f"\n✅ Seleccionado: {movie_info['title']} ({movie_info.get('release_date', '')[:4]})")
    
    # Paso 3: Pedir datos de ZonaHack
    print("\n📋 Ahora necesito los datos de ZonaHack:")
    print("   1. Ve a ZonaHack y busca esta película")
    print("   2. Abre DevTools (F12) > Network > Doc")
    print("   3. Recarga la página y copia el listen_url\n")
    
    zonahack_url = input("URL de ZonaHack: ").strip()
    listen_url = input("Listen URL (channel?...): ").strip()
    
    if not listen_url:
        print("❌ listen_url es requerido")
        return
    
    # Paso 4: Crear entrada
    entry = {
        'tmdb_id': tmdb_id,
        'title': movie_info['title'],
        'title_es': movie_info.get('title', ''),
        'type': 'movie',
        'poster_path': movie_info.get('poster_path'),
        'zonahack_url': zonahack_url,
        'listen_url': listen_url,
        'status': 'verified',
        'added_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    # Paso 5: Actualizar Gist
    print("\n📥 Cargando Gist actual...")
    content, filename = get_gist_content()
    
    content[str(tmdb_id)] = entry
    
    print("📤 Actualizando Gist...")
    update_gist_content(content, filename)
    
    print(f"\n✅ ¡Película '{movie_info['title']}' agregada correctamente!")
    print(f"   Total de películas: {sum(1 for v in content.values() if v.get('type') == 'movie')}")

def add_series_season():
    """Modo interactivo para agregar una temporada de serie"""
    print("\n" + "="*60)
    print("📺 AGREGAR TEMPORADA DE SERIE")
    print("="*60)
    
    # Paso 1: Buscar en TMDB
    query = input("\n🔍 Buscar serie en TMDB: ").strip()
    
    search_response = requests.get(
        'https://api.themoviedb.org/3/search/tv',
        params={'api_key': TMDB_API_KEY, 'query': query, 'language': 'es-ES'}
    )
    results = search_response.json().get('results', [])[:5]
    
    if not results:
        print("❌ No se encontraron resultados")
        return
    
    print("\nResultados:")
    for i, series in enumerate(results, 1):
        year = series.get('first_air_date', '')[:4] if series.get('first_air_date') else 'N/A'
        print(f"{i}. {series['name']} ({year}) - ID: {series['id']}")
    
    choice = int(input("\nSelecciona una opción (1-5): ")) - 1
    selected_series = results[choice]
    tmdb_id = selected_series['id']
    
    # Paso 2: Obtener detalles completos
    series_info = get_tmdb_series_info(tmdb_id)
    
    print(f"\n✅ Seleccionado: {series_info['name']}")
    print(f"   Temporadas disponibles: {series_info['number_of_seasons']}")
    
    season_number = int(input("\n¿Qué temporada quieres agregar? "))
    
    # Obtener info de la temporada
    season_response = requests.get(
        f'https://api.themoviedb.org/3/tv/{tmdb_id}/season/{season_number}',
        params={'api_key': TMDB_API_KEY, 'language': 'es-ES'}
    )
    season_info = season_response.json()
    
    print(f"\n📋 Temporada {season_number}: {len(season_info['episodes'])} episodios")
    
    # Paso 3: Pedir datos de ZonaHack
    print("\n📋 Ahora necesito los datos de ZonaHack:")
    print("   1. Ve a ZonaHack y busca esta serie/temporada")
    print("   2. Abre DevTools (F12) > Network > Doc")
    print("   3. Recarga la página y copia el listen_url\n")
    
    zonahack_url = input(f"URL de ZonaHack (Temporada {season_number}): ").strip()
    listen_url = input("Listen URL (channel?...): ").strip()
    
    if not listen_url:
        print("❌ listen_url es requerido")
        return
    
    # Paso 4: Crear/actualizar entrada
    print("\n📥 Cargando Gist actual...")
    content, filename = get_gist_content()
    
    # Verificar si la serie ya existe
    if str(tmdb_id) not in content:
        # Crear entrada de serie nueva
        content[str(tmdb_id)] = {
            'tmdb_id': tmdb_id,
            'title': series_info['name'],
            'title_es': series_info.get('name', ''),
            'type': 'series',
            'poster_path': series_info.get('poster_path'),
            'status': 'verified',
            'added_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'seasons': {}
        }
    
    # Agregar temporada
    if 'seasons' not in content[str(tmdb_id)]:
        content[str(tmdb_id)]['seasons'] = {}
    
    content[str(tmdb_id)]['seasons'][str(season_number)] = {
        'season_number': season_number,
        'episodes': len(season_info['episodes']),
        'zonahack_url': zonahack_url,
        'listen_url': listen_url,
        'added_at': datetime.now().isoformat()
    }
    
    content[str(tmdb_id)]['updated_at'] = datetime.now().isoformat()
    
    # Paso 5: Actualizar Gist
    print("📤 Actualizando Gist...")
    update_gist_content(content, filename)
    
    print(f"\n✅ ¡Temporada {season_number} de '{series_info['name']}' agregada correctamente!")
    print(f"   Episodios: {len(season_info['episodes'])}")
    print(f"   Total de series: {sum(1 for v in content.values() if v.get('type') == 'series')}")

def list_content():
    """Lista todo el contenido en el Gist"""
    print("\n📋 Contenido actual en Gist:")
    print("="*60)
    
    content, _ = get_gist_content()
    
    movies = [v for v in content.values() if v.get('type') == 'movie']
    series = [v for v in content.values() if v.get('type') == 'series']
    
    print(f"\n🎬 PELÍCULAS ({len(movies)}):")
    for movie in sorted(movies, key=lambda x: x.get('added_at', ''), reverse=True)[:10]:
        print(f"   - {movie['title']} (ID: {movie['tmdb_id']})")
    
    print(f"\n📺 SERIES ({len(series)}):")
    for show in sorted(series, key=lambda x: x.get('added_at', ''), reverse=True)[:10]:
        seasons_count = len(show.get('seasons', {}))
        print(f"   - {show['title']} ({seasons_count} temporadas) (ID: {show['tmdb_id']})")
    
    print(f"\n📊 TOTAL: {len(content)} contenidos")

def main():
    """Menú principal"""
    if not GITHUB_TOKEN or not GIST_ID or not TMDB_API_KEY:
        print("❌ Error: Configura las variables de entorno:")
        print("   - GITHUB_TOKEN: Tu Personal Access Token de GitHub")
        print("   - GIST_ID: ID de tu Gist")
        print("   - TMDB_API_KEY: Tu API key de TMDB")
        return
    
    while True:
        print("\n" + "="*60)
        print("🎬 GIST DB UPDATER - Yuubi API")
        print("="*60)
        print("\n1. 🎬 Agregar Película")
        print("2. 📺 Agregar Temporada de Serie")
        print("3. 📋 Ver Contenido Actual")
        print("4. 🚪 Salir")
        
        choice = input("\nSelecciona una opción: ").strip()
        
        if choice == '1':
            add_movie()
        elif choice == '2':
            add_series_season()
        elif choice == '3':
            list_content()
        elif choice == '4':
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")

if __name__ == '__main__':
    main()