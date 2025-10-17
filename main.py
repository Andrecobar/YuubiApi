from api_novelas import app
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Servidor iniciado en http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
from api_novelas import app
import os
import sys

if __name__ == '__main__':
    # Obtener puerto de la variable de entorno o usar 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Deshabilitar el reloader para evitar conflictos
    use_reloader = '--no-reload' not in sys.argv
    
    print(f"🚀 Servidor iniciado en http://localhost:{port}")
    print(f"🌐 Accede desde: http://127.0.0.1:{port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        use_reloader=False  # Deshabilita el auto-reload
    )