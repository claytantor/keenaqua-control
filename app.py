import RPi.GPIO as GPIO
import sys
import os
import yaml
import argparse
import schedule
import time
import pytz

from time import sleep  # Import the sleep function from the time module
from datetime import datetime, timedelta
from pytz import timezone


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

lookup = {
    "on": GPIO.HIGH,
    "off": GPIO.LOW
}


def get_current_command(values, current): 
   idex = 0
   sorted_times = sorted(values, key = lambda i: i['value']) 
   print(sorted_times)
   for val in sorted_times:
      if(current<int(val['value'].replace(':',''))):
         current_value = sorted_times[idex-1]['command']
         return current_value

      idex+=1

def current_time(tz):
   fmt = '%H:%M'

   loc_dt = datetime.now(tz)
   print("current time: ",loc_dt.strftime(fmt))

   current = int(loc_dt.strftime(fmt).replace(':',''))
   return current

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

def keenaqua_job(device, schedule_item, tz):

    current = current_time(tz)

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

def convert_localtime_to_gmt(timeval, local_tz):
   all_date = "{0} {1}:00".format(datetime.now().strftime("%Y-%m-%d"), timeval)
   naive = datetime.strptime(all_date, "%Y-%m-%d %H:%M:%S")
   local_dt = local_tz.localize(naive, is_dst=None)
   utc_dt = local_dt.astimezone(pytz.utc)
   return utc_dt

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
    ka_tz = timezone(config['timezone'])  

    for device in config['devices']:  
        print(device['name'], device['schedule']) 

        if(device['type'] == "daily"):
            current = current_time(ka_tz)
            current_command_val = get_current_command(device['schedule'], current)
            print("setting current value to: ", current_command_val)
                
            # set the command value
            GPIO.output(state[device["relay_name"]]["GPIO"], lookup[current_command_val]) 

        for schedule_item in device['schedule']:
            if(schedule_item['rate'] == 'day'):
                schedule_gmt = convert_localtime_to_gmt(schedule_item['value'], ka_tz).strftime("%H:%M")
                print("scheduling GMT: {0} to {1}".format(schedule_gmt,schedule_item['command']))
                schedule.every().day.at(schedule_gmt).do(keenaqua_job, device=device, schedule_item=schedule_item, tz=ka_tz )
            elif(schedule_item['rate'] == 'hours'):
                schedule.every(schedule_item['value']).hours.do(keenaqua_job, device=device, schedule_item=schedule_item, tz=ka_tz )
            elif(schedule_item['rate'] == 'minutes'):
                schedule.every(schedule_item['value']).minutes.do(keenaqua_job, device=device, schedule_item=schedule_item, tz=ka_tz )    
            else:
                pass

    while True:  # Run forever
        schedule.run_pending()


if __name__ == "__main__":
    main(sys.argv[1:])
