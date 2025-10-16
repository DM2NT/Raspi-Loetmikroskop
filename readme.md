# Raspberry Pi Lötmikroskop

Ein vollständiges digitales Lötmikroskop basierend auf Raspberry Pi 4, HQ Kamera und 7" Touchscreen.

![Version](https://img.shields.io/badge/version-0.1-green)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.9+-blue)

## Features

✅ **Digitaler Zoom** bis 8x mit Pan-Funktion  
✅ **4 Auflösungsmodi** (720p bis 12MP)  
✅ **Bildanpassungen** in Echtzeit (Helligkeit, Kontrast, Farbe, Belichtung, ISO)  
✅ **Foto-Funktion** mit Zeitstempel  
✅ **180° Bildrotation** per Knopfdruck  
✅ **GPIO-Lichtsteuerung** für externe LEDs (Kalt-/Warmweiß)  
✅ **Touchscreen-Bedienung** - vollständig optimiert  
✅ **Auto-Menü-Timeout** nach 15 Sekunden  
✅ **Shutdown-Funktion** direkt aus dem Programm  

## Hardware

### Benötigte Komponenten

- **Raspberry Pi 4** (4GB RAM empfohlen, 2GB funktioniert auch)
- **Raspberry Pi HQ Kamera** oder kompatible Arducam
- **7" Touchscreen** (800x480 oder höher)
- **Objektiv** (28mm Festbrennweite empfohlen, oder C-Mount Adapter)
- **microSD-Karte** (16GB+)
- **Netzteil** (5V/3A)
- **Gehäuse** (selbst gebaut oder 3D-gedruckt)

### Optional

- **LED-Ringleuchte** (5V, bis 1A)
- **MOSFETs** (IRLZ34N oder ähnlich) für LED-Steuerung
- **Objektiv-Adapter** (falls nötig)

## Software Installation

### 1. Raspberry Pi OS vorbereiten

```bash
# Raspberry Pi OS (64-bit) installieren
# Empfohlen: "Raspberry Pi OS with Desktop" (Bookworm)
```

### 2. System aktualisieren

```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Abhängigkeiten installieren

```bash
sudo apt install -y python3-opencv python3-picamera2 python3-pil python3-pil.imagetk python3-tk python3-numpy
```

### 4. Programm herunterladen

```bash
cd ~
git clone https://github.com/DEIN_USERNAME/rpi-loetmikroskop.git
cd rpi-loetmikroskop
chmod +x loetmikroskop.py
```

### 5. Autostart einrichten (optional)

```bash
mkdir -p ~/.config/autostart
cp loetmikroskop.desktop ~/.config/autostart/
```

### 6. Desktop-Icon erstellen (optional)

```bash
cp loetmikroskop.desktop ~/Desktop/
chmod +x ~/Desktop/loetmikroskop.desktop
```

### 7. Sudo ohne Passwort für Shutdown

```bash
sudo visudo
```

Am Ende der Datei hinzufügen:
```
pi ALL=(ALL) NOPASSWD: /sbin/shutdown
```

Speichern mit `Ctrl+X`, `Y`, `Enter`.

## Verwendung

### Programm starten

```bash
python3 loetmikroskop.py
```

Oder per Desktop-Icon / Autostart.

### Bedienung

**Hauptbuttons (links):**
- ⚙ - Einstellungen öffnen
- 📷 - Foto aufnehmen
- ▭ - Auflösung wählen
- ☀ - Beleuchtung steuern
- ↻ - Bild um 180° drehen

**Buttons (rechts oben):**
- ✕ - Programm beenden
- ⏻ - Raspberry Pi herunterfahren

**Zoom & Pan:**
- Zoom-Regler in Einstellungen verschieben
- Bei aktivem Zoom: Bild durch Ziehen verschieben

**Einstellungen:**
- Alle Regler per Touch bedienbar
- AUTO/MANUELL-Modus für Belichtung
- Menü schließt automatisch nach 15 Sekunden
- Klick außerhalb des Menüs schließt es

**Fotos:**
- Werden in `~/Fotos/` gespeichert
- Format: `foto_YYYYMMDD_HHMMSS.jpg`
- Bestätigung erscheint neben Kamera-Button

## GPIO-Pinbelegung

Für externe LED-Steuerung:

| GPIO | Pin | Funktion |
|------|-----|----------|
| GPIO 17 | 11 | Kaltweiß LED |
| GPIO 27 | 13 | Warmweiß LED |
| GND | 6,9,14,20,25,30,34,39 | Masse |
| 5V | 2,4 | LED Stromversorgung |

**⚠️ WICHTIG:** LEDs NICHT direkt an GPIO anschließen! Verwende MOSFETs oder Transistoren zum Schalten.

### LED-Schaltung mit MOSFET

```
Raspberry Pi 5V (Pin 2) → LED Ring (+)
LED Ring (-) → MOSFET Drain
MOSFET Source → GND
GPIO 17/27 → MOSFET Gate
```

**Empfohlene MOSFETs:**
- IRLZ34N (Logic-Level)
- IRL540N
- Beliebiger N-Channel MOSFET mit "IRL" Bezeichnung

## Technische Details

### Unterstützte Auflösungen

| Modus | Auflösung | FPS (ca.) | Empfohlen für |
|-------|-----------|-----------|---------------|
| HD Ready | 1280x720 | ~60 | Sehr flüssig |
| Full HD | 1920x1080 | ~40 | Gute Balance |
| 3MP | 2028x1520 | ~30 | **Standard** |
| 12MP | 4056x3040 | ~10 | Maximale Qualität |

### Performance

- **Raspberry Pi 4 (4GB):** Empfohlen, volle Performance
- **Raspberry Pi 4 (2GB):** Funktioniert, etwas langsamer
- **Raspberry Pi 4 (1GB):** Möglich, aber nicht empfohlen
- **Raspberry Pi 3B:** Zu langsam, nicht empfohlen

## Anpassungen

### GPIO-Pins ändern

In `loetmikroskop.py` Zeilen 22-23:

```python
s.gpio_kaltweiss = 17  # Ändern auf gewünschten GPIO
s.gpio_warmweiss = 27  # Ändern auf gewünschten GPIO
```

### Standard-Auflösung ändern

Zeile 36:

```python
main={"size":(2028,1520)}  # Ändern auf gewünschte Auflösung
```

### Timeout anpassen

Zeile 215:

```python
s.menu_timeout_id = s.root.after(15000, s.close_all_menus)  # 15000 = 15 Sekunden
```

## Troubleshooting

### Kamera wird nicht erkannt

```bash
# Kamera prüfen
vcgencmd get_camera
# Sollte ausgeben: supported=1 detected=1

# Kabel-Anschluss prüfen
# - Richtiger Port (CSI, nicht DSI)
# - Kontakte zur Platine
# - Blaue Seite zu USB-Ports
```

### Touchscreen funktioniert nicht

```bash
# Touchscreen kalibrieren
xinput_calibrator
```

### Programm startet nicht

```bash
# Fehlerlog anzeigen
python3 loetmikroskop.py 2>&1 | tee fehler.txt
cat fehler.txt
```

### GPIO-Steuerung funktioniert nicht

- Prüfe Verkabelung (MOSFET richtig angeschlossen?)
- Teste GPIO direkt:
```bash
# GPIO 17 einschalten
echo 17 > /sys/class/gpio/export
echo out > /sys/class/gpio/gpio17/direction
echo 1 > /sys/class/gpio/gpio17/value
```

## Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei.

## Autor

(c) 2025 DM2NT

## Beitragen

Contributions sind willkommen! 

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## Danksagung

- Raspberry Pi Foundation für die Hardware
- Picamera2 Library Entwickler
- OpenCV Community
- Claude für die Unterstützung beim Code

## Screenshots

### Hauptansicht Lötmikroskop
![Hauptansicht](images/hauptansicht.jpg)

### Einstellungsmöglichkeiten
![Zoom beim Löten](images/einstellungen.jpg)

### Auflösungen
![Hardware](images/auflösungen.jpg)



## Changelog

### Version 0.1 (2025-10-16)
- Initial Release
- Basis-Funktionalität implementiert
- Touch-Steuerung
- GPIO-Lichtsteuerung
- Foto-Funktion

## Support

Bei Fragen oder Problemen:
- GitHub Issues: [Issues](https://github.com/DEIN_USERNAME/rpi-loetmikroskop/issues)

---

**Hinweis:** Dieses Projekt ist für Hobby- und Bildungszwecke gedacht. Für professionelle Anwendungen sollte ein kommerzielles Mikroskop verwendet werden.
