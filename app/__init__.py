from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Register blueprints
    from app.routes.upload import upload_bp
    from app.routes.analysis import analysis_bp
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(analysis_bp, url_prefix='/api')

    return app
