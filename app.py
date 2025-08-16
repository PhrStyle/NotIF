import flask
from dotenv import load_dotenv
from flask import Flask, send_from_directory
import os
import json

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

app.register_blueprint(screens_bp)

# Rota para servir arquivos estáticos da pasta files
@app.route('/static/files/<filename>')
def uploaded_file(filename):
    return send_from_directory('/home/phrstyle/dev/NotIF/static/files', filename)

if __name__ == '__main__':
    app.run(debug=True)