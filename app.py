import flask
from dotenv import load_dotenv
from flask import Flask, send_from_directory
import os
import json
import re

from blueprints.screens_bp import screens_bp
from db_init import init_db

load_dotenv()

SQLALCHEMY_TRACK_MODIFICATIONS = False

init_db()

app = Flask(__name__)

# Registrar filtro personalizado para JSON
@app.template_filter('tojsonfilter')
def to_json_filter(obj):
    return json.dumps(obj)

# Filtro para extrair ID do YouTube
@app.template_filter('extract_youtube_id')
def extract_youtube_id(url):
    """
    Extrai o ID do vídeo/playlist do YouTube de uma URL
    Suporta formatos como:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID
    """
    if not url:
        return ''
    
    # Padrões para capturar o ID do vídeo
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'v=([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return ''

app.register_blueprint(screens_bp)

# Rota para servir arquivos estáticos da pasta files
@app.route('/static/files/<filename>')
def uploaded_file(filename):
    return send_from_directory('/home/phrstyle/dev/NotIF/static/files', filename)

if __name__ == '__main__':
    app.run(debug=True)