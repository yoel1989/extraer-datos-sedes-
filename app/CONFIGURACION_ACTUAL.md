# CONFIGURACIÓN ACTUAL - SISTEMA DE EXTRACCIÓN DE DATOS
# Fecha: 14/12/2025
# Estado: ✅ FUNCIONANDO CORRECTAMENTE

## INFORMACIÓN GENERAL
- Aplicación Flask para extracción de datos de Telegram
- Base de datos: SQLite (extractions.db)
- Sesión Telegram: session_name.session (autorizada y funcionando)
- Directorio de reports: /reports/ (PDFs generados automáticamente)

## COMPONENTES PRINCIPALES

### 1. Aplicación Web
- **Archivo**: app.py
- **Puerto**: 5000
- **Acceso**: http://127.0.0.1:5000 o http://192.168.1.29:5000

### 2. Scripts de Extracción
- **Directorio**: /scripts/
- **Sitios configurados**: 11 sitios
  - BRISAS (telegram_brisas_pdf.py)
  - CACHICAMO (telegram_cachicamo_pdf.py)
  - CANO LAJAS (telegram_cano_lajas_pdf.py)
  - CANO PESCADO (telegram_cano_pescado_pdf.py)
  - CERRITOS (telegram_cerritos_pdf.py)
  - MANANTIALES (telegram_manantiales_1_pdf.py)
  - MANANTIALES-2 (telegram_manantiales_2_pdf.py)
  - MIRAVALLE (telegram_miravalle_pdf.py)
  - SAN MIGUEL (telegram_san_miguel_pdf.py)
  - LA TORTUGA (telegram_tortuga_pdf.py)
  - TROPEZON (telegram_tropezon_pdf.py)

### 3. Configuración Telegram
- **API_ID**: <VALOR_EN_.env>
- **API_HASH**: <VALOR_EN_.env>
- **PHONE**: <VALOR_EN_.env>
- **Sesión**: session_name.session (autorizada)

## DEPENDENCIAS
```
Flask==2.3.3
Werkzeug==2.3.7
telethon==1.34.0
reportlab==4.0.4
```

## ESTRUCTURA DE DIRECTORIOS
```
app/
├── app.py                    # Aplicación principal Flask
├── session_name.session      # Sesión de Telegram (NO ELIMINAR)
├── extractions.db           # Base de datos SQLite
├── requirements.txt         # Dependencias Python
├── scripts/                 # Scripts de extracción
│   ├── telegram_brisas_pdf.py
│   ├── telegram_cachicamo_pdf.py
│   └── ... (demás scripts)
├── templates/               # Plantillas HTML
│   └── index.html
├── reports/                 # PDFs generados
│   ├── reporte_BRISAS_*.pdf
│   └── reportes_*.zip
├── start.bat               # Inicio rápido
└── start_clean.bat         # Inicio limpio
```

## FUNCIONALIDADES PRINCIPALES

### 1. Extracción Individual
- **Endpoint**: POST /api/extract_site/<sitio_key>
- **Sitios**: brisas, cachicamo, cano_lajas, cano_pescado, cerritos, manantiales_1, manantiales_2, miravalle, san_miguel, tortuga, tropezon

### 2. Extracción Masiva
- **Endpoint**: POST /api/extract_all
- **Endpoint**: POST /api/generate_and_download_all

### 3. Gestión de Reportes
- **Listar PDFs**: GET /api/list_pdfs
- **Descargar PDF**: GET /reports/<filename>
- **Descargar todos**: POST /api/download_all_pdfs

### 4. Administración
- **Historial**: GET /api/extractions
- **Logs**: GET /api/logs
- **Estadísticas**: GET /api/database_stats
- **Limpiar DB**: POST /api/clean_database

## INSTRUCCIONES DE MANTENIMIENTO

### Inicio Rápido
```bash
# Opción 1: Usar batch files
start.bat          # Inicio normal
start_clean.bat    # Inicio limpio

# Opción 2: Manual
python app.py
```

### Si la Sesión de Telegram Falla
1. Eliminar session_name.session
2. Ejecutar: python create_session.py
3. Ingresar código de verificación de Telegram
4. Reiniciar aplicación

### Limpieza de Archivos Temporales
```bash
# Eliminar caché Python
rmdir /s /q __pycache__
rmdir /s /q scripts\__pycache__

# Limpiar logs antiguos (opcional)
del service_error.log
```

## ESTADO ACTUAL
- ✅ Sesión Telegram: Autorizada y funcionando
- ✅ Extracciones: Generando datos reales ($1,667,000 confirmados)
- ✅ PDFs: Siendo generados correctamente
- ✅ Base de datos: Funcionando
- ✅ Interface web: Operativa

## NOTAS IMPORTANTES
1. **NO ELIMINAR** session_name.session (contiene la autenticación)
2. **BACKUP** recomendado: extractions.db y reports/
3. **REINICIAR** aplicación si hay errores de conexión
4. **VERIFICAR** acceso a internet y conexión con Telegram

## CONTACTO/SOPORTE
- Configuración guardada: 14/12/2025
- Última verificación: Funcionamiento correcto confirmado