import requests
from datetime import datetime, timedelta

def validate_url(url):
    """Validar si una URL es accesible"""
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code < 400
    except:
        return False

def is_link_expired(checked_at, days=7):
    """Verificar si un link debe ser re-verificado"""
    if not checked_at:
        return True
    
    last_check = datetime.fromisoformat(checked_at)
    return datetime.now() - last_check > timedelta(days=days)

def clean_html(text):
    """Limpiar texto HTML"""
    if not text:
        return ""
    text = text.replace('<p>', '').replace('</p>', '')
    text = text.replace('<br>', ' ').replace('<br/>', ' ')
    text = text.replace('&nbsp;', ' ')
    return text.strip()

def parse_duration(minutes):
    """Convertir minutos a formato legible"""
    if not minutes:
        return "N/A"
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}h {mins}m"
    return f"{mins}m"
