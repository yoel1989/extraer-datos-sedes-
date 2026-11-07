from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import asyncio
import sys
import os

# Configuración de Telegram
API_ID = int(os.environ['TELEGRAM_API_ID'])
API_HASH = os.environ['TELEGRAM_API_HASH']
PHONE = os.environ['TELEGRAM_PHONE']

async def create_session():
    """Crear nueva sesión de Telegram"""
    print("=== CREAR NUEVA SESIÓN DE TELEGRAM ===")
    print(f"Teléfono: {PHONE}")
    print("Espera el código de verificación en tu teléfono Telegram")
    print("Si tienes 2FA, también te pedirá la contraseña")
    print()
    
    client = TelegramClient('session_name', API_ID, API_HASH)
    
    try:
        print("Conectando...")
        await client.start(phone=PHONE)
        print("✅ Sesión creada exitosamente")
        
        # Probar conexión y obtener información
        me = await client.get_me()
        print(f"✅ Conectado como: {me.first_name} {me.last_name or ''}")
        print(f"✅ Username: @{me.username if me.username else 'Sin username'}")
        print(f"✅ ID: {me.id}")
        
        # Listar algunos chats para verificar
        print("\n📋 Verificando acceso a chats...")
        async for dialog in client.iter_dialogs(limit=5):
            if dialog.name:
                print(f"   - {dialog.name}")
        
        await client.disconnect()
        print("\n✅ Sesión guardada como 'session_name.session'")
        print("✅ Ya puedes usar el sistema de extracción")
        
    except Exception as e:
        print(f"❌ Error creando sesión: {e}")
        import traceback
        traceback.print_exc()
        
        # Intentar limpiar sesión parcial
        try:
            await client.disconnect()
        except:
            pass

if __name__ == '__main__':
    from telethon import TelegramClient
    asyncio.run(create_session())