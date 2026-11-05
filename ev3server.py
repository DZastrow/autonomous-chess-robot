#!/usr/bin/env python3

import os
import socket
import time
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, SpeedPercent

HOST = ''
PORT = 5000

# motors
motor_x = LargeMotor(OUTPUT_D)
motor_y = LargeMotor(OUTPUT_C)
motor_z = LargeMotor(OUTPUT_A)
claw = MediumMotor(OUTPUT_B)
# reset encoders at start
motor_x.reset()
motor_y.reset()
motor_z.reset()
claw.reset()
# calibration constants
Z_UP = 0
Z_DOWN = -2000
CLAW_OPEN = 0
CLAW_CLOSED = 175

CAPTURE_POSITION = (2500, 0)
# hard-coded board positions. could probably be done dynamically but that was very finicky when tested
BOARD_POSITIONS = { 
    "a1": (1970, -1225), "b1": (1970, -1085), "c1": (1970, -945), "d1": (1970, -805), "e1": (1970, -665), "f1": (1970, -525), "g1": (1970, -385), "h1": (1970, -245),
    "a2": (1715, -1225), "b2": (1715, -1085), "c2": (1715, -945), "d2": (1715, -805), "e2": (1715, -665), "f2": (1715, -525), "g2": (1715, -385), "h2": (1715, -245),
    "a3": (1470, -1225), "b3": (1470, -1085), "c3": (1470, -945), "d3": (1470, -805), "e3": (1470, -665), "f3": (1470, -525), "g3": (1470, -385), "h3": (1470, -245),
    "a4": (1230, -1225), "b4": (1230, -1085), "c4": (1230, -945), "d4": (1230, -805), "e4": (1230, -665), "f4": (1230, -525), "g4": (1230, -385), "h4": (1230, -245),
    "a5": (990, -1225), "b5": (990, -1085), "c5": (990, -945), "d5": (990, -805), "e5": (990, -665), "f5": (990, -525), "g5": (990, -385), "h5": (990, -245),
    "a6": (750, -1225), "b6": (750, -1085), "c6": (750, -945), "d6": (750, -805), "e6": (750, -665), "f6": (750, -525), "g6": (750, -385), "h6": (750, -245),
    "a7": (520, -1225), "b7": (520, -1085), "c7": (520, -945), "d7": (520, -805), "e7": (520, -665), "f7": (520, -525), "g7": (520, -385), "h7": (520, -245),
    "a8": (270, -1225), "b8": (270, -1085), "c8": (270, -945), "d8": (270, -805), "e8": (270, -665), "f8": (270, -525), "g8": (270, -385), "h8": (270, -245)
}

def go_home():
    print("Going home")
    motor_y.on_to_position(SpeedPercent(30), 0)
    motor_x.on_to_position(SpeedPercent(30), -100)
    motor_x.reset()

def move_to(x, y):
    print("Moving X to ", x)
    motor_x.on_to_position(SpeedPercent(30), x)
    print("Moving Y to ", y)
    motor_y.on_to_position(SpeedPercent(30), y)

def move_z_up():
    print("Moving Z up")
    motor_z.on_to_position(SpeedPercent(30), Z_UP)

def move_z_down():
    print("Moving Z down")
    motor_z.on_to_position(SpeedPercent(30), Z_DOWN)

def grab():
    move_z_down()
    print("Closing claw")
    claw.on_to_position(SpeedPercent(30), CLAW_CLOSED)
    move_z_up()

def release():
    move_z_down()
    print("Opening claw")
    claw.on_to_position(SpeedPercent(30), CLAW_OPEN)
    move_z_up()

def execute_move(move_str):
    from_square, to_square = move_str[:2], move_str[2:]
    print("Executing move: ", from_square, " -> ", to_square)
    x1, y1 = BOARD_POSITIONS[from_square]
    x2, y2 = BOARD_POSITIONS[to_square]
    # move to source
    move_to(x1, y1)
    grab()
    time.sleep(1)
    # move to destination
    move_to(x2, y2)
    release()
    go_home()

def capture(move_str):
    at_square = move_str[2:]
    print("Capturing piece: ", at_square)
    x1, y1 = BOARD_POSITIONS[at_square]
    x2, y2 = CAPTURE_POSITION
    move_to(x1, y1)
    grab()
    time.sleep(1)
    move_to(x2, y2)
    claw.on_to_position(SpeedPercent(30), CLAW_OPEN)
    go_home()
    execute_move(move_str)

os.system('setfont Lat15-TerminusBold14')
print('Starting server...')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)
print("Waiting for connection...")
conn, addr = s.accept()
print("Connected:", addr)

while True:
    data = conn.recv(1024).decode().strip()
    if not data:
        break
    print("Received:", data)
    parts = data.split()
    cmd = parts[0]
    if cmd == "MOVE":
        execute_move(parts[1])
    elif cmd == "CAPTURE":
        capture(parts[1])
    time.sleep(2)

conn.close()

