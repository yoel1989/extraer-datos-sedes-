"""
Script de prueba para verificar la importación y ejecución básica
"""

import asyncio
import sys
import os

def test_import():
    """Probar importación del script de Brisas"""
    try:
        # Agregar el directorio de scripts al path
        scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        sys.path.insert(0, scripts_dir)
        
        print(f"Directorio de scripts: {scripts_dir}")
        print(f"Scripts disponibles: {os.listdir(scripts_dir)}")
        
        # Intentar importar
        import telegram_brisas_pdf
        print("OK: Script telegram_brisas_pdf importado correctamente")
        
        # Verificar funciones
        if hasattr(telegram_brisas_pdf, 'obtener_todos_los_mensajes'):
            print("OK: Función obtener_todos_los_mensajes encontrada")
        else:
            print("ERROR: Función obtener_todos_los_mensajes NO encontrada")
            
        if hasattr(telegram_brisas_pdf, 'crear_pdf'):
            print("OK: Función crear_pdf encontrada")
        else:
            print("ERROR: Función crear_pdf NO encontrada")
            
        return True
        
    except Exception as e:
        print(f"ERROR: Error importando script: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if scripts_dir in sys.path:
            sys.path.remove(scripts_dir)

async def test_basic_extraction():
    """Probar extracción básica"""
    try:
        scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        sys.path.insert(0, scripts_dir)
        
        import telegram_brisas_pdf
        
        print("Iniciando prueba de extracción...")
        # Probar con fechas recientes
        mensajes = await telegram_brisas_pdf.obtener_todos_los_mensajes("2025-12-13", "2025-12-14")
        print(f"Se obtuvieron {len(mensajes) if mensajes else 0} mensajes")
        
        return mensajes
        
    except Exception as e:
        print(f"❌ Error en extracción: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        if scripts_dir in sys.path:
            sys.path.remove(scripts_dir)

if __name__ == "__main__":
    print("=== PRUEBA DE IMPORTACIÓN ===")
    if test_import():
        print("\n=== PRUEBA DE EXTRACCIÓN ===")
        asyncio.run(test_basic_extraction())