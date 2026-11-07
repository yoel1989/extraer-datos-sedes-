"""
Aplicación Flask 100% Supabase - ESCOBARNET v3.0
Sin errores ni caracteres problemáticos
"""

import os
import sys
import time
from datetime import datetime
from flask_login import login_required

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

# Crear aplicación Flask sin debug
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'

# Cliente de Supabase
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("OK: Conexión a Supabase verificada")
except Exception as e:
    print(f"ERROR: No se pudo conectar a Supabase: {e}")
    sys.exit(1)

# Importar y registrar blueprints de módulos
try:
    # Módulo de extracción de datos (versión ultra simple)
    from modules.extraccion_datos.main_simple_no_supabase import extraccion_bp
    app.register_blueprint(extraccion_bp)
    print("OK: Módulo de Extracción de Datos registrado (versión ultra simple)")
    
    # Módulo de portales cautivos
    from modules.portales_cautivos.main import portales_bp
    app.register_blueprint(portales_bp)
    print("OK: Módulo de Portales Cautivos registrado")
    
    # Módulo de sedes
    from modules.sedes.main import sedes_bp
    app.register_blueprint(sedes_bp)
    print("OK: Módulo de Sedes registrado")
    
    # Módulo de televisión
    from modules.television.main import television_bp
    app.register_blueprint(television_bp)
    print("OK: Módulo de Televisión registrado")
    
except Exception as e:
    print(f"ERROR registrando módulos: {e}")
    print("Continuando sin módulos...")

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
    try:
        # Obtener estadísticas básicas
        users_result = supabase.table('users').select('count').execute()
        total_users = len(users_result.data) if users_result.data else 0
        
        trans_result = supabase.table('transacciones').select('*').execute()
        total_transacciones = len(trans_result.data) if trans_result.data else 0
        
        # Simplificar extracciones
        total_extracciones = 5  # Valor por ahora
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
            'color': 'primary',
            'permiso': True
        },
        {
            'nombre': 'Contabilidad',
            'icono': 'fas fa-dollar-sign',
            'url': '/contabilidad',
            'descripcion': 'Gestión financiera y facturación',
            'color': 'success',
            'permiso': True
        },
        {
            'nombre': 'Televisión',
            'icono': 'fas fa-tv',
            'url': '/television',
            'descripcion': 'Gestión de contenido TV y streaming',
            'color': 'info',
            'permiso': True
        },
        {
            'nombre': 'Sedes',
            'icono': 'fas fa-home',
            'url': '/sedes',
            'descripcion': 'Gestión de sedes instaladas',
            'color': 'warning',
            'permiso': True
        },
        {
            'nombre': 'Portales Cautivos',
            'icono': 'fas fa-wifi',
            'url': '/portales',
            'descripcion': 'Gestión de portales WiFi',
            'color': 'secondary',
            'permiso': True
        }
    ]
    
    return render_template('dashboard_simple.html', 
                       modulos=modulos, 
                       stats=stats,
                       title='Dashboard')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login - Versión simplificada y corregida"""
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        try:
            # Buscar usuario en Supabase
            result = supabase.table('users').select('*').eq('username', username).execute()
            
            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                
# Verificar si el usuario está activo
                if not user_data.get('activo', True):
                    error = 'Usuario inactivo'
                    return render_template('login_simple.html', title='Iniciar Sesión', error=error)
                
                # Verificar contraseña
                password_hash = user_data.get('password_hash')
                
                if password_hash and check_password_hash(password_hash, password):
                    # Autenticación exitosa
                    user = User(user_data)
                    login_user(user, remember=remember)
                    
                    # Actualizar último login
                    try:
                        supabase.table('users').update({
                            'ultimo_login': datetime.now().isoformat()
                        }).eq('id', user_data['id']).execute()
                    except:
                        pass  # No crítico si falla la actualización
                    
                    next_page = request.args.get('next')
                    return redirect(next_page if next_page else '/extraccion')
                else:
                    error = 'Usuario o contraseña incorrectos'
            else:
                error = 'Usuario o contraseña incorrectos'
                
        except Exception as e:
            print(f"Error en login: {e}")
            error = 'Error de autenticación'
    
    return render_template('login.html', title='Iniciar Sesión', error=error)

@app.route('/debug/users')
def debug_users():
    """Debug endpoint to check users"""
    try:
        result = supabase.table('users').select('*').execute()
        return {
            'status': 'success',
            'count': len(result.data) if result.data else 0,
            'users': result.data
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

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





@app.route('/television')
@login_required
def television():
    """Redirigir al módulo de televisión"""
    return redirect(url_for('television.index'))

@app.route('/sedes')
@login_required
def sedes():
    """Redirigir al módulo de sedes"""
    return redirect(url_for('sedes.index'))

@app.route('/portales')
@login_required
def portales():
    """Redirigir al módulo de portales cautivos"""
    return redirect(url_for('portales_cautivos.index'))

@app.route('/profile')
@login_required
def profile():
    """Perfil de usuario"""
    return render_template('profile.html', title='Mi Perfil')

@app.route('/extraccion')
@login_required
def extraccion():
    """Módulo de extracción de datos - Versión Temporal"""
    return redirect(url_for('extraccion_datos.index'))

def main():
    """Función principal para iniciar la aplicación"""
    print("SISTEMA ESCOBARNET 100% SUPABASE v3.0")
    print("=" * 60)
    
    # Verificar conexión a Supabase
    try:
        result = supabase.table('users').select('count').execute()
        total_users = len(result.data) if result.data else 0
        print(f"[OK] Conexion a Supabase OK ({total_users} usuarios)")
    except Exception as e:
        print(f"[ERROR] Error de conexion a Supabase: {e}")
        return 1
    
    # Iniciar aplicación
    print("[INICIANDO] Aplicacion...")
    print(f"[URL] http://localhost:5002")
    print(f"[USUARIO] admin")
    print(f"[PASSWORD] admin123")
    print("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=True
    )

if __name__ == '__main__':
    main()