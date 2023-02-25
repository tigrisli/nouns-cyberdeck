from buttonshim import ButtonShim
from fetch_nouns_vert import *
from active_proposals import *
from pending_proposals import *

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

# Start main loop
while True:
    button_shim.wait_for_press()
