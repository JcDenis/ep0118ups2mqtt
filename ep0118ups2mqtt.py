###
# Send EP-0118 UPS values to MQTT
#
###
# See :
# https://wiki.52pi.com/index.php/UPS_(With_RTC_%26_Coulometer)_For_Raspberry_Pi_SKU:_EP-0118
# https://github.com/JcDenis/ep0118ups2mqtt
#
###
# Required :
# sudo apt install python3-pip
# sudo pip3 install paho-mqtt pi-ina219
#
###
# Copy this file to /home/pi
# nano /home/pi/ep0118ups2mqtt.py
#
###
# Start at boot :
# sudo nano /etc/systemd/system/ep0118ups2mqtt.service
#
# Copy the next bloc without #
#
###
#[Unit]
#Description=ep0118ups2mqtt
#After=syslog.target network.target
#
#[Service]
#Type=simple
#WorkingDirectory=/home/pi/
#ExecStart=sudo python3 /home/pi/ep0118ups2mqtt.py
#
#RestartSec=5
#Restart=on-failure
#
#[Install]
#WantedBy=multi-user.target
#
###
# Then execute :
# sudo systemctl daemon-reload
# sudo systemctl enable ep0118ups2mqtt.service
# sudo systemctl start ep0118ups2mqtt.service
#
###


# Libs
import argparse, sys, math, time, subprocess, socket
import paho.mqtt.client as mqtt
import json
from ina219 import INA219
from ina219 import DeviceRangeError
SHUNT_OHMS = 0.05

# Read script arguments
def getOptions(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description="Parses command.")
    parser.add_argument("-c", "--client", help="Client name aka topic name")
    parser.add_argument("-b", "--host", help="Broker IP")
    parser.add_argument("-p", "--port", type=int, help="Broker port")
    parser.add_argument("-u", "--user", help="Broker user login")
    parser.add_argument("-w", "--password", help="Broker user password")
    parser.add_argument("-t", "--topic", help="Main topic")
    parser.add_argument("-i", "--interval", type=int, help="Refresh interval in seconds")
    parser.add_argument("-v", "--verbose",dest='verbose',action='store_true', help="Verbose mode.")
    options = parser.parse_args(args)
    return options

options = getOptions(sys.argv[1:])

# Print non default arguments
if options.verbose:
    print(options)

# Parse arguments and clean up
opt_client = socket.gethostname()
if options.client:
    opt_client = options.client
opt_host = "192.168.0.1"
if options.host:
    opt_host = options.host
opt_port = 1883
if options.port:
    opt_port = options.port
opt_user = "pi"
if options.user:
    opt_user = options.user
opt_password = "raspberry"
if options.password:
    opt_password = options.password
opt_topic = "ups"
if options.topic:
    opt_topic = options.topic
opt_interval = 60
if options.interval:
    opt_interval = options.interval

# Set up default values
v = {'time': 0, 'ip': "", 'name': "", 'voltage': 0, 'current': 0, 'power': 0, 'shunt': 0, 'overflow': 0}
next_reading = time.time()

# Prepare MQTT client and connexion
client = mqtt.Client(opt_client)
client.username_pw_set(opt_user, opt_password)
client.connect(opt_host, opt_port, 60)
client.loop_start()
ina = INA219(SHUNT_OHMS)
ina.configure()

# Let's go to the loop
try:
  while True:
    v['time'] = math.trunc(time.time())
    v['ip'] = subprocess.check_output("hostname -I | cut -d' ' -f1 | tr -d '\n'", shell=True).decode("utf-8")
    v['name'] = socket.gethostname()

    ina.wake()
    v['voltage'] = round(ina.voltage(),3) #V
    try:
      v['current'] = round(ina.current()/1000,3) #A
      v['power'] = round(ina.power()/1000,3) #W
      v['shunt'] = round(ina.shunt_voltage()/1000,3) #V
      v['overflow'] = ina.current_overflow() #1/0
    except DeviceRangeError as e:
      v['overflow'] = 1
    ina.sleep()

    topic = opt_topic + '/' + opt_client
    client.publish(topic, json.dumps(v), 1)

    if options.verbose:
      print(v)

    next_reading += opt_interval
    sleep_time = next_reading-time.time()
    if sleep_time > 0:
      time.sleep(sleep_time)
except KeyboardInterrupt:
  pass

client.loop_stop()
client.disconnect()