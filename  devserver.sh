cat > devserver.sh << 'EOF'
#!/bin/bash
source .venv/bin/activate
export FLASK_APP=main.py
export FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=${PORT:-5000}
EOF