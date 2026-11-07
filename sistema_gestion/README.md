# SISTEMA INTEGRADO DE GESTIÓN v1.0

## 🚀 INICIO RÁPIDO

### Requisitos
- Python 3.8+
- pip (gestor de paquetes de Python)

### Instalación
1. **Clonar o descargar el proyecto**
2. **Ejecutar el script de inicio:**
   ```bash
   # Windows
   INICIO.bat
   
   # O manualmente:
   pip install -r requirements.txt
   python app.py
   ```

3. **Acceder a la aplicación:**
   - URL: http://127.0.0.1:5000
   - Usuario: `admin`
   - Contraseña: `admin123`

## 📋 MÓDULOS DISPONIBLES

### 1. 🏠 Dashboard Principal
- **Descripción:** Vista general con estadísticas y acceso rápido
- **Funciones:**
  - Estadísticas en tiempo real
  - Acceso a todos los módulos
  - Notificaciones del sistema
  - Acciones rápidas

### 2. 📊 Extracción de Datos (Existente)
- **Descripción:** Sistema para extraer datos de Telegram y generar reportes
- **Estado:** ✅ Funcionando (integrado del sistema anterior)
- **Funciones:**
  - Extracción de múltiples sitios
  - Generación de PDFs
  - Reportes automáticos
  - Exportación de datos

### 3. 💰 Contabilidad
- **Descripción:** Gestión financiera y facturación
- **Estado:** 🚧 En desarrollo
- **Funciones planificadas:**
  - Gestión de ingresos/egresos
  - Facturación electrónica
  - Reportes contables
  - Conciliación bancaria

### 4. 📺 Televisión
- **Descripción:** Gestión de contenido TV y streaming
- **Estado:** 🚧 En desarrollo
- **Funciones planificadas:**
  - Programación de contenido
  - Gestión de streaming
  - Estadísticas de visualización
  - Control de canales

### 5. 🏢 Sedes Instaladas
- **Descripción:** Gestión de ubicaciones y contacto de sedes
- **Estado:** 🚧 En desarrollo
- **Funciones planificadas:**
  - Registro de sedes
  - Información de contacto
  - Estado de instalaciones
  - Mapa de ubicaciones

### 6. 🔐 Portales Cautivos
- **Descripción:** Gestión de portales WiFi y autenticación
- **Estado:** 🚧 En desarrollo
- **Funciones planificadas:**
  - Gestión de portales WiFi
  - Autenticación de usuarios
  - Estadísticas de acceso
  - Configuración de redes

## 🛠️ TECNOLOGÍAS

### Backend
- **Framework:** Flask 2.3.3
- **Base de datos:** SQLAlchemy 2.0.21 (SQLite/PostgreSQL)
- **Autenticación:** Flask-Login 0.6.3
- **API REST:** Blueprint architecture

### Frontend
- **Framework:** Bootstrap 5.3.0
- **Iconos:** Font Awesome 6.4.0
- **JavaScript:** Vanilla JS + Bootstrap JS
- **Diseño:** Responsive y moderno

### Integraciones
- **Telegram API:** Telethon 1.34.0
- **Reportes:** ReportLab 4.0.4
- **Formularios:** Flask-WTF 1.1.1

## 📁 ESTRUCTURA DEL PROYECTO

```
sistema_gestion/
├── app.py                    # Aplicación principal
├── config.py                 # Configuración del sistema
├── requirements.txt          # Dependencias Python
├── INICIO.bat              # Script de inicio rápido
├── database.db              # Base de datos SQLite
├── static/                  # Archivos estáticos
│   ├── css/style.css        # Estilos personalizados
│   ├── js/app.js           # JavaScript principal
│   └── images/             # Imágenes del sistema
├── templates/               # Plantillas HTML
│   ├── base.html           # Plantilla base
│   ├── dashboard.html      # Dashboard principal
│   ├── login.html          # Página de login
│   └── profile.html        # Perfil de usuario
├── modules/                # Módulos del sistema
│   ├── extraccion_datos/   # ✅ Extracción de datos
│   ├── contabilidad/       # 🚧 Contabilidad
│   ├── television/         # 🚧 Televisión
│   ├── sedes/             # 🚧 Sedes instaladas
│   └── portales_cautivos/ # 🚧 Portales cautivos
└── utils/                  # Utilidades compartidas
    ├── database.py         # Configuración de DB
    └── auth.py             # Autenticación y permisos
```

## 🔐 SEGURIDAD

### Autenticación
- Sistema de login seguro
- Gestión de roles (Admin/Usuario)
- Control de acceso por módulos
- Sesiones seguras

### Permisos
- **Administrador:** Acceso completo a todos los módulos
- **Usuario:** Acceso limitado según configuración

### Prácticas de seguridad
- Contraseñas encriptadas (bcrypt)
- Protección CSRF
- Validación de entrada
- Logs de auditoría

## 🚀 DESPLIEGUE

### Desarrollo
```bash
python app.py
```

### Producción
```bash
# Usar WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Variables de entorno
```bash
export FLASK_CONFIG=production
export SECRET_KEY=tu-clave-secreta-aqui
export DATABASE_URL=postgresql://user:pass@localhost/dbname
```

## 📊 ESTADÍSTICAS Y MONITOREO

### Métricas disponibles
- Usuarios activos
- Uso por módulo
- Extracciones realizadas
- Reportes generados
- Tiempos de respuesta

### Logs del sistema
- Logs de aplicación
- Logs de base de datos
- Logs de seguridad
- Logs de errores

## 🔄 ACTUALIZACIONES

### Versión 1.0 (Actual)
- ✅ Sistema base funcional
- ✅ Dashboard principal
- ✅ Módulo de extracción integrado
- ✅ Sistema de autenticación
- ✅ Estructura modular

### Próximas versiones
- 🔄 Completar módulo de contabilidad
- 🔄 Completar módulo de televisión
- 🔄 Completar módulo de sedes
- 🔄 Completar módulo de portales
- 🔄 API REST completa
- 🔄 Sistema de notificaciones
- 🔄 Modo oscuro/claro

## 🛠️ MANTENIMIENTO

### Tareas recomendadas
1. **Diarias:**
   - Revisar logs de errores
   - Verificar respaldos de base de datos

2. **Semanales:**
   - Actualizar dependencias
   - Limpiar archivos temporales

3. **Mensuales:**
   - Generar reportes de uso
   - Optimizar base de datos

### Respaldo
```bash
# Base de datos
cp database.db backup/database_$(date +%Y%m%d).db

# Archivos de configuración
cp config.py backup/config_$(date +%Y%m%d).py
```

## 📞 SOPORTE

### Documentación
- README.md (este archivo)
- Comentarios en código fuente
- Documentación inline

### Contacto
- Issues: GitHub repository
- Email: [tu-email@dominio.com]

---

**Nota:** Este sistema está en constante desarrollo. Los módulos marcados como "En desarrollo" estarán disponibles en futuras actualizaciones.

**Versión:** 1.0  
**Última actualización:** 14/12/2025  
**Estado:** Estable para producción del módulo de extracción