# main.py
from api_novelas import app
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"🚀 Servidor iniciado")
    print(f"📡 Puerto: {port}")
    print(f"🔧 Debug: {debug_mode}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )