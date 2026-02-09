import os
import signal
import gi
import sys

try:
    from nm_handler import NMHandler
    from system_monitor import SystemMonitor
    from ui.menu import SentinelMenu
    from utils import actions
except ImportError as e:
    print(f"Error: {e}")
    sys.exit(1)

gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import Gtk, GLib, AppIndicator3

APP_ID = "Sentinel_Pro_Clean"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")

class SentinelApp:
    def __init__(self):
        self.indicator = AppIndicator3.Indicator.new(
            APP_ID,
            "sentinel-loading",
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.panic_mode = False
        self.current_color = "green"
        self.frame_index = 0
        
        self.frames = {
            "green": ["status_green_1.png", "status_green_2.png", "status_green_3.png"],
            "yellow": ["status_yellow_1.png", "status_yellow_2.png", "status_yellow_3.png"],
            "red": ["status_red_1.png", "status_red_2.png", "status_red_3.png"],
        }

        self.nm = NMHandler()
        self.mon = SystemMonitor()
        
        self.ui = SentinelMenu(
            on_panic_toggle=self.toggle_panic, 
            on_quit=Gtk.main_quit
        )
        self.indicator.set_menu(self.ui.get_gtk_menu())

        GLib.timeout_add(250, self.animate_loop)
        GLib.timeout_add(2000, self.logic_loop)
        self.logic_loop()

    def toggle_panic(self, widget):
        self.panic_mode = not self.panic_mode
        actions.set_internet_access(not self.panic_mode)
        self.logic_loop()

    def animate_loop(self):
        try:
            frame_list = self.frames[self.current_color]
            icon_file = frame_list[self.frame_index]
            icon_path = os.path.join(ASSETS_DIR, icon_file)
            if os.path.exists(icon_path):
                self.indicator.set_icon_full(icon_path, "Sentinel")
            self.frame_index = (self.frame_index + 1) % len(frame_list)
        except: pass
        return True

    def logic_loop(self):
        try:
            # --- Panic Mode ---
            if self.panic_mode:
                self.current_color = "red"
                self.ui.update_view({
                    'threat_msg': "Link Severed",
                    'ssid': "Offline",
                    'ip': "---",
                    'conns': 0,
                    'conn_details': [],
                    'is_panic': True
                })
                return True

            # --- Veri ---
            ssid, net_color = self.nm.get_active_connection_info()
            # hw_msg artık "Cam: Firefox" gibi bir string döndürecek
            hw_active, hw_msg = self.mon.check_mic_cam()
            conns_count, conns_list = self.mon.get_detailed_connections()
            local_ip = actions.get_local_ip()

            # --- Karar ---
            new_color = "green"
            msg = "Secure"

            if hw_active:
                new_color = "red"
                # BURAYI DÜZELTTİK: Artık sabit yazı değil, gelen mesajı basıyoruz
                msg = hw_msg 
            elif conns_count > 100:
                new_color = "yellow"
                msg = "High Traffic"
            elif net_color == "yellow":
                new_color = "yellow"
                msg = "No Connection"

            self.current_color = new_color

            self.ui.update_view({
                'threat_msg': msg,
                'ssid': ssid,
                'ip': local_ip,
                'conns': conns_count,
                'conn_details': conns_list,
                'is_panic': False
            })

        except Exception as e:
            print(f"Logic Error: {e}")
            
        return True

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    print("Sentinel Pro UI Started.")
    SentinelApp()
    Gtk.main()