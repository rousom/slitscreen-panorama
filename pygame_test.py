import pygame
import time

def main():
    pygame.init()
    pygame.joystick.init()

    # Prüfen, ob ein Joystick verfügbar ist
    if pygame.joystick.get_count() == 0:
        print("❌ Kein Controller erkannt. Bitte anschließen und erneut starten.")
        return

    # Ersten Joystick auswählen
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"✅ Verbunden mit Controller: {joystick.get_name()}")
    print("🎮 Starte Debug-Modus (STRG+C zum Beenden) ...\n")

    try:
        while True:
            pygame.event.pump()  # Eingaben aktualisieren

            # --- D-Pad (Hat-Switch) ---
            hat_count = joystick.get_numhats()
            for i in range(hat_count):
                hat = joystick.get_hat(i)
                print(f"[Hat {i}] D-Pad: {hat}")

            # --- Buttons ---
            button_count = joystick.get_numbuttons()
            for i in range(button_count):
                if joystick.get_button(i):
                    print(f"[Button {i}] gedrückt")

            # --- Analog-Sticks / Trigger (Achsen) ---
            axis_count = joystick.get_numaxes()
            for i in range(axis_count):
                axis = joystick.get_axis(i)
                # Nur anzeigen, wenn sich deutlich bewegt
                if abs(axis) > 0.1:
                    print(f"[Achse {i}] Wert: {axis:.2f}")

            print("-" * 40)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n🚪 Debug-Modus beendet.")
        pygame.quit()

if __name__ == "__main__":
    main()
