import os
import sys

# Asegurar que estamos en el directorio backend
backend_path = os.path.dirname(os.path.abspath(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from database import init_db, get_db_path
from routes import movies_bp, series_bp, admin_bp

app = Flask(__name__)
CORS(app)

app.config['JSON_SORT_KEYS'] = False

# Inicializar BD
init_db()

# Registrar blueprints
app.register_blueprint(movies_bp, url_prefix='/api')
app.register_blueprint(series_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        'message': 'Netflix Personal API',
        'version': '1.0.0',
        'status': 'running',
        'database': get_db_path(),
        'endpoints': {
            'movies': '/api/movies',
            'series': '/api/series',
            'search': '/api/search?q=title',
            'trending': '/api/trending',
            'admin': '/api/admin/*'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=config.DEBUG)
