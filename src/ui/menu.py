import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

class SentinelMenu:
    def __init__(self, on_panic_toggle, on_quit):
        self.menu = Gtk.Menu()
        
        # --- BAŞLIK YOK (Temiz Görünüm) ---
        # "Sentinel Core" yazısını kaldırdık. Doğrudan veriye giriyoruz.
        
        # --- BİLGİ SATIRLARI ---
        # create_styled_item fonksiyonu ile hepsini aynı font yapıyoruz.
        self.item_threat = self.create_styled_item("Status   : ...")
        self.item_ssid   = self.create_styled_item("Network  : ...")
        self.item_ip     = self.create_styled_item("Local IP : ...")
        
        # --- TRAFFIC (Alt Menülü) ---
        self.item_traffic = self.create_styled_item("Traffic  : ...")
        self.traffic_submenu = Gtk.Menu()
        self.item_traffic.set_submenu(self.traffic_submenu)
        
        # --- HAVUZ SİSTEMİ ---
        self.connection_slots = []
        for _ in range(20):
            # Alt menüdeki fontlar da düzgün olsun
            item = Gtk.MenuItem()
            label = Gtk.Label()
            label.set_use_markup(True)
            label.set_xalign(0.0) # Sola yasla
            item.add(label)
            
            # Saklamak için item'a label referansını ekleyelim
            item.child_label = label 
            
            item.set_no_show_all(True)
            item.hide()
            self.traffic_submenu.append(item)
            self.connection_slots.append(item)
            
        # Taşma slotu
        self.overflow_slot = Gtk.MenuItem(label="...")
        self.traffic_submenu.append(self.overflow_slot)
        
        # Menüye Ekle
        self.menu.append(self.item_threat)
        self.menu.append(self.item_ssid)
        self.menu.append(self.item_ip)
        self.menu.append(self.item_traffic)
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # --- AKSİYONLAR (Standart Font) ---
        # Aksiyon butonları normal fontta kalsın, ayrışsın.
        self.item_panic = Gtk.MenuItem(label="Kill Switch")
        self.item_panic.connect("activate", on_panic_toggle)
        self.menu.append(self.item_panic)
        
        self.item_scan = Gtk.MenuItem(label="Refresh Scan")
        self.menu.append(self.item_scan)
        
        self.menu.append(Gtk.SeparatorMenuItem())
        
        item_quit = Gtk.MenuItem(label="Exit")
        item_quit.connect("activate", on_quit)
        self.menu.append(item_quit)
        
        self.menu.show_all()
        self.overflow_slot.hide()

    def create_styled_item(self, initial_text):
        """
        Özel fontlu menü elemanı oluşturur.
        Label widget'ı MenuItem'ın içine gömeriz.
        """
        item = Gtk.MenuItem()
        label = Gtk.Label(label=initial_text)
        label.set_use_markup(True) # HTML/Pango etiketlerini aç
        label.set_xalign(0.0)      # Metni sola yasla
        
        # Label'ı item'ın içine koy
        item.add(label)
        
        # Daha sonra güncellemek için label'a kolay erişim yolu ekle
        item.child_label = label
        return item

    def set_text(self, item, label_text, value_text, color=None):
        """
        Metni formatlar:
        label_text : Sabit kısım (örn: "Status")
        value_text : Değişken kısım (örn: "Secure") -> Kalın olur
        """
        # Monospace fontu hizalama sağlar. 
        # Label kısmını 9 karakter genişliğinde sabitliyoruz (Mükemmel hizalama için)
        if color:
            val_markup = f"<span foreground='{color}' weight='bold'>{value_text}</span>"
        else:
            val_markup = f"<b>{value_text}</b>"
            
        markup = f"<tt>{label_text.ljust(9)}:</tt> {val_markup}"
        item.child_label.set_markup(markup)

    def update_view(self, data):
        # Duruma göre renk seçimi
        status_color = "#2ecc71" # Yeşil
        if "High" in data['threat_msg'] or "No" in data['threat_msg']:
            status_color = "#f1c40f" # Sarı
        if "Hardware" in data['threat_msg'] or "Severed" in data['threat_msg']:
            status_color = "#e74c3c" # Kırmızı

        # --- GÜNCELLEME (Hizalı ve Renkli) ---
        self.set_text(self.item_threat, "Status", data['threat_msg'], status_color)
        self.set_text(self.item_ssid,   "Network", data['ssid'])
        self.set_text(self.item_ip,     "Local IP", data['ip'])
        self.set_text(self.item_traffic,"Traffic", f"{data['conns']} Active")
        
        # --- ALT MENÜ GÜNCELLEME ---
        new_details = data.get('conn_details', [])
        
        for i, item in enumerate(self.connection_slots):
            if i < len(new_details):
                # Alt menüde de Monospace kullanalım
                markup = f"<tt><small>{new_details[i]}</small></tt>"
                item.child_label.set_markup(markup)
                item.show()
            else:
                item.hide()
        
        # Panik Butonu
        if data['is_panic']:
            self.item_panic.set_label("Restore Connection")
        else:
            self.item_panic.set_label("Kill Switch")

    def get_gtk_menu(self):
        return self.menu