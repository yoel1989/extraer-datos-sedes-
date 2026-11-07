from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import asyncio
import sys
import os

# Agregar el directorio de scripts al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

# Configuración de Telegram
API_ID = int(os.environ['TELEGRAM_API_ID'])
API_HASH = os.environ['TELEGRAM_API_HASH']
PHONE = os.environ['TELEGRAM_PHONE']

async def create_session():
    """Crear sesión de Telegram"""
    print("Creando sesión de Telegram...")
    print("Espera el código de verificación en tu teléfono Telegram")
    
    client = TelegramClient('session_name', API_ID, API_HASH)
    
    try:
        await client.start(phone=PHONE)
        print("✅ Sesión creada exitosamente")
        
        # Probar conexión
        me = await client.get_me()
        print(f"✅ Conectado como: {me.first_name} {me.last_name or ''}")
        
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ Error creando sesión: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    from telethon import TelegramClient
    asyncio.run(create_session())