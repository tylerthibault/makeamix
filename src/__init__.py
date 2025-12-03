from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


# Create global db instance
db = SQLAlchemy()
bcrypt = Bcrypt()

# create app
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'cd1e5049c9b4160cdf5a7d08'

    # init db
    init_db(app)

    # init blueprints
    init_blueprints(app)

    # error handlers
    error_handlers(app)

    return app
    
    

# init db
def init_db(app):
    """
        initialize the sql alchemy sqlite database. Will create all the tables in the model files. 
    """
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///makeamix.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        from src.models.user import User
        from src.models.logbook import Logbook
        from src.models.song import Song
        from src.models.playlist import Playlist
        db.create_all()



# init blueprints
def init_blueprints(app):
    """
        initialize all blueprints for the application. 
    """

    from src.controllers.routes import main_bp
    app.register_blueprint(main_bp)

    from src.controllers.auth import auth_bp
    app.register_blueprint(auth_bp)

    from src.controllers.user import user_bp
    app.register_blueprint(user_bp)

    from src.controllers.song import song_bp
    app.register_blueprint(song_bp)

    from src.controllers.playlist import playlist_bp
    app.register_blueprint(playlist_bp)


def error_handlers(app):
    # Register 404 error handler
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500