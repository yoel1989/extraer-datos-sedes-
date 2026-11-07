import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import asyncio
from telethon import TelegramClient

API_ID = int(os.environ['TELEGRAM_API_ID'])
API_HASH = os.environ['TELEGRAM_API_HASH']
PHONE = os.environ['TELEGRAM_PHONE']

async def create_session():
    print("=== CREAR NUEVA SESION DE TELEGRAM ===")
    print(f"Telefono: {PHONE}")
    print("Espera el codigo de verificacion en tu telefono Telegram")
    print("Si tienes 2FA, tambien te pedira la contrasena")
    print()
    
    session_name = 'session_extraccion'
    
    try:
        print("Conectando...")
        client = TelegramClient(session_name, API_ID, API_HASH)
        await client.start(phone=PHONE)
        
        print("SESION CREADA EXITOSAMENTE")
        print("Archivo de session:", session_name + ".session")
        
        # Probar conexión obteniendo información del usuario
        me = await client.get_me()
        print(f"Conectado como: {me.first_name} {me.last_name or ''}")
        print(f"Username: @{me.username}")
        print(f"ID: {me.id}")
        
        await client.disconnect()
        print("Conexion cerrada correctamente")
        
    except Exception as e:
        print(f"ERROR creando sesion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_session())