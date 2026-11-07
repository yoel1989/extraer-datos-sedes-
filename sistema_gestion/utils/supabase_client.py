"""
Configuración y conexión a Supabase
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class SupabaseClient:
    """Clase para gestionar la conexión con Supabase"""
    
    _instance = None
    _client: Client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Inicializar el cliente de Supabase"""
        try:
            # Obtener variables de entorno
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            if not supabase_url or not supabase_key:
                raise ValueError("Faltan variables de entorno de Supabase")
            
            # Crear cliente
            self._client = create_client(supabase_url, supabase_key)
            print("✅ Conexión a Supabase establecida")
            
        except Exception as e:
            print(f"❌ Error conectando a Supabase: {e}")
            raise
    
    @property
    def client(self) -> Client:
        """Obtener el cliente de Supabase"""
        if self._client is None:
            self._initialize_client()
        return self._client
    
    def test_connection(self) -> bool:
        """Probar la conexión a Supabase"""
        try:
            # Intentar obtener versión del servidor
            response = self.client.rpc('version', {}).execute()
            return True
        except:
            # Si no hay función version, intentar una consulta simple
            try:
                response = self.client.table('users').select('count').execute()
                return True
            except:
                return False

# Instancia global
supabase_client = SupabaseClient()

def get_supabase() -> Client:
    """Obtener instancia del cliente Supabase"""
    return supabase_client.client

# Tablas del sistema
TABLES = {
    'users': 'users',
    'extractions': 'extractions',
    'extraction_logs': 'extraction_logs',
    'transacciones': 'transacciones',
    'categorias': 'categorias'
}