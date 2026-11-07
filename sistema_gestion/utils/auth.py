from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from utils.database import db

class User(UserMixin, db.Model):
    """Modelo de usuario para autenticación"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    rol = db.Column(db.String(20), default='usuario')  # admin, usuario
    activo = db.Column(db.Boolean, default=True)
    ultimo_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Establecer contraseña encriptada"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Verificar si es administrador"""
        return self.rol == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'

class Permisos:
    """Clase para gestionar permisos"""
    MODULOS = {
        'dashboard': 'Dashboard',
        'extraccion_datos': 'Extracción de Datos',
        'contabilidad': 'Contabilidad',
        'television': 'Televisión',
        'sedes': 'Sedes Instaladas',
        'portales_cautivos': 'Portales Cautivos'
    }
    
    ACCIONES = {
        'ver': 'Ver',
        'crear': 'Crear',
        'editar': 'Editar',
        'eliminar': 'Eliminar',
        'exportar': 'Exportar'
    }
    
    @staticmethod
    def puede_acceder(user, modulo, accion='ver'):
        """Verificar si un usuario puede acceder a un módulo/acción"""
        if user.is_admin():
            return True
        
        # Lógica de permisos por rol (se puede expandir)
        permisos_por_rol = {
            'usuario': [
                'dashboard.ver',
                'extraccion_datos.ver',
                'extraccion_datos.exportar'
            ]
        }
        
        permiso_requerido = f"{modulo}.{accion}"
        return permiso_requerido in permisos_por_rol.get(user.rol, [])