import os
from datetime import timedelta
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# Configurar zona horaria para Colombia
import os
os.environ['TZ'] = 'America/Bogota'

class Config:
    """Configuración base de la aplicación - Solo Supabase"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu-clave-secreta-aqui-cambiar-en-produccion'
    
    # Configuración de Supabase (OBLIGATORIA)
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    
    # SQLite eliminado - ahora solo Supabase
    SQLALCHEMY_DATABASE_URI = None  # Ya no se usa
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Verificación obligatoria de Supabase
    @staticmethod
    def validate_supabase():
        if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_ANON_KEY'):
            raise ValueError("ERROR: Las variables SUPABASE_URL y SUPABASE_ANON_KEY son obligatorias")
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Configuración de uploads
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Configuración Telegram (para módulo de extracción)
    TELEGRAM_API_ID = int(os.getenv('TELEGRAM_API_ID', '0'))
    TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH', '')
    TELEGRAM_PHONE = os.getenv('TELEGRAM_PHONE', '')
    
    # Configuración de reportes
    REPORTS_FOLDER = 'static/reports'
    
    @staticmethod
    def init_app(app):
        """Inicialización de la aplicación"""
        # Crear directorios necesarios
        os.makedirs(os.path.join(app.root_path, Config.UPLOAD_FOLDER), exist_ok=True)
        os.makedirs(os.path.join(app.root_path, Config.REPORTS_FOLDER), exist_ok=True)

class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestingConfig(Config):
    """Configuración de pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}