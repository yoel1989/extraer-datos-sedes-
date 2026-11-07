# SISTEMA INTEGRADO DE GESTIÓN
# Versión: 1.0
# Fecha: 14/12/2025
# Arquitectura: Aplicación web modular con Flask

## MÓDULOS PRINCIPALES

### 1. 🏠 Dashboard Principal
- Vista general de todos los módulos
- Estadísticas consolidadas
- Acceso rápido a cada módulo

### 2. 📊 Extracción de Datos (Existente)
- Sistema actual de extracción de Telegram
- Generación de PDFs y reportes
- Gestión de múltiples sitios

### 3. 💰 Contabilidad
- Gestión financiera
- Ingresos y egresos
- Reportes contables
- Facturación

### 4. 📺 Televisión
- Gestión de contenido TV
- Programación
- Control de streaming
- Estadísticas de visualización

### 5. 🏢 Sedes Instaladas
- Registro de sedes
- Gestión de ubicaciones
- Información de contacto
- Estado de instalaciones

### 6. 🔐 Portales Cautivos
- Gestión de portales WiFi
- Autenticación de usuarios
- Estadísticas de acceso
- Configuración de redes

## ESTRUCTURA DE DIRECTORIOS

```
sistema_gestion/
├── app.py                    # Aplicación principal
├── config.py                 # Configuración global
├── requirements.txt          # Dependencias
├── database.db              # Base de datos principal
├── static/                  # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
├── templates/               # Plantillas HTML
│   ├── base.html
│   ├── dashboard.html
│   └── modulos/
├── modules/                # Módulos del sistema
│   ├── __init__.py
│   ├── extraccion_datos/    # Módulo existente
│   ├── contabilidad/
│   ├── television/
│   ├── sedes/
│   └── portales_cautivos/
└── utils/                  # Utilidades compartidas
    ├── __init__.py
    ├── database.py
    └── auth.py
```

## TECNOLOGÍAS

- **Backend**: Flask + SQLAlchemy
- **Frontend**: Bootstrap 5 + JavaScript
- **Database**: SQLite (desarrollo) / PostgreSQL (producción)
- **Authentication**: Flask-Login
- **Charts**: Chart.js
- **Icons**: Font Awesome

## FUNCIONALIDADES CRUZADAS

- 🔐 Autenticación centralizada
- 📊 Dashboard con estadísticas en tiempo real
- 📱 Responsive design
- 🌙 Modo oscuro/claro
- 📤 Exportación de datos
- 🔔 Sistema de notificaciones
- 📋 Auditoría de acciones