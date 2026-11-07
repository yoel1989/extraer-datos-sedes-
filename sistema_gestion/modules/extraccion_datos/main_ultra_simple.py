"""
Módulo de Extracción de Datos - Versión Ultra Simple
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import time

# Crear Blueprint para el módulo
extraccion_bp = Blueprint('extraccion_datos', __name__, 
                        url_prefix='/extraccion',
                        template_folder='templates',
                        static_folder='static')

# SITIOS CONFIGURADOS
SITIOS = {
    'brisas': {'name': 'BRISAS'},
    'cachicamo': {'name': 'CACHICAMO'},
    'cano_lajas': {'name': 'CANO LAJAS'},
    'cano_pescado': {'name': 'CANO PESCADO'},
    'cerritos': {'name': 'CERRITOS'},
    'manantiales_1': {'name': 'MANANTIALES'},
    'manantiales_2': {'name': 'MANANTIALES-2'},
    'miravalle': {'name': 'MIRAVALLE'},
    'san_miguel': {'name': 'SAN MIGUEL'},
    'tortuga': {'name': 'LA TORTUGA'},
    'tropezon': {'name': 'TROPEZON'}
}

@extraccion_bp.route('/')
@login_required
def index():
    """Página principal del módulo de extracción de datos"""
    return render_template('index.html', sitios=SITIOS)

@extraccion_bp.route('/status')
@login_required
def status():
    """Estado del módulo"""
    return {
        'modulo': 'Extracción de Datos',
        'estado': 'Activo (Modo Simple)',
        'descripcion': 'Sistema para extraer datos de Telegram y generar reportes PDF',
        'sitios_configurados': len(SITIOS)
    }

@extraccion_bp.route('/api/extract_site/<sitio_key>', methods=['POST'])
@login_required
def extract_site(sitio_key):
    """Extraer datos de un sitio específico - Versión Simple"""
    if sitio_key not in SITIOS:
        return jsonify({'success': False, 'error': 'Sitio no encontrado'}), 404
    
    sitio_info = SITIOS[sitio_key]
    
    # Simulación de extracción
    return jsonify({
        'success': True,
        'extraction_id': f"mock_{sitio_key}_{int(time.time())}",
        'message': f'Extracción de {sitio_info["name"]} iniciada (Modo Simple)',
        'note': 'Funcionalidad completa requiere configuración de scripts'
    })

@extraccion_bp.route('/api/extract_all', methods=['POST'])
def extract_all():
    """Extraer datos de todos los sitios - Versión Simple"""
    try:
        from flask_login import current_user
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401
        
        print(f"[API] Petición recibida en extract_all")
        print(f"[API] Método: {request.method}")
        print(f"[API] Headers: {dict(request.headers)}")
        print(f"[API] Datos JSON: {request.json}")
            
        data = request.json
        if not data:
            print("[API] ERROR: No hay datos JSON")
            return jsonify({'success': False, 'error': 'No se recibieron datos JSON'}), 400
            
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        print(f"[API] Fechas: {fecha_inicio} - {fecha_fin}")
        
        if not fecha_inicio or not fecha_fin:
            print("[API] ERROR: Fechas no proporcionadas")
            return jsonify({'success': False, 'error': 'Fechas requeridas'}), 400
        
        # Respuesta simple SIN interactuar con Supabase para evitar el error de constraint
        result = {
            'success': True,
            'extraction_id': f"mock_all_{int(time.time())}",
            'message': 'Extracción masiva iniciada (Modo Simple)',
            'note': 'Funcionalidad completa requiere configuración de scripts'
        }
        
        print(f"[API] Respuesta: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"[API] ERROR: {e}")
        import traceback
        print(f"[API] TRACEBACK: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@extraccion_bp.route('/api/extractions')
@login_required
def get_extractions():
    """Obtener historial de extracciones - Versión Simple"""
    # Datos de ejemplo
    mock_extractions = [
        {
            'id': 1,
            'sitio': 'BRISAS',
            'fecha_inicio': '2025-12-20',
            'fecha_fin': '2025-12-27',
            'estado': 'completado',
            'total_ventas': 15,
            'total_valor': 750000,
            'creado_en': '2025-12-27T10:30:00'
        },
        {
            'id': 2,
            'sitio': 'CERRITOS',
            'fecha_inicio': '2025-12-20',
            'fecha_fin': '2025-12-27',
            'estado': 'completado',
            'total_ventas': 12,
            'total_valor': 600000,
            'creado_en': '2025-12-27T09:15:00'
        }
    ]
    
    return jsonify(mock_extractions)

@extraccion_bp.route('/api/database_stats')
@login_required
def get_database_stats():
    """Obtener estadísticas - Versión Simple"""
    return jsonify({
        'total_extractions': 2,
        'total_logs': 15,
        'estado_stats': {
            'completado': 2,
            'procesando': 0,
            'error': 0
        }
    })