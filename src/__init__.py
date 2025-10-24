from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import os

db = SQLAlchemy()

def create_app(config=None):
    app = Flask(__name__)
    
    try:
        # Configure the app
        if config:
            app.config.update(config)
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
            
            # File upload configuration
            app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads', 'songs')
            app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
        
        # Initialize extensions
        init_db(app)
        init_blueprint(app)
        init_logger(app)
        
        return app
    except Exception as e:
        print(f"Error creating Flask app: {e}")
        import traceback
        traceback.print_exc()
        raise

def init_db(app):
    """Initialize SQLAlchemy with the Flask app"""
    try:
        db.init_app(app)
        
        with app.app_context():
            # Import all models so SQLAlchemy knows about them
            from src.models import User, Role, Mix, Song, MixLike, PlayHistory
            db.create_all()
            print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        raise

def init_blueprint(app):
    """Initialize and register blueprints"""
    try:
        # Import and register your blueprints here
        from src.controllers.routes import main_bp
        app.register_blueprint(main_bp)

        from src.controllers.user_controller import user_bp
        app.register_blueprint(user_bp, url_prefix='/user')
        
        from src.controllers.music_controller import music_bp
        app.register_blueprint(music_bp)
        
        print("Blueprints registered successfully")
    except Exception as e:
        print(f"Error registering blueprints: {e}")
        import traceback
        traceback.print_exc()
        raise

def init_logger(app):
    """Initialize logging configuration"""
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Application startup')