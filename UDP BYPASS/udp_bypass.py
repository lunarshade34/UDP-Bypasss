import ipaddress
import re
import time
import sys
import subprocess

DEFAULT_PORT = 80
DEFAULT_SECONDS = 5
SERVER_PROCESS_NAME = "server.exe"  # istersen burayı değiştir

def ask_ip():
    raw = input("IP: ").strip()
    if raw == "":
        raise KeyboardInterrupt("Kullanıcı iptal etti.")
    # validate IP
    try:
        ipaddress.ip_address(raw)
    except ValueError:
        raise ValueError(f"Geçersiz IP adresi: {raw}")
    return raw

def ask_port(default=DEFAULT_PORT):
    raw = input(f"Port: ").strip()
    if raw == "":
        return default
    try:
        port = int(raw)
    except ValueError:
        raise ValueError("Port bir tam sayı olmalı.")
    if not (1 <= port <= 65535):
        raise ValueError("Port 1 ile 65535 arasında olmalı.")
    return port

def ask_seconds(default=DEFAULT_SECONDS):
    raw = input(f"Süre: ").strip().lower()
    if raw == "":
        return default
    m = re.fullmatch(r'(\d+)(s|m)?', raw)
    if not m:
        raise ValueError("Süre formatı hatalı. Örnek: 120")
    value = int(m.group(1))
    suffix = m.group(2)
    if suffix == 'm':
        return value * 60
    else:
        return value

def is_process_running(name):
    name_lower = name.lower()
    try:
        import psutil
        for p in psutil.process_iter(['name']):
            try:
                pname = (p.info.get('name') or "").lower()
                if pname == name_lower:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    except Exception:
        
        if sys.platform.startswith("win"):
            try:
                out = subprocess.check_output(["tasklist"], text=True, stderr=subprocess.DEVNULL)
                for line in out.splitlines():
                    
                    if line:
                        first_col = line.split()[0].lower()
                        if first_col == name_lower:
                            return True
                return False
            except Exception:
                return False
        else:
            try:
                ret = subprocess.run(["pgrep", "-f", name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return ret.returncode == 0
            except Exception:
                return False

def wait_for_server(process_name=SERVER_PROCESS_NAME, check_interval=1, max_wait=None):
    waited = 0
    print(f"\n{process_name} çalışana kadar bekleniyor... (server.exe'yi çalıştırın)")
    while True:
        if is_process_running(process_name):
            print(f"{process_name} bulundu — devam ediliyor.")
            return True
        if max_wait is not None and waited >= max_wait:
            print(f"Zaman aşımı: {max_wait} saniye içinde {process_name} bulunamadı.")
            return False
        time.sleep(check_interval)
        waited += check_interval

def prompt_start_confirmation():
    try:
        import msvcrt
        print("Başlamak için ENTER tuşuna basın...")
        key = msvcrt.getch()
        if key in (b'\r', b'\n'):
            return True
        return False
    except ImportError:
        confirm = input("Başlamak için ENTER tuşuna basın...: ")
        return confirm == ""

if __name__ == "__main__":
    try:
        ip = ask_ip()
        port = ask_port()
        seconds = ask_seconds()
        print("\nGiriş Başarılı:")
        print(f"  IP: {ip}")
        print(f"  Port: {port}")
        print(f"  Süre: {seconds}s")

        
        ok = wait_for_server(SERVER_PROCESS_NAME, check_interval=1, max_wait=None)
        if not ok:
            print("Server çalışmadığı için sonlandırılıyor.")
            sys.exit(1)

        
        if not prompt_start_confirmation():
            print("İşlem iptal edildi.")
            sys.exit(0)

        
        for i in range(seconds):
            print(f"Çalışıyor... {i+1}/{seconds}", end="\r")
            time.sleep(1)
        print("\nİşlem tamamlandı.")

    except KeyboardInterrupt as e:
        print("\nİptal edildi.")
        sys.exit(0)
    except ValueError as e:
        print("Hata:", e)
        sys.exit(1)
