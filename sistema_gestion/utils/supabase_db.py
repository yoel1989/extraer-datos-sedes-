"""
Gestor de base de datos para Supabase
100% Supabase - Sin compatibilidad SQLite
"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from flask import current_app
from supabase import create_client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class SupabaseManager:
    """Gestor dedicado para Supabase"""
    
    def __init__(self):
        # Obtener de variables de entorno o usar valores por defecto
        self.supabase_url = os.getenv('SUPABASE_URL') or 'https://hczttwjggqgzzhdtgml.supabase.co'
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY') or 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlbiI6ImFub24iLCJpYXQiOjE3NDQ2Mzk0OTcsImV4cCI6MjA1OTM3MzQ5NywiaWF0IjoxNzQ0NjM5NDk3fQ.BBPfWk7sDxGJ0KivS-nOv5YnEc3-p6ajHw2aKJ2A'
        self._client = None
        
        print(f"[SUPABASE] URL: {self.supabase_url}")
        print(f"[SUPABASE] Key: {self.supabase_key[:20]}...")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Faltan variables de entorno de Supabase")
    
    @property
    def client(self):
        """Obtener cliente de Supabase (lazy loading)"""
        if self._client is None:
            self._client = create_client(self.supabase_url, self.supabase_key)
        return self._client
    
    # ==================== MÉTODOS PARA USUARIOS ====================
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crear un nuevo usuario"""
        user_data['creado_en'] = datetime.utcnow().isoformat()
        user_data['actualizado_en'] = datetime.utcnow().isoformat()
        
        result = self.client.table('users').insert(user_data).execute()
        return result.data[0] if result.data else None
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Obtener usuario por username"""
        result = self.client.table('users').select('*').eq('username', username).execute()
        return result.data[0] if result.data else None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Obtener usuario por ID"""
        result = self.client.table('users').select('*').eq('id', user_id).execute()
        return result.data[0] if result.data else None
    
    # ==================== MÉTODOS PARA EXTRACCIONES ====================
    
    def create_extraction(self, extraction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crear nueva extracción"""
        result = self.client.table('extractions').insert(extraction_data).execute()
        return result.data[0] if result.data else None
    
    def get_extractions(self, **filters) -> List[Dict[str, Any]]:
        """Obtener extracciones con filtros opcionales"""
        query = self.client.table('extractions').select('*')
        
        for key, value in filters.items():
            if value is not None:
                if key == 'order' and value:
                    # Manejar ordenamiento: 'creado_en:desc'
                    if ':' in value:
                        field, direction = value.split(':')
                        query = query.order(field, desc=direction.lower() == 'desc')
                elif key == 'limit' and isinstance(value, int):
                    query = query.limit(value)
                else:
                    query = query.eq(key, value)
        
        result = query.execute()
        return result.data if result.data else []
    
    def update_extraction(self, extraction_id: int, data: Dict[str, Any]) -> bool:
        """Actualizar extracción"""
        result = self.client.table('extractions').update(data).eq('id', extraction_id).execute()
        return len(result.data) > 0 if result.data else False
    
    def create_extraction_log(self, log_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crear log de extracción"""
        log_data['creado_en'] = datetime.utcnow().isoformat()
        
        result = self.client.table('extraction_logs').insert(log_data).execute()
        return result.data[0] if result.data else None
    
    def get_extraction_logs(self, extraction_id: int) -> List[Dict[str, Any]]:
        """Obtener logs de una extracción"""
        result = self.client.table('extraction_logs').select('*').eq('extraction_id', extraction_id).order('creado_en', desc=True).execute()
        return result.data if result.data else []
    
    # ==================== MÉTODOS PARA CONTABILIDAD ====================
    
    def create_categoria(self, categoria_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crear categoría"""
        categoria_data['creado_en'] = datetime.utcnow().isoformat()
        
        result = self.client.table('categorias').insert(categoria_data).execute()
        return result.data[0] if result.data else None
    
    def get_categorias(self, tipo: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtener categorías"""
        query = self.client.table('categorias').select('*')
        
        if tipo:
            query = query.eq('tipo', tipo)
        
        result = query.order('nombre').execute()
        return result.data if result.data else []
    
    def create_transaccion(self, transaccion_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Crear transacción"""
        transaccion_data['creado_en'] = datetime.utcnow().isoformat()
        transaccion_data['actualizado_en'] = datetime.utcnow().isoformat()
        
        result = self.client.table('transacciones').insert(transaccion_data).execute()
        return result.data[0] if result.data else None
    
    def get_transacciones(self, **filters) -> List[Dict[str, Any]]:
        """Obtener transacciones con filtros opcionales"""
        query = self.client.table('transacciones').select('*')
        
        for key, value in filters.items():
            if value is not None:
                if key == 'order' and value:
                    # Manejar ordenamiento
                    if ':' in value:
                        field, direction = value.split(':')
                        query = query.order(field, desc=direction.lower() == 'desc')
                elif key == 'limit' and isinstance(value, int):
                    query = query.limit(value)
                else:
                    query = query.eq(key, value)
        
        result = query.execute()
        return result.data if result.data else []
    
    def update_transaccion(self, transaccion_id: int, data: Dict[str, Any]) -> bool:
        """Actualizar transacción"""
        data['actualizado_en'] = datetime.utcnow().isoformat()
        
        result = self.client.table('transacciones').update(data).eq('id', transaccion_id).execute()
        return len(result.data) > 0 if result.data else False
    
    def delete_transaccion(self, transaccion_id: int) -> bool:
        """Eliminar transacción"""
        result = self.client.table('transacciones').delete().eq('id', transaccion_id).execute()
        return len(result.data) > 0 if result.data else False
    
    def get_resumen_financiero(self) -> Dict[str, Any]:
        """Obtener resumen financiero"""
        try:
            # Usar función SQL si existe
            result = self.client.rpc('resumen_financiero', {}).execute()
            if result.data and len(result.data) > 0:
                data = result.data[0]
                return {
                    'ingresos': float(data.get('total_ingresos', 0)),
                    'egresos': float(data.get('total_egresos', 0)),
                    'balance': float(data.get('balance', 0))
                }
        except:
            pass
        
        # Fallback: calcular manualmente
        transacciones = self.get_transacciones()
        ingresos = sum(t['monto'] for t in transacciones if t['tipo'] == 'ingreso')
        egresos = sum(t['monto'] for t in transacciones if t['tipo'] == 'egreso')
        
        return {
            'ingresos': ingresos,
            'egresos': egresos,
            'balance': ingresos - egresos
        }
    
    def get_estadisticas_categorias(self) -> List[Dict[str, Any]]:
        """Obtener estadísticas por categoría"""
        try:
            result = self.client.rpc('estadisticas_categorias', {}).execute()
            return result.data if result.data else []
        except:
            # Fallback: calcular manualmente
            transacciones = self.get_transacciones()
            categorias = self.get_categorias()
            
            stats = []
            for cat in categorias:
                monto_total = sum(t['monto'] for t in transacciones if t['categoria'] == cat['nombre'])
                cantidad = len([t for t in transacciones if t['categoria'] == cat['nombre']])
                
                if monto_total > 0:
                    stats.append({
                        'nombre': cat['nombre'],
                        'color': cat['color'],
                        'tipo': cat['tipo'],
                        'total': monto_total,
                        'cantidad': cantidad
                    })
            
            return sorted(stats, key=lambda x: x['total'], reverse=True)
    
    def test_connection(self) -> bool:
        """Probar la conexión a Supabase"""
        try:
            result = self.client.table('users').select('count').execute()
            return True
        except:
            return False

# Instancia global
supabase_manager = SupabaseManager()

# Funciones de compatibilidad para el código existente
def get_supabase():
    """Obtener instancia del cliente Supabase"""
    return supabase_manager.client

# Tablas del sistema
TABLES = {
    'users': 'users',
    'extractions': 'extractions',
    'extraction_logs': 'extraction_logs',
    'transacciones': 'transacciones',
    'categorias': 'categorias'
}

# Gestor principal (reemplaza a database_manager)
db_manager = supabase_manager