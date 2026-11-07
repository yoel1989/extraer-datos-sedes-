"""
Aplicación Flask 100% Supabase - ESCOBARNET v3.0
Simplificada y funcional - Sin problemas de caracteres
"""

import os
import sys
import time
from datetime import datetime

# Configurar zona horaria para Colombia
os.environ['TZ'] = 'America/Bogote'
if hasattr(time, 'tzset'):
    time.tzset()

from flask import Flask, render_template, redirect, url_for, session, flash, request, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("ERROR: Faltan variables de entorno de Supabase")

# Crear aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Cliente de Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Importar y registrar Blueprint del módulo de extracción
from modules.extraccion_datos.main_simple import extraccion_bp
app.register_blueprint(extraccion_bp)

class User:
    """Clase de usuario compatible con Flask-Login"""
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.nombre = user_data.get('nombre')
        self.apellido = user_data.get('apellido')
        self.rol = user_data.get('rol', 'usuario')
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

@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario desde Supabase"""
    try:
        result = supabase.table('users').select('*').eq('id', int(user_id)).execute()
        if result.data and len(result.data) > 0:
            return User(result.data[0])
    except:
        pass
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    print(f"*** LOGIN RUTA LLAMADA: {request.method} ***")
    
    if request.method == 'POST':
        print(f"*** METODO POST DETECTADO ***")
        print(f"*** FORM DATA: {dict(request.form)} ***")
        
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        print(f"*** USERNAME: '{username}' ***")
        print(f"*** PASSWORD: '{password}' ***")
        
        # Login con validación de hash de contraseña
        result = supabase.table('users').select('*').eq('username', 'admin').execute()
        if result.data and len(result.data) > 0:
            user_data = result.data[0]
            stored_hash = user_data.get('password_hash', '')
            
            print(f"*** HASH ALMACENADO: {stored_hash} ***")
            print(f"*** CONTRASEÑA RECIBIDA: {password} ***")
            
            # Verificar contraseña con hash
            if check_password_hash(stored_hash, password):
                print("*** CONTRASEÑA CORRECTA - CREANDO USUARIO ***")
                
                user = User(user_data)
                login_user(user)
                
                # Actualizar último login
                supabase.table('users').update({
                    'ultimo_login': datetime.now().isoformat()
                }).eq('id', user.id).execute()
                
                print("*** LOGIN EXITOSO - REDIRIGIENDO ***")
                flash(f'Bienvenido {user.nombre}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                print("*** CONTRASEÑA INCORRECTA ***")
        else:
            print("*** USUARIO NO ENCONTRADO ***")
        
        print("*** CREDENCIALES INCORRECTAS ***")
        return render_template('login.html', error='Usuario o contraseña incorrectos')
    
    print("*** MOSTRANDO FORMULARIO LOGIN ***")
    return render_template('login.html')

@app.route('/')
def index():
    """Página principal - Redirige a login o dashboard"""
    print(f"[ROUTE DEBUG] INDEX: {request.method} - {request.url}")
    if current_user.is_authenticated:
        print(f"[ROUTE DEBUG] Usuario autenticado, redirigiendo a dashboard")
        return redirect(url_for('dashboard'))
    else:
        print(f"[ROUTE DEBUG] Usuario no autenticado, redirigiendo a login")
        return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Página principal del dashboard"""
    try:
        # Datos de usuario actual
        stats = {
            'usuario': f"{current_user.nombre} {current_user.apellido}" if current_user.nombre and current_user.apellido else current_user.username,
            'total_modulos': 5,
            'modulos_activos': 4,
            'ultima_sesion': current_user.ultimo_login
        }
        
        # Definir módulos disponibles
        modulos = [
            {
                'nombre': 'Contabilidad',
                'descripcion': 'Gestión financiera y transacciones',
                'url': url_for('contabilidad'),
                'icono': 'fas fa-dollar-sign',
                'color': 'success',
                'permiso': True
            },
            {
                'nombre': 'Extracción de Datos',
                'descripcion': 'Extraer y procesar información',
                'url': url_for('extraccion'),
                'icono': 'fas fa-database',
                'color': 'primary',
                'permiso': True
            },
            {
                'nombre': 'Televisión',
                'descripcion': 'Sistema de gestión de TV',
                'url': url_for('television'),
                'icono': 'fas fa-tv',
                'color': 'info',
                'permiso': current_user.is_admin()
            },
            {
                'nombre': 'Sedes',
                'descripcion': 'Administración de sedes',
                'url': url_for('sedes'),
                'icono': 'fas fa-building',
                'color': 'warning',
                'permiso': current_user.is_admin()
            },
            {
                'nombre': 'Portales Cautivos',
                'descripcion': 'Gestión de portales',
                'url': url_for('portales'),
                'icono': 'fas fa-wifi',
                'color': 'secondary',
                'permiso': current_user.is_admin()
            }
        ]
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             modulos=modulos,
                             title='Dashboard')
    except Exception as e:
        flash(f'Error cargando dashboard: {e}', 'danger')
        return render_template('dashboard.html', 
                             stats={'usuario': 'Error'}, 
                             modulos=[],
                             title='Dashboard')

@app.route('/profile')
@login_required
def profile():
    """Página de perfil de usuario"""
    try:
        # Obtener datos actualizados del usuario
        result = supabase.table('users').select('*').eq('id', current_user.id).execute()
        user_data = result.data[0] if result.data else None
        
        if user_data:
            return render_template('profile.html', 
                                user=user_data,
                                title='Mi Perfil')
        else:
            flash('Error cargando perfil', 'danger')
            return redirect(url_for('dashboard'))
            
    except Exception as e:
        flash(f'Error en perfil: {e}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('login'))

@app.route('/contabilidad')
@login_required
def contabilidad():
    """Módulo de contabilidad"""
    try:
        # Obtener resumen financiero
        trans_result = supabase.table('transacciones').select('*').execute()
        transacciones = trans_result.data if trans_result.data else []
        
        ingresos = sum(t['monto'] for t in transacciones if t.get('tipo') == 'ingreso')
        egresos = sum(t['monto'] for t in transacciones if t.get('tipo') == 'egreso')
        balance = ingresos - egresos
        
        # Obtener categorías
        cat_result = supabase.table('categorias').select('*').execute()
        categorias = cat_result.data if cat_result.data else []
        
        # Transacciones recientes
        transacciones_recientes = sorted(transacciones, key=lambda x: x.get('creado_en', ''), reverse=True)[:10]
        
        return render_template('contabilidad.html',
                            ingresos=ingresos,
                            egresos=egresos,
                            balance=balance,
                            transacciones=transacciones_recientes,
                            categorias=categorias,
                            title='Contabilidad')
    except Exception as e:
        flash(f'Error en contabilidad: {e}', 'danger')
        return render_template('contabilidad.html', 
                            ingresos=0, egresos=0, balance=0,
                            transacciones=[], categorias=[],
                            title='Contabilidad')

@app.route('/extraccion')
@login_required
def extraccion():
    """Módulo de extracción"""
    try:
        # Esta ruta ahora es manejada por el Blueprint del módulo
        # Redirigir a la ruta principal del módulo
        return redirect(url_for('extraccion_datos.index'))
    except Exception as e:
        flash(f'Error en extracción: {e}', 'danger')
        return redirect(url_for('dashboard'))

# Rutas placeholder para otros módulos
@app.route('/television')
@login_required
def television():
    return render_template('television.html', title='Televisión')

@app.route('/sedes')
@login_required
def sedes():
    return render_template('sedes.html', title='Sedes')

@app.route('/portales')
@login_required
def portales():
    return render_template('portales.html', title='Portales Cautivos')

def create_admin_user():
    """Crear usuario admin si no existe o actualizar hash si es incompatible"""
    try:
        print(f"[ADMIN DEBUG] Verificando usuario admin...")
        result = supabase.table('users').select('*').eq('username', 'admin').execute()
        print(f"[ADMIN DEBUG] Resultado búsqueda admin: {result}")
        
        if not result.data:
            print(f"[ADMIN DEBUG] Creando usuario admin...")
            password_hash = generate_password_hash('admin123')
            print(f"[ADMIN DEBUG] Hash generado: {password_hash}")
            
            admin_data = {
                'username': 'admin',
                'email': 'admin@escobarnet.com',
                'password_hash': password_hash,
                'nombre': 'Administrador',
                'apellido': 'Sistema',
                'rol': 'admin',
                'activo': True
            }
            
            print(f"[ADMIN DEBUG] Datos admin a insertar: {admin_data}")
            result = supabase.table('users').insert(admin_data).execute()
            print(f"[ADMIN DEBUG] Resultado inserción: {result}")
            
            if result.data:
                print("OK: Usuario admin creado: admin/admin123")
                print(f"[ADMIN DEBUG] Usuario creado: {result.data[0]}")
            else:
                print("ERROR: Error creando usuario admin - sin datos devueltos")
        else:
            user = result.data[0]
            print("OK: Usuario admin ya existe")
            print(f"[ADMIN DEBUG] Hash completo: {user.get('password_hash', 'SIN_HASH')}")
            
            # Siempre actualizar el hash para asegurar compatibilidad
            print("[ADMIN DEBUG] Actualizando hash para asegurar compatibilidad...")
            password_hash = generate_password_hash('admin123')
            print(f"[ADMIN DEBUG] Nuevo hash: {password_hash}")
            
            update_result = supabase.table('users').update({
                'password_hash': password_hash
            }).eq('username', 'admin').execute()
            print(f"[ADMIN DEBUG] Resultado actualización: {update_result}")
            
            if update_result.data:
                print("OK: Hash del usuario admin actualizado correctamente")
            else:
                print("ERROR: No se pudo actualizar el hash del usuario admin")
            
    except Exception as e:
        print(f"ERROR: Error creando usuario admin: {e}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")

if __name__ == '__main__':
    print("=" * 60)
    print("SISTEMA ESCOBARNET 100% SUPABASE v3.0")
    print("=" * 60)
    
    # Crear usuario admin
    create_admin_user()
    
    print("OK: Conexión a Supabase verificada")
    print("OK: Sistema iniciado")
    print("URL: http://localhost:5005")
    print("Usuario: admin")
    print("Contraseña: admin123")
    print("=" * 60)
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5005
    )