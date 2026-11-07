from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)
app.secret_key = 'test'

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Login</title>
</head>
<body>
    <h1>TEST SIMPLE LOGIN</h1>
    
    {% if request.method == 'POST' %}
        <div style="background: yellow; padding: 10px;">
            FORMULARIO RECIBIDO:<br>
            Username: {{ username }}<br>
            Password: {{ password }}<br>
            Método: {{ request.method }}<br>
        </div>
    {% endif %}
    
    <form method="POST" style="border: 2px solid red; padding: 20px;">
        <div>
            <label>Username:</label><br>
            <input type="text" name="username" value="admin">
        </div><br>
        <div>
            <label>Password:</label><br>
            <input type="password" name="password" value="admin123">
        </div><br>
        <button type="submit">Enviar</button>
    </form>
    
    <h3>Información de la petición:</h3>
    <pre>
Método: {{ request.method }}
URL: {{ request.url }}
Form Data: {{ dict(request.form) }}
    </pre>
</body>
</html>
"""

@app.route('/test', methods=['GET', 'POST'])
def test_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        print(f"*** TEST: POST RECIBIDO - Username: {username}, Password: {password} ***")
        return render_template_string(LOGIN_TEMPLATE, username=username, password=password)
    else:
        print("*** TEST: PETICIÓN GET ***")
        return render_template_string(LOGIN_TEMPLATE)

if __name__ == '__main__':
    print("=== INICIANDO TEST LOGIN ===")
    print("ABRE: http://localhost:5003/test")
    print("=================================")
    app.run(debug=True, host='0.0.0.0', port=5003)