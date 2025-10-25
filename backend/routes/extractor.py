from flask import Blueprint, request, jsonify
from services.link_extractor import link_extractor

extractor_bp = Blueprint('extractor', __name__)

@extractor_bp.route('/link-extractor', methods=['POST'])
def extract_links():
    """
    Extrae links de video de una URL
    
    Body:
    {
        "url": "https://pelisplushd.to/pelicula/inception",
        "listen_url": "https://firestore.googleapis.com/..."  // Solo para zonahack
    }
    """
    data = request.get_json()
    
    url = data.get('url')
    listen_url = data.get('listen_url')
    
    if not url:
        return jsonify({'error': 'URL requerida'}), 400
    
    # Extraer links
    result = link_extractor.extract(url, listen_url)
    
    return jsonify(result)

@extractor_bp.route('/link-extractor', methods=['GET'])
def extract_links_get():
    """Versión GET del extractor"""
    url = request.args.get('url')
    listen_url = request.args.get('listen_url')
    
    if not url:
        return jsonify({'error': 'URL requerida'}), 400
    
    result = link_extractor.extract(url, listen_url)
    
    return jsonify(result)
