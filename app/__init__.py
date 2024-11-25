from flask import Flask
from app.config import Config
from app.routes import main
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    
    cdn_path = os.path.join(app.root_path, 'cdn')
    if not os.path.exists(cdn_path):
        os.makedirs(cdn_path)
    app.register_blueprint(main)
    
    return app
