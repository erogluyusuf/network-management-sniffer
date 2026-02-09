import socket
import subprocess

def get_local_ip():
    """Dış dünyaya (Google DNS) bağlanarak gerçek yerel IP'yi bulur."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Bilinmiyor"

def set_internet_access(enable=True):
    """
    enable=True -> İnterneti açar
    enable=False -> İnterneti keser (Panik Modu)
    """
    state = "on" if enable else "off"
    try:
        # Linux NetworkManager komutu
        subprocess.run(["nmcli", "networking", state], check=False)
        return True
    except:
        return False