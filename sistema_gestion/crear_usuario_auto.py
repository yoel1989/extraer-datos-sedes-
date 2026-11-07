#!/usr/bin/env python3
"""
Crear usuarios en Supabase - Version automatica
Crea un usuario de prueba automaticamente
"""

import os
import sys
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from supabase import create_client

def main():
    """Crear usuario de prueba automaticamente"""
    
    print("=" * 60)
    print("CREAR USUARIO DE PRUEZA - ESCOBARNET SUPABASE")
    print("=" * 60)
    
    # Cargar variables de entorno
    load_dotenv()
    
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("ERROR: Faltan variables de entorno de Supabase")
        return 1
    
    print(f"Conexion a Supabase: {SUPABASE_URL[:30]}...")
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Datos del usuario de prueba
        username = "usuario1"
        email = "usuario1@escobarnet.com"
        nombre = "Usuario"
        apellido = "Prueba"
        rol = "usuario"
        password = "123456"
        activo = True
        
        print(f"Creando usuario: {username}")
        print(f"Email: {email}")
        print(f"Nombre: {nombre} {apellido}")
        print(f"Rol: {rol}")
        print(f"Contrasena: {password}")
        print(f"Activo: {activo}")
        
        # Verificar si ya existe
        existing_user = client.table('users').select('*').eq('username', username).execute()
        
        if existing_user.data and len(existing_user.data) > 0:
            print(f"WARNING: El usuario '{username}' ya existe")
            print("Intentando borrar y recrear...")
            
            # Borrar usuario existente
            delete_result = client.table('users').delete().eq('username', username).execute()
            if delete_result.data:
                print("Usuario existente borrado")
            else:
                print("ERROR: No se pudo borrar usuario existente")
                return 1
        
        # Crear hash de contraseña
        password_hash = generate_password_hash(password)
        
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'nombre': nombre,
            'apellido': apellido,
            'rol': rol,
            'activo': activo
        }
        
        # Insertar usuario
        print("Creando usuario en Supabase...")
        result = client.table('users').insert(user_data).execute()
        
        if result.data:
            print("SUCCESS: Usuario creado exitosamente!")
            print(f"Usuario: {username}")
            print(f"Email: {email}")
            print(f"Contrasena: {password}")
            print(f"URL de acceso: http://localhost:5002")
            print("")
            print("AHORA PUEDES INICIAR SESION CON:")
            print(f"Usuario: {username}")
            print(f"Contrasena: {password}")
            print(f"URL: http://localhost:5002")
            
            # También resetear contraseña de admin
            print("")
            print("Resetando contraseña de admin a admin123...")
            admin_password_hash = generate_password_hash('admin123')
            
            admin_result = client.table('users').update({
                'password_hash': admin_password_hash
            }).eq('username', 'admin').execute()
            
            if admin_result.data:
                print("SUCCESS: Contraseña de admin actualizada a admin123")
            else:
                print("WARNING: No se pudo actualizar contraseña de admin")
            
            return 0
        else:
            print("ERROR: No se pudo crear el usuario")
            return 1
            
    except Exception as e:
        print(f"ERROR: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())