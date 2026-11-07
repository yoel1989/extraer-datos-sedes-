"""
Aplicación Flask 100% Supabase - ESCOBARNET v3.0
Simplificada y funcional
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

@app.route('/')
@login_required
def dashboard():
    """Dashboard principal"""
    
    # Estadísticas básicas
    try:
        # Obtener usuarios
        users_result = supabase.table('users').select('count').execute()
        total_users = len(users_result.data) if users_result.data else 0
        
        # Obtener transacciones
        trans_result = supabase.table('transacciones').select('*').execute()
        total_transacciones = len(trans_result.data) if trans_result.data else 0
        
        # Obtener extracciones
        extr_result = supabase.table('extractions').select('*').execute()
        total_extracciones = len(extr_result.data) if extr_result.data else 0
        
        stats = {
            'total_users': total_users,
            'total_transacciones': total_transacciones,
            'total_extracciones': total_extracciones,
            'modulos_activos': 5,
            'usuario': current_user.nombre if current_user.is_authenticated else 'Invitado'
        }
    except Exception as e:
        print(f"Error obteniendo estadísticas: {e}")
        stats = {
            'total_users': 0,
            'total_transacciones': 0,
            'total_extracciones': 0,
            'modulos_activos': 5,
            'usuario': current_user.nombre if current_user.is_authenticated else 'Invitado'
        }
    
    # Lista de módulos
    modulos = [
        {
            'nombre': 'Extracción de Datos',
            'icono': 'fas fa-database',
            'url': '/extraccion',
            'descripcion': 'Extraer datos de Telegram y generar reportes',
            'color': 'primary'
        },
        {
            'nombre': 'Contabilidad',
            'icono': 'fas fa-dollar-sign',
            'url': '/contabilidad',
            'descripcion': 'Gestión financiera y facturación',
            'color': 'success'
        },
        {
            'nombre': 'Televisión',
            'icono': 'fas fa-tv',
            'url': '/television',
            'descripcion': 'Gestión de contenido TV y streaming',
            'color': 'info'
        },
        {
            'nombre': 'Sedes',
            'icono': 'fas fa-home',
            'url': '/sedes',
            'descripcion': 'Gestión de sedes instaladas',
            'color': 'warning'
        },
        {
            'nombre': 'Portales Cautivos',
            'icono': 'fas fa-wifi',
            'url': '/portales',
            'descripcion': 'Gestión de portales WiFi',
            'color': 'secondary'
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
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        try:
            # Buscar usuario en Supabase
            result = supabase.table('users').select('*').eq('username', username).execute()
            
            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                
                # Verificar contraseña
                if user_data.get('activo', True) and check_password_hash(user_data['password_hash'], password):
                    user = User(user_data)
                    login_user(user, remember=remember)
                    
                    # Actualizar último login
                    supabase.table('users').update({'ultimo_login': datetime.now().isoformat()}).eq('id', user_data['id']).execute()
                    
                    next_page = request.args.get('next')
                    return redirect(next_page) if next_page else redirect(url_for('dashboard'))
                else:
                    flash('Contraseña incorrecta', 'danger')
            else:
                flash('Usuario no encontrado', 'danger')
                
        except Exception as e:
            print(f"Error en login: {e}")
            flash('Error en el sistema de autenticación', 'danger')
    
    return render_template('login.html', title='Iniciar Sesión')

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
        # Obtener extracciones
        result = supabase.table('extractions').select('*').execute()
        extracciones = result.data if result.data else []
        
        return render_template('extraccion.html', 
                            extracciones=extracciones,
                            title='Extracción de Datos')
    except Exception as e:
        flash(f'Error en extracción: {e}', 'danger')
        return render_template('extraccion.html', 
                            extracciones=[],
                            title='Extracción de Datos')

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
    """Crear usuario admin si no existe"""
    try:
        result = supabase.table('users').select('*').eq('username', 'admin').execute()
        
        if not result.data:
            admin_data = {
                'username': 'admin',
                'email': 'admin@escobarnet.com',
                'password_hash': generate_password_hash('admin123'),
                'nombre': 'Administrador',
                'apellido': 'Sistema',
                'rol': 'admin',
                'activo': True
            }
            
            result = supabase.table('users').insert(admin_data).execute()
            if result.data:
                print("✅ Usuario admin creado: admin/admin123")
            else:
                print("❌ Error creando usuario admin")
        else:
            print("✅ Usuario admin ya existe")
            
    except Exception as e:
        print(f"❌ Error creando usuario admin: {e}")

if __name__ == '__main__':
    print("🚀 SISTEMA ESCOBARNET 100% SUPABASE")
    print("=" * 50)
    
    # Crear usuario admin
    create_admin_user()
    
    print("✅ Iniciando aplicación en http://localhost:5002")
    print("🔐 Usuario: admin")
    print("🔑 Contraseña: admin123")
    print("=" * 50)
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5002
    )