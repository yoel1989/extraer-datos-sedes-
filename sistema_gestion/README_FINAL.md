# 🚀 SISTEMA DE GESTIÓN ESCOBARNET v3.0

**100% Supabase - Sin SQLite**

## 📋 Descripción

Sistema web integral para la gestión de extracciones de datos, contabilidad, televisión y portales cautivos. Funciona completamente con Supabase como base de datos en la nube.

## 🌟 Características Principales

- **☁️ Base de datos en la nube** con Supabase PostgreSQL
- **👥 Multiusuario real** - Acceso concurrente sin límites
- **🔒 Seguridad avanzada** - Row Level Security y autenticación
- **📊 Contabilidad completa** - Gestión financiera con reportes
- **📤 Extracción automatizada** - Telegram integration
- **🖥️ Módulos múltiples** - Dashboard, Contabilidad, TV, Sedes, Portales
- **📈 Escalabilidad infinita** - Sin límite de usuarios o datos

## 🚀 Instalación y Ejecución

### 1. **Requisitos**
- Python 3.8+
- Cuenta de Supabase (ya configurada)

### 2. **Instalación**
```bash
# Clonar repositorio
git clone <repositorio-url>
cd sistema_gestion

# Instalar dependencias
pip install -r requirements.txt
```

### 3. **Configuración**
El archivo `.env` ya está configurado con tu proyecto Supabase:
```env
SUPABASE_URL=<VALOR_EN_.env>
SUPABASE_ANON_KEY=<VALOR_EN_.env>
FLASK_RUN_PORT=5002
```

### 4. **Ejecución**
```bash
# Opción 1: Script personalizado (recomendado)
python run_escobarnet.py

# Opción 2: Archivo batch (Windows)
INICIO.bat

# Opción 3: Flask CLI
flask run --port 5002
```

## 🌐 Acceso al Sistema

- **URL:** http://localhost:5002
- **Usuario:** admin
- **Contraseña:** admin123

## 📁 Estructura del Proyecto

```
sistema_gestion/
├── 📄 app.py                    # Aplicación Flask principal
├── 📄 config.py                 # Configuración (solo Supabase)
├── 📄 .env                      # Variables de entorno
├── 📄 run_escobarnet.py         # Script de inicio
├── 📄 INICIO.bat               # Inicio rápido Windows
├── 
├── 📁 modules/                  # Módulos del sistema
│   ├── 📁 contabilidad/         # Gestión financiera
│   ├── 📁 extraccion_datos/     # Extracción automática
│   ├── 📁 television/           # Módulo de TV
│   ├── 📁 sedes/               # Gestión de sedes
│   └── 📁 portales_cautivos/   # Portales WiFi
├── 
├── 📁 utils/                    # Utilidades
│   ├── 📄 supabase_db.py        # Gestor de base de datos
│   ├── 📄 auth.py              # Autenticación
│   └── 📄 supabase_client.py   # Cliente Supabase
├── 
├── 📁 templates/               # Plantillas HTML
├── 📁 static/                  # Archivos estáticos
└── 📁 scripts/                # Scripts de mantenimiento
    └── 📄 supabase_setup.sql   # Script SQL inicial
```

## 🗄️ Base de Datos Supabase

### **Tablas Principales:**
- **users** - Usuarios y autenticación
- **extractions** - Datos de extracciones
- **extraction_logs** - Logs del sistema
- **transacciones** - Movimientos financieros
- **categorias** - Categorías contables

### **Características Avanzadas:**
- ✅ **Índices optimizados** para rendimiento
- ✅ **Triggers automáticos** para timestamps
- ✅ **Funciones SQL** para reportes complejos
- ✅ **50+ categorías pre-configuradas**
- ✅ **Row Level Security** configurable

## 🔧 Módulos

### **💰 Contabilidad**
- Gestión completa de ingresos y egresos
- Categorías personalizables
- Reportes financieros y gráficos
- Exportación a PDF y Excel
- Resumen por sedes, clientes, TV

### **📤 Extracción de Datos**
- Automatización con Telegram
- Soporte para 11 sedes configuradas
- Generación de reportes PDF
- Sistema de logs y monitoreo
- Estado en tiempo real

### **📺 Televisión**
- Gestión de servicios de TV
- Control de suscripciones
- Reportes de ingresos TV
- Administración de contenido

### **🏢 Sedes**
- Gestión de sedes instaladas
- Control de estado y configuración
- Reportes por ubicación

### **📶 Portales Cautivos**
- Administración de portales WiFi
- Gestión de clientes
- Configuración de acceso

## 👥 Usuarios y Permisos

### **👑 Administrador (admin)**
- Acceso completo a todos los módulos
- Gestión de usuarios
- Configuración del sistema
- Ver, crear, editar, eliminar todo

### **👤 Usuario (usuario)**
- Acceso limitado a módulos específicos
- Solo puede ver y exportar datos
- No puede configurar el sistema

## 🔐 Seguridad

- **🛡️ Row Level Security** en Supabase
- **🔑 Contraseñas encriptadas** con bcrypt
- **🚫 Protección CSRF** en formularios
- **📝 Logs de auditoría** automático
- **⏰ Sesiones con timeout configurable**

## 📊 Reportes y Análisis

### **📈 Contabilidad**
- Balance general (ingresos vs egresos)
- Evolución mensual
- Análisis por categorías
- Detalle por sedes/clientes/TV

### **📋 Extracciones**
- Reportes por sede y período
- Estadísticas de ventas
- Comisiones calculadas
- Estado de procesamiento

## 🚀 Despliegue

### **🏠 Desarrollo**
```bash
python run_escobarnet.py
```

### **🌐 Producción**
```bash
# Usando gunicorn
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:5002 app:app

# O usando Docker (crear Dockerfile)
docker build -t escobarnet .
docker run -p 5002:5002 escobarnet
```

## 🔍 Monitoreo

- **📊 Dashboard principal** con estadísticas en tiempo real
- **📋 Logs de errores** centralizados
- **⚡ Estado de módulos** individual
- **📈 Métricas de uso** por usuario

## 🛠️ Mantenimiento

### **📦 Actualizaciones**
```bash
# Actualizar dependencias
pip install -r requirements.txt --upgrade

# Reiniciar servicios
python run_escobarnet.py
```

### **💾 Backups**
- Supabase maneja **backups automáticos**
- Retención configurable en el dashboard
- Exportación manual disponible

## 🐛 Solución de Problemas

### **❌ Errores Comunes**

1. **"Cannot connect to Supabase"**
   - Verificar variables de entorno
   - Revisar conexión a internet

2. **"Table does not exist"**
   - Ejecutar script SQL en Supabase
   - Verificar credenciales

3. **"Module not found"**
   - Ejecutar `pip install -r requirements.txt`
   - Revisar entorno virtual

### **📋 Logs y Depuración**
- Logs guardados en consola y Supabase
- Modo debug disponible para desarrollo
- Errores detallados con stack trace

## 📞 Soporte

- **📧 Email:** soporte@escobarnet.com
- **📱 Teléfono:** +57 XXX XXX XXXX
- **🌐 Web:** https://escobarnet.com
- **💬 Soporte en línea:** Dashboard → Ayuda

## 📜 Licencia

Este software está bajo **Licencia Propietaria ESCOBARNET**.
Uso exclusivo para fines comerciales autorizados.

---

**🏆 ESCOBARNET - Sistema de Gestión Integral v3.0**  
*100% Cloud • 100% Supabase • 100% Profesional*