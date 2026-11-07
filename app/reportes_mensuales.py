"""Genera los reportes mensuales de todas las sedes y los guarda en Supabase.

Periodo automatico (sin argumentos): desde el dia 29 del mes anterior hasta hoy
(hora de Colombia, normalmente el 28). Si el mes anterior no tiene dia 29 se usa
su ultimo dia, asi febrero queda del 28 al 28, como en los reportes ya generados.

Uso:
  python reportes_mensuales.py                         # periodo automatico
  python reportes_mensuales.py 2026-01-29 2026-02-28   # periodo manual

Variables de entorno necesarias: TELEGRAM_API_ID, TELEGRAM_API_HASH,
TELEGRAM_PHONE, SUPABASE_URL y SUPABASE_SERVICE_KEY. El archivo
session_name.session debe estar en esta misma carpeta.
"""
import asyncio
import calendar
import importlib
import os
import shutil
import sys
import tempfile
from datetime import date, datetime
from zoneinfo import ZoneInfo

import requests
from dotenv import find_dotenv, load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')

load_dotenv(find_dotenv())
# Los scripts abren session_name.session y crean el PDF en el directorio actual.
os.chdir(BASE_DIR)
sys.path.insert(0, SCRIPTS_DIR)

BUCKET = 'reportes-sedes'

# (clave, nombre visible, modulo del script en scripts/)
SEDES = [
    ('brisas', 'BRISAS', 'telegram_brisas_pdf'),
    ('cachicamo', 'CACHICAMO', 'telegram_cachicamo_pdf'),
    ('cano_lajas', 'CANO LAJAS', 'telegram_cano_lajas_pdf'),
    ('cano_pescado', 'CANO PESCADO', 'telegram_cano_pescado_pdf'),
    ('manantiales_1', 'MANANTIALES', 'telegram_manantiales_1_pdf'),
    ('manantiales_2', 'MANANTIALES-2', 'telegram_manantiales_2_pdf'),
    ('miravalle', 'MIRAVALLE', 'telegram_miravalle_pdf'),
    ('tortuga', 'LA TORTUGA', 'telegram_tortuga_pdf'),
    ('tropezon', 'TROPEZON', 'telegram_tropezon_pdf'),
]


def periodo_automatico():
    hoy = datetime.now(ZoneInfo('America/Bogota')).date()
    anio = hoy.year - 1 if hoy.month == 1 else hoy.year
    mes = 12 if hoy.month == 1 else hoy.month - 1
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    return date(anio, mes, min(29, ultimo_dia)).isoformat(), hoy.isoformat()


def leer_periodo():
    if len(sys.argv) == 3:
        inicio, fin = sys.argv[1], sys.argv[2]
    else:
        inicio, fin = periodo_automatico()
    # Valida el formato antes de llamar a Telegram.
    datetime.strptime(inicio, '%Y-%m-%d')
    datetime.strptime(fin, '%Y-%m-%d')
    return inicio, fin


async def generar_pdf(clave, modulo_nombre, inicio, fin, carpeta):
    modulo = importlib.import_module(modulo_nombre)
    mensajes = await modulo.obtener_todos_los_mensajes(inicio, fin)
    if not mensajes:
        return None
    ruta_generada, ventas, _ = modulo.crear_pdf(mensajes, inicio, fin)
    destino = os.path.join(carpeta, f'{clave}.pdf')
    shutil.move(ruta_generada, destino)
    return destino, ventas, len(mensajes)


def subir(url, key, clave, nombre, inicio, fin, ruta_pdf, ventas, total_mensajes):
    ruta_storage = f'{inicio}_a_{fin}/{clave}.pdf'
    cabeceras = {'Authorization': f'Bearer {key}', 'apikey': key}

    with open(ruta_pdf, 'rb') as archivo:
        r = requests.post(
            f'{url}/storage/v1/object/{BUCKET}/{ruta_storage}',
            headers={**cabeceras, 'Content-Type': 'application/pdf', 'x-upsert': 'true'},
            data=archivo,
            timeout=120,
        )
    r.raise_for_status()

    fila = {
        'sede_clave': clave,
        'sede': nombre,
        'periodo_inicio': inicio,
        'periodo_fin': fin,
        'archivo_path': ruta_storage,
        'archivo_nombre': os.path.basename(ruta_pdf),
        'total_ventas': ventas['total_valor'],
        'total_mensajes': total_mensajes,
    }
    r = requests.post(
        f'{url}/rest/v1/reportes_sedes?on_conflict=sede_clave,periodo_inicio',
        headers={
            **cabeceras,
            'Content-Type': 'application/json',
            'Prefer': 'resolution=merge-duplicates,return=minimal',
        },
        json=fila,
        timeout=60,
    )
    r.raise_for_status()


async def main():
    url = os.environ['SUPABASE_URL'].rstrip('/')
    key = os.environ['SUPABASE_SERVICE_KEY']
    inicio, fin = leer_periodo()
    print(f'Periodo: {inicio} a {fin}')

    carpeta = tempfile.mkdtemp(prefix='reportes_')
    errores = []
    try:
        for clave, nombre, modulo in SEDES:
            print(f'\n== {nombre} ==')
            try:
                resultado = await generar_pdf(clave, modulo, inicio, fin, carpeta)
                if resultado is None:
                    print('Sin mensajes en el periodo; no se sube nada.')
                    continue
                ruta_pdf, ventas, total_mensajes = resultado
                subir(url, key, clave, nombre, inicio, fin, ruta_pdf, ventas, total_mensajes)
                print(f'Subido: {total_mensajes} mensajes.')
            except Exception as e:  # una sede con error no detiene a las demas
                errores.append(nombre)
                print(f'ERROR en {nombre}: {type(e).__name__}: {e}')
    finally:
        shutil.rmtree(carpeta, ignore_errors=True)

    if errores:
        print(f'\nSedes con error: {", ".join(errores)}')
        sys.exit(1)
    print('\nListo.')


if __name__ == '__main__':
    asyncio.run(main())
