import pygame
import time
from flask import Flask
from flask_socketio import SocketIO
import threading
import math

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

pygame.init()
pygame.joystick.init()
if pygame.joystick.get_count() == 0:
    raise RuntimeError("❌ Kein Controller gefunden.")
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"✅ Controller erkannt: {joystick.get_name()}")

# Für sanfte Annäherung (Low-Pass Filter)
smooth_vx, smooth_vy = 0.0, 0.0
alpha = 0.15  # Glättungsfaktor (kleiner = langsamer)

def normalize_vector(x, y):
    length = math.sqrt(x*x + y*y)
    if length < 0.01:
        return 0.0, 0.0
    return x/length, y/length

def main_loop():
    global smooth_vx, smooth_vy
    try:
        while True:
            pygame.event.pump()

            # Rohwerte
            raw_vx = joystick.get_axis(0)      # links/rechts
            raw_vy = joystick.get_axis(1)     # oben/unten invertiert

            # Normalisieren auf Länge 1 (oder 0 wenn kein Input)
            norm_vx, norm_vy = normalize_vector(raw_vx, raw_vy)

            # Sanft Annähern (Low-Pass)
            smooth_vx = (1 - alpha) * smooth_vx + alpha * norm_vx
            smooth_vy = (1 - alpha) * smooth_vy + alpha * norm_vy

            # Buttons
            a_pressed = joystick.get_button(0)   # A
            b_pressed = joystick.get_button(1)   # B
            rt_pressed = joystick.get_button(10)  # rechter Trigger

            vz = 0.1 if a_pressed else (-0.1 if b_pressed else 0)

            # Daten senden
            socketio.emit("controller_data", {
                "vx": smooth_vx,
                "vy": smooth_vy,
                "vz": vz,
                "a": a_pressed,
                "b": b_pressed,
                "rt": rt_pressed
            })

            time.sleep(0.05)
    except KeyboardInterrupt:
        print("Beende Programm.")
    finally:
        pygame.quit()

def run_flask():
    socketio.run(app, host='0.0.0.0', port=5500)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    print("🕹 Starte Controller-Loop...")
    main_loop()
