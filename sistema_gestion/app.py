"""
Sistema Integrado de Gestión
Aplicación principal con múltiples módulos
"""

import os
import time
from flask import Flask, render_template, redirect, url_for, session, flash
from flask_login import current_user, login_required, logout_user
from config import config
from utils.database import init_extensions, db
# from utils.auth import User, Permisos  # Comentado - ahora usa Supabase

# Configurar zona horaria para Colombia
os.environ['TZ'] = 'America/Bogota'
if hasattr(time, 'tzset'):
    time.tzset()

# Forzar uso de hora local
import locale
try:
    locale.setlocale(locale.LC_TIME, 'es_CO.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Colombia.1252')
    except:
        pass  # Usar configuración por defecto

# Importar módulos
from modules.extraccion_datos.main import extraccion_bp
from modules.contabilidad.main import contabilidad_bp
from modules.television.main import television_bp
from modules.sedes.main import sedes_bp
from modules.portales_cautivos.main import portales_bp

def create_app(config_name='default'):
    """Función factory para crear la aplicación Flask"""
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    init_extensions(app)
    config[config_name].init_app(app)
    
    # Registrar Blueprints de módulos
    app.register_blueprint(extraccion_bp)
    app.register_blueprint(contabilidad_bp)
    app.register_blueprint(television_bp)
    app.register_blueprint(sedes_bp)
    app.register_blueprint(portales_bp)
    
    # Rutas principales
    @app.route('/')
    @login_required
    def dashboard():
        """Dashboard principal"""
        # Estadísticas básicas (se expandirá)
        stats = {
            'total_modulos': 5,
            'modulos_activos': 5,
            'usuario': current_user.nombre if current_user.is_authenticated else 'Invitado'
        }
        
        # Lista de módulos con permisos
        modulos = [
            {
                'nombre': 'Extracción de Datos',
                'icono': 'fas fa-database',
                'url': '/extraccion',
                'descripcion': 'Extraer datos de Telegram y generar reportes',
                'color': 'primary',
                # 'permiso': Permisos.puede_acceder(current_user, 'extraccion_datos')  # Comentado - simplificado
            },
            {
                'nombre': 'Contabilidad',
                'icono': 'fas fa-dollar-sign',
                'url': '/contabilidad',
                'descripcion': 'Gestión financiera y facturación',
                'color': 'success',
                # 'permiso': Permisos.puede_acceder(current_user, 'contabilidad')  # Comentado - simplificado
            },
            {
                'nombre': 'Televisión',
                'icono': 'fas fa-tv',
                'url': '/television',
                'descripcion': 'Gestión de contenido TV y streaming',
                'color': 'info',
                # 'permiso': Permisos.puede_acceder(current_user, 'television')  # Comentado - simplificado
            },
            {
                'nombre': 'Sedes Instaladas',
                'icono': 'fas fa-building',
                'url': '/sedes',
                'descripcion': 'Gestión de ubicaciones y contacto',
                'color': 'warning',
                # 'permiso': Permisos.puede_acceder(current_user, 'sedes')  # Comentado - simplificado
            },
            {
                'nombre': 'Portales Cautivos',
                'icono': 'fas fa-wifi',
                'url': '/portales',
                'descripcion': 'Gestión de portales WiFi',
                'color': 'secondary',
                # 'permiso': Permisos.puede_acceder(current_user, 'portales_cautivos')  # Comentado - simplificado
            }
        ]
        
        return render_template('dashboard.html', 
                           modulos=modulos, 
                           stats=stats,
                           title='Dashboard')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Página de login"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        from flask import request
        from flask_login import login_user
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            remember = request.form.get('remember') == 'on'
            
            try:
                # Intentar obtener usuario desde Supabase
                from utils.supabase_db import db_manager
                user_data = db_manager.get_user_by_username(username)
                
                if user_data:
                    # Crear objeto User compatible para validación
                    class SupabaseUser:
                        def __init__(self, data):
                            self.username = data.get('username')
                            self.email = data.get('email')
                            self.nombre = data.get('nombre')
                            self.apellido = data.get('apellido')
                            self.rol = data.get('rol')
                            self.activo = data.get('activo', True)
                            self.ultimo_login = data.get('ultimo_login')
                            self.password_hash = data.get('password_hash', '')  # Solo para validación
                        
                        def is_active(self):
                            return self.activo
                        
                        def is_authenticated(self):
                            return True
                        
                        def is_anonymous(self):
                            return False
                        
                        def get_id(self):
                            return str(self.__dict__.get('id', user_data.get('id', 0)))
                        
                        def is_admin(self):
                            return self.rol == 'admin'
                        
                        def check_password(self, password):
                            # Validar contraseña - admin123 es la temporal
                            from werkzeug.security import check_password_hash
                            return check_password_hash(self.password_hash, password)
                    
                    user = SupabaseUser(user_data)
                    
                    if user.check_password(password):
                        login_user(user, remember=remember)
                        next_page = request.args.get('next')
                        return redirect(next_page) if next_page else redirect(url_for('dashboard'))
                    else:
                        flash('Usuario o contraseña incorrectos', 'danger')
                else:
                    flash('Usuario o contraseña incorrectos', 'danger')
                    
            except Exception as e:
                print(f"Error en login: {e}")
                flash('Error en el sistema de autenticación', 'danger')
        
        return render_template('login.html', title='Iniciar Sesión')
    
    @app.route('/logout')
    @login_required
    def logout():
        """Cerrar sesión"""
        logout_user()
        flash('Has cerrado sesión correctamente', 'info')
        return redirect(url_for('login'))
    
    @app.route('/profile')
    @login_required
    def profile():
        """Perfil de usuario"""
        return render_template('profile.html', title='Mi Perfil')
    
    # API para verificar estado de módulos
    @app.route('/api/modulos/status')
    @login_required
    def modulos_status():
        """API para verificar estado de todos los módulos"""
        modulos_info = []
        
        # Obtener estado de cada módulo
        try:
            from modules.extraccion_datos.main import extraccion_bp
            modulos_info.append({
                'nombre': 'Extracción de Datos',
                'estado': 'Activo',
                'url': '/extraccion/status'
            })
        except:
            modulos_info.append({
                'nombre': 'Extracción de Datos',
                'estado': 'Error',
                'url': None
            })
        
        # Agregar otros módulos (simulado por ahora)
        for nombre in ['Contabilidad', 'Televisión', 'Sedes', 'Portales Cautivos']:
            modulos_info.append({
                'nombre': nombre,
                'estado': 'En desarrollo',
                'url': None
            })
        
        return {'modulos': modulos_info}
    
    # Crear usuario admin en Supabase si no existe
    with app.app_context():
        try:
            from utils.supabase_db import db_manager
            from werkzeug.security import generate_password_hash
            
            # Verificar si ya existe el admin
            admin_user = db_manager.get_user_by_username('admin')
            if not admin_user:
                admin_data = {
                    'username': 'admin',
                    'email': 'admin@escobarnet.com',
                    'password_hash': generate_password_hash('admin123'),  # Contraseña por defecto
                    'nombre': 'Administrador',
                    'apellido': 'Sistema',
                    'rol': 'admin',
                    'activo': True
                }
                
                result = db_manager.create_user(admin_data)
                if result:
                    print("Usuario admin creado en Supabase: admin")
                else:
                    print("Error creando usuario admin en Supabase")
            else:
                print("Usuario admin ya existe en Supabase")
                
        except Exception as e:
            print(f"Error configurando usuario admin: {e}")
            print("El sistema continuará funcionando, pero debes crear el usuario manualmente")
    
    return app

# Crear instancia de la aplicación
app = create_app(os.getenv('FLASK_CONFIG', 'development'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)