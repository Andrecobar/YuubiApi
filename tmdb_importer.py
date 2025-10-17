import requests
import sqlite3
from config import TMDB_API_KEY, TMDB_BASE_URL, TMDB_IMAGE_BASE_URL
import time

class TMDBImporter:
    """Importador de series y películas desde TMDB"""
    
    def __init__(self):
        self.api_key = TMDB_API_KEY
        self.base_url = TMDB_BASE_URL
        self.image_base_url = TMDB_IMAGE_BASE_URL
        self.conn = sqlite3.connect('novelas.db')
        self.cursor = self.conn.cursor()
    
    def buscar_series_por_pais(self, pais, cantidad=20, genero=None):
        """
        Busca series populares por país
        
        Args:
            pais: Código del país ('MX', 'CO', 'KR', 'ES', etc.)
            cantidad: Número de series a importar
            genero: ID del género (opcional)
        """
        print(f"\n🔍 Buscando series de {pais}...")
        
        params = {
            'api_key': self.api_key,
            'language': 'es-MX',
            'with_origin_country': pais,
            'sort_by': 'popularity.desc',
            'page': 1
        }
        
        if genero:
            params['with_genres'] = genero
        
        try:
            response = requests.get(f"{self.base_url}/discover/tv", params=params)
            response.raise_for_status()
            data = response.json()
            
            series_importadas = 0
            for serie in data.get('results', [])[:cantidad]:
                if self.importar_serie_detallada(serie['id']):
                    series_importadas += 1
                time.sleep(0.3)  # Esperar para no saturar la API
            
            print(f"✅ Importadas {series_importadas} series de {pais}")
            return series_importadas
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al buscar series: {e}")
            return 0
    
    def importar_serie_detallada(self, serie_id):
        """Importa una serie con todos sus detalles y episodios"""
        
        try:
            # Obtener detalles de la serie
            response = requests.get(
                f"{self.base_url}/tv/{serie_id}",
                params={'api_key': self.api_key, 'language': 'es-MX'}
            )
            response.raise_for_status()
            serie = response.json()
            
            # Preparar datos
            titulo = serie.get('name', 'Sin título')
            descripcion = serie.get('overview', 'Sin descripción')
            anio = int(serie.get('first_air_date', '2000')[:4]) if serie.get('first_air_date') else 2000
            generos = ', '.join([g['name'] for g in serie.get('genres', [])])
            imagen = f"{self.image_base_url}{serie.get('poster_path')}" if serie.get('poster_path') else ''
            
            # Insertar serie
            self.cursor.execute('''
                INSERT OR IGNORE INTO series (titulo, descripcion, anio, genero, imagen_portada)
                VALUES (?, ?, ?, ?, ?)
            ''', (titulo, descripcion, anio, generos, imagen))
            
            if self.cursor.rowcount == 0:
                print(f"  ⚠️  {titulo} ya existe")
                return False
            
            serie_db_id = self.cursor.lastrowid
            self.conn.commit()
            
            print(f"  ✅ {titulo} ({anio})")
            
            # Importar episodios de la primera temporada
            episodios_importados = self.importar_episodios(serie_id, serie_db_id, temporada=1)
            if episodios_importados > 0:
                print(f"     📺 {episodios_importados} episodios importados")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error al importar serie {serie_id}: {e}")
            return False
    
    def importar_episodios(self, tmdb_serie_id, db_serie_id, temporada=1):
        """Importa episodios de una temporada específica"""
        
        try:
            response = requests.get(
                f"{self.base_url}/tv/{tmdb_serie_id}/season/{temporada}",
                params={'api_key': self.api_key, 'language': 'es-MX'}
            )
            response.raise_for_status()
            season_data = response.json()
            
            episodios_importados = 0
            for episodio in season_data.get('episodes', []):
                self.cursor.execute('''
                    INSERT OR IGNORE INTO episodios 
                    (serie_id, numero_episodio, titulo, duracion, url_video)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    db_serie_id,
                    episodio.get('episode_number'),
                    episodio.get('name', f"Episodio {episodio.get('episode_number')}"),
                    episodio.get('runtime'),
                    ''  # URL del video (lo agregarás después)
                ))
                episodios_importados += 1
            
            self.conn.commit()
            return episodios_importados
            
        except requests.exceptions.RequestException as e:
            print(f"     ⚠️  Error al importar episodios: {e}")
            return 0
    
    def buscar_peliculas_por_pais(self, pais, cantidad=20):
        """Busca películas populares por país"""
        
        print(f"\n🔍 Buscando películas de {pais}...")
        
        params = {
            'api_key': self.api_key,
            'language': 'es-MX',
            'with_origin_country': pais,
            'sort_by': 'popularity.desc',
            'page': 1
        }
        
        try:
            response = requests.get(f"{self.base_url}/discover/movie", params=params)
            response.raise_for_status()
            data = response.json()
            
            peliculas_importadas = 0
            for pelicula in data.get('results', [])[:cantidad]:
                if self.importar_pelicula(pelicula['id']):
                    peliculas_importadas += 1
                time.sleep(0.3)
            
            print(f"✅ Importadas {peliculas_importadas} películas de {pais}")
            return peliculas_importadas
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error al buscar películas: {e}")
            return 0
    
    def importar_pelicula(self, pelicula_id):
        """Importa una película con todos sus detalles"""
        
        try:
            response = requests.get(
                f"{self.base_url}/movie/{pelicula_id}",
                params={'api_key': self.api_key, 'language': 'es-MX'}
            )
            response.raise_for_status()
            pelicula = response.json()
            
            titulo = pelicula.get('title', 'Sin título')
            descripcion = pelicula.get('overview', 'Sin descripción')
            anio = int(pelicula.get('release_date', '2000')[:4]) if pelicula.get('release_date') else 2000
            generos = ', '.join([g['name'] for g in pelicula.get('genres', [])])
            imagen = f"{self.image_base_url}{pelicula.get('poster_path')}" if pelicula.get('poster_path') else ''
            duracion = pelicula.get('runtime')
            
            self.cursor.execute('''
                INSERT OR IGNORE INTO peliculas 
                (titulo, descripcion, anio, genero, imagen_portada, duracion, url_video)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (titulo, descripcion, anio, generos, imagen, duracion, ''))
            
            if self.cursor.rowcount == 0:
                return False
            
            self.conn.commit()
            print(f"  ✅ {titulo} ({anio})")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error al importar película: {e}")
            return False
    
    def buscar_por_nombre(self, nombre, tipo='tv'):
        """
        Busca series o películas por nombre
        
        Args:
            nombre: Nombre a buscar
            tipo: 'tv' para series, 'movie' para películas
        """
        print(f"\n🔍 Buscando '{nombre}'...")
        
        params = {
            'api_key': self.api_key,
            'language': 'es-MX',
            'query': nombre
        }
        
        try:
            response = requests.get(f"{self.base_url}/search/{tipo}", params=params)
            response.raise_for_status()
            resultados = response.json().get('results', [])
            
            if not resultados:
                print("❌ No se encontraron resultados")
                return
            
            print(f"\n📋 Encontrados {len(resultados)} resultados:")
            for i, item in enumerate(resultados[:10], 1):
                nombre_item = item.get('name' if tipo == 'tv' else 'title')
                anio = item.get('first_air_date' if tipo == 'tv' else 'release_date', '')[:4]
                print(f"{i}. {nombre_item} ({anio})")
            
            seleccion = input("\n¿Cuál quieres importar? (número o 0 para cancelar): ")
            
            if seleccion.isdigit() and 0 < int(seleccion) <= len(resultados):
                item_id = resultados[int(seleccion) - 1]['id']
                
                if tipo == 'tv':
                    self.importar_serie_detallada(item_id)
                else:
                    self.importar_pelicula(item_id)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error en la búsqueda: {e}")
    
    def importar_paquete_completo(self):
        """Importa un paquete completo de novelas populares"""
        
        print("\n" + "="*60)
        print("📦 IMPORTACIÓN MASIVA DE CONTENIDO")
        print("="*60)
        
        # Novelas Mexicanas
        print("\n🇲🇽 NOVELAS MEXICANAS")
        self.buscar_series_por_pais('MX', cantidad=30)
        self.buscar_peliculas_por_pais('MX', cantidad=15)
        
        # Novelas Colombianas
        print("\n🇨🇴 NOVELAS COLOMBIANAS")
        self.buscar_series_por_pais('CO', cantidad=25)
        self.buscar_peliculas_por_pais('CO', cantidad=10)
        
        # Doramas Coreanos
        print("\n🇰🇷 DORAMAS COREANOS")
        self.buscar_series_por_pais('KR', cantidad=30)
        self.buscar_peliculas_por_pais('KR', cantidad=15)
        
        # Doramas Japoneses
        print("\n🇯🇵 DORAMAS JAPONESES")
        self.buscar_series_por_pais('JP', cantidad=20)
        
        # Series Españolas
        print("\n🇪🇸 SERIES ESPAÑOLAS")
        self.buscar_series_por_pais('ES', cantidad=15)
        
        print("\n" + "="*60)
        print("✅ ¡IMPORTACIÓN COMPLETA!")
        print("="*60)
        
        # Mostrar estadísticas
        self.mostrar_estadisticas()
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas de la base de datos"""
        
        self.cursor.execute("SELECT COUNT(*) FROM series")
        total_series = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM episodios")
        total_episodios = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM peliculas")
        total_peliculas = self.cursor.fetchone()[0]
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   📺 Series: {total_series}")
        print(f"   🎬 Episodios: {total_episodios}")
        print(f"   🎥 Películas: {total_peliculas}")
        print(f"   📚 Total: {total_series + total_peliculas} contenidos")
    
    def cerrar(self):
        """Cierra la conexión a la base de datos"""
        self.conn.close()


# ==========================================
# MENÚ INTERACTIVO
# ==========================================

def menu_principal():
    """Menú interactivo para importar contenido"""
    
    importer = TMDBImporter()
    
    while True:
        print("\n" + "="*60)
        print("🎬 IMPORTADOR DE NOVELAS DESDE TMDB")
        print("="*60)
        print("1. Importar paquete completo (recomendado)")
        print("2. Importar series por país")
        print("3. Importar películas por país")
        print("4. Buscar serie específica por nombre")
        print("5. Buscar película específica por nombre")
        print("6. Ver estadísticas")
        print("7. Salir")
        print("="*60)
        
        opcion = input("\nSelecciona una opción: ")
        
        if opcion == '1':
            confirmar = input("\n⚠️  Esto importará ~150 series y películas. ¿Continuar? (s/n): ")
            if confirmar.lower() == 's':
                importer.importar_paquete_completo()
        
        elif opcion == '2':
            pais = input("Código del país (MX/CO/KR/JP/ES): ").upper()
            cantidad = int(input("¿Cuántas series importar?: "))
            importer.buscar_series_por_pais(pais, cantidad)
        
        elif opcion == '3':
            pais = input("Código del país (MX/CO/KR/JP/ES): ").upper()
            cantidad = int(input("¿Cuántas películas importar?: "))
            importer.buscar_peliculas_por_pais(pais, cantidad)
        
        elif opcion == '4':
            nombre = input("Nombre de la serie: ")
            importer.buscar_por_nombre(nombre, 'tv')
        
        elif opcion == '5':
            nombre = input("Nombre de la película: ")
            importer.buscar_por_nombre(nombre, 'movie')
        
        elif opcion == '6':
            importer.mostrar_estadisticas()
        
        elif opcion == '7':
            print("\n👋 ¡Hasta luego!")
            importer.cerrar()
            break
        
        else:
            print("❌ Opción inválida")


if __name__ == '__main__':
    menu_principal()