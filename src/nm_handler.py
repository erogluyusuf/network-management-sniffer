import dbus

class NMHandler:
    NM_BUS_NAME = "org.freedesktop.NetworkManager"
    
    def __init__(self):
        try:
            self.bus = dbus.SystemBus()
            self.nm_proxy = self.bus.get_object(self.NM_BUS_NAME, "/org/freedesktop/NetworkManager")
            self.nm_props = dbus.Interface(self.nm_proxy, "org.freedesktop.DBus.Properties")
        except Exception as e:
            # Hata olsa bile sessiz kal, program çökmesin
            self.bus = None

    def get_active_connection_info(self):
        if not self.bus: return "Bağlantı Yok", "red"
        
        try:
            active_paths = self.nm_props.Get(self.NM_BUS_NAME, "ActiveConnections")
            if not active_paths: return "Disconnected", "yellow"
            
            conn_obj = self.bus.get_object(self.NM_BUS_NAME, active_paths[0])
            conn_props = dbus.Interface(conn_obj, "org.freedesktop.DBus.Properties")
            
            id_str = conn_props.Get("org.freedesktop.NetworkManager.Connection.Active", "Id")
            return str(id_str), "green"
        except:
            return "Bilinmiyor", "yellow"
