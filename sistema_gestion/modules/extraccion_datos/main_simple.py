"""
Módulo de Extracción de Datos - Versión Simplificada
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
from werkzeug.utils import secure_filename

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

def get_db_path():
    """Obtener ruta de la base de datos del módulo - ya no se usa con Supabase"""
    # Obtener ruta absoluta al directorio principal del proyecto
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(current_dir, 'instance', 'extractions.db')

def get_reports_path():
    """Obtener ruta del directorio de reportes"""
    # Obtener ruta absoluta al directorio principal del proyecto
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    reports_path = os.path.join(current_dir, 'static', 'reports')
    os.makedirs(reports_path, exist_ok=True)
    return reports_path

def init_db():
    """Inicialización - ahora usa Supabase, no necesita SQLite"""
    print("[INIT] Sistema usa Supabase - no se requiere inicialización local")

def log_extraction(extraction_id, mensaje, tipo='info'):
    """Guardar log de extracción en Supabase"""
    try:
        from datetime import datetime, timezone, timedelta
        
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
        print(f"[LOG SUPABASE] ID:{extraction_id} - {tipo} - {mensaje}")
        return result
    except Exception as e:
        print(f"[ERROR] Guardando log en Supabase: {e}")
        return None

def update_extraction_status(extraction_id, estado, **kwargs):
    """Actualizar estado de extracción en Supabase"""
    try:
        from datetime import datetime, timezone, timedelta
        
        # Forzar hora local de Colombia (UTC-5)
        utc_now = datetime.now(timezone.utc)
        colombia_time = utc_now - timedelta(hours=5)
        ahora_local = colombia_time.isoformat()
        
        # Preparar datos de actualización
        update_data = {
            'estado': estado,
            'completado_en': ahora_local if estado == 'completado' else '',
            'actualizado_en': ahora_local,
            'archivo_pdf': ''  # Usar string vacío en lugar de None
        }
        
        # Agregar campos adicionales
        update_data.update(kwargs)
        
        result = db_manager.update_extraction(extraction_id, update_data)
        print(f"[STATUS SUPABASE] ID:{extraction_id} - {estado}")
        return result
    except Exception as e:
        print(f"[ERROR] Actualizando estado en Supabase: {e}")
        return False

@extraccion_bp.route('/')
@login_required
def index():
    """Página principal del módulo de extracción de datos"""
    try:
        init_db()
        print("Base de datos inicializada correctamente")
    except Exception as e:
        print(f"Error inicializando base de datos: {e}")
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

@extraccion_bp.route('/api/extract_all', methods=['POST'])
@login_required
def extract_all():
    """Extraer datos de todos los sitios configurados"""
    data = request.json
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    
    print(f"Extracción masiva solicitada del {fecha_inicio} al {fecha_fin}")
    
    # Crear extracción masiva en Supabase
    from datetime import datetime, timezone, timedelta
    
    utc_now = datetime.now(timezone.utc)
    colombia_time = utc_now - timedelta(hours=5)
    ahora_local = colombia_time.isoformat()
    
    extraction_data = {
        'sitio': 'EXTRACCIÓN MASIVA',
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'estado': 'procesando',
        'creado_en': ahora_local,
        # Valores por defecto para cumplir constraints
        'total_ventas': 0,
        'total_valor': 0,
        'total_comision': 0,
        'total_enviar': 0,
        'archivo_pdf': ''
    }
    
    result = db_manager.create_extraction(extraction_data)
    if not result:
        return jsonify({'success': False, 'error': 'Error creando extracción masiva en Supabase'}), 500
    
    extraction_id = result['id']
    log_extraction(extraction_id, f"Iniciando extracción masiva en Supabase", 'info')
    print(f"[SUPABASE] Extracción masiva creada: ID {extraction_id}")
    
    def run_mass_extraction():
        print(f"[MASS_EXTRACTION] Iniciando extracción masiva REAL (ID: {extraction_id})")
        
        # Importar aquí para evitar problemas de contexto
        import asyncio
        import sys
        import os
        
        # Configurar paths
        scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        
        # Crear event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            log_extraction(extraction_id, "Iniciando extracción masiva de todos los sitios", 'info')
            
            # Scripts de todos los sitios
            sitios_scripts = {
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
            
            total_ventas = 0
            total_valor = 0
            total_comision = 0
            sitios_procesados = 0
            
            for sitio_key, module_name in sitios_scripts.items():
                try:
                    print(f"[MASS] Procesando sitio: {sitio_key}")
                    log_extraction(extraction_id, f"Procesando sitio: {sitio_key}", 'info')
                    
                    script_module = __import__(module_name)
                    
                    # Ejecutar extracción REAL
                    mensajes = loop.run_until_complete(
                        script_module.obtener_todos_los_mensajes(fecha_inicio, fecha_fin)
                    )
                    
                    if mensajes:
                        log_extraction(extraction_id, f"{sitio_key}: {len(mensajes)} mensajes encontrados", 'success')
                        
                        # Crear PDF REAL
                        archivo_pdf, ventas, nombre_sitio = script_module.crear_pdf(mensajes, fecha_inicio, fecha_fin)
                        
                        # Mover PDF al directorio de reports
                        import shutil
                        destino_pdf = os.path.join(get_reports_path(), os.path.basename(archivo_pdf))
                        shutil.move(archivo_pdf, destino_pdf)
                        
                        log_extraction(extraction_id, f"{sitio_key}: PDF creado {os.path.basename(destino_pdf)}", 'success')
                        
                        # Acumular totales
                        total_ventas += ventas['total_ventas']
                        total_valor += ventas['total_valor']
                        total_comision += ventas['total_comision']
                        sitios_procesados += 1
                        
                        print(f"[MASS] {sitio_key}: {len(mensajes)} mensajes, ${ventas['total_valor']} valor")
                    else:
                        log_extraction(extraction_id, f"{sitio_key}: No se encontraron mensajes", 'warning')
                        
                except Exception as e:
                    log_extraction(extraction_id, f"{sitio_key}: Error - {str(e)}", 'error')
                    print(f"[MASS] Error en {sitio_key}: {e}")
                    continue
            
            total_enviar = total_valor - total_comision
            
            # Crear ZIP con todos los PDFs generados
            zip_filename = f"reporte_completo_{fecha_inicio.replace('-', '')}_al_{fecha_fin.replace('-', '')}.zip"
            zip_path = os.path.join(get_reports_path(), zip_filename)
            
            try:
                import glob
                from datetime import datetime
                
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    pdf_files = []
                    
                    # Buscar TODOS los PDFs generados recientemente
                    fecha_actual = datetime.now()
                    
                    for filename in os.listdir(get_reports_path()):
                        if filename.endswith('.pdf'):
                            pdf_path = os.path.join(get_reports_path(), filename)
                            
                            # Verificar si el PDF es reciente (de esta extracción)
                            try:
                                file_time = datetime.fromtimestamp(os.path.getmtime(pdf_path))
                                time_diff = (fecha_actual - file_time).total_seconds()
                                
                                # Si fue modificado en los últimos 5 minutos, lo incluimos
                                if time_diff < 300:  # 5 minutos
                                    zipf.write(pdf_path, filename)
                                    pdf_files.append(filename)
                                    print(f"[MASS] Agregando al ZIP: {filename}")
                            except:
                                # Si no podemos leer el tiempo, lo incluimos por seguridad
                                zipf.write(pdf_path, filename)
                                pdf_files.append(filename)
                    
                    log_extraction(extraction_id, f"ZIP creado con {len(pdf_files)} PDFs: {zip_filename}", 'success')
                    print(f"[MASS] ZIP creado: {zip_filename} con {len(pdf_files)} archivos")
                    
            except Exception as e:
                log_extraction(extraction_id, f"Error creando ZIP: {str(e)}", 'error')
                print(f"[MASS] Error creando ZIP: {e}")
            
            # Actualizar con datos REALES y archivo ZIP
            update_extraction_status(extraction_id, 'completado',
                                 archivo_pdf=zip_filename if os.path.exists(zip_path) else '',
                                 total_ventas=total_ventas,
                                 total_valor=total_valor,
                                 total_comision=total_comision,
                                 total_enviar=total_enviar)
            
            log_extraction(extraction_id, f"Extracción masiva completada: {sitios_procesados} sitios, ${total_valor} total", 'success')
            print(f"[MASS] Extracción masiva {extraction_id} completada: {sitios_procesados} sitios, ${total_valor}")
            
        except Exception as e:
            error_msg = f"Error en extracción masiva: {str(e)}"
            log_extraction(extraction_id, error_msg, 'error')
            update_extraction_status(extraction_id, 'error')
            print(f"[MASS] Error en extracción masiva {extraction_id}: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            loop.close()
    
    thread = threading.Thread(target=run_mass_extraction)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'extraction_id': extraction_id,
        'message': 'Extracción masiva simulada iniciada'
    })

@extraccion_bp.route('/api/extract_site/<sitio_key>', methods=['POST'])
@login_required
def extract_site(sitio_key):
    """Extraer datos de un sitio específico"""
    if sitio_key not in SITIOS:
        return jsonify({'success': False, 'error': 'Sitio no encontrado'}), 404
    
    data = request.json
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    
    sitio_info = SITIOS[sitio_key]
    
    # Crear registro de extracción en Supabase
    from datetime import datetime, timezone, timedelta
    
    utc_now = datetime.now(timezone.utc)
    colombia_time = utc_now - timedelta(hours=5)
    ahora_local = colombia_time.isoformat()
    
    extraction_data = {
        'sitio': sitio_info['name'],
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'estado': 'procesando',
        'creado_en': ahora_local,
        # Valores por defecto para cumplir constraints
        'total_ventas': 0,
        'total_valor': 0,
        'total_comision': 0,
        'total_enviar': 0,
        'archivo_pdf': None
    }
    
    result = db_manager.create_extraction(extraction_data)
    if not result:
        print(f"[ERROR] No se pudo crear extracción para {sitio_info['name']}")
        return jsonify({'success': False, 'error': 'Error creando extracción en Supabase'}), 500
    
    extraction_id = result['id']
    print(f"[SUPABASE] Extracción creada: ID {extraction_id}")
    
    def run_extraction():
        try:
            print(f"[WEB] Iniciando extracción REAL para {sitio_key} (ID: {extraction_id})")
            
            # Importar aquí para evitar problemas de contexto
            import asyncio
            import sys
            import os
            
            # Configurar paths
            scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
            
            # Crear event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
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
                
                log_extraction(extraction_id, f"Conectando a Telegram para {sitio_key}", 'info')
                
                # Ejecutar extracción REAL
                mensajes = loop.run_until_complete(
                    script_module.obtener_todos_los_mensajes(fecha_inicio, fecha_fin)
                )
                
                if mensajes:
                    log_extraction(extraction_id, f"Se encontraron {len(mensajes)} mensajes REALES", 'success')
                    
                    # Crear PDF REAL
                    archivo_pdf, ventas, nombre_sitio = script_module.crear_pdf(mensajes, fecha_inicio, fecha_fin)
                    
                    # Mover PDF al directorio de reports
                    import shutil
                    destino_pdf = os.path.join(get_reports_path(), os.path.basename(archivo_pdf))
                    shutil.move(archivo_pdf, destino_pdf)
                    
                    log_extraction(extraction_id, f"PDF REAL creado: {os.path.basename(destino_pdf)}", 'success')
                    
                    # Actualizar estado con datos REALES
                    update_extraction_status(
                        extraction_id, 
                        'completado',
                        archivo_pdf=os.path.basename(destino_pdf),
                        total_ventas=ventas['total_ventas'],
                        total_valor=ventas['total_valor'],
                        total_comision=ventas['total_comision'],
                        total_enviar=ventas['total_a_enviar']
                    )
                    
                    print(f"[WEB] Extracción REAL {extraction_id} completada exitosamente con {len(mensajes)} mensajes")
                    
                else:
                    log_extraction(extraction_id, "No se encontraron mensajes REALES", 'warning')
                    update_extraction_status(extraction_id, 'error')
                    
            except Exception as e:
                error_msg = f"Error en extracción REAL: {str(e)}"
                log_extraction(extraction_id, error_msg, 'error')
                update_extraction_status(extraction_id, 'error')
                print(f"[WEB] Error en extracción REAL {extraction_id}: {e}")
                import traceback
                traceback.print_exc()
                
            finally:
                loop.close()
                
        except Exception as e:
            error_msg = f"Error general en thread REAL: {str(e)}"
            log_extraction(extraction_id, error_msg, 'error')
            update_extraction_status(extraction_id, 'error')
            print(f"[WEB] Error general REAL {extraction_id}: {e}")
    
    # Ejecutar en thread
    import threading
    thread = threading.Thread(target=run_extraction)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'extraction_id': extraction_id,
        'message': f'Extracción de {sitio_info["name"]} iniciada'
    })

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
        
        print(f"[SUPABASE] Estadísticas: {len(all_extractions)} extracciones, {total_logs} logs")
        
        return jsonify({
            'total_extractions': len(all_extractions),
            'total_logs': total_logs,
            'estado_stats': estado_stats
        })
        
    except Exception as e:
        print(f"[ERROR] Obteniendo estadísticas de Supabase: {e}")
        return jsonify({
            'total_extractions': 0,
            'total_logs': 0,
            'estado_stats': {}
        })

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
        
        print(f"[SUPABASE] Obtenidas {len(extractions)} extracciones")
        return jsonify(extractions)
    except Exception as e:
        print(f"[ERROR] Obteniendo extracciones de Supabase: {e}")
        return jsonify([])

@extraccion_bp.route('/api/extraction/<int:extraction_id>/logs')
@login_required
def get_extraction_logs(extraction_id):
    """Obtener logs de una extracción desde Supabase"""
    try:
        logs = db_manager.get_extraction_logs(extraction_id)
        print(f"[SUPABASE] Obtenidos {len(logs)} logs para extracción {extraction_id}")
        return jsonify(logs)
    except Exception as e:
        print(f"[ERROR] Obteniendo logs de Supabase: {e}")
        return jsonify([])

@extraccion_bp.route('/reports/<filename>')
@login_required
def download_report(filename):
    """Descargar reporte PDF"""
    return send_file(
        os.path.join(get_reports_path(), filename),
        as_attachment=True
    )