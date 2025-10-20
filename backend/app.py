import os
import sys

backend_path = os.path.dirname(os.path.abspath(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from flask import Flask, jsonify
from flask_cors import CORS
from config import config
from database import init_db

app = Flask(__name__)
CORS(app)
app.config['JSON_SORT_KEYS'] = False

# Inicializar BD
init_db()

# Cargar datos iniciales si BD está vacía
try:
    from init_data import init_with_data
    init_with_data()
except Exception as e:
    print(f"⚠️ Error cargando datos iniciales: {e}")

# Importar y registrar blueprints DESPUÉS de init_db
from routes import movies_bp, series_bp, admin_bp

app.register_blueprint(movies_bp, url_prefix='/api')
app.register_blueprint(series_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')

@app.route('/api/', methods=['GET'])
def index():
    return jsonify({'status': 'ok', 'message': 'API funcionando'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': str(error)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=config.DEBUG)
