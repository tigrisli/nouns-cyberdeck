import RPi.GPIO as GPIO
import time
import subprocess
import threading

class Control:
    def __init__(self, button_pin_map):
        self.buttons = []
        GPIO.setmode(GPIO.BCM)
        for pin, name in button_pin_map.items():
            button = Button(name, pin)
            self.buttons.append(button)
            button.when_pressed = self.on_button_pressed
        self.script_threads = {}
    
    def on_button_pressed(self, button):
        if button.name in self.script_threads and self.script_threads[button.name].is_alive():
            return
        script_thread = threading.Thread(target=self.run_script, args=(button.script_name,))
        self.script_threads[button.name] = script_thread
        script_thread.start()
    
    def run_script(self, script_name):
        subprocess.run(['python', script_name])
            
class Button:
    def __init__(self, name, pin, script_name):
        self.name = name
        self.pin = pin
        self.script_name = script_name
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.when_pressed = None
        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self._on_pressed, bouncetime=500)
    
    def _on_pressed(self, pin):
        if self.when_pressed is not None:
            self.when_pressed(self)

button_pin_map = {
    26: ('E', 'fetch_nouns_vert.py'),
    19: ('D', 'active-proposals.py'),
    13: ('C', 'pending-proposals.py')
}

control = Control({pin: Button(name, pin, script_name) for pin, (name, script_name) in button_pin_map.items()})
