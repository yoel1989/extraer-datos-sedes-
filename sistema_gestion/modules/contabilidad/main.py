"""
Módulo de Contabilidad
Gestión financiera, facturación y reportes contables
"""

from flask import Blueprint, render_template, render_template_string, request, jsonify, current_app
from flask_login import login_required

import os
from datetime import datetime, timedelta
import json
import time
from functools import wraps

# Importar gestor de Supabase
from utils.supabase_db import db_manager

# Crear Blueprint para el módulo
contabilidad_bp = Blueprint('contabilidad', __name__, 
                         url_prefix='/contabilidad',
                         template_folder='templates',
                         static_folder='static')



def get_db_path():
    """Obtener ruta de la base de datos del módulo (legacy - ya no se usa)"""
    # Esta función se mantiene por compatibilidad pero no se usa
    return None

def _agrupar_ingresos_por_tipo(transacciones):
    """Agrupar ingresos por tipo (función helper para Supabase)"""
    grupos = {}
    for trans in transacciones:
        categoria = trans.get('categoria', '')
        
        if 'Ventas' in categoria:
            tipo = 'Ingresos por Sedes'
        elif 'Clientes' in categoria:
            tipo = 'Ingresos por Clientes'
        elif 'TV' in categoria or 'Suscripcion' in categoria:
            tipo = 'Ingresos TV'
        elif 'Extra' in categoria or 'Adicional' in categoria or 'Eventual' in categoria:
            tipo = 'Ingresos Extras'
        else:
            tipo = 'Otros Ingresos'
        
        if tipo not in grupos:
            grupos[tipo] = {'total': 0, 'cantidad': 0}
        
        grupos[tipo]['total'] += trans.get('monto', 0)
        grupos[tipo]['cantidad'] += 1
    
    return [(tipo, data['total'], data['cantidad']) for tipo, data in grupos.items()]

def _agrupar_por_categoria(transacciones, patron):
    """Agrupar transacciones por categoría con patrón (función helper para Supabase)"""
    grupos = {}
    
    # Convertir patrón SQL a lógica Python
    if patron == 'Ventas%':
        filtro = lambda cat: 'Ventas' in cat
    elif patron == 'Clientes%':
        filtro = lambda cat: 'Clientes' in cat
    elif patron == '%TV%':
        filtro = lambda cat: 'TV' in cat or 'Suscripcion' in cat
    elif patron == '%Extra%':
        filtro = lambda cat: any(x in cat for x in ['Extra', 'Adicional', 'Eventual'])
    else:
        filtro = lambda cat: True
    
    for trans in transacciones:
        categoria = trans.get('categoria', '')
        if filtro(categoria):
            if categoria not in grupos:
                grupos[categoria] = {'total': 0, 'cantidad': 0}
            grupos[categoria]['total'] += trans.get('monto', 0)
            grupos[categoria]['cantidad'] += 1
    
    return [(cat, data['total'], data['cantidad']) for cat, data in grupos.items()]

def init_contabilidad_db():
    """Inicializar tablas de contabilidad (solo Supabase)"""
    # Las tablas ya están creadas en Supabase mediante el script SQL
    # Esta función mantiene compatibilidad pero no hace nada
    pass

@contabilidad_bp.route('/')
@login_required
def index():
    """Dashboard principal de contabilidad - Solo Supabase"""
    init_contabilidad_db()
    
    # Usar Supabase exclusivamente
    resumen = db_manager.get_resumen_financiero()
    
    # Obtener transacciones recientes
    transacciones_recientes = db_manager.get_transacciones(
        order='creado_en:desc',
        limit=10
    )
    
    # Resumen por tipo de ingreso
    transacciones_ingresos = db_manager.get_transacciones(tipo='ingreso')
    resumen_ingresos_tipo = _agrupar_ingresos_por_tipo(transacciones_ingresos)
    
    # Detalles por categoría
    detalle_ingresos_sedes = _agrupar_por_categoria(transacciones_ingresos, 'Ventas%')
    detalle_ingresos_clientes = _agrupar_por_categoria(transacciones_ingresos, 'Clientes%')
    detalle_ingresos_tv = _agrupar_por_categoria(transacciones_ingresos, '%TV%')
    detalle_ingresos_extras = _agrupar_por_categoria(transacciones_ingresos, '%Extra%')
    
    ingresos = resumen['ingresos']
    egresos = resumen['egresos']
    balance = resumen['balance']
    
    # Especificar la ruta completa para evitar conflictos con otras plantillas
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    return render_template_string(template_content, 
                       ingresos=ingresos,
                       egresos=egresos,
                       balance=balance,
                       transacciones_recientes=transacciones_recientes,
                       resumen_ingresos_tipo=resumen_ingresos_tipo,
                       detalle_ingresos_sedes=detalle_ingresos_sedes,
                       detalle_ingresos_clientes=detalle_ingresos_clientes,
                       detalle_ingresos_tv=detalle_ingresos_tv,
                       detalle_ingresos_extras=detalle_ingresos_extras)

@contabilidad_bp.route('/api/transacciones')
@login_required
def get_transacciones():
    """Obtener todas las transacciones - Solo Supabase"""
    try:
        # Usar Supabase exclusivamente
        transacciones = db_manager.get_transacciones(order='creado_en:desc')
        
        # Enriquecer con datos de categorías
        categorias = db_manager.get_categorias()
        categoria_map = {cat['nombre']: cat for cat in categorias}
        
        for trans in transacciones:
            cat_info = categoria_map.get(trans.get('categoria', {}), {})
            trans['categoria_nombre'] = trans.get('categoria', '')
            trans['categoria_color'] = cat_info.get('color', '#007bff')
        
        return jsonify(transacciones)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contabilidad_bp.route('/api/transaccion', methods=['POST'])
@login_required
def add_transaccion():
    """Agregar nueva transacción - Solo Supabase"""
    try:
        data = request.json
        
        transaccion_data = {
            'tipo': data.get('tipo'),
            'categoria': data.get('categoria'),
            'descripcion': data.get('descripcion'),
            'monto': float(data.get('monto')),
            'referencia': data.get('referencia'),
            'fecha': data.get('fecha') or datetime.now().strftime('%Y-%m-%d')
        }
        
        # Usar Supabase exclusivamente
        result = db_manager.create_transaccion(transaccion_data)
        if result:
            return jsonify({'success': True, 'message': 'Transacción agregada correctamente', 'data': result})
        else:
            return jsonify({'success': False, 'error': 'Error al crear transacción'}), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@contabilidad_bp.route('/api/categorias')
@login_required
def get_categorias():
    """Obtener todas las categorías - Solo Supabase"""
    try:
        # Usar Supabase exclusivamente
        categorias = db_manager.get_categorias()
        return jsonify(categorias)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contabilidad_bp.route('/api/resumen_financiero')
@login_required
def get_resumen_financiero():
    """Obtener resumen financiero completo - Solo Supabase"""
    try:
        # Usar Supabase exclusivamente
        resumen = db_manager.get_resumen_financiero()
        
        # Obtener resumen por categoría
        categorias = db_manager.get_categorias()
        transacciones = db_manager.get_transacciones()
        
        resumen_categorias = []
        for cat in categorias:
            monto_total = sum(t['monto'] for t in transacciones if t['categoria'] == cat['nombre'])
            cantidad = len([t for t in transacciones if t['categoria'] == cat['nombre']])
            
            if monto_total > 0:
                resumen_categorias.append({
                    'nombre': cat['nombre'],
                    'color': cat['color'],
                    'tipo': cat['tipo'],
                    'total': monto_total,
                    'cantidad': cantidad
                })
        
        resumen_categorias.sort(key=lambda x: x['total'], reverse=True)
        
        # Evolución mensual (simplificado)
        evolucion_mensual = _calcular_evolucion_mensual(transacciones)
        
        return jsonify({
            'totales': resumen,
            'resumen_categorias': resumen_categorias,
            'evolucion_mensual': evolucion_mensual
        })
        
    except Exception as e:
        current_app.logger.error(f"Error en resumen financiero: {str(e)}")
        return jsonify({'error': str(e)}), 500

def _calcular_evolucion_mensual(transacciones):
    """Calcular evolución mensual (función helper para Supabase)"""
    from collections import defaultdict
    from datetime import datetime, timedelta
    
    meses = defaultdict(lambda: {'ingresos': 0, 'egresos': 0})
    
    # Últimos 6 meses
    fecha_limite = datetime.now() - timedelta(days=180)
    
    for trans in transacciones:
        fecha_trans = datetime.fromisoformat(trans.get('fecha', ''))
        if fecha_trans >= fecha_limite:
            mes_key = fecha_trans.strftime('%Y-%m')
            
            if trans.get('tipo') == 'ingreso':
                meses[mes_key]['ingresos'] += trans.get('monto', 0)
            elif trans.get('tipo') == 'egreso':
                meses[mes_key]['egresos'] += trans.get('monto', 0)
    
    # Convertir a lista y ordenar
    resultado = []
    for mes in sorted(meses.keys()):
        datos = meses[mes]
        resultado.append({
            'mes': mes,
            'ingresos': datos['ingresos'],
            'egresos': datos['egresos']
        })
    
    return resultado

@contabilidad_bp.route('/api/sincronizar_extracciones', methods=['POST'])
@login_required
def sincronizar_extracciones():
    """Sincronizar datos de extracciones como transacciones"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Obtener extracciones completadas que no estén sincronizadas
        cursor.execute('''
            SELECT id, sitio, total_valor, total_comision, creado_en
            FROM extractions 
            WHERE estado = 'completado' 
            AND id NOT IN (
                SELECT DISTINCT CAST(referencia AS INTEGER) 
                FROM transacciones 
                WHERE referencia IS NOT NULL
            )
        ''')
        extracciones_pendientes = cursor.fetchall()
        
        sincronizadas = 0
        for extraccion in extracciones_pendientes:
            # Agregar transacción de ventas
            cursor.execute('''
                INSERT INTO transacciones (tipo, categoria, descripcion, monto, referencia, fecha)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                'ingreso',
                'Ventas',
                f'Ventas {extraccion[1]}',
                float(extraccion[2]),
                str(extraccion[0]),
                extraccion[4].split()[0]  # Solo la fecha
            ))
            
            # Agregar transacción de comisiones si hay comisión
            if extraccion[3] > 0:
                cursor.execute('''
                    INSERT INTO transacciones (tipo, categoria, descripcion, monto, referencia, fecha)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    'egreso',
                    'Comisiones',
                    f'Comisiones {extraccion[1]}',
                    float(extraccion[3]),
                    str(extraccion[0]),
                    extraccion[4].split()[0]  # Solo la fecha
                ))
            
            sincronizadas += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Se sincronizaron {sincronizadas} extracciones',
            'sincronizadas': sincronizadas
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@contabilidad_bp.route('/api/ingresos_sedes')
@login_required
def get_ingresos_sedes():
    """Obtener ingresos por sedes para un mes específico"""
    try:
        mes = request.args.get('mes')
        ano = request.args.get('ano')
        
        if not mes or not ano:
            # Por defecto, mes actual
            from datetime import datetime
            ahora = datetime.now()
            mes = ahora.strftime('%m')
            ano = ahora.strftime('%Y')
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Buscar ingresos por sedes para el mes específico
        cursor.execute('''
            SELECT 
                c.nombre as categoria,
                COALESCE(SUM(t.monto), 0) as total,
                COALESCE(COUNT(*), 0) as cantidad
            FROM transacciones t
            LEFT JOIN categorias c ON t.categoria = c.nombre
            WHERE t.tipo = 'ingreso' 
            AND c.nombre LIKE 'Ventas%'
            AND strftime('%m', t.fecha) = ?
            AND strftime('%Y', t.fecha) = ?
            GROUP BY c.nombre
            ORDER BY c.nombre
        ''', (mes, ano))
        
        ingresos_sedes = cursor.fetchall()
        conn.close()
        
        # Convertir a diccionario para fácil manipulación
        resultado = {}
        for item in ingresos_sedes:
            resultado[item[0]] = {
                'total': item[1],
                'cantidad': item[2]
            }
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@contabilidad_bp.route('/api/ingresos_sedes', methods=['POST'])
@login_required
def update_ingresos_sedes():
    """Actualizar ingresos por sedes para un mes específico"""
    try:
        data = request.json
        mes = data.get('mes')
        ano = data.get('ano')
        ingresos = data.get('ingresos', {})
        
        if not mes or not ano:
            return jsonify({'success': False, 'error': 'Mes y año son requeridos'}), 400
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Eliminar ingresos existentes para el mes
        cursor.execute('''
            DELETE FROM transacciones 
            WHERE tipo = 'ingreso' 
            AND categoria LIKE 'Ventas%'
            AND strftime('%m', fecha) = ?
            AND strftime('%Y', fecha) = ?
        ''', (mes, ano))
        
        # Insertar nuevos ingresos
        for categoria, datos in ingresos.items():
            if datos.get('total', 0) > 0:
                cursor.execute('''
                    INSERT INTO transacciones (tipo, categoria, descripcion, monto, fecha)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    'ingreso',
                    categoria,
                    f'Ventas {categoria.replace("Ventas ", "")} - {mes}/{ano}',
                    float(datos['total']),
                    f'{ano}-{mes}-01'
                ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Ingresos actualizados correctamente'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@contabilidad_bp.route('/api/meses_disponibles')
@login_required
def get_meses_disponibles():
    """Obtener lista de meses con ingresos registrados"""
    try:
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT 
                strftime('%Y-%m', fecha) as mes_ano,
                strftime('%m', fecha) as mes,
                strftime('%Y', fecha) as ano,
                CASE strftime('%m', fecha)
                    WHEN '01' THEN 'Enero'
                    WHEN '02' THEN 'Febrero'
                    WHEN '03' THEN 'Marzo'
                    WHEN '04' THEN 'Abril'
                    WHEN '05' THEN 'Mayo'
                    WHEN '06' THEN 'Junio'
                    WHEN '07' THEN 'Julio'
                    WHEN '08' THEN 'Agosto'
                    WHEN '09' THEN 'Septiembre'
                    WHEN '10' THEN 'Octubre'
                    WHEN '11' THEN 'Noviembre'
                    WHEN '12' THEN 'Diciembre'
                END as mes_nombre
            FROM transacciones 
            WHERE tipo = 'ingreso' AND categoria LIKE 'Ventas%'
            ORDER BY mes_ano DESC
        ''')
        
        meses = cursor.fetchall()
        conn.close()
        
        return jsonify(meses)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500









def exportar_pdf_simple(transacciones, periodo):
    """Exportar a formato PDF simplificado"""
    try:
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        elements = []
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Centrado
        )
        
        # Título
        elements.append(Paragraph(f"Reporte de Contabilidad - Período {periodo}", title_style))
        elements.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Calcular totales
        total_ingresos = sum(t[4] for t in transacciones if t[1] == 'ingreso')
        total_egresos = sum(t[4] for t in transacciones if t[1] == 'egreso')
        balance = total_ingresos - total_egresos
        
        # Resumen
        resumen_data = [
            ['Concepto', 'Monto'],
            ['Total Ingresos', f"${total_ingresos:,.0f}"],
            ['Total Egresos', f"${total_egresos:,.0f}"],
            ['Balance', f"${balance:,.0f}"]
        ]
        
        resumen_table = Table(resumen_data, colWidths=[3*inch, 2*inch])
        resumen_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F7F7F7')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        elements.append(resumen_table)
        elements.append(Spacer(1, 30))
        
        # Tabla de transacciones
        headers = ['Tipo', 'Concepto', 'Descripción', 'Monto', 'Fecha']
        data = [headers]
        
        for transaccion in transacciones:
            data.append([
                transaccion[1].capitalize(),
                transaccion[2][:20] + '...' if len(transaccion[2]) > 20 else transaccion[2],
                transaccion[3][:30] + '...' if len(transaccion[3]) > 30 else transaccion[3],
                f"${transaccion[4]:,.0f}",
                transaccion[5]
            ])
        
        # Crear tabla
        table = Table(data, colWidths=[0.8*inch, 1.5*inch, 2*inch, 0.8*inch, 0.8*inch])
        
        # Estilo de tabla
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F7F7F7')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        
        # Alternar colores de filas
        for i in range(1, len(data)):
            if i % 2 == 0:
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#E8E8E8'))
                ]))
        
        elements.append(table)
        
        # Construir PDF
        doc.build(elements)
        buffer.seek(0)
        
        from flask import send_file
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'contabilidad_{periodo}.pdf'
        )
        
    except ImportError:
        return jsonify({'error': 'reportlab no está instalado'}), 500
    except Exception as e:
        current_app.logger.error(f"Error exportando PDF simple: {str(e)}")
        return jsonify({'error': str(e)}), 500











@contabilidad_bp.route('/status')
@login_required
def status():
    """Estado del módulo"""
    return {
        'modulo': 'Contabilidad',
        'estado': 'Activo',
        'descripcion': 'Gestión financiera mejorada con navegación por períodos'
    }