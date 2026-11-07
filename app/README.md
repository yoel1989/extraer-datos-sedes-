# Sistema de Extracción de Datos - Telegram

Aplicación web profesional para extraer datos de múltiples sitios de Telegram y generar reportes PDF automáticamente.

## 🚀 Características

- **Web Interface**: Interfaz web moderna y responsiva
- **One-Click Extraction**: Extraer todos los sitios con un solo botón
- **Individual Site Extraction**: Extraer sitios individualmente
- **Real-time Progress**: Seguimiento en tiempo real del progreso
- **Historial**: Base de datos con historial de extracciones
- **PDF Reports**: Generación automática de reportes PDF
- **Professional UI**: Diseño moderno con Bootstrap 5

## 📋 Sitios Configurados

- BRISAS
- CACHICAMO  
- CANO LAJAS
- CANO PESCADO
- MANANTIALES
- MANANTIALES-2
- MIRAVALLE
- LA TORTUGA
- TROPEZON

## 🛠️ Instalación

### Prerrequisitos
- Python 3.8+
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Navegar al directorio de la aplicación**:
   ```bash
   cd "C:\Users\yoooe\OneDrive\Desktop\EXTRAER DATOS\app"
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Iniciar la aplicación**:
   ```bash
   python app.py
   ```
   
   O simplemente hacer doble clic en `start.bat`

## 🌐 Uso

### Acceso a la Aplicación
1. Abre tu navegador web
2. Navega a: `http://localhost:5000`
3. La aplicación se cargará automáticamente

### Extracción de Datos

#### Opción 1: Extraer Todos los Sitios
1. Selecciona las fechas de inicio y fin
2. Haz clic en el botón verde **"Extraer Todo"**
3. La aplicación procesará todos los sitios automáticamente

#### Opción 2: Extraer Sitio Individual
1. Selecciona las fechas
2. Haz clic en el botón **"Extraer"** del sitio deseado
3. El sitio se procesará individualmente

### Monitoreo
- **Progreso en Tiempo Real**: Visualiza el progreso de cada extracción
- **Historial**: Consulta todas las extracciones anteriores
- **Logs Detallados**: Revisa logs detallados de cada extracción
- **Descarga de PDFs**: Descarga los reportes generados

## 📊 Estructura de Archivos

```
app/
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias de Python
├── start.bat             # Script de inicio para Windows
├── static/
│   ├── css/
│   │   └── style.css     # Estilos personalizados
│   └── js/
│       └── app.js        # Lógica del frontend
├── templates/
│   └── index.html        # Interfaz web principal
├── scripts/              # Scripts de Telegram (copiar aquí)
├── reports/              # Reportes PDF generados
└── extractions.db        # Base de datos SQLite
```

## 🔧 Configuración

### Variables de Configuración
Las credenciales de Telegram están configuradas en cada script individual:

```python
API_ID = <VALOR_EN_.env>
API_HASH = '<VALOR_EN_.env>'
PHONE = '<VALOR_EN_.env>'
```

### Precios de Pines
Configurados en cada script:

```python
PRECIOS_PINES = {
    "1Hora": 2000,
    "3Horas": 4000,
    "5Horas": 6000,
    "10Horas": 10000
}
```

## 📱 Características de la Interfaz

### Panel de Control
- Selector de fechas con validación
- Botón principal de extracción
- Botón de refresco

### Sitios Disponibles
- Tarjetas visuales para cada sitio
- Indicadores de estado en tiempo real
- Botones de extracción individual

### Sistema de Progreso
- Barras de progreso animadas
- Notificaciones en tiempo real
- Estados actualizados automáticamente

### Historial de Extracciones
- Tabla detallada con todas las extracciones
- Filtros y ordenamiento
- Descarga directa de PDFs
- Logs detallados por extracción

## 🚨 Solución de Problemas

### Problemas Comunes

1. **Error de Conexión a Telegram**
   - Verifica las credenciales API
   - Asegúrate de tener conexión a internet

2. **Error de Dependencias**
   - Ejecuta: `pip install -r requirements.txt`
   - Verifica la versión de Python (3.8+)

3. **Puerto en Uso**
   - Cambia el puerto en `app.py`: `app.run(port=5001)`

4. **Permisos de Archivos**
   - Ejecuta como administrador
   - Verifica permisos de escritura en el directorio

### Logs y Depuración
- Los logs se guardan en la base de datos SQLite
- Revisa la consola para errores detallados
- Usa el modal de logs en la interfaz web

## 🔄 Actualización

Para actualizar la aplicación:

1. **Backup de datos**:
   ```bash
   cp extractions.db extractions_backup.db
   ```

2. **Actualizar código**:
   - Reemplazar archivos de la aplicación
   - Mantener `extractions.db` y `reports/`

3. **Reinstalar dependencias**:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

## 📞 Soporte

Si encuentras algún problema:

1. Revisa los logs en la interfaz web
2. Verifica la consola de la aplicación
3. Asegúrate de que todos los scripts de Telegram estén en el directorio correcto

## 🎯 Mejoras Futuras

- [ ] Sistema de notificaciones por email
- [ ] Programación de extracciones automáticas
- [ ] Dashboard analítico avanzado
- [ ] Exportación a Excel
- [ ] Sistema de usuarios y permisos
- [ ] API REST para integración externa

---

**Desarrollado con ❤️ usando Flask, Bootstrap 5 y ReportLab**