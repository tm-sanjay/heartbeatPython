import paho.mqtt.client as mqtt
import time
import threading
import datetime
from tinydb import TinyDB, Query

#initialize DB file(create is not there)
db = TinyDB('./HB_data.json')

start_time = int(time.time())
previousSec = 0
newStart = True

# MQTT
client = mqtt.Client()
client.username_pw_set("mqtt","mqtt")
client.connect("192.168.5.36", 1883, 60)

# subscribe once connected to Broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("local/pi/#")

# print if data is comming from MQTT 
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

# send Hearbeat to MQTT broker ever 5min and save data every 30min
def printit():
    global previousSec, newStart

    while(True):
        #time formating
        currentSec = int(time.time()) - start_time
        elapsedDays = time.strftime("%j",time.gmtime(currentSec))
        currentSec_string = time.strftime("%T",time.gmtime(currentSec))
        
        # json data to be sent 
        mqttJson = {
                "days": elapsedDays,
                "uptime": currentSec_string
                }

        # check is 30min is passed
        if ((currentSec - previousSec >= 60*1) or newStart):
            previousSec = currentSec

            todayTime = datetime.datetime.now()
            # inset data to DB (json)
            if newStart:
                newStart = False
                print("--New Satrt--")
                db.insert({'Start_time': str(todayTime), 'days':elapsedDays, 'uptime': currentSec_string})
            else:
                print("--30 min over--")
                db.insert({'time': str(todayTime), 'days':elapsedDays, 'uptime': currentSec_string})

        # publish uptime json to the broker
        print("published to local/pi/H", str(mqttJson))
        client.publish("local/pi/H", str(mqttJson))
        time.sleep(60*0.5)

# create a thread to send message every 5min
threading.Timer(0.0, printit).start()

client.on_connect = on_connect
client.on_message = on_message
# These functions implement a threaded interface to the network loop
client.loop_start()