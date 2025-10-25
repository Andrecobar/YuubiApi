from .base_scraper import BaseScraper
import re
import json
import requests
from urllib.parse import urlparse, parse_qs, unquote

class ZonaHackScraper(BaseScraper):
    """Scraper para zonahack.com.ar - Requiere LISTEN_URL manual"""
    
    def can_handle(self, url: str) -> bool:
        return 'zonahack' in url.lower()
    
    def extract_links(self, url: str, listen_url: str = None) -> dict:
        """
        Extrae links de zonahack usando la URL de Firestore
        
        Args:
            url: URL de la película (solo para referencia)
            listen_url: URL completa de channel?... de Firestore (REQUERIDO)
        """
        if not listen_url:
            return {
                'success': False,
                'source': 'zonahack',
                'error': 'Se requiere listen_url para zonahack',
                'links': [],
                'total': 0
            }
        
        try:
            data = self._extract_firestore_data(listen_url)
            
            if not data:
                return {
                    'success': False,
                    'source': 'zonahack',
                    'error': 'No se encontraron datos (sesión expirada?)',
                    'links': [],
                    'total': 0
                }
            
            # Aplanar todos los links de todos los idiomas
            all_links = []
            for movie in data:
                for idioma, hosts in movie.get('idiomas', {}).items():
                    for host, link_url in hosts.items():
                        all_links.append({
                            'server': host,
                            'url': link_url,
                            'language': idioma
                        })
            
            return {
                'success': True,
                'source': 'zonahack',
                'links': all_links,
                'total': len(all_links),
                'movies_found': len(data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'source': 'zonahack',
                'error': str(e),
                'links': [],
                'total': 0
            }
    
    def _clean_text_response(self, text):
        """Quita el prefijo XSSI si lo hay"""
        return re.sub(r"^\)\]\}'\s*", "", text, flags=re.MULTILINE).strip()
    
    def _decode_iframe_url(self, url):
        """Decodifica URLs de tipo teomovie.web.app/iframe.html?url=..."""
        if "iframe.html?url=" not in url:
            return url
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        inner = qs.get("url", [None])[0]
        return unquote(inner) if inner else url
    
    def _extract_firestore_data(self, listen_url):
        """Extrae datos de la respuesta de Firestore"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/141.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Origin": "https://zonahack.com.ar",
            "Referer": "https://zonahack.com.ar/",
        }
        
        r = requests.get(listen_url, headers=headers, timeout=25)
        r.raise_for_status()
        
        text = self._clean_text_response(r.text)
        
        # Buscar bloques "document"
        docs = re.findall(r'"document"\s*:\s*\{(.*?)\}\s*,\s*"targetIds"', text, re.DOTALL)
        
        movies = []
        for doc_text in docs:
            try:
                doc_json = json.loads("{" + doc_text + "}")
            except:
                continue
            
            fields = doc_json.get("fields", {})
            
            nombre = fields.get("NOMBRE", {}).get("stringValue")
            idiomas = {}
            
            # Extraer idiomas
            for label, idioma_nombre in [
                ("SERVERCASTELLANO", "Castellano"),
                ("SERVERSUB", "Subtitulado"),
                ("IDIOMAS", "Latino")
            ]:
                idioma_data = fields.get(label, {}).get("mapValue", {}).get("fields", {})
                enlaces = {
                    host: self._decode_iframe_url(data["stringValue"])
                    for host, data in idioma_data.items()
                }
                if enlaces:
                    idiomas[idioma_nombre] = enlaces
            
            if idiomas:
                movies.append({
                    "nombre": nombre,
                    "idiomas": idiomas
                })
        
        return movies
