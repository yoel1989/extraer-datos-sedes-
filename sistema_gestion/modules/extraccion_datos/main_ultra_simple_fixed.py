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
        'descripcion': 'Sistema básico de extracción'
    }

@extraccion_bp.route('/api/extract_all', methods=['POST'])
def extract_all():
    """Extraer datos de todos los sitios - Versión Simple SIN Supabase"""
    try:
        from flask_login import current_user
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': 'No autenticado'}), 401
        
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No se recibieron datos JSON'}), 400
            
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        
        if not fecha_inicio or not fecha_fin:
            return jsonify({'success': False, 'error': 'Fechas requeridas'}), 400
        
        # Respuesta simulada SIN guardar en Supabase
        result = {
            'success': True,
            'extraction_id': f"mock_all_{int(time.time())}",
            'message': 'Extracción masiva iniciada (Modo Simple)',
            'note': 'Funcionalidad completa requiere configuración de scripts',
            'sitios_procesados': list(SITIOS.keys()),
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@extraccion_bp.route('/api/extractions')
@login_required
def get_extractions():
    """Obtener historial de extracciones - Versión Simple"""
    # Datos de ejemplo
    mock_extractions = [
        {
            'id': 1,
            'sitio': 'TODOS',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31',
            'estado': 'completado',
            'total_registros': 1250,
            'pdfs_generados': 11,
            'creado_en': '2024-01-15 10:30:00'
        },
        {
            'id': 2,
            'sitio': 'BRISAS',
            'fecha_inicio': '2024-01-10',
            'fecha_fin': '2024-01-20',
            'estado': 'procesando',
            'total_registros': 0,
            'pdfs_generados': 0,
            'creado_en': '2024-01-20 14:15:00'
        }
    ]
    
    return jsonify({
        'success': True,
        'extractions': mock_extractions
    })

@extraccion_bp.route('/api/stats')
@login_required
def get_stats():
    """Obtener estadísticas - Versión Simple"""
    stats = {
        'total_extracciones': 45,
        'exitosas': 42,
        'fallidas': 3,
        'total_registros': 15680,
        'total_pdfs': 165
    }
    
    return jsonify({
        'success': True,
        'stats': stats
    })