"""
Módulo de Portales Cautivos
Gestión de portales WiFi y autenticación
"""

from flask import Blueprint

# Crear Blueprint para el módulo
portales_bp = Blueprint('portales_cautivos', __name__, 
                       url_prefix='/portales',
                       template_folder='templates',
                       static_folder='static')

@portales_bp.route('/')
def index():
    """Página principal del módulo de portales cautivos"""
    return "<h1>Módulo de Portales Cautivos</h1><p>En desarrollo...</p>"

@portales_bp.route('/status')
def status():
    """Estado del módulo"""
    return {
        'modulo': 'Portales Cautivos',
        'estado': 'En desarrollo',
        'descripcion': 'Gestión de portales WiFi y autenticación'
    }