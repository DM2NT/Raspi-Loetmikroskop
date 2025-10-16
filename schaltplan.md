# Schaltplan - LED-Steuerung

## Einfache Variante mit MOSFET

```
                    Raspberry Pi 4
                    ┌─────────────┐
                    │             │
    GPIO 17 (Pin 11)├─────┐       │
                    │     │       │
    GPIO 27 (Pin 13)├───┐ │       │
                    │   │ │       │
       GND (Pin 6/9)├─┐ │ │       │
                    │ │ │ │       │
        5V (Pin 2/4)├┐│ │ │       │
                    └┼┼─┼─┼───────┘
                     ││ │ │
                     ││ │ │
    ┌────────────────┘│ │ │
    │  ┌──────────────┘ │ │
    │  │  ┌─────────────┘ │
    │  │  │  ┌────────────┘
    │  │  │  │
    │  │  │  │   LED Ring Kaltweiß (5V, 1A)
    │  │  │  │   ┌─────────────────┐
    │  │  │  │   │      (+)         │
    │  │  │  └───┤ LED Ring         │
    │  │  │      │      (-)         │
    │  │  │      └────┬─────────────┘
    │  │  │           │
    │  │  │         Drain
    │  │  │           │
    │  │  │      ┌────▼────┐
    │  │  │      │ MOSFET  │  IRLZ34N
    │  │  └──────┤Gate     │  oder ähnlich
    │  │         │ Source  │
    │  │         └────┬────┘
    │  │              │
    │  └──────────────┘
    │
    │                 LED Ring Warmweiß (5V, 1A)
    │                 ┌─────────────────┐
    │                 │      (+)         │
    └─────────────────┤ LED Ring         │
                      │      (-)         │
                      └────┬─────────────┘
                           │
                         Drain
                           │
                      ┌────▼────┐
                      │ MOSFET  │  IRLZ34N
        GPIO 27───────┤Gate     │  oder ähnlich
                      │ Source  │
                      └────┬────┘
                           │
             GND───────────┘
```

## Bauteile-Liste

| Bauteil | Anzahl | Beispiel | Kosten |
|---------|--------|----------|--------|
| N-Channel MOSFET | 2x | IRLZ34N, IRL540N | ~1€ |
| LED-Ring 5V | 1-2x | Beliebig (max. 1A) | ~5-15€ |
| Kabel | - | Dupont-Kabel | ~2€ |

**Gesamt: ~10€**

## Anschluss

### Raspberry Pi → MOSFET (Kaltweiß)

```
Pin 11 (GPIO 17) → MOSFET Gate
Pin 6  (GND)     → MOSFET Source
```

### Raspberry Pi → MOSFET (Warmweiß)

```
Pin 13 (GPIO 27) → MOSFET Gate
Pin 9  (GND)     → MOSFET Source
```

### LED-Versorgung

```
Pin 2 (5V)       → LED Ring (+)
LED Ring (-)     → MOSFET Drain
MOSFET Source    → GND
```

## Wichtige Hinweise

⚠️ **NIEMALS LEDs direkt an GPIO anschließen!**
- GPIO liefert max. 16mA
- LED-Ring braucht bis zu 1000mA (1A)
- **= Raspberry Pi wird zerstört!**

✅ **MOSFET als Schalter verwenden:**
- MOSFET schaltet die 1A für die LEDs
- GPIO steuert nur den MOSFET (braucht <1mA)
- Sicher für den Raspberry Pi!

## Pinbelegung Raspberry Pi 4

```
    3.3V  (1) (2)  5V     ← LED-Versorgung
   GPIO2  (3) (4)  5V     ← LED-Versorgung
   GPIO3  (5) (6)  GND    ← MOSFET Source
   GPIO4  (7) (8)  GPIO14
     GND  (9) (10) GPIO15
  GPIO17 (11) (12) GPIO18 ← Kaltweiß
  GPIO27 (13) (14) GND    ← Warmweiß
  GPIO22 (15) (16) GPIO23
    3.3V (17) (18) GPIO24
  GPIO10 (19) (20) GND
   GPIO9 (21) (22) GPIO25
  GPIO11 (23) (24) GPIO8
     GND (25) (26) GPIO7
   GPIO0 (27) (28) GPIO1
   GPIO5 (29) (30) GND
   GPIO6 (31) (32) GPIO12
  GPIO13 (33) (34) GND
  GPIO19 (35) (36) GPIO16
  GPIO26 (37) (38) GPIO20
     GND (39) (40) GPIO21
```

## Alternative: Transistor statt MOSFET

Falls kein MOSFET verfügbar, geht auch ein **BC337-40**:

```
GPIO 17/27 ─┬─ 1kΩ Widerstand ─┬─ Basis (Transistor)
            │                   │
           GND              LED (-) ─ Kollektor
                            LED (+) ─ 5V
                              Emitter ─ GND
```

**Nachteil:** Transistor wird warm bei 1A!  
**Vorteil:** Sehr günstig (~0.10€)

## Test ohne Elektronik

**LED-Ring dauerhaft an (ohne Schaltung):**

```
5V (Pin 2)  → LED (+)
GND (Pin 6) → LED (-)
```

LEDs leuchten permanent, keine Steuerung möglich.

## Hilfreiche Links

- [IRLZ34N Datenblatt](https://www.infineon.com/dgdl/irlz34npbf.pdf)
- [Raspberry Pi Pinout](https://pinout.xyz)
- [MOSFET Tutorial](https://learn.sparkfun.com/tutorials/transistors)

---

Bei Fragen: GitHub Issues oder README.md