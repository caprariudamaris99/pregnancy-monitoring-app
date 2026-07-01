from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from config import config
import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_name=None):
    """Factory pentru crearea aplicației Flask."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inițializare extensii
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Vă rugăm să vă autentificați.'
    
    # Creare directoare
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Înregistrare modele
    from app.models import appointment, doctor, document, medication, message, patient, pregnancy, symptom, user
    
    # Înregistrare blueprint-uri
    from app.routes import auth, patient_routes, doctor_routes, common
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(patient_routes.bp)
    app.register_blueprint(doctor_routes.bp)
    app.register_blueprint(common.bp)
    
    # User loader pentru Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_notifications():
        from flask_login import current_user
        from app.models.message import Notification
        if current_user.is_authenticated:
            unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
            recent = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()
            return {'unread_notifications_count': unread, 'recent_notifications': recent}
        return {'unread_notifications_count': 0, 'recent_notifications': []}
    
    # Crear tabele în context aplicației
    with app.app_context():
        db.create_all()
    
    return app
