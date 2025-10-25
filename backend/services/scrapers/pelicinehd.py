from .base_scraper import BaseScraper
from bs4 import BeautifulSoup

class PeliCineHDScraper(BaseScraper):
    """Scraper para pelicinehd.com"""
    
    def can_handle(self, url: str) -> bool:
        return 'pelicinehd' in url.lower()
    
    def extract_links(self, url: str) -> dict:
        try:
            html = self.get_html(url)
            soup = BeautifulSoup(html, 'html.parser')
            
            links = []
            
            # Buscar <iframe> dentro de .Video
            for video_div in soup.select('div.Video'):
                iframe = video_div.find('iframe')
                if iframe and iframe.get('src'):
                    link_url = iframe.get('src')
                    server_name = self._detect_server(link_url)
                    
                    links.append({
                        'server': server_name,
                        'url': link_url,
                        'language': 'Español'
                    })
            
            # También buscar iframes fuera de .Video
            for iframe in soup.select('iframe[src]'):
                link_url = iframe.get('src')
                if any(s in link_url for s in ['voe', 'streamwish', 'filemoon', 'vidhide']):
                    server_name = self._detect_server(link_url)
                    
                    if not any(l['url'] == link_url for l in links):
                        links.append({
                            'server': server_name,
                            'url': link_url,
                            'language': 'Español'
                        })
            
            return {
                'success': True,
                'source': 'pelicinehd',
                'links': links,
                'total': len(links)
            }
            
        except Exception as e:
            return {
                'success': False,
                'source': 'pelicinehd',
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
