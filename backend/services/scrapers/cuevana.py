from .base_scraper import BaseScraper
from bs4 import BeautifulSoup

class CuevanaScraper(BaseScraper):
    """Scraper para cuevana.biz"""
    
    def can_handle(self, url: str) -> bool:
        return 'cuevana' in url.lower()
    
    def extract_links(self, url: str) -> dict:
        try:
            html = self.get_html(url)
            soup = BeautifulSoup(html, 'html.parser')
            
            links = []
            
            # Buscar iframes
            for iframe in soup.select('iframe[src]'):
                link_url = iframe.get('src')
                if link_url and any(s in link_url for s in ['voe', 'streamwish', 'filemoon', 'vidhide', 'streamtape']):
                    server_name = self._detect_server(link_url)
                    
                    links.append({
                        'server': server_name,
                        'url': link_url,
                        'language': 'Latino'
                    })
            
            return {
                'success': True,
                'source': 'cuevana',
                'links': links,
                'total': len(links)
            }
            
        except Exception as e:
            return {
                'success': False,
                'source': 'cuevana',
                'error': str(e),
                'links': [],
                'total': 0
            }
    
    def _detect_server(self, url: str) -> str:
        servers = {
            'voe': 'voe',
            'streamwish': 'streamwish',
            'filemoon': 'filemoon',
            'vidhide': 'vidhide',
            'streamtape': 'streamtape'
        }
        
        url_lower = url.lower()
        for key, name in servers.items():
            if key in url_lower:
                return name
        
        return 'desconocido'
