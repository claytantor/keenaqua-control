import RPi.GPIO as GPIO
import sys
import os
import yaml
import argparse
import schedule

from time import sleep  # Import the sleep function from the time module

GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering

relays = ["GREEN_LED", "BLUE_LED", "RED_LED"]

state = {
    "GREEN_LED": {
        "relay": 1,
        "GPIO": 26,
        "state": GPIO.LOW
    },
    "BLUE_LED": {
        "relay": 2,
        "GPIO": 20,
        "state": GPIO.LOW
    },
    "RED_LED": {
        "relay": 3,
        "GPIO": 21,
        "state": GPIO.LOW
    }
}

def setup_relays(relays):
    for relay in relays:
        print("setup_relay", relay, state[relay]["GPIO"] )
        GPIO.setup(state[relay]["GPIO"], GPIO.OUT, initial=GPIO.LOW)

def toggle_state(name, state):
    state_element = state[name]
    if state_element["state"] == GPIO.LOW:
        state[name]["state"] = GPIO.HIGH
    else:
        state[name]["state"] = GPIO.LOW


def set_pin(name, state):
    print(name, state)
    pin = state[name]["GPIO"]
    state_value = state[name]["state"]
    GPIO.output(pin, state_value)  # set state


def toggle_pin(name, state):
    toggle_state(name, state)
    set_pin(name, state)

def keenaqua_job(device, schedule_item):

    lookup = {
        "on": GPIO.HIGH,
        "off": GPIO.LOW
    }

    #set_pin(device["relay_name"], lookup[schedule_item["command"]])
    # state[device["relay_name"]]["state"] = lookup[schedule_item["command"]]
    # set_pin(device["relay_name"], state[device["relay_name"]]["state"])

    print("job ==== ", 
        device["relay_name"], 
        state[device["relay_name"]]["GPIO"],
        schedule_item["command"])

    GPIO.output(state[device["relay_name"]]["GPIO"], lookup[schedule_item["command"]])
    

def loadConfig(configFile):
    cfg = None
    with open(configFile, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
    return cfg


def main(argv):
    print("starting keenaqua control app.")

    # Read in command-line parameters
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config", action="store",
                        required=True, dest="config", help="the YAML configuration file")

    args = parser.parse_args()
    config = loadConfig(args.config)['keenaqua-scheduler']
    print(config)

    setup_relays(relays)

    for device in config['devices']: 
        print(device['name'], device['schedule']) 
        for schedule_item in device['schedule']:
            if(schedule_item['rate'] == 'day'):
                schedule.every().day.at(schedule_item['value']).do(keenaqua_job, device=device, schedule_item=schedule_item )
            if(schedule_item['rate'] == 'hours'):
                schedule.every(schedule_item['value']).hours.do(keenaqua_job, device=device, schedule_item=schedule_item )
            if(schedule_item['rate'] == 'minutes'):
                schedule.every(schedule_item['value']).minutes.do(keenaqua_job, device=device, schedule_item=schedule_item )    

    while True:  # Run forever
        schedule.run_pending()
        # for relay in relays:
        #     toggle_pin(relay, state)
        #     sleep(1)  # Sleep for 1 second


if __name__ == "__main__":
    main(sys.argv[1:])
