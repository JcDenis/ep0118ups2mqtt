# ep0118ups2mqtt
Send EP-0118 UPS values to MQTT

This python3 script reads current, voltage, power, ... from The Raspberry Pi UPS Expension card EP-0118 using ina219 librairies, and send values to an MQTT brocker.

See board at [52Pi Wiki for EP-0118](https://wiki.52pi.com/index.php/UPS_(With_RTC_%26_Coulometer)_For_Raspberry_Pi_SKU:_EP-0118)

# Usage

This script required pyhton3-pip, pip paho-mqtt and pi-ina219. You can install them like this :
```
sudo apt install python3-pip
sudo pip3 install paho-mqtt pi-ina219
```

Put ep0118ups2mqtt.py to your home directory eg: /home/pi

You can test it using arguments, for exemple to see result in your console every 10 secondes with broker IP 192.168.0.10 :

```sudo pyhton3 /home/pi/ep0118ups2mqtt.py -i 10 -b 192.168.0.10 -v```

Script arguments can be :
- -c Client name (this will be end topic name), by default rpi hostname is used
- -b Broker IP
- -p Broker Port, by default "1883"
- -u Broker user
- -w Broker password
- -t Main Topic, by default "ups"
- -i Update interval
- -v Verbose

# Always On

To run this script in background you can set up a systemd service.

Edit file :
```sudo nano /etc/systemd/system/ep0118ups2mqtt.service```

Fill it like that, assuming your script is in dir /home/pi, and don't forget to change xxx,yyy,zzz,... according to your env :
```
[Unit]
Description=ep0118ups2mqtt
After=syslog.target network.target

[Service]
Type=simple
WorkingDirectory=/home/pi/
ExecStart=sudo python3 /home/pi/ep0118ups2mqtt.py -b xxx.xxx.xxx.xxx -u yyy -w zzz

RestartSec=5
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Save changes, then to run service, execute these 3 lines :

```
sudo systemctl daemon-reload
sudo systemctl enable ep0118ups2mqtt.service
sudo systemctl start ep0118ups2mqtt.service`
````

Enjoy.
