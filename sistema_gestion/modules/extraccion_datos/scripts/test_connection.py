from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import asyncio
import sys
import os

# Agregar directorio de scripts al path
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from telethon import TelegramClient
from datetime import datetime

async def test_connection():
    print("=== PROBANDO CONEXION A TELEGRAM ===")
    
    try:
        # Mismo config que los scripts
        API_ID = int(os.environ['TELEGRAM_API_ID'])
        API_HASH = os.environ['TELEGRAM_API_HASH']
        PHONE = os.environ['TELEGRAM_PHONE']
        
        session_path = 'session_extraccion'
        print(f"Usando session: {session_path}")
        
        client = TelegramClient(session_path, API_ID, API_HASH)
        
        print("Conectando...")
        await client.start(phone=PHONE)
        
        print("¡Conexion exitosa!")
        
        # Probar obtener mensajes
        print("Obteniendo info del usuario...")
        me = await client.get_me()
        print(f"Conectado como: {me.first_name} {me.last_name or ''}")
        print(f"Username: @{me.username}")
        print(f"ID: {me.id}")
        
        # Probar un grupo de ejemplo
        print("Probando acceso a grupos...")
        async for dialog in client.iter_dialogs(limit=5):
            if dialog.is_group or dialog.is_channel:
                print(f"Grupo: {dialog.name} (ID: {dialog.id})")
                break
        
        await client.disconnect()
        print("Conexion cerrada correctamente")
        
    except Exception as e:
        print(f"ERROR DE CONEXION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connection())