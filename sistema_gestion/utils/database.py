"""
Configuración de base de datos - Versión simplificada
Soporte solo para Supabase
"""

import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import datetime

# Inicialización de extensiones
db = SQLAlchemy()
login_manager = LoginManager()

def init_extensions(app):
    """Inicializar todas las extensiones de la aplicación"""
    # Ya no inicializamos SQLAlchemy porque usamos Supabase
    login_manager.init_app(app)
    
    # Configurar LoginManager
    login_manager.login_view = 'login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario para Flask-Login desde Supabase"""
    try:
        from utils.supabase_db import db_manager
        user = db_manager.get_user_by_id(int(user_id))
        if user:
            # Crear objeto compatible con Flask-Login
            class UserWrapper:
                def __init__(self, user_data):
                    self.id = user_data.get('id')
                    self.username = user_data.get('username')
                    self.email = user_data.get('email')
                    self.nombre = user_data.get('nombre')
                    self.apellido = user_data.get('apellido')
                    self.rol = user_data.get('rol')
                    self.activo = user_data.get('activo', True)
                    self.ultimo_login = user_data.get('ultimo_login')
                
                def is_active(self):
                    return self.activo
                
                def is_authenticated(self):
                    return True
                
                def is_anonymous(self):
                    return False
                
                def get_id(self):
                    return str(self.id)
                
                def is_admin(self):
                    return self.rol == 'admin'
            
            return UserWrapper(user)
        return None
    except:
        return None

class BaseModel:
    """Modelo base - Ya no se usa con Supabase"""
    __abstract__ = True
    
    pass