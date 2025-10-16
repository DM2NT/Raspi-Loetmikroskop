#!/bin/bash
# Installationsskript für Raspberry Pi Lötmikroskop
# (c) 2025 DM2NT

echo "=========================================="
echo "Raspberry Pi Lötmikroskop - Installation"
echo "=========================================="
echo ""

# Prüfe ob als Pi-User ausgeführt
if [ "$USER" != "pi" ]; then
    echo "⚠️  Warnung: Dieses Skript sollte als Benutzer 'pi' ausgeführt werden."
    read -p "Trotzdem fortfahren? (j/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Jj]$ ]]; then
        exit 1
    fi
fi

# System aktualisieren
echo "📦 Aktualisiere System..."
sudo apt update
sudo apt upgrade -y

# Abhängigkeiten installieren
echo "📦 Installiere Abhängigkeiten..."
sudo apt install -y python3-opencv python3-picamera2 python3-pil python3-pil.imagetk python3-tk python3-numpy

# Prüfe Kamera
echo ""
echo "📷 Prüfe Kamera..."
if vcgencmd get_camera | grep -q "detected=1"; then
    echo "✓ Kamera erkannt!"
else
    echo "⚠️  Kamera nicht erkannt. Bitte Kabel prüfen."
fi

# Erstelle Foto-Verzeichnis
echo ""
echo "📁 Erstelle Foto-Verzeichnis..."
mkdir -p ~/Fotos
echo "✓ Verzeichnis ~/Fotos erstellt"

# Sudo ohne Passwort für Shutdown
echo ""
read -p "Sudo ohne Passwort für Shutdown einrichten? (j/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]; then
    echo "pi ALL=(ALL) NOPASSWD: /sbin/shutdown" | sudo tee -a /etc/sudoers.d/loetmikroskop-shutdown
    sudo chmod 0440 /etc/sudoers.d/loetmikroskop-shutdown
    echo "✓ Shutdown-Berechtigung eingerichtet"
fi

# Desktop-Icon erstellen
echo ""
read -p "Desktop-Icon erstellen? (j/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]; then
    cp loetmikroskop.desktop ~/Desktop/
    chmod +x ~/Desktop/loetmikroskop.desktop
    echo "✓ Desktop-Icon erstellt"
fi

# Autostart einrichten
echo ""
read -p "Autostart beim Booten einrichten? (j/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Jj]$ ]]; then
    mkdir -p ~/.config/autostart
    cp loetmikroskop.desktop ~/.config/autostart/
    echo "✓ Autostart eingerichtet"
fi

echo ""
echo "=========================================="
echo "✓ Installation abgeschlossen!"
echo "=========================================="
echo ""
echo "Starte das Programm mit:"
echo "  python3 loetmikroskop.py"
echo ""
echo "Oder verwende das Desktop-Icon."
echo ""
echo "Bei Problemen siehe README.md"
echo ""