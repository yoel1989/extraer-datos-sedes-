from flask import Flask, render_template, redirect, url_for, request, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
import os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from supabase import create_client

# Configuración básica
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Conexión a Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.username = user_data.get('username')
        self.nombre = user_data.get('nombre', user_data.get('username'))
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
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
    modulos = [
        {
            'nombre': 'Extracción de Datos',
            'url': '/extraccion',
            'descripcion': 'Extraer datos de Telegram y generar reportes'
        },
        {
            'nombre': 'Contabilidad',
            'url': '/contabilidad',
            'descripcion': 'Gestión financiera y facturación'
        },
        {
            'nombre': 'Televisión',
            'url': '/television',
            'descripcion': 'Gestión de contenido TV y streaming'
        },
        {
            'nombre': 'Sedes',
            'url': '/sedes',
            'descripcion': 'Gestión de sedes instaladas'
        },
        {
            'nombre': 'Portales Cautivos',
            'url': '/portales',
            'descripcion': 'Gestión de portales WiFi'
        }
    ]
    
    return render_template('dashboard_simple.html', modulos=modulos, usuario=session.get('user_name'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Login attempt: {username}")
        
        try:
            # Buscar usuario
            result = supabase.table('users').select('*').eq('username', username).execute()
            
            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                password_hash = user_data.get('password_hash')
                
                if password_hash and check_password_hash(password_hash, password):
                    user = User(user_data)
                    login_user(user)
                    session['user_name'] = user.nombre
                    return redirect('/extraccion')
                else:
                    return render_template('login_simple.html', error='Contraseña incorrecta')
            else:
                return render_template('login_simple.html', error='Usuario no encontrado')
                
        except Exception as e:
            print(f"Login error: {e}")
            return render_template('login_ultra_simple.html', error=f'Error: {str(e)}')
    
    return render_template('login_simple.html')

@app.route('/extraccion')
@login_required
def extraccion():
    sitios = {
        'brisas': {'name': 'BRISAS'},
        'cachicamo': {'name': 'CACHICAMO'},
        'cano_lajas': {'name': 'CANO LAJAS'},
        'cano_pescado': {'name': 'CANO PESCADO'},
        'cerritos': {'name': 'CERRITOS'},
        'manantiales_1': {'name': 'MANANTIALES'},
        'manantiales_2': {'name': 'MANANTIALES-2'},
        'miravalle': {'name': 'MIRAVALLE'},
        'san_miguel': {'name': 'SAN MIGUEL'},
        'tortuga': {'name': 'LA TORTUGA'},
        'tropezon': {'name': 'TROPEZON'}
    }
    return render_template('extraccion_temporal.html', title='Extracción de Datos', sitios=sitios)

@app.route('/contabilidad')
@login_required
def contabilidad():
    return "<h1>Contabilidad - En desarrollo</h1>"

@app.route('/television')
@login_required
def television():
    return "<h1>Televisión - En desarrollo</h1>"

@app.route('/sedes')
@login_required
def sedes():
    return "<h1>Sedes - En desarrollo</h1>"

@app.route('/portales')
@login_required
def portales():
    return "<h1>Portales Cautivos - En desarrollo</h1>"

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)