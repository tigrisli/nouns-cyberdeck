#!/usr/bin/python
import os
import sys
import subprocess
import RPi.GPIO as GPIO
import time
import signal
import buttonshim
from fetch_nouns_vert import *
from active_proposals import *
from pending_proposals import *

print("""
Button SHIM: control-main.py

Light up the LED a different color of the rainbow with each button pressed.
""")

# Define button press functions
def button_a_pressed():
    print("Button A pressed")

def button_b_pressed():
    print("Button B pressed")

def button_c_pressed():
    pending_proposals_function()
    print("Button C script finished running")

def button_d_pressed():
    active_proposals_function()
    print("Button D script finished running")

def button_e_pressed():
    fetch_nouns_vert_function()
    print("Button E script finished running")

# Set up Button SHIM
button_shim = ButtonShim()

# Define button handlers
button_shim.set_handler('A', button_a_pressed)
button_shim.set_handler('B', button_b_pressed)
button_shim.set_handler('C', button_c_pressed)
button_shim.set_handler('D', button_d_pressed)
button_shim.set_handler('E', button_e_pressed)

@buttonshim.on_press(buttonshim.BUTTON_A)
def button_a(button, pressed):
    global button_flag
    button_flag = "button_1"
    
@buttonshim.on_press(buttonshim.BUTTON_B)
def button_b(button, pressed):
    global button_flag
    button_flag = "button_2"
    
@buttonshim.on_press(buttonshim.BUTTON_C)
def button_c(button, pressed):
    global button_flag
    button_flag = "button_3"

@buttonshim.on_press(buttonshim.BUTTON_D)
def button_d(button, pressed):
    global button_flag
    button_flag = "button_4"

@buttonshim.on_press(buttonshim.BUTTON_E)
def button_e(button, pressed):    
    global button_flag
    button_flag = "button_5"

# Start main loop
button_flag = "null"
while True:
    time.sleep(.1)
    if button_flag == "button_1":
        buttonshim.set_pixel(0x94, 0x00, 0xd3)
        button_a_pressed()
        button_flag = "null"
    elif button_flag == "button_2":
        buttonshim.set_pixel(0x00, 0x00, 0xff)
        button_b_pressed()
        button_flag = "null"
    elif button_flag == "button_3":
        buttonshim.set_pixel(0x00, 0xff, 0x00)
        button_c_pressed()
        button_flag = "null"
    elif button_flag == "button_4":
        buttonshim.set_pixel(0xff, 0xff, 0x00)
        button_d_pressed()
        button_flag = "null"
    elif button_flag == "button_5":
        buttonshim.set_pixel(0xff, 0x00, 0x00)
        button_e_pressed()
        button_flag = "null"
