# app/__init__.py
import os
from flask import Flask
from app.extensions import db
import app.extensions as extensions
import firebase_admin
from firebase_admin import credentials, firestore

def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class or 'config.Config')

    if not firebase_admin._apps:
        key_path = app.config.get('FIREBASE_KEY_PATH')
        if not key_path or not os.path.exists(key_path):
            raise FileNotFoundError(
                "Firebase service account key not found. "
                "Set FIREBASE_KEY_PATH to your JSON key file or place it at "
                f"{app.config.get('FIREBASE_KEY_PATH')}."
            )
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
    
    extensions.db = firestore.client()


    from app.auth.routes import auth_bp 
    from app.core.routes import core_bp
    from app.ai.routes import ai_bp

    app.register_blueprint(core_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(ai_bp, url_prefix="/api/chat")

    return app
