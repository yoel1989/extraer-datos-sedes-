#!/usr/bin/env python3
"""
Crear usuarios en Supabase - Version simplificada
"""

import os
import sys
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from supabase import create_client

def crear_usuario_manual():
    """Crear usuario de forma simple"""
    
    print("=" * 60)
    print("CREAR USUARIO - ESCOBARNET SUPABASE")
    print("=" * 60)
    
    load_dotenv()
    
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("ERROR: Faltan variables de entorno de Supabase")
        return 1
    
    print(f"Conexion a Supabase: {SUPABASE_URL[:30]}...")
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Datos del usuario - puedes modificar estos valores
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
            print(f"ERROR: El usuario '{username}' ya existe")
            return 1
        
        # Crear usuario
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
        
        result = client.table('users').insert(user_data).execute()
        
        if result.data:
            print("SUCCESS: Usuario creado exitosamente!")
            print(f"Usuario: {username}")
            print(f"Contrasena: {password}")
            print(f"URL: http://localhost:5002")
            print("Ya puedes iniciar sesion")
            return 0
        else:
            print("ERROR: No se pudo crear el usuario")
            return 1
            
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

def reset_password_admin():
    """Resetear contraseña del admin a admin123"""
    
    print("=" * 60)
    print("RESETAR CONTRASEÑA ADMIN")
    print("=" * 60)
    
    load_dotenv()
    
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Buscar admin
        result = client.table('users').select('*').eq('username', 'admin').execute()
        
        if result.data and len(result.data) > 0:
            # Actualizar contraseña
            password_hash = generate_password_hash('admin123')
            
            result = client.table('users').update({
                'password_hash': password_hash
            }).eq('id', result.data[0]['id']).execute()
            
            if result.data:
                print("SUCCESS: Contraseña de admin actualizada")
                print("Usuario: admin")
                print("Nueva contraseña: admin123")
                print("URL: http://localhost:5002")
                return 0
            else:
                print("ERROR: No se pudo actualizar")
                return 1
        else:
            print("ERROR: Usuario admin no encontrado")
            return 1
            
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

def listar_usuarios():
    """Listar todos los usuarios"""
    
    print("=" * 60)
    print("LISTAR USUARIOS")
    print("=" * 60)
    
    load_dotenv()
    
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        result = client.table('users').select('*').execute()
        
        if result.data:
            print(f"Total usuarios: {len(result.data)}")
            print("-" * 40)
            
            for user in result.data:
                print(f"Usuario: {user['username']}")
                print(f"Email: {user['email']}")
                print(f"Nombre: {user['nombre']} {user['apellido']}")
                print(f"Rol: {user['rol']}")
                print(f"Activo: {user['activo']}")
                print(f"ID: {user['id']}")
                print("-" * 40)
        else:
            print("No hay usuarios en el sistema")
            
        return 0
            
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

def main():
    """Menu principal"""
    
    print("=" * 60)
    print("SISTEMA DE USUARIOS - ESCOBARNET")
    print("=" * 60)
    print("1. Crear usuario de prueba")
    print("2. Resetear contraseña admin a admin123")
    print("3. Listar usuarios existentes")
    print("4. Salir")
    print("=" * 60)
    
    try:
        opcion = int(input("Selecciona una opcion (1-4): "))
    except:
        print("Opcion invalida")
        return 1
    
    if opcion == 1:
        return crear_usuario_manual()
    elif opcion == 2:
        return reset_password_admin()
    elif opcion == 3:
        return listar_usuarios()
    elif opcion == 4:
        print("Saliendo...")
        return 0
    else:
        print("Opcion invalida")
        return 1

if __name__ == '__main__':
    sys.exit(main())