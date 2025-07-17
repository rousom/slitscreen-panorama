import pygame
import json

pygame.init()

# Joystick and Mapping Setup
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"🎮 Controller verbunden: {joystick.get_name()}")
with open("controller_mappings.json") as f:
    controller_mappings = json.load(f)
m = controller_mappings.get(joystick.get_name(), controller_mappings["default"])

a_status = False


try:
    while True:
        a_released = False
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            elif event.type == pygame.JOYBUTTONDOWN:
                if joystick.get_button(m["A"]):
                    a_status = True
            elif event.type == pygame.JOYBUTTONUP:
                if a_status:
                    a_released = True
        if a_released:
            print("a releases")
except KeyboardInterrupt:
    print("EXITING NOW")
    pygame.quit()