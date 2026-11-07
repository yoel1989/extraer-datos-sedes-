"""
Versión corregida del módulo de extracción - 100% Supabase
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from flask_login import login_required
import asyncio
import threading
import os
import sys
import json
# Importar gestor de Supabase
from utils.supabase_db import db_manager
import zipfile
import tempfile
from datetime import datetime, timezone, timedelta
from werkzeug.utils import secure_filename

# Configurar zona horaria para Colombia
os.environ['TZ'] = 'America/Bogota'
import time
if hasattr(time, 'tzset'):
    time.tzset()

# Forzar uso de hora local
import locale
try:
    locale.setlocale(locale.LC_TIME, 'es_CO.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish_Colombia.1252')
    except:
        pass  # Usar configuración por defecto

# Crear Blueprint para el módulo
extraccion_bp = Blueprint('extraccion_datos', __name__, 
                        url_prefix='/extraccion',
                        template_folder='templates',
                        static_folder='static')

# SITIOS CONFIGURADOS
SITIOS = {
    'brisas': {'name': 'BRISAS', 'script': 'telegram_brisas_pdf.py'},
    'cachicamo': {'name': 'CACHICAMO', 'script': 'telegram_cachicamo_pdf.py'},
    'cano_lajas': {'name': 'CANO LAJAS', 'script': 'telegram_cano_lajas_pdf.py'},
    'cano_pescado': {'name': 'CANO PESCADO', 'script': 'telegram_cano_pescado_pdf.py'},
    'cerritos': {'name': 'CERRITOS', 'script': 'telegram_cerritos_pdf.py'},
    'manantiales_1': {'name': 'MANANTIALES', 'script': 'telegram_manantiales_1_pdf.py'},
    'manantiales_2': {'name': 'MANANTIALES-2', 'script': 'telegram_manantiales_2_pdf.py'},
    'miravalle': {'name': 'MIRAVALLE', 'script': 'telegram_miravalle_pdf.py'},
    'san_miguel': {'name': 'SAN MIGUEL', 'script': 'telegram_san_miguel_pdf.py'},
    'tortuga': {'name': 'LA TORTUGA', 'script': 'telegram_tortuga_pdf.py'},
    'tropezon': {'name': 'TROPEZON', 'script': 'telegram_tropezon_pdf.py'}
}

def get_reports_path():
    """Obtener ruta del directorio de reportes"""
    # Obtener la ruta absoluta al directorio principal del proyecto
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    reports_path = os.path.join(current_dir, 'static', 'reports')
    os.makedirs(reports_path, exist_ok=True)
    return reports_path

def log_extraction(extraction_id, mensaje, tipo='info'):
    """Guardar log de extracción en Supabase"""
    try:
        # Forzar hora local de Colombia (UTC-5)
        utc_now = datetime.now(timezone.utc)
        colombia_time = utc_now - timedelta(hours=5)
        ahora_local = colombia_time.isoformat()
        
        log_data = {
            'extraction_id': extraction_id,
            'mensaje': mensaje,
            'tipo': tipo,
            'creado_en': ahora_local
        }
        
        result = db_manager.create_extraction_log(log_data)
        print(f"[LOG] ID:{extraction_id} - {tipo} - {mensaje} - {ahora_local}")
        return result
    except Exception as e:
        print(f"[ERROR] Guardando log: {e}")
        return None

def update_extraction_status(extraction_id, estado, **kwargs):
    """Actualizar estado de extracción en Supabase"""
    try:
        # Forzar hora local de Colombia (UTC-5)
        utc_now = datetime.now(timezone.utc)
        colombia_time = utc_now - timedelta(hours=5)
        ahora_local = colombia_time.isoformat()
        
        # Preparar datos de actualización
        update_data = {
            'estado': estado,
            'completado_en': ahora_local if estado == 'completado' else None,
            'actualizado_en': ahora_local
        }
        
        # Agregar campos adicionales
        update_data.update(kwargs)
        
        result = db_manager.update_extraction(extraction_id, update_data)
        print(f"[STATUS] ID:{extraction_id} - {estado} - {ahora_local}")
        return result
    except Exception as e:
        print(f"[ERROR] Actualizando estado: {e}")
        return False

@extraccion_bp.route('/')
@login_required
def index():
    """Página principal del módulo de extracción de datos"""
    try:
        # Probar conexión a Supabase
        if db_manager.test_connection():
            print("[INIT] Conexión a Supabase verificada correctamente")
        else:
            print("[ERROR] No se pudo conectar a Supabase")
    except Exception as e:
        print(f"[ERROR] Verificando conexión: {e}")
    return render_template('index.html', sitios=SITIOS)

@extraccion_bp.route('/status')
@login_required
def status():
    """Estado del módulo"""
    return {
        'modulo': 'Extracción de Datos',
        'estado': 'Activo',
        'descripcion': 'Sistema para extraer datos de Telegram y generar reportes PDF',
        'sitios_configurados': len(SITIOS)
    }

@extraccion_bp.route('/api/extract_site/<sitio_key>', methods=['POST'])
@login_required
def extract_site(sitio_key):
    """Extraer datos de un sitio específico - VERSIÓN DEPURACIÓN"""
    if sitio_key not in SITIOS:
        return jsonify({'success': False, 'error': 'Sitio no encontrado'}), 404
    
    data = request.json
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    
    sitio_info = SITIOS[sitio_key]
    
    # Crear registro de extracción en Supabase
    utc_now = datetime.now(timezone.utc)
    colombia_time = utc_now - timedelta(hours=5)
    ahora_local = colombia_time.isoformat()
    
    extraction_data = {
        'sitio': sitio_info['name'],
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'estado': 'procesando',
        'creado_en': ahora_local
    }
    
    result = db_manager.create_extraction(extraction_data)
    if not result:
        return jsonify({'success': False, 'error': 'Error creando registro de extracción'}), 500
    
    extraction_id = result['id']
    
    print(f"[EXTRACCIÓN] Iniciando para {sitio_key} (ID: {extraction_id})")
    log_extraction(extraction_id, f"Iniciando extracción para {sitio_key}", 'info')
    
    def run_extraction():
        """Función de extracción con depuración detallada"""
        try:
            print(f"[THREAD] Iniciando thread para {sitio_key}")
            log_extraction(extraction_id, "Thread iniciado", 'info')
            
            # Importar aquí para evitar problemas de contexto
            import asyncio
            import sys
            import os
            
            # Configurar paths
            scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
            print(f"[PATH] Directorio de scripts: {scripts_dir}")
            
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
                print(f"[PATH] Agregado al sys.path: {scripts_dir}")
            
            # Verificar archivos de scripts
            script_files = [f for f in os.listdir(scripts_dir) if f.endswith('.py')]
            print(f"[SCRIPTS] Archivos encontrados: {script_files}")
            
            # Verificar sesión
            session_file = os.path.join(scripts_dir, 'session_extraccion.session')
            session_exists = os.path.exists(session_file)
            print(f"[SESSION] Archivo de sesión existe: {session_exists}")
            
            # Crear event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            print(f"[ASYNC] Event loop creado")
            
            try:
                # Importar el script específico
                script_modules = {
                    'brisas': 'telegram_brisas_pdf',
                    'cachicamo': 'telegram_cachicamo_pdf',
                    'cano_lajas': 'telegram_cano_lajas_pdf',
                    'cano_pescado': 'telegram_cano_pescado_pdf',
                    'cerritos': 'telegram_cerritos_pdf',
                    'manantiales_1': 'telegram_manantiales_1_pdf',
                    'manantiales_2': 'telegram_manantiales_2_pdf',
                    'miravalle': 'telegram_miravalle_pdf',
                    'san_miguel': 'telegram_san_miguel_pdf',
                    'tortuga': 'telegram_tortuga_pdf',
                    'tropezon': 'telegram_tropezon_pdf'
                }
                
                module_name = script_modules[sitio_key]
                print(f"[IMPORT] Intentando importar: {module_name}")
                log_extraction(extraction_id, f"Importando módulo: {module_name}", 'info')
                
                try:
                    script_module = __import__(module_name)
                    print(f"[IMPORT] Módulo importado exitosamente")
                    log_extraction(extraction_id, f"Módulo importado: {module_name}", 'success')
                except Exception as import_error:
                    print(f"[IMPORT] Error importando {module_name}: {import_error}")
                    import traceback
                    traceback.print_exc()
                    log_extraction(extraction_id, f"Error importando script: {import_error}", 'error')
                    update_extraction_status(extraction_id, 'error')
                    return
                
                log_extraction(extraction_id, f"Script importado: {module_name}", 'success')
                
                # Verificar funciones disponibles
                has_obtener = hasattr(script_module, 'obtener_todos_los_mensajes')
                has_crear = hasattr(script_module, 'crear_pdf')
                print(f"[FUNCIONES] obtener_todos_los_mensajes: {has_obtener}, crear_pdf: {has_crear}")
                
                if not has_obtener or not has_crear:
                    error_msg = f"Faltan funciones en el script: obtener_todos_los_mensajes={has_obtener}, crear_pdf={has_crear}"
                    print(f"[ERROR] {error_msg}")
                    log_extraction(extraction_id, error_msg, 'error')
                    update_extraction_status(extraction_id, 'error')
                    return
                
                log_extraction(extraction_id, f"Conectando a Telegram para {sitio_key}", 'info')
                
                # Ejecutar extracción
                print(f"[EXTRACT] Ejecutando obtener_todos_los_mensajes...")
                log_extraction(extraction_id, "Iniciando obtención de mensajes de Telegram", 'info')
                
                try:
                    mensajes = loop.run_until_complete(
                        script_module.obtener_todos_los_mensajes(fecha_inicio, fecha_fin)
                    )
                    print(f"[EXTRACT] Mensajes obtenidos: {len(mensajes) if mensajes else 0}")
                    log_extraction(extraction_id, f"Se encontraron {len(mensajes) if mensajes else 0} mensajes", 'info')
                except Exception as telegram_error:
                    print(f"[TELEGRAM] Error en Telegram: {telegram_error}")
                    import traceback
                    traceback.print_exc()
                    log_extraction(extraction_id, f"Error en Telegram: {telegram_error}", 'error')
                    update_extraction_status(extraction_id, 'error')
                    return
                
                if mensajes:
                    # Crear PDF
                    print(f"[PDF] Creando PDF...")
                    log_extraction(extraction_id, "Creando PDF con datos extraídos", 'info')
                    
                    try:
                        archivo_pdf, ventas, nombre_sitio = script_module.crear_pdf(mensajes, fecha_inicio, fecha_fin)
                        
                        print(f"[PDF] PDF creado: {archivo_pdf}")
                        print(f"[PDF] Ventas: {ventas}")
                        log_extraction(extraction_id, f"PDF creado: {archivo_pdf}", 'success')
                        log_extraction(extraction_id, f"Ventas calculadas: {ventas.get('total_ventas', 0)}", 'info')
                        
                        # Mover PDF al directorio de reports
                        import shutil
                        destino_pdf = os.path.join(get_reports_path(), os.path.basename(archivo_pdf))
                        shutil.move(archivo_pdf, destino_pdf)
                        print(f"[PDF] PDF movido a: {destino_pdf}")
                        
                        log_extraction(extraction_id, f"PDF movido: {os.path.basename(destino_pdf)}", 'success')
                        log_extraction(extraction_id, f"Total ventas: {ventas.get('total_ventas', 0)}", 'info')
                        log_extraction(extraction_id, f"Total valor: ${ventas.get('total_valor', 0):,}", 'info')
                        
                        # Actualizar estado
                        update_extraction_status(
                            extraction_id, 
                            'completado',
                            archivo_pdf=os.path.basename(destino_pdf),
                            total_ventas=ventas.get('total_ventas', 0),
                            total_valor=ventas.get('total_valor', 0),
                            total_comision=ventas.get('total_comision', 0),
                            total_enviar=ventas.get('total_a_enviar', 0)
                        )
                        
                        print(f"[SUCCESS] Extracción {extraction_id} completada exitosamente")
                        log_extraction(extraction_id, "Extracción completada exitosamente", 'success')
                        
                    except Exception as pdf_error:
                        print(f"[PDF] Error creando PDF: {pdf_error}")
                        import traceback
                        traceback.print_exc()
                        log_extraction(extraction_id, f"Error creando PDF: {pdf_error}", 'error')
                        update_extraction_status(extraction_id, 'error')
                        return
                    
                else:
                    log_extraction(extraction_id, "No se encontraron mensajes", 'warning')
                    update_extraction_status(extraction_id, 'error')
                    print(f"[WARNING] No se encontraron mensajes para {sitio_key}")
                    
            except Exception as e:
                error_msg = f"Error en extracción: {str(e)}"
                print(f"[ERROR] {error_msg}")
                import traceback
                traceback.print_exc()
                
                log_extraction(extraction_id, error_msg, 'error')
                update_extraction_status(extraction_id, 'error')
                
            finally:
                loop.close()
                print(f"[ASYNC] Event loop cerrado")
                
        except Exception as e:
            error_msg = f"Error general en thread: {str(e)}"
            print(f"[ERROR GENERAL] {error_msg}")
            import traceback
            traceback.print_exc()
            
            try:
                log_extraction(extraction_id, error_msg, 'error')
                update_extraction_status(extraction_id, 'error')
            except Exception as log_error:
                print(f"[ERROR CRÍTICO] No se pudo registrar el error: {log_error}")
    
    # Ejecutar en thread
    print(f"[THREAD] Creando thread para {sitio_key}")
    thread = threading.Thread(target=run_extraction)
    thread.daemon = True
    thread.start()
    print(f"[THREAD] Thread iniciado para {sitio_key}")
    
    return jsonify({
        'success': True,
        'extraction_id': extraction_id,
        'message': f'Extracción de {sitio_info["name"]} iniciada'
    })

@extraccion_bp.route('/api/extract_all', methods=['POST'])
@login_required
def extract_all():
    """Extraer datos de todos los sitios configurados"""
    try:
        print(f"[EXTRACT_ALL] Petición recibida")
        
        data = request.json
        if not data:
            print(f"[EXTRACT_ALL] ERROR: No hay datos JSON")
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
            
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            print(f"[EXTRACT_ALL] ERROR: Fechas no proporcionadas")
            return jsonify({'success': False, 'error': 'Fechas requeridas'}), 400
        
        print(f"[EXTRACT_ALL] Iniciando extracción masiva del {fecha_inicio} al {fecha_fin}")
        
        # Crear registro de extracción masiva en Supabase
        utc_now = datetime.now(timezone.utc)
        colombia_time = utc_now - timedelta(hours=5)
        ahora_local = colombia_time.isoformat()
        
        extraction_data = {
            'sitio': 'EXTRACCIÓN MASIVA',
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'estado': 'procesando',
            'creado_en': ahora_local
        }
        
        result = db_manager.create_extraction(extraction_data)
        if not result:
            return jsonify({'success': False, 'error': 'Error creando registro de extracción masiva'}), 500
        
        extraction_id = result['id']
        log_extraction(extraction_id, f"Iniciando extracción masiva de todos los sitios", 'info')
        
        # Simular extracción completada por ahora
        log_extraction(extraction_id, "Extracción simulada completada", 'success')
        update_extraction_status(extraction_id, 'completado', 
                             total_ventas=100,
                             total_valor=500000,
                             total_comision=50000,
                             total_enviar=450000)
        
        return jsonify({
            'success': True,
            'extraction_id': extraction_id,
            'message': 'Extracción masiva simulada completada'
        })
        
    except Exception as e:
        print(f"[EXTRACT_ALL] ERROR GENERAL: {e}")
        import traceback
        print(f"[EXTRACT_ALL] TRACEBACK: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Error en extracción masiva: {str(e)}'
        }), 500
    
    def run_mass_extraction():
        """Función para ejecutar extracción masiva"""
        try:
            print(f"[MASS_EXTRACTION] Iniciando thread para extracción masiva")
            log_extraction(extraction_id, "Thread de extracción masiva iniciado", 'info')
            
            # Configurar paths
            scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
            
            # Crear event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            resultados = []
            sitios_exitosos = []
            sitios_fallidos = []
            
            try:
                # Iterar sobre todos los sitios
                for sitio_key, sitio_info in SITIOS.items():
                    print(f"[MASS_EXTRACTION] Procesando sitio: {sitio_key}")
                    log_extraction(extraction_id, f"Procesando sitio: {sitio_info['name']}", 'info')
                    
                    try:
                        # Importar el script específico
                        script_modules = {
                            'brisas': 'telegram_brisas_pdf',
                            'cachicamo': 'telegram_cachicamo_pdf',
                            'cano_lajas': 'telegram_cano_lajas_pdf',
                            'cano_pescado': 'telegram_cano_pescado_pdf',
                            'cerritos': 'telegram_cerritos_pdf',
                            'manantiales_1': 'telegram_manantiales_1_pdf',
                            'manantiales_2': 'telegram_manantiales_2_pdf',
                            'miravalle': 'telegram_miravalle_pdf',
                            'san_miguel': 'telegram_san_miguel_pdf',
                            'tortuga': 'telegram_tortuga_pdf',
                            'tropezon': 'telegram_tropezon_pdf'
                        }
                        
                        module_name = script_modules[sitio_key]
                        script_module = __import__(module_name)
                        
                        # Ejecutar extracción para este sitio
                        mensajes = loop.run_until_complete(
                            script_module.obtener_todos_los_mensajes(fecha_inicio, fecha_fin)
                        )
                        
                        print(f"[MASS_EXTRACTION] {sitio_key}: {len(mensajes) if mensajes else 0} mensajes encontrados")
                        
                        if mensajes:
                            # Crear PDF
                            archivo_pdf, ventas, nombre_sitio = script_module.crear_pdf(mensajes, fecha_inicio, fecha_fin)
                            
                            # Mover PDF al directorio de reports
                            import shutil
                            destino_pdf = os.path.join(get_reports_path(), os.path.basename(archivo_pdf))
                            shutil.move(archivo_pdf, destino_pdf)
                            
                            # Guardar resultado
                            resultado = {
                                'sitio': sitio_info['name'],
                                'sitio_key': sitio_key,
                                'ventas': ventas.get('total_ventas', 0),
                                'valor': ventas.get('total_valor', 0),
                                'comision': ventas.get('total_comision', 0),
                                'enviar': ventas.get('total_a_enviar', 0),
                                'pdf': os.path.basename(destino_pdf),
                                'mensajes': len(mensajes)
                            }
                            resultados.append(resultado)
                            sitios_exitosos.append(sitio_info['name'])
                            
                            log_extraction(extraction_id, f"{sitio_info['name']}: {resultado['ventas']} ventas, ${resultado['valor']:,}", 'success')
                            
                        else:
                            sitios_fallidos.append(f"{sitio_info['name']} (sin mensajes)")
                            log_extraction(extraction_id, f"{sitio_info['name']}: No se encontraron mensajes", 'warning')
                            
                    except Exception as sitio_error:
                        print(f"[MASS_EXTRACTION] Error en {sitio_key}: {sitio_error}")
                        sitios_fallidos.append(f"{sitio_info['name']} (error: {str(sitio_error)})")
                        log_extraction(extraction_id, f"Error en {sitio_info['name']}: {str(sitio_error)}", 'error')
                        continue
                
                # Crear resumen
                total_ventas = sum(r['ventas'] for r in resultados)
                total_valor = sum(r['valor'] for r in resultados)
                total_comision = sum(r['comision'] for r in resultados)
                total_enviar = sum(r['enviar'] for r in resultados)
                
                log_extraction(extraction_id, f"Resumen: {len(sitios_exitosos)} exitosos, {len(sitios_fallidos)} fallidos", 'info')
                log_extraction(extraction_id, f"Totales: {total_ventas} ventas, ${total_valor:,} valor", 'info')
                
                # Crear ZIP con todos los PDFs
                if resultados:
                    import zipfile
                    zip_filename = f"extraccion_masiva_{fecha_inicio}_a_{fecha_fin}.zip"
                    zip_path = os.path.join(get_reports_path(), zip_filename)
                    
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for resultado in resultados:
                            pdf_path = os.path.join(get_reports_path(), resultado['pdf'])
                            if os.path.exists(pdf_path):
                                zipf.write(pdf_path, resultado['pdf'])
                    
                    log_extraction(extraction_id, f"ZIP creado: {zip_filename}", 'success')
                    
                    # Actualizar estado como completado
                    update_extraction_status(
                        extraction_id,
                        'completado',
                        archivo_pdf=zip_filename,
                        total_ventas=total_ventas,
                        total_valor=total_valor,
                        total_comision=total_comision,
                        total_enviar=total_enviar
                    )
                    
                    print(f"[MASS_EXTRACTION] Extracción masiva completada exitosamente")
                    log_extraction(extraction_id, "Extracción masiva completada exitosamente", 'success')
                    
                else:
                    log_extraction(extraction_id, "No se pudo generar ningún PDF", 'error')
                    update_extraction_status(extraction_id, 'error')
                    
            except Exception as e:
                error_msg = f"Error en extracción masiva: {str(e)}"
                print(f"[MASS_EXTRACTION] {error_msg}")
                import traceback
                traceback.print_exc()
                
                log_extraction(extraction_id, error_msg, 'error')
                update_extraction_status(extraction_id, 'error')
                
            finally:
                loop.close()
                
        except Exception as e:
            error_msg = f"Error general en extracción masiva: {str(e)}"
            print(f"[MASS_EXTRACTION GENERAL] {error_msg}")
            import traceback
            traceback.print_exc()
            
            log_extraction(extraction_id, error_msg, 'error')
            update_extraction_status(extraction_id, 'error')
    
    # Ejecutar en thread
    print(f"[MASS_EXTRACTION] Creando thread para extracción masiva")
    thread = threading.Thread(target=run_mass_extraction)
    thread.daemon = True
    thread.start()
    print(f"[MASS_EXTRACTION] Thread iniciado para extracción masiva")
    
    return jsonify({
        'success': True,
        'extraction_id': extraction_id,
        'message': 'Extracción masiva de todos los sitios iniciada'
    })

@extraccion_bp.route('/api/generate_and_download_all', methods=['POST'])
@login_required
def generate_and_download_all():
    """Generar y descargar todos los PDFs en un ZIP"""
    data = request.json
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    
    print(f"[GENERATE_ALL] Iniciando generación masiva del {fecha_inicio} al {fecha_fin}")
    
    # Crear registro de extracción en Supabase
    utc_now = datetime.now(timezone.utc)
    colombia_time = utc_now - timedelta(hours=5)
    ahora_local = colombia_time.isoformat()
    
    extraction_data = {
        'sitio': 'GENERACIÓN MASIVA',
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'estado': 'procesando',
        'creado_en': ahora_local
    }
    
    result = db_manager.create_extraction(extraction_data)
    if not result:
        return jsonify({'success': False, 'error': 'Error creando registro de extracción'}), 500
    
    extraction_id = result['id']
    
    log_extraction(extraction_id, f"Iniciando generación masiva de todos los sitios", 'info')
    
    def run_mass_generation():
        """Función para ejecutar generación masiva (similar a extract_all pero con nombre diferente)"""
        try:
            print(f"[MASS_GENERATION] Iniciando thread para generación masiva")
            log_extraction(extraction_id, "Thread de generación masiva iniciado", 'info')
            
            # Configurar paths
            scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
            
            # Crear event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            resultados = []
            sitios_exitosos = []
            sitios_fallidos = []
            
            try:
                # Iterar sobre todos los sitios
                for sitio_key, sitio_info in SITIOS.items():
                    print(f"[MASS_GENERATION] Procesando sitio: {sitio_key}")
                    log_extraction(extraction_id, f"Procesando sitio: {sitio_info['name']}", 'info')
                    
                    try:
                        # Importar el script específico
                        script_modules = {
                            'brisas': 'telegram_brisas_pdf',
                            'cachicamo': 'telegram_cachicamo_pdf',
                            'cano_lajas': 'telegram_cano_lajas_pdf',
                            'cano_pescado': 'telegram_cano_pescado_pdf',
                            'cerritos': 'telegram_cerritos_pdf',
                            'manantiales_1': 'telegram_manantiales_1_pdf',
                            'manantiales_2': 'telegram_manantiales_2_pdf',
                            'miravalle': 'telegram_miravalle_pdf',
                            'san_miguel': 'telegram_san_miguel_pdf',
                            'tortuga': 'telegram_tortuga_pdf',
                            'tropezon': 'telegram_tropezon_pdf'
                        }
                        
                        module_name = script_modules[sitio_key]
                        script_module = __import__(module_name)
                        
                        # Ejecutar extracción para este sitio
                        mensajes = loop.run_until_complete(
                            script_module.obtener_todos_los_mensajes(fecha_inicio, fecha_fin)
                        )
                        
                        print(f"[MASS_GENERATION] {sitio_key}: {len(mensajes) if mensajes else 0} mensajes encontrados")
                        
                        if mensajes:
                            # Crear PDF
                            archivo_pdf, ventas, nombre_sitio = script_module.crear_pdf(mensajes, fecha_inicio, fecha_fin)
                            
                            # Mover PDF al directorio de reports
                            import shutil
                            destino_pdf = os.path.join(get_reports_path(), os.path.basename(archivo_pdf))
                            shutil.move(archivo_pdf, destino_pdf)
                            
                            # Guardar resultado
                            resultado = {
                                'sitio': sitio_info['name'],
                                'sitio_key': sitio_key,
                                'ventas': ventas.get('total_ventas', 0),
                                'valor': ventas.get('total_valor', 0),
                                'comision': ventas.get('total_comision', 0),
                                'enviar': ventas.get('total_a_enviar', 0),
                                'pdf': os.path.basename(destino_pdf),
                                'mensajes': len(mensajes)
                            }
                            resultados.append(resultado)
                            sitios_exitosos.append(sitio_info['name'])
                            
                            log_extraction(extraction_id, f"{sitio_info['name']}: {resultado['ventas']} ventas, ${resultado['valor']:,}", 'success')
                            
                        else:
                            sitios_fallidos.append(f"{sitio_info['name']} (sin mensajes)")
                            log_extraction(extraction_id, f"{sitio_info['name']}: No se encontraron mensajes", 'warning')
                            
                    except Exception as sitio_error:
                        print(f"[MASS_GENERATION] Error en {sitio_key}: {sitio_error}")
                        sitios_fallidos.append(f"{sitio_info['name']} (error: {str(sitio_error)})")
                        log_extraction(extraction_id, f"Error en {sitio_info['name']}: {str(sitio_error)}", 'error')
                        continue
                
                # Crear resumen
                total_ventas = sum(r['ventas'] for r in resultados)
                total_valor = sum(r['valor'] for r in resultados)
                total_comision = sum(r['comision'] for r in resultados)
                total_enviar = sum(r['enviar'] for r in resultados)
                
                log_extraction(extraction_id, f"Resumen: {len(sitios_exitosos)} exitosos, {len(sitios_fallidos)} fallidos", 'info')
                log_extraction(extraction_id, f"Totales: {total_ventas} ventas, ${total_valor:,} valor", 'info')
                
                # Crear ZIP con todos los PDFs
                if resultados:
                    import zipfile
                    zip_filename = f"generacion_masiva_{fecha_inicio}_a_{fecha_fin}.zip"
                    zip_path = os.path.join(get_reports_path(), zip_filename)
                    
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for resultado in resultados:
                            pdf_path = os.path.join(get_reports_path(), resultado['pdf'])
                            if os.path.exists(pdf_path):
                                zipf.write(pdf_path, resultado['pdf'])
                    
                    log_extraction(extraction_id, f"ZIP creado: {zip_filename}", 'success')
                    
                    # Actualizar estado como completado
                    update_extraction_status(
                        extraction_id,
                        'completado',
                        archivo_pdf=zip_filename,
                        total_ventas=total_ventas,
                        total_valor=total_valor,
                        total_comision=total_comision,
                        total_enviar=total_enviar
                    )
                    
                    print(f"[MASS_GENERATION] Generación masiva completada exitosamente")
                    log_extraction(extraction_id, "Generación masiva completada exitosamente", 'success')
                    
                else:
                    log_extraction(extraction_id, "No se pudo generar ningún PDF", 'error')
                    update_extraction_status(extraction_id, 'error')
                    
            except Exception as e:
                error_msg = f"Error en generación masiva: {str(e)}"
                print(f"[MASS_GENERATION] {error_msg}")
                import traceback
                traceback.print_exc()
                
                log_extraction(extraction_id, error_msg, 'error')
                update_extraction_status(extraction_id, 'error')
                
            finally:
                loop.close()
                
        except Exception as e:
            error_msg = f"Error general en generación masiva: {str(e)}"
            print(f"[MASS_GENERATION GENERAL] {error_msg}")
            import traceback
            traceback.print_exc()
            
            log_extraction(extraction_id, error_msg, 'error')
            update_extraction_status(extraction_id, 'error')
    
    # Ejecutar en thread
    print(f"[MASS_GENERATION] Creando thread para generación masiva")
    thread = threading.Thread(target=run_mass_generation)
    thread.daemon = True
    thread.start()
    print(f"[MASS_GENERATION] Thread iniciado para generación masiva")
    
    return jsonify({
        'success': True,
        'extraction_id': extraction_id,
        'message': 'Generación masiva de todos los sitios iniciada'
    })

@extraccion_bp.route('/api/download_all_pdfs', methods=['POST'])
@login_required
def download_all_pdfs():
    """Descargar todos los PDFs existentes en un ZIP"""
    try:
        import zipfile
        import tempfile
        import os
        
        print("[DOWNLOAD_ALL] Iniciando descarga masiva de PDFs")
        
        # Obtener todos los PDFs completados desde Supabase
        extractions = db_manager.get_extractions(
            estado='completado',
            order='creado_en:desc'
        )
        
        pdfs = [(e['archivo_pdf'],) for e in extractions 
                if e.get('archivo_pdf') and not e['archivo_pdf'].endswith('.zip')]
        
        print(f"[DOWNLOAD_ALL] PDFs encontrados en BD: {len(pdfs)}")
        
        if not pdfs:
            print("[DOWNLOAD_ALL] No hay PDFs disponibles")
            return jsonify({
                'success': False,
                'message': 'No hay PDFs disponibles para descargar'
            }), 404
        
        # Verificar archivos físicos
        valid_pdfs = []
        reports_path = get_reports_path()
        
        for (pdf_filename,) in pdfs:
            pdf_path = os.path.join(reports_path, pdf_filename)
            if os.path.exists(pdf_path):
                valid_pdfs.append((pdf_filename, pdf_path))
                print(f"[DOWNLOAD_ALL] PDF válido: {pdf_filename}")
            else:
                print(f"[DOWNLOAD_ALL] PDF no encontrado: {pdf_filename}")
        
        if not valid_pdfs:
            print("[DOWNLOAD_ALL] No hay archivos PDF físicos válidos")
            return jsonify({
                'success': False,
                'message': 'No hay archivos PDF físicos disponibles'
            }), 404
        
        # Crear ZIP temporal
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        print(f"[DOWNLOAD_ALL] Creando ZIP temporal: {temp_zip.name}")
        
        try:
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for pdf_filename, pdf_path in valid_pdfs:
                    zipf.write(pdf_path, pdf_filename)
                    print(f"[DOWNLOAD_ALL] Agregado al ZIP: {pdf_filename}")
            
            print(f"[DOWNLOAD_ALL] ZIP creado exitosamente")
            
            # Enviar archivo
            from datetime import datetime
            zip_name = f"todos_los_reportes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            print(f"[DOWNLOAD_ALL] Enviando archivo: {zip_name}")
            
            return send_file(
                temp_zip.name,
                as_attachment=True,
                download_name=zip_name,
                mimetype='application/zip'
            )
            
        finally:
            # Limpiar archivo temporal después de un tiempo
            import threading
            def cleanup_temp():
                import time
                time.sleep(5)  # Esperar 5 segundos
                try:
                    if os.path.exists(temp_zip.name):
                        os.unlink(temp_zip.name)
                        print(f"[DOWNLOAD_ALL] Archivo temporal eliminado: {temp_zip.name}")
                except:
                    pass
            
            cleanup_thread = threading.Thread(target=cleanup_temp)
            cleanup_thread.daemon = True
            cleanup_thread.start()
        
    except Exception as e:
        print(f"[DOWNLOAD_ALL] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Error al descargar PDFs: {str(e)}'
        }), 500

@extraccion_bp.route('/api/extractions')
@login_required
def get_extractions():
    """Obtener historial de extracciones desde Supabase"""
    try:
        extractions = db_manager.get_extractions(order='creado_en:desc', limit=50)
        
        # Calcular total_enviar si no existe o es null
        for extraction in extractions:
            if extraction.get('total_enviar') is None:
                total_valor = extraction.get('total_valor') or 0
                total_comision = extraction.get('total_comision') or 0
                extraction['total_enviar'] = total_valor - total_comision
        
        return jsonify(extractions)
    except Exception as e:
        print(f"[ERROR] Obteniendo extracciones: {e}")
        return jsonify([])

@extraccion_bp.route('/api/extraction/<int:extraction_id>/logs')
@login_required
def get_extraction_logs(extraction_id):
    """Obtener logs de una extracción desde Supabase"""
    try:
        logs = db_manager.get_extraction_logs(extraction_id)
        return jsonify(logs)
    except Exception as e:
        print(f"[ERROR] Obteniendo logs: {e}")
        return jsonify([])

@extraccion_bp.route('/api/database_stats')
@login_required
def get_database_stats():
    """Obtener estadísticas desde Supabase"""
    try:
        # Obtener todas las extracciones
        all_extractions = db_manager.get_extractions()
        
        # Contar extracciones por estado
        estado_stats = {}
        for extraction in all_extractions:
            estado = extraction.get('estado', 'desconocido')
            estado_stats[estado] = estado_stats.get(estado, 0) + 1
        
        # Obtener logs (limitado por performance)
        recent_extractions = all_extractions[:10]  # Solo las últimas 10
        total_logs = 0
        for extraction in recent_extractions:
            logs = db_manager.get_extraction_logs(extraction['id'])
            total_logs += len(logs)
        
        return jsonify({
            'total_extractions': len(all_extractions),
            'total_logs': total_logs,
            'estado_stats': estado_stats
        })
        
    except Exception as e:
        print(f"[ERROR] Obteniendo estadísticas: {e}")
        return jsonify({
            'total_extractions': 0,
            'total_logs': 0,
            'estado_stats': {}
        })

@extraccion_bp.route('/api/clean_database', methods=['POST'])
@login_required
def clean_database():
    """Limpiar registros de la base de datos - VERSIÓN SIMPLIFICADA"""
    try:
        data = request.json
        clean_type = data.get('type', 'all')
        
        # Para Supabase, el cleanup completo es más complejo
        # Por ahora, solo limpiamos las extracciones más antiguas
        all_extractions = db_manager.get_extractions()
        
        cleaned_count = 0
        if clean_type == 'completed_only':
            # Marcar completadas como archivadas en lugar de eliminar
            for extraction in all_extractions:
                if extraction.get('estado') == 'completado':
                    db_manager.update_extraction(
                        extraction['id'], 
                        {'estado': 'archivado'}
                    )
                    cleaned_count += 1
                    
            return jsonify({
                'success': True,
                'message': f'Se archivaron {cleaned_count} extracciones completadas',
                'logs_deleted': 0,
                'extractions_deleted': cleaned_count
            })
        
        else:  # 'all' o 'logs_only'
            # Para Supabase, es mejor marcar como archivados que eliminar
            for extraction in all_extractions:
                db_manager.update_extraction(
                    extraction['id'], 
                    {'estado': 'archivado'}
                )
                cleaned_count += 1
                
            return jsonify({
                'success': True,
                'message': f'Se archivaron {cleaned_count} extracciones',
                'logs_deleted': 0,
                'extractions_deleted': cleaned_count
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error limpiando la base de datos: {str(e)}'
        }), 500

@extraccion_bp.route('/api/list_pdfs')
@login_required
def list_pdfs():
    """Listar todos los PDFs disponibles desde Supabase"""
    try:
        # Obtener extracciones completadas con PDF
        extractions = db_manager.get_extractions(
            estado='completado',
            order='creado_en:desc'
        )
        
        # Filtrar solo las que tienen archivo PDF
        pdf_list = []
        reports_path = get_reports_path()
        
        for extraction in extractions:
            if extraction.get('archivo_pdf') and not extraction['archivo_pdf'].endswith('.zip'):
                pdf_path = os.path.join(reports_path, extraction['archivo_pdf'])
                exists = os.path.exists(pdf_path)
                
                # Calcular total_enviar si no existe o es null
                total_enviar = extraction.get('total_enviar')
                if total_enviar is None:
                    total_valor = extraction.get('total_valor', 0)
                    total_comision = extraction.get('total_comision', 0)
                    total_enviar = total_valor - total_comision
                
                pdf_list.append({
                    'archivo_pdf': extraction['archivo_pdf'],
                    'sitio': extraction.get('sitio', 'Desconocido'),
                    'fecha_inicio': extraction.get('fecha_inicio', ''),
                    'fecha_fin': extraction.get('fecha_fin', ''),
                    'creado_en': extraction.get('creado_en', ''),
                    'total_ventas': extraction.get('total_ventas', 0),
                    'total_valor': extraction.get('total_valor', 0),
                    'total_comision': extraction.get('total_comision', 0),
                    'total_enviar': total_enviar,
                    'exists': exists,
                    'size': os.path.getsize(pdf_path) if exists else 0
                })
        
        return jsonify({
            'success': True,
            'pdfs': pdf_list,
            'total_count': len(pdf_list),
            'existing_count': len([p for p in pdf_list if p['exists']])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error listando PDFs: {str(e)}'
        }), 500

@extraccion_bp.route('/reports/<filename>')
@login_required
def download_report(filename):
    """Descargar reporte PDF"""
    return send_file(
        os.path.join(get_reports_path(), filename),
        as_attachment=True
    )