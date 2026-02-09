import subprocess
import re

class SystemMonitor:
    def check_mic_cam(self):
        """Mikrofon veya Kamerayı kullanan uygulamanın ADINI bulur."""
        status_msg = []
        is_active = False
        apps = set() # Aynı uygulama 5 kere görünmesin diye set kullanıyoruz

        # --- KAMERA KONTROLÜ ---
        try:
            # /dev/video* cihazlarını kullananları listele
            # Başlıkları atla (tail -n +2)
            cmd = "lsof /dev/video0 2>/dev/null | tail -n +2"
            output = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
            
            if output:
                is_active = True
                lines = output.splitlines()
                for line in lines:
                    parts = line.split()
                    if len(parts) > 0:
                        app_name = parts[0] # İlk sütun uygulama adıdır (örn: firefox)
                        # Tarayıcılar bazen "Web Content" gibi görünür, onları düzeltelim
                        if "Web" in app_name or "Iso" in app_name:
                            app_name = "Browser"
                        apps.add(app_name.capitalize()) # Baş harfi büyüt (Firefox)

                # Bulunan uygulamaları listeye ekle
                if apps:
                    app_list = ", ".join(apps)
                    status_msg.append(f"Cam: {app_list}")
                else:
                    status_msg.append("Cam: Unknown")
                    
        except: 
            pass

        # --- MİKROFON KONTROLÜ (Geliştirilebilir) ---
        # Şimdilik basit tutuyoruz, Pactl entegrasyonu karmaşık olabilir.
        # Eğer mikrofon için de benzer bir şey istersen 'pactl' komutunu ekleyebiliriz.
        
        if not status_msg:
            return False, ""
            
        return is_active, ", ".join(status_msg)

    def get_detailed_connections(self):
        """Aktif bağlantıları analiz eder."""
        connection_list = []
        count = 0
        try:
            cmd = "ss -tunp state established"
            output = subprocess.check_output(cmd, shell=True).decode("utf-8")
            lines = output.splitlines()[1:]
            count = len(lines)
            for line in lines:
                parts = line.split()
                if len(parts) < 5: continue
                remote_addr = parts[4]
                process_info = parts[-1]
                proc_match = re.search(r'"([^"]+)"', process_info)
                proc_name = proc_match.group(1) if proc_match else "System"
                
                # İsimleri temizle (python3.10 -> Python)
                if "python" in proc_name: proc_name = "Sentinel"
                
                connection_list.append(f"{proc_name[:10]} -> {remote_addr}")

            return count, connection_list[:15]
        except:
            return 0, []

    def check_traffic_load(self):
        c, _ = self.get_detailed_connections()
        return c