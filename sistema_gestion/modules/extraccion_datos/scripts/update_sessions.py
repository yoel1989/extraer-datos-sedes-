import os
import re

# Directorio de scripts
scripts_dir = os.path.dirname(os.path.abspath(__file__))

# Patrón a buscar y reemplazar
old_pattern = r"client = TelegramClient\('session_name', API_ID, API_HASH\)"
new_code = """import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    session_path = os.path.join(script_dir, 'session_name')
    client = TelegramClient(session_path, API_ID, API_HASH)"""

# Actualizar todos los scripts telegram_*.py
for filename in os.listdir(scripts_dir):
    if filename.startswith('telegram_') and filename.endswith('.py'):
        filepath = os.path.join(scripts_dir, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar el patrón
        new_content = re.sub(old_pattern, new_code, content)
        
        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Actualizado: {filename}")
        else:
            print(f"Sin cambios: {filename}")

print("Actualización completada.")