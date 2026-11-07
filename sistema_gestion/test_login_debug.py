"""
Test de login simple para depurar
"""

import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = 'test-debug'

# Simular usuario con hash
PASSWORD_HASH = generate_password_hash('admin123')

@app.route('/test-login', methods=['GET', 'POST'])
def test_login():
    print(f"*** RUTA ACCEDIDA: {request.method} ***")
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        print(f"*** DATOS RECIBIDOS - Username: '{username}', Password: '{password}' ***")
        print(f"*** HASH ALMACENADO: {PASSWORD_HASH} ***")
        
        if username == 'admin':
            print(f"*** VERIFICANDO CONTRASEÑA ***")
            if check_password_hash(PASSWORD_HASH, password):
                print(f"*** CONTRASEÑA CORRECTA ***")
                session['user'] = 'admin'
                return redirect(url_for('success'))
            else:
                print(f"*** CONTRASEÑA INCORRECTA ***")
        else:
            print(f"*** USUARIO INCORRECTO ***")
        
        return render_template('test_login.html', error='Credenciales incorrectas')
    
    print(f"*** MOSTRANDO FORMULARIO ***")
    return render_template('test_login.html')

@app.route('/success')
def success():
    if 'user' in session:
        return f"<h1>¡LOGIN EXITOSO! Bienvenido {session['user']}</h1>"
    return redirect(url_for('test_login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('test_login'))

if __name__ == '__main__':
    print("=== TEST LOGIN DEBUG ===")
    print("ABRE: http://localhost:5004/test-login")
    print("USUARIO: admin")
    print("CONTRASEÑA: admin123")
    print("="*40)
    app.run(debug=True, host='0.0.0.0', port=5004)