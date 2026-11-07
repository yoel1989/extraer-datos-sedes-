from flask import Flask, render_template, request, jsonify, send_file
import asyncio
import threading
import os
import sys
from datetime import datetime
import sqlite3
import json
import zipfile
import tempfile
import traceback
from werkzeug.utils import secure_filename

# Fijar directorio de trabajo al de app.py
APP_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_DIR)
print(f"[INICIO] Directorio de trabajo: {APP_DIR}")
print(f"[INICIO] Sesión existe: {os.path.exists(os.path.join(APP_DIR, 'session_name.session'))}")

app = Flask(__name__)

# Configuración
app.config['REPORTS_FOLDER'] = 'reports'
app.config['DATABASE'] = 'extractions.db'

# Asegurar que los directorios existan
os.makedirs(app.config['REPORTS_FOLDER'], exist_ok=True)

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

def init_db():
    """Inicializar la base de datos SQLite"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extractions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sitio TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            archivo_pdf TEXT,
            total_ventas INTEGER DEFAULT 0,
            total_valor INTEGER DEFAULT 0,
            total_comision INTEGER DEFAULT 0,
            total_enviar INTEGER DEFAULT 0,
            estado TEXT DEFAULT 'pendiente',
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completado_en TIMESTAMP NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extraction_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            extraction_id INTEGER,
            mensaje TEXT,
            tipo TEXT DEFAULT 'info',
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (extraction_id) REFERENCES extractions (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def log_extraction(extraction_id, mensaje, tipo='info'):
    """Guardar log de extracción"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO extraction_logs (extraction_id, mensaje, tipo)
        VALUES (?, ?, ?)
    ''', (extraction_id, mensaje, tipo))
    conn.commit()
    conn.close()

def update_extraction_status(extraction_id, estado, **kwargs):
    """Actualizar estado de extracción"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    if kwargs:
        # Construir query dinámicamente
        set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [estado, extraction_id]
        cursor.execute(f'''
            UPDATE extractions 
            SET {set_clause}, estado = ?, completado_en = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', values)
    else:
        cursor.execute('''
            UPDATE extractions SET estado = ?, completado_en = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (estado, extraction_id))
    
    conn.commit()
    conn.close()

class TelegramExtractor:
    def __init__(self):
        self.current_extraction_id = None
        self.progress_callback = None
    
    def set_progress_callback(self, callback):
        self.progress_callback = callback
    
    def emit_progress(self, sitio, mensaje, tipo='info'):
        if self.progress_callback:
            self.progress_callback(sitio, mensaje, tipo)
        if self.current_extraction_id:
            log_extraction(self.current_extraction_id, f"{sitio}: {mensaje}", tipo)
    
    async def extract_site_data(self, sitio_key, fecha_inicio, fecha_fin):
        """Extraer datos de un sitio específico"""
        sitio_info = SITIOS[sitio_key]
        
        self.emit_progress(sitio_key, f"Iniciando extracción de {sitio_info['name']}", 'info')
        print(f"\n=== EXTRACCIÓN: {sitio_key} ===")
        
        try:
            app_dir = os.path.dirname(os.path.abspath(__file__))
            scripts_dir = os.path.join(app_dir, 'scripts')
            
            sys.path.insert(0, scripts_dir)
            
            # Mapeo de scripts a módulos
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
            
            if sitio_key not in script_modules:
                raise ValueError(f"Script no encontrado para sitio: {sitio_key}")
            
            module_name = script_modules[sitio_key]
            print(f"[DEBUG] Importando módulo: {module_name}")
            script_module = __import__(module_name)
            print(f"[DEBUG] Módulo importado OK")
            
            self.emit_progress(sitio_key, "Conectando a Telegram...", 'info')
            print(f"[DEBUG] Llamando obtener_todos_los_mensajes({fecha_inicio}, {fecha_fin})")
            
            # Ejecutar la extracción
            mensajes = await script_module.obtener_todos_los_mensajes(fecha_inicio, fecha_fin)
            
            print(f"[DEBUG] Mensajes obtenidos: {len(mensajes) if mensajes else 0}")
            
            if mensajes:
                self.emit_progress(sitio_key, f"Se encontraron {len(mensajes)} mensajes", 'success')
                
                # Crear PDF
                print(f"[DEBUG] Creando PDF...")
                archivo_pdf, ventas, nombre_sitio = script_module.crear_pdf(mensajes, fecha_inicio, fecha_fin)
                print(f"[DEBUG] PDF creado: {archivo_pdf}")
                
                # Mover PDF al directorio de reports
                import shutil
                destino_pdf = os.path.join(app.config['REPORTS_FOLDER'], os.path.basename(archivo_pdf))
                shutil.move(archivo_pdf, destino_pdf)
                
                self.emit_progress(sitio_key, f"PDF creado: {os.path.basename(destino_pdf)}", 'success')
                self.emit_progress(sitio_key, f"Total ventas: ${ventas['total_valor']:,}", 'success')
                
                return {
                    'success': True,
                    'archivo_pdf': os.path.basename(destino_pdf),
                    'ventas': ventas,
                    'total_mensajes': len(mensajes)
                }
            else:
                self.emit_progress(sitio_key, "No se encontraron mensajes", 'warning')
                print(f"[DEBUG] No se encontraron mensajes para {sitio_key}")
                return {'success': False, 'error': 'No se encontraron mensajes'}
                
        except Exception as e:
            traceback.print_exc()
            self.emit_progress(sitio_key, f"Error: {str(e)}", 'error')
            print(f"[ERROR] {sitio_key}: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            if scripts_dir in sys.path:
                sys.path.remove(scripts_dir)

# Instancia global del extractor
extractor = TelegramExtractor()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html', sitios=SITIOS)

@app.route('/api/extract_all', methods=['POST'])
def extract_all():
    """Extraer datos de todos los sitios"""
    data = request.json
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    
    # Crear registro de extracción principal
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO extractions (sitio, fecha_inicio, fecha_fin, estado)
        VALUES (?, ?, ?, ?)
    ''', ('TODOS', fecha_inicio, fecha_fin, 'procesando'))
    extraction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    def run_extraction():
        """Ejecutar extracción en background"""
        try:
            os.chdir(APP_DIR)
            print(f"[DEBUG] CWD fijado a: {os.getcwd()}")
            print(f"[DEBUG] session existe: {os.path.exists('session_name.session')}")
            
            extractor.current_extraction_id = extraction_id
            extractor.set_progress_callback(lambda sitio, msg, tipo: None)
            
            resultados = {}
            
            for sitio_key in SITIOS.keys():
                log_extraction(extraction_id, f"Iniciando procesamiento de {sitio_key}", 'info')
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    resultado = loop.run_until_complete(
                        extractor.extract_site_data(sitio_key, fecha_inicio, fecha_fin)
                    )
                    resultados[sitio_key] = resultado
                    log_extraction(extraction_id, f"Resultado {sitio_key}: {resultado}", 'info')
                except Exception as e:
                    error_msg = f"Error procesando {sitio_key}: {str(e)}"
                    resultados[sitio_key] = {'success': False, 'error': str(e)}
                    log_extraction(extraction_id, error_msg, 'error')
                    print(f"ERROR: {error_msg}")
                finally:
                    loop.close()
            
            # Generar ZIP con todos los PDFs generados
            pdfs_generados = []
            for sitio_key, resultado in resultados.items():
                if resultado.get('success') and resultado.get('archivo_pdf'):
                    pdf_path = os.path.join(app.config['REPORTS_FOLDER'], resultado['archivo_pdf'])
                    if os.path.exists(pdf_path):
                        pdfs_generados.append({
                            'sitio': SITIOS[sitio_key]['name'],
                            'archivo': resultado['archivo_pdf'],
                            'path': pdf_path
                        })
            
            zip_generado = None
            if pdfs_generados:
                try:
                    temp_dir = tempfile.mkdtemp()
                    zip_filename = os.path.join(temp_dir, f'reportes_todos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')
                    
                    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for pdf_info in pdfs_generados:
                            zipf.write(pdf_info['path'], pdf_info['archivo'])
                    
                    # Mover el ZIP al directorio de reports
                    final_zip_name = f'reportes_todos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
                    final_zip_path = os.path.join(app.config['REPORTS_FOLDER'], final_zip_name)
                    
                    import shutil
                    shutil.move(zip_filename, final_zip_path)
                    zip_generado = final_zip_name
                    
                    log_extraction(extraction_id, f"ZIP generado con {len(pdfs_generados)} PDFs: {final_zip_name}", 'success')
                    
                except Exception as e:
                    log_extraction(extraction_id, f"Error generando ZIP: {str(e)}", 'error')
            
            # Actualizar estado final
            update_extraction_status(
                extraction_id, 
                'completado',
                archivo_pdf=zip_generado,
                total_ventas=len(pdfs_generados),
                total_valor=sum(r.get('ventas', {}).get('total_valor', 0) for r in resultados.values() if r.get('success')),
                total_comision=sum(r.get('ventas', {}).get('total_comision', 0) for r in resultados.values() if r.get('success')),
                total_enviar=sum(r.get('ventas', {}).get('total_a_enviar', 0) for r in resultados.values() if r.get('success'))
            )
            log_extraction(extraction_id, "Extracción completada", 'success')
            
        except Exception as e:
            error_msg = f"Error general en extracción: {str(e)}"
            update_extraction_status(extraction_id, 'error')
            log_extraction(extraction_id, error_msg, 'error')
            print(f"ERROR GENERAL: {error_msg}")
            import traceback
            traceback.print_exc()
    
    # Ejecutar en background
    thread = threading.Thread(target=run_extraction)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'extraction_id': extraction_id,
        'message': 'Extracción iniciada'
    })

@app.route('/api/extract_site/<sitio_key>', methods=['POST'])
def extract_site(sitio_key):
    """Extraer datos de un sitio específico"""
    if sitio_key not in SITIOS:
        return jsonify({'success': False, 'error': 'Sitio no encontrado'}), 404
    
    data = request.json
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    
    sitio_info = SITIOS[sitio_key]
    
    # Crear registro de extracción
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO extractions (sitio, fecha_inicio, fecha_fin, estado)
        VALUES (?, ?, ?, ?)
    ''', (sitio_info['name'], fecha_inicio, fecha_fin, 'procesando'))
    extraction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    def run_extraction():
        try:
            os.chdir(APP_DIR)
            extractor.current_extraction_id = extraction_id
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            resultado = loop.run_until_complete(
                extractor.extract_site_data(sitio_key, fecha_inicio, fecha_fin)
            )
            
            if resultado['success']:
                update_extraction_status(
                    extraction_id, 
                    'completado',
                    archivo_pdf=resultado['archivo_pdf'],
                    total_ventas=resultado['ventas']['total_ventas'],
                    total_valor=resultado['ventas']['total_valor'],
                    total_comision=resultado['ventas']['total_comision'],
                    total_enviar=resultado['ventas']['total_a_enviar']
                )
            else:
                update_extraction_status(extraction_id, 'error')
                
        except Exception as e:
            update_extraction_status(extraction_id, 'error')
            log_extraction(extraction_id, f"Error: {str(e)}", 'error')
        finally:
            loop.close()
    
    thread = threading.Thread(target=run_extraction)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'extraction_id': extraction_id,
        'message': f'Extracción de {sitio_info["name"]} iniciada'
    })

@app.route('/api/extractions')
def get_extractions():
    """Obtener historial de extracciones"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM extractions 
        ORDER BY creado_en DESC 
        LIMIT 50
    ''')
    extractions = cursor.fetchall()
    conn.close()
    
    # Convertir a diccionarios
    columns = [desc[0] for desc in cursor.description]
    result = []
    for row in extractions:
        extraction_dict = dict(zip(columns, row))
        
        # Calcular total_enviar si no existe o es null
        if extraction_dict.get('total_enviar') is None:
            total_valor = extraction_dict.get('total_valor') or 0
            total_comision = extraction_dict.get('total_comision') or 0
            extraction_dict['total_enviar'] = total_valor - total_comision
        
        result.append(extraction_dict)
    
    return jsonify(result)

@app.route('/api/extraction/<int:extraction_id>/logs')
def get_extraction_logs(extraction_id):
    """Obtener logs de una extracción"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM extraction_logs 
        WHERE extraction_id = ?
        ORDER BY creado_en ASC
    ''', (extraction_id,))
    logs = cursor.fetchall()
    conn.close()
    
    columns = [desc[0] for desc in cursor.description]
    result = []
    for row in logs:
        result.append(dict(zip(columns, row)))
    
    return jsonify(result)

@app.route('/api/clean_database', methods=['POST'])
def clean_database():
    """Limpiar registros de la base de datos"""
    data = request.json
    clean_type = data.get('type', 'all')  # 'all', 'logs_only', 'completed_only'
    
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    try:
        if clean_type == 'logs_only':
            # Solo limpiar logs
            cursor.execute('DELETE FROM extraction_logs')
            logs_deleted = cursor.rowcount
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': f'Se eliminaron {logs_deleted} registros de logs',
                'logs_deleted': logs_deleted,
                'extractions_deleted': 0
            })
            
        elif clean_type == 'completed_only':
            # Solo extracciones completadas
            cursor.execute('''
                DELETE FROM extraction_logs 
                WHERE extraction_id IN (
                    SELECT id FROM extractions WHERE estado = 'completado'
                )
            ''')
            logs_deleted = cursor.rowcount
            
            cursor.execute('DELETE FROM extractions WHERE estado = "completado"')
            extractions_deleted = cursor.rowcount
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': f'Se eliminaron {extractions_deleted} extracciones completadas y {logs_deleted} logs',
                'logs_deleted': logs_deleted,
                'extractions_deleted': extractions_deleted
            })
            
        else:  # 'all'
            # Eliminar todo
            cursor.execute('DELETE FROM extraction_logs')
            logs_deleted = cursor.rowcount
            
            cursor.execute('DELETE FROM extractions')
            extractions_deleted = cursor.rowcount
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': f'Se eliminaron {extractions_deleted} extracciones y {logs_deleted} logs',
                'logs_deleted': logs_deleted,
                'extractions_deleted': extractions_deleted
            })
            
    except Exception as e:
        conn.rollback()
        return jsonify({
            'success': False,
            'message': f'Error limpiando la base de datos: {str(e)}'
        }), 500
    finally:
        conn.close()

@app.route('/api/database_stats')
def get_database_stats():
    """Obtener estadísticas de la base de datos"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    try:
        # Contar extracciones por estado
        cursor.execute('''
            SELECT estado, COUNT(*) as count 
            FROM extractions 
            GROUP BY estado
        ''')
        estado_stats = dict(cursor.fetchall())
        
        # Contar logs
        cursor.execute('SELECT COUNT(*) FROM extraction_logs')
        total_logs = cursor.fetchone()[0]
        
        # Contar extracciones totales
        cursor.execute('SELECT COUNT(*) FROM extractions')
        total_extractions = cursor.fetchone()[0]
        
        return jsonify({
            'total_extractions': total_extractions,
            'total_logs': total_logs,
            'estado_stats': estado_stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error obteniendo estadísticas: {str(e)}'
        }), 500
    finally:
        conn.close()

@app.route('/api/logs')
def get_all_logs():
    """Obtener todos los logs para depuración"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute('''
        SELECT el.*, e.sitio 
        FROM extraction_logs el
        LEFT JOIN extractions e ON el.extraction_id = e.id
        ORDER BY el.creado_en DESC
        LIMIT 100
    ''')
    logs = cursor.fetchall()
    conn.close()
    
    columns = [desc[0] for desc in cursor.description]
    result = []
    for row in logs:
        result.append(dict(zip(columns, row)))
    
    return jsonify(result)

@app.route('/reports/<filename>')
def download_report(filename):
    """Descargar reporte PDF"""
    return send_file(
        os.path.join(app.config['REPORTS_FOLDER'], filename),
        as_attachment=True
    )

@app.route('/api/download_all_pdfs', methods=['POST'])
def download_all_pdfs():
    """Descargar todos los PDFs generados en un ZIP"""
    try:
        # Primero verificar si hay PDFs existentes en el directorio
        pdf_files = []
        if os.path.exists(app.config['REPORTS_FOLDER']):
            for filename in os.listdir(app.config['REPORTS_FOLDER']):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(app.config['REPORTS_FOLDER'], filename)
                    if os.path.exists(file_path):
                        pdf_files.append({
                            'filename': filename,
                            'path': file_path,
                            'size': os.path.getsize(file_path)
                        })
        
        # Si no hay PDFs, intentar generarlos
        if not pdf_files:
            return jsonify({
                'success': False,
                'message': 'No hay PDFs disponibles. Por favor, ejecuta una extracción primero.',
                'needs_extraction': True
            }), 400
        
        # Crear archivo ZIP temporal
        temp_dir = tempfile.mkdtemp()
        zip_filename = os.path.join(temp_dir, f'reportes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for pdf_file in pdf_files:
                # Usar el nombre original del archivo
                zipf.write(pdf_file['path'], pdf_file['filename'])
        
        # Enviar el archivo ZIP
        return send_file(
            zip_filename,
            as_attachment=True,
            download_name=f'reportes_todos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creando archivo ZIP: {str(e)}'
        }), 500
        
        # Crear archivo ZIP temporal
        temp_dir = tempfile.mkdtemp()
        zip_filename = os.path.join(temp_dir, f'reportes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            pdf_count = 0
            
            for archivo_pdf, sitio, fecha_inicio, fecha_fin in extractions:
                pdf_path = os.path.join(app.config['REPORTS_FOLDER'], archivo_pdf)
                
                if os.path.exists(pdf_path):
                    # Nombre descriptivo para el archivo en el ZIP
                    zip_name = f"{sitio}_{fecha_inicio}_a_{fecha_fin}.pdf"
                    zipf.write(pdf_path, zip_name)
                    pdf_count += 1
        
        if pdf_count == 0:
            # Limpiar directorio temporal
            import shutil
            shutil.rmtree(temp_dir)
            
            return jsonify({
                'success': False,
                'message': 'No se encontraron archivos PDF físicos'
            }), 404
        
        # Enviar el archivo ZIP
        return send_file(
            zip_filename,
            as_attachment=True,
            download_name=f'reportes_completos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip',
            mimetype='application/zip'
        )
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error creando archivo ZIP: {str(e)}'
        }), 500

@app.route('/api/generate_and_download_all', methods=['POST'])
def generate_and_download_all():
    """Generar todos los PDFs y descargarlos en ZIP"""
    try:
        data = request.json
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({
                'success': False,
                'message': 'Se requieren fechas de inicio y fin'
            }), 400
        
        # Crear registro de extracción masiva
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO extractions (sitio, fecha_inicio, fecha_fin, estado)
            VALUES (?, ?, ?, ?)
        ''', ('TODOS_MASIVO', fecha_inicio, fecha_fin, 'procesando'))
        extraction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        def run_massive_extraction():
            try:
                os.chdir(APP_DIR)
                extractor.current_extraction_id = extraction_id
                extractor.set_progress_callback(lambda sitio, msg, tipo: None)
                
                resultados = {}
                pdfs_generados = []
                
                for sitio_key in SITIOS.keys():
                    log_extraction(extraction_id, f"Generando PDF para {sitio_key}", 'info')
                    
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        resultado = loop.run_until_complete(
                            extractor.extract_site_data(sitio_key, fecha_inicio, fecha_fin)
                        )
                        resultados[sitio_key] = resultado
                        
                        if resultado['success']:
                            pdfs_generados.append({
                                'sitio': SITIOS[sitio_key]['name'],
                                'archivo': resultado['archivo_pdf'],
                                'path': os.path.join(app.config['REPORTS_FOLDER'], resultado['archivo_pdf'])
                            })
                            log_extraction(extraction_id, f"PDF generado para {sitio_key}: {resultado['archivo_pdf']}", 'success')
                        else:
                            log_extraction(extraction_id, f"Error generando PDF para {sitio_key}: {resultado.get('error', 'Error desconocido')}", 'error')
                            
                    except Exception as e:
                        error_msg = f"Error procesando {sitio_key}: {str(e)}"
                        resultados[sitio_key] = {'success': False, 'error': str(e)}
                        log_extraction(extraction_id, error_msg, 'error')
                        print(f"ERROR: {error_msg}")
                    finally:
                        loop.close()
                
                # Crear ZIP con todos los PDFs generados
                if pdfs_generados:
                    temp_dir = tempfile.mkdtemp()
                    zip_filename = os.path.join(temp_dir, f'reportes_masivos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')
                    
                    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for pdf_info in pdfs_generados:
                            if os.path.exists(pdf_info['path']):
                                zipf.write(pdf_info['path'], pdf_info['archivo'])
                    
                    # Mover el ZIP al directorio de reports para descarga
                    final_zip_name = f'reportes_masivos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
                    final_zip_path = os.path.join(app.config['REPORTS_FOLDER'], final_zip_name)
                    
                    import shutil
                    shutil.move(zip_filename, final_zip_path)
                    
                    # Actualizar estado con el ZIP generado
                    update_extraction_status(
                        extraction_id, 
                        'completado',
                        archivo_pdf=final_zip_name,
                        total_ventas=len(pdfs_generados),
                        total_valor=sum(r.get('ventas', {}).get('total_valor', 0) for r in resultados.values() if r.get('success')),
                        total_comision=sum(r.get('ventas', {}).get('total_comision', 0) for r in resultados.values() if r.get('success')),
                        total_enviar=sum(r.get('ventas', {}).get('total_a_enviar', 0) for r in resultados.values() if r.get('success'))
                    )
                    
                    log_extraction(extraction_id, f"ZIP masivo creado: {final_zip_name}", 'success')
                    
                else:
                    update_extraction_status(extraction_id, 'error')
                    log_extraction(extraction_id, "No se pudo generar ningún PDF", 'error')
                    
            except Exception as e:
                error_msg = f"Error general en extracción masiva: {str(e)}"
                update_extraction_status(extraction_id, 'error')
                log_extraction(extraction_id, error_msg, 'error')
                print(f"ERROR GENERAL: {error_msg}")
                import traceback
                traceback.print_exc()
        
        # Ejecutar en background
        thread = threading.Thread(target=run_massive_extraction)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'extraction_id': extraction_id,
            'message': 'Extracción masiva iniciada. Se generará un ZIP con todos los PDFs.',
            'status': 'processing'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error iniciando extracción masiva: {str(e)}'
        }), 500

@app.route('/api/list_pdfs')
def list_pdfs():
    """Listar todos los PDFs disponibles"""
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        cursor.execute('''
            SELECT archivo_pdf, sitio, fecha_inicio, fecha_fin, creado_en,
                   total_ventas, total_valor, total_comision, total_enviar
            FROM extractions 
            WHERE estado = 'completado' AND archivo_pdf IS NOT NULL
            ORDER BY creado_en DESC
        ''')
        pdfs = cursor.fetchall()
        conn.close()
        
        # Verificar existencia física de archivos
        pdf_list = []
        for row in pdfs:
            pdf_path = os.path.join(app.config['REPORTS_FOLDER'], row[0])
            exists = os.path.exists(pdf_path)
            
            # Calcular total_enviar si no existe o es null
            total_enviar = row[8] if row[8] is not None else (row[6] - row[7] if row[6] and row[7] else 0)
            
            pdf_list.append({
                'archivo_pdf': row[0],
                'sitio': row[1],
                'fecha_inicio': row[2],
                'fecha_fin': row[3],
                'creado_en': row[4],
                'total_ventas': row[5],
                'total_valor': row[6],
                'total_comision': row[7],
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)