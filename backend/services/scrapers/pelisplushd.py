from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import os

class PelisPlusHDScraper(BaseScraper):
    """Scraper para pelisplushd.to - Optimizado para Render.com"""
    
    def can_handle(self, url: str) -> bool:
        return 'pelisplushd' in url.lower()
    
    def extract_links(self, url: str) -> dict:
        """
        Extrae links desde el HTML de pelisplushd.to
        Estrategia: Intentar múltiples métodos
        """
        try:
            # Método 1: Scraping directo (puede fallar en Render por 403)
            try:
                return self._extract_from_html(url)
            except Exception as e:
                error_msg = str(e)
                
                # Si es 403, intentar método alternativo
                if '403' in error_msg:
                    return self._extract_alternative(url)
                raise
                
        except Exception as e:
            return {
                'success': False,
                'source': 'pelisplushd',
                'error': str(e),
                'links': [],
                'total': 0,
                'suggestion': 'Intenta acceder directamente a la página en tu navegador y copiar los enlaces manualmente, o usa una VPN.'
            }
    
    def _extract_from_html(self, url: str) -> dict:
        """Método principal: Extrae desde HTML"""
        html = self.get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Buscar todos los <li class="playurl"> con data-url
        links = []
        playurl_items = soup.find_all('li', {'data-url': True})
        
        for li in playurl_items:
            link_url = li.get('data-url')
            language = li.get('data-name', 'Desconocido')
            
            # Detectar servidor desde el texto del <a> o desde la URL
            server_name = 'Desconocido'
            a_tag = li.find('a')
            if a_tag and a_tag.text:
                server_name = a_tag.text.strip().title()
            
            # Si no se detectó del texto, detectar de la URL
            if server_name == 'Desconocido':
                server_name = self._detect_server(link_url)
            
            if link_url:
                links.append({
                    'server': server_name,
                    'url': link_url,
                    'language': language
                })
        
        # Remover duplicados
        seen = set()
        unique_links = []
        for link in links:
            key = (link['url'], link['language'])
            if key not in seen:
                seen.add(key)
                unique_links.append(link)
        
        return {
            'success': len(unique_links) > 0,
            'source': 'pelisplushd',
            'links': unique_links,
            'total': len(unique_links),
            'method': 'html'
        }
    
    def _extract_alternative(self, url: str) -> dict:
        """
        Método alternativo: Usa una API proxy si está configurada
        Esto permite bypassear el bloqueo 403 en Render
        """
        # Verificar si hay API proxy configurada
        proxy_api = os.getenv('SCRAPER_PROXY_API')
        
        if not proxy_api:
            return {
                'success': False,
                'source': 'pelisplushd',
                'error': 'Error 403 - IP bloqueada. Configura SCRAPER_PROXY_API en variables de entorno.',
                'links': [],
                'total': 0,
                'suggestion': 'Configura una API de proxy (ScraperAPI, Bright Data, etc.) en las variables de entorno de Render.'
            }
        
        # Usar proxy API
        try:
            import requests
            proxy_url = f"{proxy_api}?url={url}&render=false"
            response = requests.get(proxy_url, timeout=25)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Mismo proceso de extracción
            links = []
            for li in soup.find_all('li', {'data-url': True}):
                link_url = li.get('data-url')
                language = li.get('data-name', 'Desconocido')
                
                server_name = 'Desconocido'
                a_tag = li.find('a')
                if a_tag and a_tag.text:
                    server_name = a_tag.text.strip().title()
                else:
                    server_name = self._detect_server(link_url)
                
                if link_url:
                    links.append({
                        'server': server_name,
                        'url': link_url,
                        'language': language
                    })
            
            # Remover duplicados
            seen = set()
            unique_links = []
            for link in links:
                key = (link['url'], link['language'])
                if key not in seen:
                    seen.add(key)
                    unique_links.append(link)
            
            return {
                'success': len(unique_links) > 0,
                'source': 'pelisplushd',
                'links': unique_links,
                'total': len(unique_links),
                'method': 'proxy'
            }
            
        except Exception as e:
            return {
                'success': False,
                'source': 'pelisplushd',
                'error': f'Error con proxy: {str(e)}',
                'links': [],
                'total': 0
            }
    
    def _detect_server(self, url: str) -> str:
        """Detecta el nombre del servidor desde la URL"""
        servers = {
            'streamwish': 'StreamWish',
            'hgplaycdn': 'StreamWish',
            'vidhide': 'VidHide',
            'filelions': 'VidHide',
            'voe.sx': 'Voe',
            'voe': 'Voe',
            'streamtape': 'StreamTape',
            'filemoon': 'FileMoon',
            'waaw': 'Waaw',
            'netu': 'Netu',
            'fembed': 'Fembed',
            'watchsb': 'StreamSB',
            'streamsb': 'StreamSB',
            'streamlare': 'StreamLare',
            'doodstream': 'DoodStream',
            'dood': 'DoodStream',
            'mixdrop': 'MixDrop',
            'upstream': 'UpStream'
        }
        
        url_lower = url.lower()
        for key, name in servers.items():
            if key in url_lower:
                return name
        
        return 'Desconocido'