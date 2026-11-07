"""
Módulo de Sedes Instaladas
Gestión de ubicaciones y contacto de sedes
"""

from flask import Blueprint

# Crear Blueprint para el módulo
sedes_bp = Blueprint('sedes', __name__, 
                     url_prefix='/sedes',
                     template_folder='templates',
                     static_folder='static')

@sedes_bp.route('/')
def index():
    """Página principal del módulo de sedes"""
    return "<h1>Módulo de Sedes Instaladas</h1><p>En desarrollo...</p>"

@sedes_bp.route('/status')
def status():
    """Estado del módulo"""
    return {
        'modulo': 'Sedes Instaladas',
        'estado': 'En desarrollo',
        'descripcion': 'Gestión de ubicaciones y contacto de sedes'
    }