from .scrapers.pelisplushd import PelisPlusHDScraper
from .scrapers.pelicinehd import PeliCineHDScraper
from .scrapers.cuevana import CuevanaScraper
from .scrapers.zonahack import ZonaHackScraper

class LinkExtractor:
    """Orquestador de scrapers"""
    
    def __init__(self):
        self.scrapers = [
            PelisPlusHDScraper(),
            PeliCineHDScraper(),
            CuevanaScraper(),
            ZonaHackScraper()
        ]
    
    def extract(self, url: str, listen_url: str = None) -> dict:
        """
        Extrae links de una URL
        
        Args:
            url: URL de la película/serie
            listen_url: URL de Firestore (solo para zonahack)
        """
        # Detectar qué scraper usar
        for scraper in self.scrapers:
            if scraper.can_handle(url):
                # Caso especial para zonahack
                if isinstance(scraper, ZonaHackScraper):
                    return scraper.extract_links(url, listen_url)
                else:
                    return scraper.extract_links(url)
        
        return {
            'success': False,
            'error': 'No se encontró scraper para esta URL',
            'url': url,
            'links': [],
            'total': 0
        }

link_extractor = LinkExtractor()
