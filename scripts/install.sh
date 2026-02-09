#!/bin/bash
echo ">>> Network Sentinel Kurulumu Başlıyor..."

# Fedora için gerekli paketler
if [ -f /etc/fedora-release ]; then
    sudo dnf install -y python3-gobject libappindicator-gtk3 python3-psutil python3-pillow python3-dbus
else
    # Ubuntu/Debian fallback
    sudo apt update
    sudo apt install -y python3-gi gir1.2-appindicator3-0.1 python3-psutil python3-pil python3-dbus
fi

# İkonları oluştur
echo ">>> İkonlar oluşturuluyor..."
python3 src/create_icons.py

echo ">>> Kurulum Tamam! Çalıştırmak için:"
echo "python3 src/main.py"
