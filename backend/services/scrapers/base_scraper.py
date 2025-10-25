import requests
from abc import ABC, abstractmethod
import time

class BaseScraper(ABC):
    """Clase base para todos los scrapers - Compatible con Render.com"""
    
    def __init__(self):
        self.session = requests.Session()
        self._setup_session()
        self.timeout = 20  # Render tiene timeout de ~30s
    
    def _setup_session(self):
        """Configura la sesión para parecer un navegador real"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        })
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Verifica si este scraper puede manejar la URL"""
        pass
    
    @abstractmethod
    def extract_links(self, url: str, **kwargs) -> dict:
        """Extrae los links de la URL"""
        pass
    
    def get_html(self, url: str, referer: str = None, retry: int = 2) -> str:
        """
        Obtiene el HTML de una URL con reintentos
        
        Args:
            url: URL a obtener
            referer: URL de referencia (opcional)
            retry: Número de reintentos
        
        Returns:
            str: Contenido HTML
        """
        headers = self.session.headers.copy()
        
        # Agregar referer si se proporciona
        if referer:
            headers['Referer'] = referer
        else:
            # Usar el dominio base como referer
            from urllib.parse import urlparse
            parsed = urlparse(url)
            headers['Referer'] = f"{parsed.scheme}://{parsed.netloc}/"
        
        headers['Sec-Fetch-Site'] = 'same-origin'
        
        last_error = None
        for attempt in range(retry):
            try:
                if attempt > 0:
                    time.sleep(1)  # Pequeño delay entre reintentos
                
                response = self.session.get(
                    url, 
                    headers=headers,
                    timeout=self.timeout,
                    allow_redirects=True,
                    verify=True  # Importante para Render
                )
                
                response.raise_for_status()
                return response.text
                
            except requests.exceptions.HTTPError as e:
                last_error = e
                if e.response.status_code == 403 and attempt < retry - 1:
                    # Intentar con un User-Agent diferente
                    self._rotate_user_agent()
                    continue
                    
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < retry - 1:
                    continue
        
        if last_error:
            raise Exception(f"Error obteniendo HTML: {last_error}")
        raise Exception("Error desconocido obteniendo HTML")
    
    def _rotate_user_agent(self):
        """Rota entre diferentes User-Agents"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]
        import random
        self.session.headers['User-Agent'] = random.choice(user_agents)
    
    def make_request(self, url: str, method: str = 'GET', **kwargs):
        """
        Hace una petición HTTP con la sesión configurada
        
        Args:
            url: URL a solicitar
            method: Método HTTP (GET, POST, etc.)
            **kwargs: Argumentos adicionales para requests
        
        Returns:
            Response: Respuesta de la petición
        """
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        return self.session.request(method, url, **kwargs)