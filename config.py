import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    FIREBASE_KEY_PATH = os.getenv("FIREBASE_KEY_PATH", os.path.join(basedir, 'serviceAccountKey.json'))
    APP_NAME = os.getenv("APP_NAME", "Haven")
    APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:5000")
    MAIL_ENABLED = os.getenv("MAIL_ENABLED", "false").lower() in {"1", "true", "yes", "on"}
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_REPLY_TO = os.getenv("MAIL_REPLY_TO")
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
