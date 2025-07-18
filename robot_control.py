import rtde_control
import rtde_receive
import pygame
import time
import numpy as np
import math
from contextlib import contextmanager
from flask import Flask, request, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import threading
import json

app = Flask(__name__)

# Server setup and connection test
socketio = SocketIO(app, cors_allowed_origins=["http://127.0.0.1:5501"])
CORS(app, resources={r"/*": {"origins": "*"}})
@app.route('/ping')
def hello():
    return "Server is running!"

@socketio.on('connect')
def handle_connect():
    print("🔌 Client connected")
    emit('message_from_server', {'msg': 'Hello from Flask WebSocket!'})

# Joystick and Mapping Setup
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"🎮 Controller verbunden: {joystick.get_name()}")
with open("controller_mappings.json") as f:
    controller_mappings = json.load(f)
m = controller_mappings.get(joystick.get_name(), controller_mappings["default"])


state = "start"
# start confirm_tutorial program_running enter_height freedrive print pause_scan finish_scan
start_mode = "portrait"

height = 172

def update_start_mode():
    print("set start mode:", start_mode)
    socketio.emit('update_start_mode', {'mode': start_mode})

def update_screen(screen): # wait, print, ...
    print("update screen: ", screen)
    socketio.emit('update_screen', {'screen': screen})

def update_height():
    print("height: ", height)
    socketio.emit('update_height', {'height': height})

def update_canvas_width_for(mode):
    print("update canvas width for: ", mode)
    socketio.emit('update_canvas_width_for', {'mode': mode})

def print_canvas():
    print("sending print request")
    socketio.emit('print_canvas', {'print': True})
def pause_canvas(yesno):
    print("sending pause request")
    socketio.emit('pause_canvas', {'pause': yesno})

def confirm_tutorial():
    global state, startmode
    if start_mode == "portrait":
        update_screen("portrait_tutorial")
        state = "confirm_tutorial"
    elif start_mode == "scan":
        update_screen("scan_tutorial")
        state = "confirm_tutorial"
    elif start_mode == "manual":
        update_screen("manual_tutorial")
        start_program()
    print("confirm tutoria > state: ", state)

def start_program():
    global state, start_pose
    if start_mode == "portrait":
        state = "program_running"
        update_canvas_width_for(start_mode)
        #SIMSWITCH
        # panorama_mode_sim()
        panorama_mode()
    if start_mode == "scan":
        update_screen("enter_height")
        state = "enter_height"
    if start_mode == "manual":
        state = "freedrive"
        update_canvas_width_for(start_mode)
        #SIMSWITCH
        # freedrive_mode_sim()
        freedrive_mode()



# button cooldown
COOLDOWN = 0.4  
last_trigger_times = {}
def is_action_allowed(action_name):
    now = time.time()
    last_time = last_trigger_times.get(action_name, 0)

    if now - last_time >= COOLDOWN:
        last_trigger_times[action_name] = now
        return True
    return False
        

# ========== Background Thread ==========
a_status = False
b_status = False
def controller_watcher():
    global state, start_mode, a_status, b_status, height
    print("thread started")
    while True:
        a_released = False
        b_released = False
        pygame.event.pump()  # Update internal state
        # print("STATE IN LOOP", state)
        a_pressed = joystick.get_button(m["A"])
        b_pressed = joystick.get_button(m["B"])

        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if joystick.get_button(m["A"]):
                    a_status = True
                if joystick.get_button(m["B"]):
                    b_status = True
            elif event.type == pygame.JOYBUTTONUP:
                if event.button == m["A"] and a_status:
                    a_released = True
                    a_status = False
                if event.button == m["B"] and b_status:
                    b_released = True
                    b_status = False

        if state == "start":
            # scan - portrait - manual
            if joystick.get_axis(m["joystick_left_h"]) < -.8 :
                if (start_mode == "portrait"):
                    start_mode = "scan"
                    update_start_mode()
                if (start_mode == "manual"):
                    start_mode = "portrait"
                    update_start_mode()
            if  joystick.get_axis(m["joystick_left_h"]) > .8 :
                if (start_mode == "portrait"):
                    start_mode = "manual"
                    update_start_mode()
                if (start_mode == "scan"):
                    start_mode = "portrait"
                    update_start_mode()
            if a_released:
                a_released = False
                confirm_tutorial()

        elif state == "confirm_tutorial":
            if a_released:
                a_released = False
                print("start program")
                start_program()
            if b_released:
                b_released = False
                print("back to menu")
                update_screen("start")
                state = "start"

        elif state == "enter_height":
            if joystick.get_axis(m["joystick_left_v"]) < -.8 and height < 200:
                height = height + 1
                update_height()
            if  joystick.get_axis(m["joystick_left_v"]) > .8 and height > 100:
                height = height - 1
                update_height()
            if a_released:
                a_released = False
                print("start scan 1")
                update_canvas_width_for(start_mode)
                #SIMSWITCH
                # person_scan_mode_front_sim(height/100)
                person_scan_go_up(height/100)
                
        elif state == "print":
            if a_released:
                a_released = False
                print("print confirmed")
                print_sim()
            if b_released:
                b_released = False
                state = "start"
                update_screen("start")

        elif state == "pause_scan":
            if a_released:
                a_released = False
                print("pause scan, pressed a - continue")
                state = "finish_scan"
                #SIMSWITCH
                # person_scan_mode_back_sim()
                person_scan_go_down()

        
        time.sleep(0.1)

# Start background thread when Flask starts
threading.Thread(target=controller_watcher, daemon=True).start()


def print_sim():
    global state
    print_canvas()
    pause_canvas(False)
    if state != "freedrive":
        state = "start"
        update_screen("start")


def panorama_mode_sim():
    global state
    update_screen("wait")
    print("starting panorama")
    time.sleep(2)
    print("panorama done")
    state = "print"
    print("pan end state(print!?) ", state)
    update_screen("print")

def person_scan_mode_front_sim(height_m):
    global state
    update_screen("wait")
    min_height = 0.45
    max_height = 2.00

    if not (min_height <= height_m <= max_height):
        print(f"⚠️ Ungültige Höhe: {height_m:.2f} m. Erlaubt sind nur Werte zwischen {min_height:.2f} m und {max_height:.2f} m.")
        return
    print("starting scan")
    time.sleep(1)

    update_screen("turn_around")
    state = "pause_scan"
    print("state(pause_scan!?) ", state)

    print("Waiting for state to become 'finish_scan'...")

    

def person_scan_mode_back_sim():
    global state
    update_screen("wait")
    print("State is now 'finsish scan', continuing...")
    time.sleep(1)

    print("scan done")
    update_screen("print")
    state = "print"
    print("scan end state(print!?) ", state)

    


def freedrive_mode_sim():
    global state
    print("starting manual")
    # update_screen("manual_tutorial")
    while state == "freedrive":
        pygame.event.pump()
        a_released = False
        b_released = False
        pygame.event.pump()  # Update internal state
        # print("STATE IN LOOP", state)
        a_pressed = joystick.get_button(m["A"])
        b_pressed = joystick.get_button(m["B"])

        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if joystick.get_button(m["A"]):
                    a_status = True
                if joystick.get_button(m["B"]):
                    b_status = True
            elif event.type == pygame.JOYBUTTONUP:
                if event.button == m["A"] and a_status:
                    a_released = True
                    a_status = False
                if event.button == m["B"] and b_status:
                    b_released = True
                    b_status = False

        if b_released:
            b_released = False
            update_screen("start")
            state = "start"
            break
        if a_released:
            a_released = False
            print("print canvas")
            print_sim()

    print("ending manaul session manual")
    


# Verbindungskonfiguration
# UR5
# ROBOT_IP = "192.168.8.167"
# UR10
ROBOT_IP = "192.168.8.24"

@contextmanager
def with_robot_connection():
    """Contextmanager für sichere Verbindung."""
    print("🔌 Stelle Verbindung zum Roboter her...")
    rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
    rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP, frequency=10)
    try:
        yield rtde_c, rtde_r
    finally:
        print("🔌 Trenne Verbindung...")
        rtde_c.speedStop()
        rtde_c.disconnect()


# Globale Parameter
base_step_size = 0.5
loop_dt = 0.05
deg_to_rad = math.pi / 180.0
JOINT_LIMITS = {
    0: (-270 * deg_to_rad, 90 * deg_to_rad),
    2: (40 * deg_to_rad, 140 * deg_to_rad),
}
SUM_JOINT_1_3_LIMITS = (-50 * deg_to_rad, 5 * deg_to_rad)
START_POS = [-90 * deg_to_rad, -100 * deg_to_rad, 120 * deg_to_rad, -20 * deg_to_rad, 90 * deg_to_rad, 90 * deg_to_rad]

def return_to_start(rtde_c):
    print("🔄 Zurück zur Startposition...")
    rtde_c.moveJ(START_POS, speed=0.4, acceleration=0.4)

def get_tcp_position(rtde_r):
    pose = rtde_r.getActualTCPPose()
    return np.array(pose[0:3])

def get_tcp_orientation(rtde_r):
    pose = rtde_r.getActualTCPPose()
    return np.array(pose[3:6])

def enforce_joint_limits(joint_idx, current_value, proposed_speed, limits, safety_margin=0.05):
    """Drosselt die Geschwindigkeit nahe der Limits sanft ab."""
    min_limit, max_limit = limits
    projected = current_value + proposed_speed * loop_dt

    # Wenn innerhalb sicherem Bereich: kein Eingriff
    if min_limit + safety_margin < current_value < max_limit - safety_margin:
        return proposed_speed

    # Drosselung abhängig von Nähe zur Grenze
    if proposed_speed > 0 and current_value >= max_limit - safety_margin:
        distance = max_limit - current_value
        scale = np.clip(distance / safety_margin, 0.0, 1.0)
        return proposed_speed * scale
    elif proposed_speed < 0 and current_value <= min_limit + safety_margin:
        distance = current_value - min_limit
        scale = np.clip(distance / safety_margin, 0.0, 1.0)
        return proposed_speed * scale

    return proposed_speed

def enforce_sum_joint_1_3_limits(current_q, proposed_joint1_speed, sum_limits, safety_margin=0.05):
    current_sum = current_q[1] + current_q[2] + current_q[3]
    projected_sum = current_sum + proposed_joint1_speed * loop_dt

    min_limit, max_limit = sum_limits

    if min_limit + safety_margin < current_sum < max_limit - safety_margin:
        return proposed_joint1_speed

    if proposed_joint1_speed > 0 and current_sum >= max_limit - safety_margin:
        distance = max_limit - current_sum
        scale = np.clip(distance / safety_margin, 0.0, 1.0)
        return proposed_joint1_speed * scale
    elif proposed_joint1_speed < 0 and current_sum <= min_limit + safety_margin:
        distance = current_sum - min_limit
        scale = np.clip(distance / safety_margin, 0.0, 1.0)
        return proposed_joint1_speed * scale

    return proposed_joint1_speed

def freedrive_mode():
    global state, a_status, b_status
    speed_multiplier = 0.4
    with with_robot_connection() as (rtde_c, rtde_r):
        return_to_start(rtde_c)
        print("🎮 Starte Freedrive-Modus. Beenden mit Button B.")
        while True:
            pygame.event.pump()
            a_released = False
            b_released = False
            pygame.event.pump()  # Update internal state
            # print("STATE IN LOOP", state)
            a_pressed = joystick.get_button(m["A"])
            b_pressed = joystick.get_button(m["B"])

            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    if joystick.get_button(m["A"]):
                        a_status = True
                    if joystick.get_button(m["B"]):
                        b_status = True
                elif event.type == pygame.JOYBUTTONUP:
                    if event.button == m["A"] and a_status:
                        a_released = True
                        a_status = False
                    if event.button == m["B"] and b_status:
                        b_released = True
                        b_status = False

            if b_released:
                b_released = False
                update_screen("start")
                state = "start"
                rtde_c.speedStop()
                time.sleep(0.5)
                return_to_start(rtde_c)
                break
            if a_released:
                print("a rel before reset", a_released)
                a_released = False
                print("a rel after reset", a_released)
                print("print canvas")
                print_sim()

            # Geschwindigkeit anpassen
            # if joystick.get_button(m["X"]):
            #     speed_multiplier = min(speed_multiplier + 0.2, 4.0)
            #     print(f"🔺 Geschwindigkeit erhöht: {speed_multiplier:.1f}x")
            #     time.sleep(0.2)
            # if joystick.get_button(m["Y"]):
            #     speed_multiplier = max(speed_multiplier - 0.2, 0.1)
            #     print(f"🔻 Geschwindigkeit verringert: {speed_multiplier:.1f}x")
            #     time.sleep(0.2)

            step_size = base_step_size * speed_multiplier
            tcp_move_step_size = step_size * 0.5

            current_q = rtde_r.getActualQ()
            tcp_pos = get_tcp_position(rtde_r)
            tcp_rotvec = get_tcp_orientation(rtde_r)

            axis_0 = joystick.get_axis(m["joystick_left_h"])
            axis_1 = joystick.get_axis(m["joystick_left_v"])

            joint_speeds = [0.0] * 6

            if abs(axis_0) > 0.2:
                proposed_speed = axis_0 * -step_size
                joint_speeds[0] = enforce_joint_limits(0, current_q[0], proposed_speed, JOINT_LIMITS[0])

            joint1_damping = 0.5
            if abs(axis_1) > 0.2:
                proposed_speed = axis_1 * step_size * joint1_damping
                proposed_speed = enforce_sum_joint_1_3_limits(current_q, proposed_speed, SUM_JOINT_1_3_LIMITS)
                joint_speeds[1] = proposed_speed

            min_joint5 = 65 * deg_to_rad
            max_joint5 = 115 * deg_to_rad
            target_90 = 90 * deg_to_rad
            target_65 = 65 * deg_to_rad
            target_115 = 115 * deg_to_rad

            current_joint5 = current_q[5]
            max_rot_speed = step_size * 2
            diagonal = abs(axis_0) > 0.3 and abs(axis_1) > 0.3

            if diagonal:
                target_angle = target_115 if (axis_0 > 0 and axis_1 > 0) or (axis_0 < 0 and axis_1 < 0) else target_65
            elif abs(axis_0) > 0.2 or abs(axis_1) > 0.2:
                target_angle = target_90
            else:
                target_angle = current_joint5

            target_angle = max(min_joint5, min(max_joint5, target_angle))
            diff = target_angle - current_joint5
            stiffness_factor = 2.0
            deadzone = 0.01
            max_step = max_rot_speed

            if abs(diff) > deadzone:
                speed = np.clip(diff * stiffness_factor, -max_step, max_step)
                projected_joint5 = current_joint5 + speed * loop_dt
                projected_joint5 = max(min_joint5, min(max_joint5, projected_joint5))
                speed = (projected_joint5 - current_joint5) / loop_dt
                proposed_rotation_speed = speed
            else:
                proposed_rotation_speed = 0.0

            joint_speeds[5] = proposed_rotation_speed

            # disabled in and out movement
            # if joystick.get_button(m["shoulder_button_left"]) or joystick.get_button(m["shoulder_button_right"]):
            #     tcp_speed_z = 0.0
            #     if joystick.get_button(m["shoulder_button_left"]): tcp_speed_z += tcp_move_step_size
            #     if joystick.get_button(m["shoulder_button_right"]): tcp_speed_z -= tcp_move_step_size

            #     theta = np.linalg.norm(tcp_rotvec)
            #     if theta < 1e-6:
            #         R = np.eye(3)
            #     else:
            #         r = tcp_rotvec / theta
            #         K = np.array([[0, -r[2], r[1]], [r[2], 0, -r[0]], [-r[1], r[0], 0]])
            #         R = np.eye(3) + math.sin(theta)*K + (1 - math.cos(theta))*(K @ K)

            #     tcp_z_axis = R[:, 2]
            #     new_tcp_pos = tcp_pos + tcp_z_axis * tcp_speed_z * loop_dt
            #     target_pose = list(new_tcp_pos) + list(tcp_rotvec)

            #     ik_q = rtde_c.getInverseKinematics(target_pose)
            #     if ik_q:
            #         joint2_delta = (ik_q[2] - current_q[2]) / loop_dt
            #         joint2_delta = enforce_joint_limits(2, current_q[2], joint2_delta, JOINT_LIMITS[2])
            #         sum_1_3_new = ik_q[1] + ik_q[2] + ik_q[3]
            #         if SUM_JOINT_1_3_LIMITS[0] <= sum_1_3_new <= SUM_JOINT_1_3_LIMITS[1]:
            #             for i in range(6):
            #                 joint_speeds[i] = (ik_q[i] - current_q[i]) / loop_dt
            #             joint_speeds[2] = joint2_delta
                        
            if any(abs(js) > 1e-4 for js in joint_speeds):
                rtde_c.speedJ(joint_speeds, acceleration=2.0, time=loop_dt)
            else:
                rtde_c.speedJ([0.0]*6, acceleration=2.0, time=loop_dt)

            time.sleep(loop_dt)
            print("a rel endloop", a_released)

def person_scan_mode(height_m):
    min_height = 0.45
    max_height = 2.00

    if not (min_height <= height_m <= max_height):
        print(f"⚠️ Ungültige Höhe: {height_m:.2f} m. Erlaubt sind nur Werte zwischen {min_height:.2f} m und {max_height:.2f} m.")
        return

    with with_robot_connection() as (rtde_c, rtde_r):
        print(f"🧍 Starte Personenscan. Zielhöhe: {height_m:.2f} m")
        return_to_start(rtde_c)

        bottom_pose = [-90 * deg_to_rad, 15 * deg_to_rad, 75 * deg_to_rad, -90 * deg_to_rad, 90 * deg_to_rad, 0]
        bottom_pose_angled = [-90 * deg_to_rad, 15 * deg_to_rad, 75 * deg_to_rad, -80 * deg_to_rad, 90 * deg_to_rad, 0]

        rtde_c.moveJ(bottom_pose, speed=0.4, acceleration=0.4)
        tcp_pose = rtde_r.getActualTCPPose()

        delta_z = height_m - 0.45
        target_pose = tcp_pose.copy()
        target_pose[2] += delta_z

        rtde_c.moveJ(bottom_pose_angled, speed=0.4, acceleration=0.4)
        rtde_c.moveL(target_pose, speed=0.2, acceleration=0.2)

        input("📸 Bitte bestätigen, wenn Scan abgeschlossen ist (ENTER drücken)...")

        rtde_c.moveL(tcp_pose, speed=0.2, acceleration=0.2)
        rtde_c.moveJ(bottom_pose_angled, speed=1, acceleration=1)
        return_to_start(rtde_c)
        print("✅ Personenscan abgeschlossen.")



# Globale Variable zur Speicherung der Höhe und Startpose für Rückfahrt
scan_height_m = None
scan_tcp_pose_before_up = None

def person_scan_go_up(height_m):
    pause_canvas(True)
    global scan_height_m, scan_tcp_pose_before_up, state

    min_height = 0.45
    max_height = 2.00

    if not (min_height <= height_m <= max_height):
        print(f"⚠️ Ungültige Höhe: {height_m:.2f} m. Erlaubt sind nur Werte zwischen {min_height:.2f} m und {max_height:.2f} m.")
        return

    scan_height_m = height_m  # Merken für zweiten Teil

    with with_robot_connection() as (rtde_c, rtde_r):
        print(f"🧍 [Teil 1] Starte Scanaufstieg bis Höhe {height_m:.2f} m")
        update_screen("wait90")

        return_to_start(rtde_c)

        # Erste untere Pose
        bottom_pose = [-90 * deg_to_rad, 15 * deg_to_rad, 75 * deg_to_rad, -90 * deg_to_rad, 90 * deg_to_rad, 0]
        bottom_pose_angled = [-90 * deg_to_rad, 15 * deg_to_rad, 75 * deg_to_rad, -80 * deg_to_rad, 90 * deg_to_rad, 0]

        rtde_c.moveJ(bottom_pose, speed=0.4, acceleration=0.4)

        # TCP-Pose merken
        scan_tcp_pose_before_up = rtde_r.getActualTCPPose()

        rtde_c.moveJ(bottom_pose_angled, speed=0.4, acceleration=0.4)

        delta_z = height_m - 0.32
        target_pose = scan_tcp_pose_before_up.copy()
        target_pose[2] += delta_z

        pause_canvas(False)
        # Fahrt nach oben zur Zielhöhe
        rtde_c.moveL(target_pose, speed=0.1, acceleration=0.2)
        pause_canvas(True)

        min_height = 0.45
        max_height = 2.00

        # update_screen("turn_around")
        # state = "pause_scan"
        # print("state(pause_scan!?) ", state)
        return_to_start(rtde_c)
        update_screen("print")
        state = "print"

        print("Waiting for state to become 'finish_scan'...")

        print("📸 Obere Zielposition erreicht. Warten auf Freigabe für Teil 2...")

# def person_scan_go_down():
#     global scan_tcp_pose_before_up, state
#     update_screen("wait")
#     print("State is now 'finsish scan', continuing...")

    
#     if scan_tcp_pose_before_up is None:
#         print("⚠️ Kein vorheriger Scan-Aufstieg gespeichert. Bitte zuerst 'person_scan_go_up()' aufrufen.")
#         return

#     with with_robot_connection() as (rtde_c, _):
#         print("🔽 [Teil 2] Rückfahrt zur unteren Position und danach zur Startposition")

#         # Rückfahrt nach unten
#         rtde_c.moveL(scan_tcp_pose_before_up, speed=0.1, acceleration=0.2)

#         # Untere geneigte Pose
#         bottom_pose_angled = [-90 * deg_to_rad, 15 * deg_to_rad, 75 * deg_to_rad, -80 * deg_to_rad, 90 * deg_to_rad, 0]
#         rtde_c.moveJ(bottom_pose_angled, speed=1.0, acceleration=1.0)

#         # Zurück zur globalen Startposition
#         return_to_start(rtde_c)
#         print("scan done")
#         update_screen("print")
#         state = "print"
#         print("scan end state(print!?) ", state)

#         print("✅ Scan abgeschlossen. Roboter wieder in Startposition.")

def panorama_mode():
    pause_canvas(True)
    global state
    update_screen("wait")
    print("starting panorama")
    with with_robot_connection() as (rtde_c, _):
        print("📸 Starte Panorama-Modus...")

        # 180deg panorama
        # start_pose = [-0 * deg_to_rad, -90 * deg_to_rad, 130 * deg_to_rad, -40 * deg_to_rad, 90 * deg_to_rad, 90 * deg_to_rad]
        # end_pose = [-180 * deg_to_rad, -90 * deg_to_rad, 130 * deg_to_rad, -40 * deg_to_rad, 90 * deg_to_rad, 90 * deg_to_rad]

        start_pose = [-35 * deg_to_rad, -90 * deg_to_rad, 130 * deg_to_rad, -40 * deg_to_rad, 90 * deg_to_rad, 90 * deg_to_rad]
        end_pose = [-125 * deg_to_rad, -90 * deg_to_rad, 130 * deg_to_rad, -40 * deg_to_rad, 90 * deg_to_rad, 90 * deg_to_rad]

        rtde_c.moveJ(start_pose, speed=0.8, acceleration=0.4)
        pause_canvas(False)
        rtde_c.moveJ(end_pose, speed=0.07, acceleration=0.2)
        pause_canvas(True)
        return_to_start(rtde_c)
        print("panorama done")
        state = "print"
        print("pan end state(print!?) ", state)
        update_screen("print")
        print("✅ Panorama-Modus beendet.")


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5051)

#     pygame.quit()


