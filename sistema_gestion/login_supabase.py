@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login - Versión Supabase"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    from flask import request
    from flask_login import login_user
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        try:
            # Usar Supabase directamente
            from supabase import create_client
            
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            client = create_client(supabase_url, supabase_key)
            
            # Buscar usuario en Supabase
            result = client.table('users').select('*').eq('username', username).execute()
            
            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                
                # Verificar contraseña
                from werkzeug.security import check_password_hash
                
                if user_data.get('activo', True) and check_password_hash(user_data['password_hash'], password):
                    
                    # Crear objeto compatible con Flask-Login
                    class SupabaseUser:
                        def __init__(self, data):
                            self.id = data.get('id')
                            self.username = data.get('username')
                            self.email = data.get('email')
                            self.nombre = data.get('nombre')
                            self.apellido = data.get('apellido')
                            self.rol = data.get('rol')
                            self.activo = data.get('activo', True)
                            self.ultimo_login = data.get('ultimo_login')
                        
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
                    
                    user = SupabaseUser(user_data)
                    login_user(user, remember=remember)
                    
                    # Actualizar último login
                    client.table('users').update({'ultimo_login': datetime.now().isoformat()}).eq('id', user_data['id']).execute()
                    
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
    
    return render_template('login.html', title='Iniciar Sesión')