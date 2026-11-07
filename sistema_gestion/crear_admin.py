#!/usr/bin/env python3
"""
Script para crear/verificar usuario admin
"""

import os
from dotenv import load_dotenv
from supabase import create_client
from werkzeug.security import generate_password_hash

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("ERROR: Faltan variables de entorno de Supabase")
    exit(1)

# Conectar a Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def crear_admin():
    """Crear usuario admin si no existe"""
    try:
        # Verificar si ya existe
        result = supabase.table('users').select('*').eq('username', 'admin').execute()
        
        if result.data and len(result.data) > 0:
            print("[OK] Usuario admin ya existe")
            user = result.data[0]
            print(f"   ID: {user['id']}")
            print(f"   Username: {user['username']}")
            print(f"   Email: {user['email']}")
            print(f"   Activo: {user.get('activo', True)}")
            
            # Actualizar contraseña si es necesario
            password_hash = generate_password_hash('admin123')
            supabase.table('users').update({
                'password_hash': password_hash
            }).eq('username', 'admin').execute()
            print("[OK] Contraseña actualizada a admin123")
            
        else:
            # Crear usuario admin
            password_hash = generate_password_hash('admin123')
            
            user_data = {
                'username': 'admin',
                'email': 'admin@escobarnet.com',
                'nombre': 'Administrador',
                'apellido': 'Sistema',
                'password_hash': password_hash,
                'rol': 'admin',
                'activo': True
            }
            
            result = supabase.table('users').insert(user_data).execute()
            print("[OK] Usuario admin creado exitosamente")
            print(f"   Username: admin")
            print(f"   Password: admin123")
            print(f"   Email: admin@escobarnet.com")
            
    except Exception as e:
        print(f"[ERROR] {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("Verificando/Creando usuario admin...")
    print("=" * 50)
    
    if crear_admin():
        print("\nListo! Ya puedes iniciar sesión con:")
        print("   URL: http://localhost:5002/login")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
    else:
        print("\nNo se pudo crear el usuario admin")