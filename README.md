

# uhostmon
This is a simple python utility build up on top of paho-mqtt and psutil to monitor my HomeAssistant host machine.
The machine is Dell Wyse 5060 with AMD K10 CPU, but it should be easy to modify this script to read from other devices as well.

The script uses MQTT protocol and will publish everything under hwinfo/ topic, as follows

```
hwinfo/k10_temperature_celsius
hwinfo/cpu_utilization_percent
hwinfo/ram_used_percent
```

# Configuration
All you need is to install python and then two requirements:
- paho-mqtt
- psutil

Then, you should create configuration file named config.ini in the working directory where you run the script:
```ini
[credentials]
user=<your mqtt username>
pass=<your mqtt password>
host=<your mqtt hostname>
```
Then, you should create a bash script, which you'll put somewhere to automatically start this python script on boot.

# Screenshots
![image](https://github.com/cziter15/uhostmon/assets/5003708/d7064310-85e2-4788-968f-4930bf5ecfad)
![image](https://github.com/cziter15/uhostmon/assets/5003708/a11ea6b3-8fef-4883-8bea-9d8801351935)
