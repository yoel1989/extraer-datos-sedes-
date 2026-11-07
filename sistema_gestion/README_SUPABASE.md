# Sistema de Gestión Integral

Sistema web integral para la gestión de extracciones de datos, contabilidad, televisión y portales cautivos.

## 🚀 Características

- **Extracción de Datos**: Automatización con Telegram para múltiples sedes
- **Contabilidad Completa**: Gestión de ingresos, egresos, reportes y gráficos
- **Módulo de Televisión**: Administración de servicios TV
- **Portales Cautivos**: Gestión de sedes y clientes
- **Autenticación y Permisos**: Sistema de usuarios y roles
- **Base de Datos Flexible**: Compatible con SQLite y Supabase

## 📋 Requisitos

- Python 3.8+
- pip (gestor de paquetes de Python)
- Cuenta de Supabase (opcional, para modo producción)

## 🛠️ Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repositorio-url>
   cd sistema_gestion
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   ```
   
   Edita el archivo `.env` con tu configuración:
   ```env
   # Configuración Flask
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=tu-clave-secreta-aqui
   
   # Configuración de Supabase (opcional)
   SUPABASE_URL=https://tu-proyecto.supabase.co
   SUPABASE_ANON_KEY=tu-llave-anon-aqui
   USE_SUPABASE=false  # Cambiar a true para usar Supabase
   
   # Configuración Telegram (para extracción de datos)
   TELEGRAM_API_ID=tu-api-id
   TELEGRAM_API_HASH=tu-api-hash
   TELEGRAM_PHONE=+573123456789
   ```

## 🗄️ Configuración de Base de Datos

### Opción 1: SQLite (Desarrollo)

Por defecto, el sistema usa SQLite. No requiere configuración adicional.

### Opción 2: Supabase (Producción)

1. **Crear proyecto en Supabase**
   - Ve a https://supabase.com y crea un nuevo proyecto
   - Copia tu URL y llave anónima al archivo `.env`

2. **Ejecutar script SQL**
   ```bash
   # En la consola SQL de Supabase, ejecuta:
   cat scripts/supabase_setup.sql
   ```
   O simplemente copia y pega el contenido del archivo `scripts/supabase_setup.sql`

3. **Activar Supabase**
   - Establece `USE_SUPABASE=true` en tu archivo `.env`

4. **Migrar datos existentes (si aplica)**
   ```bash
   python scripts/migrate_to_supabase.py
   ```

## 🚀 Ejecución

### Método 1: Script Personalizado (Recomendado)

```bash
python run_escobarnet.py
```

### Método 2: Flask CLI

```bash
flask run --port 5002
```

### Método 3: Python Directo

```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5002`

### Modo Producción

```bash
# Establecer variables de entorno
export FLASK_ENV=production
export USE_SUPABASE=true

# Iniciar aplicación
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
```

## 📁 Estructura del Proyecto

```
sistema_gestion/
├── app.py                    # Aplicación principal Flask
├── config.py                 # Configuración de la aplicación
├── modules/                  # Módulos del sistema
│   ├── contabilidad/         # Módulo de contabilidad
│   ├── extraccion_datos/     # Módulo de extracción de datos
│   ├── television/           # Módulo de televisión
│   ├── sedes/               # Módulo de sedes
│   └── portales_cautivos/   # Módulo de portales cautivos
├── utils/                    # Utilidades compartidas
│   ├── database.py          # Configuración SQLAlchemy (legacy)
│   ├── auth.py              # Autenticación y usuarios
│   ├── supabase_client.py   # Cliente de Supabase
│   └── database_manager.py # Gestor unificado de BD
├── templates/               # Plantillas HTML base
├── static/                  # Archivos estáticos
├── instance/               # Archivos SQLite
├── scripts/                # Scripts de mantenimiento
│   ├── supabase_setup.sql  # Script SQL para Supabase
│   └── migrate_to_supabase.py # Script de migración
├── requirements.txt        # Dependencias Python
├── .env.example           # Plantilla de variables de entorno
└── README.md             # Este archivo
```

## 🔧 Módulos

### Contabilidad
- Gestión de transacciones financieras
- Categorías personalizadas
- Reportes y gráficos interactivos
- Exportación a PDF y Excel
- Sincronización con extracciones de datos

### Extracción de Datos
- Automatización con Telegram
- Soporte para múltiples sedes
- Reportes PDF automáticos
- Sistema de logs y monitoreo

### Televisión
- Gestión de servicios de TV
- Control de suscripciones
- Reportes de ingresos

### Portales Cautivos
- Administración de sedes
- Gestión de clientes
- Configuración de portales

## 👥 Usuarios y Roles

### Admin
- Acceso completo a todos los módulos
- Gestión de usuarios
- Configuración del sistema

### Usuario
- Acceso limitado a módulos específicos
- Solo puede ver y exportar datos

## 🔑 Credenciales por Defecto

- **Usuario**: admin
- **Contraseña**: admin123
- **URL**: http://localhost:5002

**Importante**: Cambia estas credenciales en producción.

## 📊 Migración de Datos

Si tienes datos existentes en SQLite y quieres migrar a Supabase:

1. **Configura tu proyecto Supabase** (ver sección arriba)
2. **Ejecuta el script de migración**:
   ```bash
   python scripts/migrate_to_supabase.py
   ```
3. **Activa Supabase en el .env**:
   ```env
   USE_SUPABASE=true
   ```

## 🐛 Troubleshooting

### Errores Comunes

1. **Error de importación de Supabase**
   ```bash
   pip install supabase
   ```

2. **Error de conexión a Supabase**
   - Verifica que las variables de entorno estén configuradas correctamente
   - Asegúrate que tu proyecto Supabase esté activo

3. **Error de migración**
   - Verifica que las tablas existan en Supabase
   - Ejecuta el script SQL `supabase_setup.sql` primero

### Logs y Depuración

- Los logs se guardan en `logs/app.log`
- Para depurar en desarrollo: `export FLASK_DEBUG=1`

## 🤝 Contribución

1. Fork del proyecto
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Licencia

Este proyecto está bajo licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico:
- Crea un issue en el repositorio
- Contacta al equipo de desarrollo

---

**Desarrollado con ❤️ por el equipo de sistemas**