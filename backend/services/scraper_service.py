import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

class ScraperService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = 10
    
    def scrape_pelisplushd(self, query):
        """Scrappear pelisplushd.mx"""
        links = []
        try:
            search_url = f"https://pelisplushd.mx/?s={query}"
            response = requests.get(search_url, headers=self.headers, timeout=self.timeout)
            response.encoding = 'utf-8'
            # Cambio aquí: usa html.parser en lugar de lxml
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if 'streamtape' in href or 'yourupload' in href:
                    links.append({
                        'url': href,
                        'source': 'pelisplushd',
                        'title': link.get_text().strip()[:50]
                    })
            
            return links[:5]
        except Exception as e:
            print(f"Error scrapeando pelisplushd: {e}")
            return []
    
    def scrape_pelicinehd(self, query):
        """Scrappear pelicinehd.com"""
        links = []
        try:
            search_url = f"https://pelicinehd.com/?s={query}"
            response = requests.get(search_url, headers=self.headers, timeout=self.timeout)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if 'streamtape' in href or 'yourupload' in href:
                    links.append({
                        'url': href,
                        'source': 'pelicinehd',
                        'title': link.get_text().strip()[:50]
                    })
            
            return links[:5]
        except Exception as e:
            print(f"Error scrapeando pelicinehd: {e}")
            return []
    
    def scrape_cuevana(self, query):
        """Scrappear cuevana.is"""
        links = []
        try:
            search_url = f"https://www.cuevana.is/?s={query}"
            response = requests.get(search_url, headers=self.headers, timeout=self.timeout)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if 'streamtape' in href or 'yourupload' in href or 'mega' in href:
                    links.append({
                        'url': href,
                        'source': 'cuevana',
                        'title': link.get_text().strip()[:50]
                    })
            
            return links[:5]
        except Exception as e:
            print(f"Error scrapeando cuevana: {e}")
            return []
    
    def get_all_sources(self, query):
        """Scrappear de todas las fuentes"""
        all_links = []
        
        all_links.extend(self.scrape_pelisplushd(query))
        all_links.extend(self.scrape_pelicinehd(query))
        all_links.extend(self.scrape_cuevana(query))
        
        unique_links = []
        seen_urls = set()
        for link in all_links:
            if link['url'] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link['url'])
        
        return unique_links
    
    def validate_link(self, url):
        """Validar si un link sigue siendo válido"""
        try:
            response = requests.head(url, headers=self.headers, timeout=5, allow_redirects=True)
            return response.status_code < 400
        except:
            return False

scraper_service = ScraperService()
