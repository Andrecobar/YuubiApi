import requests
from typing import List, Dict

class NovelasAPI:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def _hacer_peticion(self, endpoint: str, metodo: str = 'GET', datos: dict = None):
        url = f"{self.base_url}{endpoint}"
        try:
            if metodo == 'GET':
                respuesta = self.session.get(url)
            elif metodo == 'POST':
                respuesta = self.session.post(url, json=datos)
            respuesta.raise_for_status()
            return respuesta.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en la petición: {e}")
            return None
    
    def obtener_series(self):
        return self._hacer_peticion('/api/series')
    
    def obtener_serie(self, serie_id: int):
        return self._hacer_peticion(f'/api/series/{serie_id}')
    
    def obtener_episodios(self, serie_id: int):
        return self._hacer_peticion(f'/api/series/{serie_id}/episodios')
    
    def obtener_peliculas(self):
        return self._hacer_peticion('/api/peliculas')
    
    def buscar(self, query: str):
        return self._hacer_peticion(f'/api/buscar?q={query}')
    
    def agregar_serie(self, titulo: str, descripcion: str = "", 
                     imagen_portada: str = "", anio: int = None, 
                     genero: str = ""):
        datos = {
            'titulo': titulo,
            'descripcion': descripcion,
            'imagen_portada': imagen_portada,
            'anio': anio,
            'genero': genero
        }
        return self._hacer_peticion('/api/series', 'POST', datos)
    
    def agregar_episodio(self, serie_id: int, numero_episodio: int,
                        titulo: str, url_video: str, 
                        duracion: int = None):
        datos = {
            'serie_id': serie_id,
            'numero_episodio': numero_episodio,
            'titulo': titulo,
            'url_video': url_video,
            'duracion': duracion
        }
        return self._hacer_peticion('/api/episodios', 'POST', datos)
