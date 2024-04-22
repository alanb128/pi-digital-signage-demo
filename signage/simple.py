import requests
import time
import json
import os

interval = 8
try:
    interval = int(os.getenv('INTERVAL', '8'))
except Exception as e:
    print("Invalid/no value for INTERVAL. Using default 5.")
    interval = 5

temperature = -100
uv = -100

pages = ["page0001.html", "page0002.html", "page0003.html"]
uv_ads = ["ad0001_uv.html"]

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
                    temperature = round(reading, 0)
                if measurement == "UVI":
                    print("Found UVI reading via {}.".format(item))
                    uv = round(reading * 10, 1)
                    # add some extra value for demo purposes
                    if uv > 0.0:
                        uv = uv + 1
    return

page_index = 0
uv_ad_index = 0
last_page = "none"

while True:

    if page_index + 1 > len(pages):
        page_index = 0
    page = pages[page_index]
    page_index = page_index + 1
    get_readings()

    if uv > 2:
        if last_page != "ad0001_uv.html":
            page = "ad0001_uv.html"

    page_request = "http://webserver/public/" + page
    last_page = page
    # load page via API
    print("Requesting page {}".format(page_request))
    payload = {'url': page_request}
    r = requests.post('http://browser:5011/url', data=payload)
    print("Request status: {}".format(r))
    print(r.content)

    time.sleep(interval)
