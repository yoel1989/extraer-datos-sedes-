import asyncio
import sys
import os

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

async def test_pdf_simple():
    try:
        import telegram_brisas_pdf
        
        print('=== PRUEBA PDF SIMPLIFICADA ===')
        
        # Obtener mensajes
        mensajes = await telegram_brisas_pdf.obtener_todos_los_mensajes('2025-12-13', '2025-12-14')
        print(f'Mensajes obtenidos: {len(mensajes)}')
        
        if mensajes:
            print('Datos del primer mensaje:')
            print(f'  {mensajes[0]}')
            
            # Probar solo el cálculo de ventas
            print('\nCalculando ventas...')
            ventas = telegram_brisas_pdf.calcular_ventas_y_comisiones(mensajes)
            print(f'Ventas calculadas: {ventas}')
            
            # Intentar crear PDF con captura de errores
            print('\nIntentando crear PDF...')
            try:
                archivo_pdf, ventas_resultado, nombre_sitio = telegram_brisas_pdf.crear_pdf(mensajes, '2025-12-13', '2025-12-14')
                print(f'PDF creado: {archivo_pdf}')
                print(f'Ventas resultado: {ventas_resultado}')
                print(f'Sitio: {nombre_sitio}')
                
                if os.path.exists(archivo_pdf):
                    size = os.path.getsize(archivo_pdf)
                    print(f'Archivo PDF existe, tamaño: {size} bytes')
                else:
                    print('ERROR: Archivo PDF no existe')
                    
            except Exception as pdf_error:
                print(f'ERROR creando PDF: {pdf_error}')
                import traceback
                traceback.print_exc()
        else:
            print('ERROR: No hay mensajes')
        
    except Exception as e:
        print(f'ERROR GENERAL: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_pdf_simple())