# app/__init__.py
from flask import Flask
from app.extensions import db
import app.extensions as extensions
import firebase_admin
from firebase_admin import credentials, firestore

def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or 'config.Config')

    if not firebase_admin._apps:
        cred = credentials.Certificate(app.config['FIREBASE_KEY_PATH'])
        firebase_admin.initialize_app(cred)
    
    extensions.db = firestore.client()


    from app.auth.routes import auth_bp 
    from app.core.routes import core_bp
    from app.ai.routes import ai_bp

    app.register_blueprint(core_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(ai_bp, url_prefix="/api/chat")

    return app