from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import asyncio
import sys
import os
import re
from datetime import datetime

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

async def debug_messages():
    """Depurar mensajes de Telegram"""
    try:
        import telegram_brisas_pdf
        
        print("=== DEPURACION DE MENSAJES BRISAS ===")
        
        # Conectar y obtener mensajes
        API_ID = int(os.environ['TELEGRAM_API_ID'])
        API_HASH = os.environ['TELEGRAM_API_HASH']
        PHONE = os.environ['TELEGRAM_PHONE']
        GROUP_ID = -4797788824
        
        from telethon import TelegramClient
        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        session_path = os.path.join(script_dir, 'session_name')
        client = TelegramClient(session_path, API_ID, API_HASH)
        
        await client.start(phone=PHONE)
        print("OK: Conectado a Telegram")
        
        # Obtener entidad del grupo
        entity = await client.get_entity(GROUP_ID)
        
        # Buscar mensajes recientes
        mensajes_encontrados = []
        mensajes_procesados = []
        
        print("\nBuscando mensajes de los ultimos 2 dias...")
        
        async for message in client.iter_messages(entity, limit=50):
            if not message.text:
                continue
            
            message_date = message.date.astimezone().replace(tzinfo=None)
            
            # Solo mensajes de últimos 2 días
            if (datetime.now() - message_date).days > 2:
                continue
            
            # Excluir "Desconectado"
            if "Desconectado" in message.text or "desconectado" in message.text:
                continue
            
            mensajes_encontrados.append({
                'texto': message.text,
                'fecha': message_date,
                'id': message.id
            })
            
            # Intentar procesar con la función del script
            datos = telegram_brisas_pdf.extraer_datos_flexible(message.text)
            if datos:
                mensajes_procesados.append(datos)
        
        print(f"\nESTADISTICAS:")
        print(f"   Total mensajes encontrados: {len(mensajes_encontrados)}")
        print(f"   Total mensajes procesados: {len(mensajes_procesados)}")
        
        if mensajes_encontrados:
            print(f"\nPRIMEROS 5 MENSAJES ENCONTRADOS:")
            for i, msg in enumerate(mensajes_encontrados[:5]):
                print(f"   {i+1}. [{msg['fecha']}] {msg['texto'][:100]}...")
        
        if mensajes_procesados:
            print(f"\nPRIMEROS 5 MENSAJES PROCESADOS:")
            for i, datos in enumerate(mensajes_procesados[:5]):
                print(f"   {i+1}. Codigo: {datos['codigo']}")
                print(f"       Ubicacion: {datos['ubicacion']}")
                print(f"       Fecha: {datos['fecha']}")
                print(f"       Tiempo: {datos['tiempo']}")
                print(f"       Original: {datos['mensaje_original'][:50]}...")
                print()
        else:
            print(f"\nNO SE PROCESO NINGUN MENSAJE")
            print("Posibles causas:")
            print("- Los mensajes no tienen el formato esperado")
            print("- No hay codigos al inicio del mensaje")
            print("- El patron de regex no coincide")
        
        await client.disconnect()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_messages())