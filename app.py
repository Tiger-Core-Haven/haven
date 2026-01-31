from dotenv import load_dotenv
load_dotenv()

import os
from app import create_app
from config import DevelopmentConfig, ProductionConfig

env = os.getenv("FLASK_ENV", "development").lower()
config = ProductionConfig if env == "production" else DevelopmentConfig

app = create_app(config)

if __name__ == "__main__":
    app.run()
