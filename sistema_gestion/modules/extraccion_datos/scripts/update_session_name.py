import os
import re

# Directorio de scripts
scripts_dir = os.path.dirname(os.path.abspath(__file__))

# Patrón a buscar y reemplazar
old_pattern = r"session_path = os.path.join\(script_dir, 'session_name'\)"
new_code = """session_path = os.path.join(script_dir, 'session_extraccion')"""

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

print("Actualización de sesión completada.")