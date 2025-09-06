import os
import re
import base64
import requests
import json
import time
from dotenv import load_dotenv
from colorama import init, Fore, Style
init()  # Inicializa colorama (necesario para Windows)

# Cargar variables desde .env
load_dotenv()

# URLs de la API
API_URL = "https://whatsapp-osint.p.rapidapi.com/wspic/b64"
API_HOST = "whatsapp-osint.p.rapidapi.com"

# Endpoints disponibles
ENDPOINTS = {
    "1": {"name": "Foto de perfil", "url": "/wspic/b64", "method": "GET"},
    "2": {"name": "Estado del usuario", "url": "/about", "method": "GET"},
    "3": {"name": "Verificación de negocio", "url": "/bizos", "method": "POST"},
    "4": {"name": "Información de dispositivos", "url": "/devices", "method": "GET"},
    "5": {"name": "Información OSINT completa", "url": "/wspic/dck", "method": "GET"},
    "6": {"name": "Configuración de privacidad", "url": "/privacy", "method": "GET"}
}

def show_banner():
    print(Fore.GREEN + """
⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⣤⣶⣶⣶⣶⣤⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣤⡀⠀⠀⠀⠀
⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠀⠀⠀
⠀⢀⣾⣿⣿⣿⣿⡿⠟⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀
⠀⣾⣿⣿⣿⣿⡟⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀
⢠⣿⣿⣿⣿⣿⣧⠀⠀⠀⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄
⢸⣿⣿⣿⣿⣿⣿⣦⠀⠀⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
⠘⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠈⠻⢿⣿⠟⠉⠛⠿⣿⣿⣿⣿⣿⣿⠃
⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄⡀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⡿⠀
⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣤⣤⣴⣾⣿⣿⣿⣿⡿⠁⠀
⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠀⠀⠀
⠀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⠁⠀⠀⠀⠀
⠠⠛⠛⠛⠉⠁⠀⠈⠙⠛⠛⠿⠿⠿⠿⠛⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀
""" + Style.RESET_ALL)
    print(Fore.GREEN + "🔍" * 15 + Style.RESET_ALL)
    print("\n" + Style.BRIGHT + Fore.GREEN + "WhatsApp OSINT Tool" + Style.RESET_ALL + "\n")

def sanitize_phone(raw: str) -> str:
    return re.sub(r"[^\d]", "", raw)

def is_valid_phone(p: str) -> bool:
    return p.isdigit() and 8 <= len(p) <= 15

def show_menu():
    print(Fore.CYAN + "🔍 Selecciona el tipo de consulta:" + Style.RESET_ALL)
    print()
    for key, endpoint in ENDPOINTS.items():
        print(f"  {Fore.YELLOW}{key}.{Style.RESET_ALL} {endpoint['name']}")
    print()

def fetch_endpoint(phone: str, api_key: str, endpoint: str, method: str = "GET"):
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": API_HOST}
    url = "https://whatsapp-osint.p.rapidapi.com" + endpoint
    
    try:
        if method == "GET":
            return requests.get(url, headers=headers, params={"phone": phone}, timeout=30)
        elif method == "POST":
            return requests.post(url, headers=headers, data=phone, timeout=30)
    except requests.RequestException as e:
        raise e

def fetch(phone: str, api_key: str):
    """Función original del repositorio"""
    headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": API_HOST}
    url = API_URL + "?phone=" + phone
    try:
        return requests.get(url, headers=headers, timeout=30)
    except requests.RequestException as e:
        raise e

def save_b64(b64_str: str, path: str) -> bool:
    try:
        img = base64.b64decode(b64_str, validate=True)
        with open(path, "wb") as f:
            f.write(img)
        return True
    except Exception:
        return False

def process_profile_picture(phone: str, api_key: str):
    """Procesa la foto de perfil (endpoint original)"""
    try:
        resp = fetch_endpoint(phone, api_key, "/wspic/b64", "GET")
    except requests.RequestException as e:
        print("❌ Error de red:", e)
        return

    print("HTTP:", resp.status_code)
    ctype = resp.headers.get("Content-Type", "")

    if resp.status_code != 200:
        print("❌ Error del servidor:", resp.text.strip())
        return

    body = resp.text.strip()

    if "application/json" in ctype.lower():
        try:
            data = resp.json()
        except Exception:
            print("❌ No se pudo leer JSON. Cuerpo:\n", body)
            return
        b64 = data.get("data") or data.get("image") or data.get("base64")
        if not b64:
            print("ℹ️ Sin campo base64 en la respuesta:", data)
            return
        fname = f"whatsapp_{phone}.jpg"
        if save_b64(b64, fname):
            print(f"✅ Imagen guardada como {fname}")
        else:
            print("❌ Base64 inválido.")
    else:
        lo = body.lower()
        if "no profile picture" in lo or "does not have a profile picture" in lo:
            print("ℹ️ Ese usuario no tiene foto de perfil (o está oculta).")
        else:
            fname = f"whatsapp_{phone}.jpg"
            if save_b64(body, fname):
                print(f"✅ Imagen guardada como {fname}")
            else:
                print(f"ℹ️ Respuesta en texto:\n{body}")

def process_user_status(phone: str, api_key: str):
    """Procesa el estado del usuario"""
    try:
        resp = fetch_endpoint(phone, api_key, "/about", "GET")
    except requests.RequestException as e:
        print("❌ Error de red:", e)
        return

    print("HTTP:", resp.status_code)
    
    if resp.status_code != 200:
        print("❌ Error del servidor:", resp.text.strip())
        return

    try:
        data = resp.json()
        print(f"\n📊 {Fore.CYAN}Estado del usuario:{Style.RESET_ALL}")
        print(f"   📱 Número: {phone}")
        
        if "about" in data:
            if data['about'] and data['about'].strip():
                print(f"   📝 Estado: {data['about']}")
            else:
                print(f"   📝 Estado: Sin estado personalizado")
        elif "status" in data:
            print(f"   📝 Estado: {data['status']}")
        if "last_seen" in data:
            print(f"   🕒 Última vez visto: {data['last_seen']}")
        if "is_online" in data:
            status = "🟢 En línea" if data['is_online'] else "🔴 Desconectado"
            print(f"   {status}")
            
    except Exception:
        print("ℹ️ Respuesta en texto:", resp.text.strip())

def process_business_verification(phone: str, api_key: str):
    """Procesa la verificación de negocio"""
    try:
        # El endpoint /bizos requiere JSON en el body
        headers = {
            "x-rapidapi-key": api_key, 
            "x-rapidapi-host": API_HOST,
            "Content-Type": "application/json"
        }
        url = "https://whatsapp-osint.p.rapidapi.com/bizos"
        data = {"phone": phone}
        resp = requests.post(url, headers=headers, json=data, timeout=30)
    except requests.RequestException as e:
        print("❌ Error de red:", e)
        return

    print("HTTP:", resp.status_code)
    
    if resp.status_code != 200:
        print("❌ Error del servidor:", resp.text.strip())
        return

    try:
        data = resp.json()
        print(f"\n🏢 {Fore.CYAN}Verificación de WhatsApp Business:{Style.RESET_ALL}")
        print(f"   📱 Número: {phone}")
        
        # La respuesta es un array con un objeto
        if isinstance(data, list) and len(data) > 0:
            business_data = data[0]
            
            if "isBusiness" in business_data:
                is_biz = business_data['isBusiness']
                if is_biz and is_biz != "false" and "Not a Business Account" not in str(is_biz) and "Not Registered" not in str(is_biz):
                    print(f"   ✅ Es WhatsApp Business: {is_biz}")
                elif "Not a Business Account" in str(is_biz):
                    print(f"   ❌ No es WhatsApp Business (es cuenta personal)")
                elif "Not Registered" in str(is_biz):
                    print(f"   ❌ No está registrado en WhatsApp")
                else:
                    print(f"   ❌ No es WhatsApp Business")
                    
            if "verifiedName" in business_data and business_data['verifiedName']:
                print(f"   🏪 Nombre verificado: {business_data['verifiedName']}")
                
            if "query" in business_data:
                print(f"   🔍 Consulta: {business_data['query']}")
        else:
            print("   ℹ️ No se encontró información de negocio")
            
    except Exception:
        print("ℹ️ Respuesta en texto:", resp.text.strip())

def process_device_info(phone: str, api_key: str):
    """Procesa la información de dispositivos"""
    try:
        resp = fetch_endpoint(phone, api_key, "/devices", "GET")
    except requests.RequestException as e:
        print("❌ Error de red:", e)
        return

    print("HTTP:", resp.status_code)
    
    if resp.status_code != 200:
        print("❌ Error del servidor:", resp.text.strip())
        return

    try:
        data = resp.json()
        print(f"\n📱 {Fore.CYAN}Información de dispositivos:{Style.RESET_ALL}")
        print(f"   📞 Número: {phone}")
        
        if "devices" in data:
            if isinstance(data['devices'], list) and data['devices']:
                print(f"   🔢 Total de dispositivos: {len(data['devices'])}")
                for i, device in enumerate(data['devices'], 1):
                    print(f"\n   📱 Dispositivo {i}:")
                    if "device_type" in device:
                        print(f"      🖥️  Tipo: {device['device_type']}")
                    if "os" in device:
                        print(f"      💻 SO: {device['os']}")
                    if "last_seen" in device:
                        print(f"      🕒 Última vez visto: {device['last_seen']}")
                    if "status" in device:
                        status = "🟢 En línea" if device['status'] == "online" else "🔴 Desconectado"
                        print(f"      {status}")
            elif isinstance(data['devices'], int):
                print(f"   🔢 Total de dispositivos: {data['devices']}")
            else:
                print("   ℹ️ No se encontró información de dispositivos")
        if "message" in data:
            print(f"   ℹ️ {data['message']}")
        if "devices" not in data and "message" not in data:
            print("   ℹ️ No se encontró información de dispositivos")
            
    except Exception:
        print("ℹ️ Respuesta en texto:", resp.text.strip())

def process_osint_info(phone: str, api_key: str):
    """Procesa la información OSINT completa"""
    try:
        resp = fetch_endpoint(phone, api_key, "/wspic/dck", "GET")
    except requests.RequestException as e:
        print("❌ Error de red:", e)
        return

    print("HTTP:", resp.status_code)
    
    if resp.status_code != 200:
        print("❌ Error del servidor:", resp.text.strip())
        return

    try:
        data = resp.json()
        print(f"\n🔍 {Fore.CYAN}Información OSINT completa:{Style.RESET_ALL}")
        print(f"   📱 Número: {phone}")
        
        if "verification_status" in data:
            print(f"   ✅ Verificación: {data['verification_status']}")
        if "last_seen" in data:
            print(f"   🕒 Última vez visto: {data['last_seen']}")
        if "profile_info" in data:
            print(f"   👤 Información del perfil disponible")
        if "osint_data" in data:
            print(f"   📊 Datos OSINT adicionales disponibles")
            
        print(f"\n📄 {Fore.YELLOW}Datos completos:{Style.RESET_ALL}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
            
    except Exception:
        print("ℹ️ Respuesta en texto:", resp.text.strip())

def process_privacy_settings(phone: str, api_key: str):
    """Procesa la configuración de privacidad"""
    try:
        resp = fetch_endpoint(phone, api_key, "/privacy", "GET")
    except requests.RequestException as e:
        print("❌ Error de red:", e)
        return

    print("HTTP:", resp.status_code)
    
    if resp.status_code != 200:
        print("❌ Error del servidor:", resp.text.strip())
        return

    try:
        data = resp.json()
        print(f"\n🔒 {Fore.CYAN}Configuración de privacidad:{Style.RESET_ALL}")
        print(f"   📱 Número: {phone}")
        
        if "privacy" in data:
            print(f"   🔒 Configuración de privacidad: {data['privacy']}")
        elif "profile_visibility" in data:
            print(f"   👤 Visibilidad del perfil: {data['profile_visibility']}")
        if "last_seen" in data:
            print(f"   🕒 Última vez visto: {data['last_seen']}")
        if "read_receipts" in data:
            receipts = "✅ Activadas" if data['read_receipts'] else "❌ Desactivadas"
            print(f"   📨 Confirmaciones de lectura: {receipts}")
        if "status_visibility" in data:
            print(f"   📝 Visibilidad del estado: {data['status_visibility']}")
        if "profile_picture" in data:
            print(f"   🖼️  Visibilidad de foto: {data['profile_picture']}")
            
    except Exception:
        print("ℹ️ Respuesta en texto:", resp.text.strip())


def main():
    show_banner()
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        print("❌ No se encontró RAPIDAPI_KEY en .env")
        return

    # Mostrar menú
    show_menu()
    
    # Seleccionar opción
    while True:
        choice = input(f"{Fore.CYAN}Selecciona una opción (1-6): {Style.RESET_ALL}").strip()
        if choice in ENDPOINTS:
            break
        print("❌ Opción no válida. Selecciona un número del 1 al 6.")

    # Obtener número de teléfono
    phone = input("Introduce el número (con código de país, sin '+', p.ej. 51916574069): ").strip()
    phone = sanitize_phone(phone)

    if not is_valid_phone(phone):
        print("❌ Formato no válido. Ejemplo: 51916574069")
        return

    print(f"\n🔍 {Fore.GREEN}Procesando consulta...{Style.RESET_ALL}")
    print(f"📱 Número: {phone}")
    print(f"🎯 Consulta: {ENDPOINTS[choice]['name']}")
    print()

    # Procesar según la opción seleccionada
    if choice == "1":
        process_profile_picture(phone, api_key)
    elif choice == "2":
        process_user_status(phone, api_key)
    elif choice == "3":
        process_business_verification(phone, api_key)
    elif choice == "4":
        process_device_info(phone, api_key)
    elif choice == "5":
        process_osint_info(phone, api_key)
    elif choice == "6":
        process_privacy_settings(phone, api_key)

    print(f"\n✅ {Fore.GREEN}Consulta completada.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
