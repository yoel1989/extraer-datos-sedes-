#!/usr/bin/env python3
"""
Verificación de conexión a Supabase - Proyecto ESCOBARNET
"""

import os
import sys

# Agregar directorio actual al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def testear_conexion():
    """Probar conexión y estado de Supabase"""
    
    print("="*60)
    print("VERIFICACION DE SUPABASE - ESCOBARNET")
    print("="*60)
    
    # Verificar variables de entorno
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    use_supabase = os.getenv('USE_SUPABASE', 'false')
    
    print(f"📁 Directorio: {os.getcwd()}")
    print(f"🔧 USE_SUPABASE: {use_supabase}")
    print(f"🌐 SUPABASE_URL: {supabase_url[:30] if supabase_url else 'NO CONFIGURADA'}...")
    
    if not supabase_url or not supabase_key:
        print("\n❌ ERROR: Faltan variables de entorno de Supabase")
        print("Por favor, configura SUPABASE_URL y SUPABASE_ANON_KEY")
        return False
    
    if use_supabase.lower() != 'true':
        print("\n⚠️  El sistema está configurado para usar SQLite")
        print("Para usar Supabase, establece USE_SUPABASE=true en el .env")
        return False
    
    try:
        # Intentar importar y conectar
        from supabase import create_client
        
        print("\n🔄 Conectando a Supabase...")
        client = create_client(supabase_url, supabase_key)
        
        # Probar consultar la tabla users
        print("📊 Probando consulta a tabla 'users'...")
        response = client.table('users').select('count').execute()
        
        if response.data is not None:
            print(f"✅ Conexion exitosa a Supabase!")
            print(f"📋 Total usuarios en BD: {len(response.data) if response.data else 0}")
            
            # Verificar tablas principales
            tablas = ['users', 'extractions', 'transacciones', 'categorias']
            
            print("\n📋 Verificando tablas principales:")
            for tabla in tablas:
                try:
                    response = client.table(tabla).select('count').execute()
                    count = len(response.data) if response.data else 0
                    print(f"   ✅ {tabla}: {count} registros")
                except Exception as e:
                    print(f"   ❌ {tabla}: ERROR - {str(e)[:50]}...")
            
            print("\n🎉 SUPABASE ESTÁ FUNCIONANDO CORRECTAMENTE!")
            print("📊 Tu sistema está usando la base de datos en la nube")
            return True
        else:
            print("⚠️  Conexion establecida pero sin datos")
            return False
            
    except ImportError:
        print("\n❌ ERROR: No se puede importar el cliente Supabase")
        print("Ejecuta: pip install supabase")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR DE CONEXION: {str(e)}")
        
        if "relation" in str(e).lower() and "does not exist" in str(e).lower():
            print("\n📝 SOLUCION:")
            print("1. Ve a tu dashboard de Supabase")
            print("2. Ejecuta el script SQL en 'scripts/supabase_setup.sql'")
            print("3. Vuelve a intentar esta prueba")
        
        return False

def main():
    """Función principal"""
    resultado = testear_conexion()
    
    if resultado:
        print("\n" + "="*60)
        print("✅ ESTADO: ACTIVO CON SUPABASE")
        print("🌐 Base de datos en la nube funcionando correctamente")
        print("📊 Tu sistema ESCOBARNET está listo para producción")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ ESTADO: NO CONFIGURADO CON SUPABASE")
        print("💾 El sistema probablemente está usando SQLite local")
        print("="*60)
        print("\n📋 PASOS PARA CONFIGURAR SUPABASE:")
        print("1. Ve a: https://app.supabase.com")
        print("2. Selecciona tu proyecto 'escobarnet'")
        print("3. Ve a SQL Editor y ejecuta 'scripts/supabase_setup.sql'")
        print("4. Verifica que USE_SUPABASE=true en tu .env")
        print("5. Reinicia tu aplicación")

if __name__ == '__main__':
    main()