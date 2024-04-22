import requests
import time
import json
import os
import RPi.GPIO as GPIO


DEBOUNCE = 500
START_UP = False
INFO_MODE = False

START_GPIO = 13
START_LED_GPIO = 19
INFO_GPIO = 6
INFO_LED_GPIO = 5


def button_press(channel):
    global START_UP
    global INFO_MODE
    
    info_data = ""
    page = ""
    sbc_info = device_info()

    print("Press: {}".format(channel))
    if channel == INFO_GPIO:
        GPIO.output(INFO_LED_GPIO, GPIO.HIGH)
        GPIO.output(START_LED_GPIO, GPIO.LOW)
        INFO_MODE = True
        START_UP = False
        info_data = "model=" + GPIO.RPI_INFO["TYPE"] + "&ram=" + GPIO.RPI_INFO["RAM"]
        print("RPi info displayed... model:{}; RAM:{}".format(GPIO.RPI_INFO["TYPE"], GPIO.RPI_INFO["RAM"]))
        page = "http://webserver/public/info.html?" + info_data + browser_info + sbc_info
        display_page(page)
    elif channel == START_GPIO:
        GPIO.output(INFO_LED_GPIO, GPIO.LOW)
        GPIO.output(START_LED_GPIO, GPIO.HIGH)
        START_UP = True
        INFO_MODE = False
    else:
        print("Unrecognized button press {}.".format(channel))
        
        
    return
        

def get_readings():
    global temperature
    global uv
    try:
        r = requests.get('http://big-sensor:7575/')
    except:
        print("Error accessing sensor service, skipping sensors")
        r = {}
    if not r:  # empty dict is false in Python
        temperature = -100
        uv = -100
    else:
        sensors = r.json()
        print("Checking sensors...")
        for item in sensors:
            for measurement, reading in sensors[item].items():
                if measurement == "temperature":
                    print("Found temperature reading via {}.".format(item))
                    temperature = round(((1.8 * reading) + 32), 0)
                if measurement == "UVI":
                    print("Found UVI reading via {}.".format(item))
                    uv = round(reading * 10, 1)
                    # add some extra value for demo purposes
                    if uv > 0.0:
                        uv = uv + 1
    return


def display_page(page):
    # load page via API
    print("Requesting page {}".format(page))
    payload = {'url': page}
    r = requests.post('http://browser:5011/url', data=payload)
    print("Page request status: {}".format(r))
    print(r.content)


def device_info():

    device_info = ""
    
    try:
        r = requests.get(os.getenv('BALENA_SUPERVISOR_ADDRESS') + "/v1/device?apikey=" + os.getenv('BALENA_SUPERVISOR_API_KEY'))
    except:
        print("Unable to access device info via Supervisor API.")
    else:
        j = r.json()
        device_info = device_info + "&ip=" + j["ip_address"]
        device_info = device_info + "&osv=" +  j["os_version"]
        device_info = device_info + "&com=" + j["commit"][:7]
        
    return device_info
    

#  %%%%%% START HERE

# Set up GPIO

GPIO.setmode(GPIO.BCM)

GPIO.setup(26, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(13, GPIO.RISING, callback=button_press, bouncetime=DEBOUNCE)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(6, GPIO.RISING, callback=button_press, bouncetime=DEBOUNCE)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(12, GPIO.RISING, callback=button_press, bouncetime=DEBOUNCE)

GPIO.output(INFO_LED_GPIO, GPIO.LOW)
GPIO.output(START_LED_GPIO, GPIO.LOW)

if GPIO.input(12) == 0:
    print("Auto start shunt on GPIO 12 detected. Auto start disabled.")
else:
    print("Auto starting signage app.")
    START_UP = True


# Get browser info
browser_info = ""
try:
    r = requests.get("http://browser:5011/gpu")
except Exception as e:
    print("Error retrieving browser info.")
else:
    if r.text == "1":
        browser_info = browser_info + "&gpu=enabled"
    else:
        browser_info = browser_info + "&gpu=disabled"
try:
    r = requests.get("http://browser:5011/version")
except Exception as e:
    print("Error retrieving browser info.")
else:
    browser_info = browser_info + "&ver=" + r.text
        
sbc_info = device_info()

# Turn on blue cased LED
GPIO.output(26, GPIO.HIGH)
    
INTERVAL = 8
try:
    INTERVAL = int(os.getenv('INTERVAL', '8'))
except Exception as e:
    print("Invalid/no value for INTERVAL. Using default 8 seconds.")
    INTERVAL = 8

temperature = 65
uv = 0

pages = ["page0001.html", "page0002.html", "page0003.html"]
uv_ads = ["ad0001_uv.html"]


page_index = 0
uv_ad_index = 0
last_page = "none"

while True:

    if START_UP:

        if page_index + 1 > len(pages):
            page_index = 0
        page = pages[page_index]
        page_index = page_index + 1
        get_readings()

        if uv > 2:
            if last_page != "ad0001_uv.html":
                page = "ad0001_uv.html"
    
        page_request = "http://webserver/public/{0}?t={1}&uv={2}".format(page, temperature, uv)
        last_page = page
        display_page(page_request)

        
        
    time.sleep(INTERVAL)    
