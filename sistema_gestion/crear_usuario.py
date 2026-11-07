#!/usr/bin/env python3
"""
Crear usuarios en Supabase - ESCOBARNET
Permite crear nuevos usuarios desde la línea de comandos
"""

import os
import sys
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from supabase import create_client

def crear_usuario():
    """Interfaz para crear usuarios en Supabase"""
    
    print("=" * 60)
    print("     CREAR USUARIO - ESCOBARNET SUPABASE")
    print("=" * 60)
    
    # Cargar variables de entorno
    load_dotenv()
    
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ ERROR: Faltan variables de entorno de Supabase")
        return 1
    
    print(f"✅ Conexión a Supabase: {SUPABASE_URL[:30]}...")
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        print("\n📝 Ingresa los datos del nuevo usuario:")
        
        # Solicitar datos del usuario
        username = input("👤 Nombre de usuario: ").strip()
        if not username:
            print("❌ El nombre de usuario es obligatorio")
            return 1
        
        email = input("📧 Correo electrónico: ").strip()
        if not email:
            print("❌ El correo electrónico es obligatorio")
            return 1
        
        nombre = input("👤 Nombre: ").strip()
        if not nombre:
            print("❌ El nombre es obligatorio")
            return 1
        
        apellido = input("👤 Apellido: ").strip()
        if not apellido:
            print("❌ El apellido es obligatorio")
            return 1
        
        rol = input("🔓 Rol (admin/usuario) [default: usuario]: ").strip()
        if not rol:
            rol = 'usuario'
        if rol not in ['admin', 'usuario']:
            rol = 'usuario'
        
        print(f"\n🔑 Contraseña para {username}:")
        password = input("🔑 Contraseña: ").strip()
        if not password:
            print("❌ La contraseña es obligatoria")
            return 1
        
        confirmar_password = input("🔑 Confirmar contraseña: ").strip()
        if password != confirmar_password:
            print("❌ Las contraseñas no coinciden")
            return 1
        
        # Confirmar datos
        print("\n" + "=" * 40)
        print("📋 Resumen del usuario a crear:")
        print(f"👤 Usuario: {username}")
        print(f"📧 Email: {email}")
        print(f"👤 Nombre completo: {nombre} {apellido}")
        print(f"🔓 Rol: {rol}")
        print(f"🔑 Contraseña: {password}")
        print(f"✅ Activo: Sí")
        print("=" * 40)
        
        confirmar = input("\n✅ ¿Confirmar creación? (S/N): ").strip().upper()
        if confirmar != 'S':
            print("❌ Creación cancelada")
            return 0
        
        # Crear el usuario
        print("\n🚀 Creando usuario en Supabase...")
        
        password_hash = generate_password_hash(password)
        
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'nombre': nombre,
            'apellido': apellido,
            'rol': rol,
            'activo': True
        }
        
        # Verificar si el usuario ya existe
        existing_user = client.table('users').select('*').eq('username', username).execute()
        if existing_user.data:
            print("❌ ERROR: Este nombre de usuario ya existe")
            return 1
        
        # Insertar usuario
        result = client.table('users').insert(user_data).execute()
        
        if result.data:
            print("✅ ¡USUARIO CREADO EXITOSAMENTE!")
            print(f"🎉 {username} ha sido agregado al sistema")
            print(f"🌐 URL de acceso: http://localhost:5002")
            print("\n📝 Puedes iniciar sesión con:")
            print(f"👤 Usuario: {username}")
            print(f"🔑 Contraseña: {password}")
        else:
            print("❌ ERROR: No se pudo crear el usuario")
            return 1
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return 1
    
    return 0

def reset_password():
    """Restablecer contraseña de un usuario existente"""
    
    print("\n" + "=" * 60)
    print("     RESTABLECER CONTRASEÑA - ESCOBARNET SUPABASE")
    print("=" * 60)
    
    load_dotenv()
    
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        username = input("👤 Nombre de usuario a resetear: ").strip()
        if not username:
            print("❌ El nombre de usuario es obligatorio")
            return 1
        
        # Buscar usuario
        user_result = client.table('users').select('*').eq('username', username).execute()
        
        if not user_result.data:
            print("❌ Usuario no encontrado")
            return 1
        
        user_data = user_result.data[0]
        
        print(f"\n👤 Usuario encontrado: {user_data['nombre']} {user_data['apellido']}")
        print(f"📧 Email: {user_data['email']}")
        print(f"🔓 Rol: {user_data['rol']}")
        
        new_password = input("\n🔑 Nueva contraseña: ").strip()
        if not new_password:
            print("❌ La contraseña es obligatoria")
            return 1
        
        confirmar_password = input("🔑 Confirmar nueva contraseña: ").strip()
        if new_password != confirmar_password:
            print("❌ Las contraseñas no coinciden")
            return 1
        
        # Actualizar contraseña
        password_hash = generate_password_hash(new_password)
        
        result = client.table('users').update({
            'password_hash': password_hash
        }).eq('id', user_data['id']).execute()
        
        if result.data:
            print("✅ ¡CONTRASEÑA ACTUALIZADA!")
            print(f"👤 Usuario: {username}")
            print(f"🔑 Nueva contraseña: {new_password}")
            print(f"🌐 URL de acceso: http://localhost:5002")
        else:
            print("❌ ERROR: No se pudo actualizar la contraseña")
            return 1
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return 1
    
    return 0

def main():
    """Menú principal"""
    
    print("=" * 60)
    print("     SISTEMA DE USUARIOS - ESCOBARNET SUPABASE")
    print("=" * 60)
    
    print("1. Crear nuevo usuario")
    print("2. Restablecer contraseña existente")
    print("3. Salir")
    
    opcion = input("\n📋 Selecciona una opción (1-3): ").strip()
    
    if opcion == '1':
        return crear_usuario()
    elif opcion == '2':
        return reset_password()
    elif opcion == '3':
        print("👋 Adiós!")
        return 0
    else:
        print("❌ Opción inválida")
        return 1

if __name__ == '__main__':
    sys.exit(main())