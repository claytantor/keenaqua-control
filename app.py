import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

import sys, os

from time import sleep # Import the sleep function from the time module

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) #Use BCM pin numbering

relays = ["GREEN_LED","BLUE_LED", "RED_LED"]

state = {
	"GREEN_LED":{
		"relay": 1,
		"GPIO": 26,
		"state": GPIO.LOW	
	},
	"BLUE_LED":{
		"relay": 2,
		"GPIO": 20,
		"state": GPIO.LOW	
	},
	"RED_LED":{
		"relay": 3,
		"GPIO": 21,
		"state": GPIO.LOW	
	}
}

  # Set pin 26 to be an output pin and set initial value to low (off)

def setup_relays(relays):
	for relay in relays:
		GPIO.setup(state[relay]["GPIO"], GPIO.OUT, initial=GPIO.LOW)


def toggle_state(name, state):
	state_element = state[name]
	if state_element["state"] == GPIO.LOW:
		state[name]["state"] = GPIO.HIGH
	else:
	    state[name]["state"] = GPIO.LOW
	   
def set_pin(name, state):
	pin = state[name]["GPIO"]
	state_value = state[name]["state"]
	GPIO.output(pin, state_value) # set state	

def toggle_pin(name, state):
	toggle_state(name, state)
	set_pin(name, state)


def main(argv):
    print("starting keenaqua control app.")

    setup_relays(relays)

    while True: # Run forever
        for relay in relays:
            toggle_pin(relay, state)
            sleep(1) # Sleep for 1 second

if __name__ == "__main__":
    main(sys.argv[1:])

