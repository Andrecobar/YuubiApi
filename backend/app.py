# app.py - Archivo principal de la API
from flask import Flask, jsonify
from flask_cors import CORS
from routes.movies import movies_bp
import os

app = Flask(__name__)

# Configurar CORS para permitir peticiones desde React Native
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Registrar blueprints
app.register_blueprint(movies_bp)

# Ruta raíz
@app.route('/')
def index():
    return jsonify({
        'name': 'Yuubi API',
        'version': '1.0.0',
        'description': 'API para streaming de películas y series',
        'endpoints': {
            'home': '/api/home',
            'search': '/api/search?q=query',
            'details': '/api/details/<tmdb_id>?type=movie|tv',
            'movie_links': '/api/links/<tmdb_id>?auto_scrape=true',
            'series_season': '/api/series/<tmdb_id>/season/<season>',
            'series_links': '/api/series/<tmdb_id>/links?season=1&episode=1',
            'stats': '/api/stats',
            'request': '/api/request'
        },
        'status': 'online',
        'docs': 'https://github.com/tu-usuario/yuubi-api'
    })

# Ruta de health check (para Render)
@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

# Solo para desarrollo local
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)