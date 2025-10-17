# Configuración de TMDB
import os
from dotenv import load_dotenv

load_dotenv()  # Cargar variables de .env

TMDB_API_KEY = os.getenv("bf499bf4324b5c99b7ec4b36dea364eb")  # ← Reemplaza esto con tu API key real
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Variables para Render
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///novelas.db')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = os.getenv('DEBUG', 'False') == 'True'