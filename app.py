import os
from flask import Flask
from config import Config
from routes import app_routes
from models import db

def create_app():
    app = Flask(__name__)

    # ✅ Load config directly from Config class
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(app_routes)
    
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)