import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')
    TMDB_BASE_URL = "https://api.themoviedb.org/3"
    TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'content.db')
    
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    SCRAPER_TIMEOUT = 10
    SCRAPER_RETRY_DAYS = 7
    
    LANGUAGE = 'es-ES'
    REGION = 'ES'

config = Config()
