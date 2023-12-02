import time
import psutil
import configparser
import paho.mqtt.client as mqtt

###################### GLOBAL SETTINGS ######################
HWMON_MQTT_PREFIX = "hwinfo/"
HWMON_MQTT_PORT = 1883
HWMON_METRIC_UPDATE_INTERVAL_S = 1 		# metric update interval
HWMON_METRIC_SEND_INTERVAL_S = 30 		# metric intervals to pass to send the metric
HWMON_KEEPALIVE_INTERVAL_S = 60
HWMON_ROUNDING_PRECISION = 1
#############################################################

class HwMonitor:
	def __init__(self, mqtt_prefix, host, user, password, updateInterval, sendInterval):
		"""
		Initialize the object with the given parameters.

		:param mqtt_prefix: The prefix for the MQTT topics.
		:param host: The MQTT broker host.
		:param user: The MQTT broker username.
		:param password: The MQTT broker password.
		:param updateInterval: The interval to update the metric values.
		:param sendInterval: The interval to send the metric values.

		:return: None
		"""
		self._prefix = mqtt_prefix
		self._client = mqtt.Client()
		self._host = host
		self._user = user
		self._password = password
		self._updateInterval = updateInterval
		self._sendInterval = sendInterval
		self._updateCounter = 0
		self._metricValues = {}
	
	def _getChipsetTemp(self):
		"""
		Returns the current temperature of the chipset.

		@return: The current temperature of the chipset.
		@rtype: float
		"""
		temperatures = psutil.sensors_temperatures()
		if 'k10temp' in temperatures:
			return temperatures['k10temp'][0].current
		return 0

	def _collect_metric(self, key, value):
		"""
		Collects a metric by adding the value to the existing metric value.

		:param key: The key of the metric.
		:param value: The value to be added to the metric.
		:return: None
		"""
		if key not in self._metricValues:
			self._metricValues[key] = 0
		self._metricValues[key] += value

	def _maybeUpdateMetrics(self):
		"""
		Check if it's time to update metrics and update them if necessary.
		"""
		tnow = time.time()
		
		# Check if it's time to update metrics
		if (tnow - self._lastMetricUpdate > self._updateInterval): 
			
			# Collect and update chipset temperature metric
			self._collect_metric("k10_temperature_celsius", self._getChipsetTemp())
			
			# Collect and update CPU utilization metric
			self._collect_metric("cpu_utilization_percent", psutil.cpu_percent())
			
			# Collect and update RAM usage metric
			self._collect_metric("ram_used_percent", psutil.virtual_memory().percent)
			
			# Increment the update counter
			self._updateCounter += 1
			
			# Update the last metric update timestamp
			self._lastMetricUpdate = tnow
				
	def _maybeSendMetrics(self):
		"""
		Send metrics if the send interval has elapsed.
		"""
		tnow = time.time()
		if (tnow - self._lastMetricSend > self._sendInterval): 
			self._lastMetricSend = tnow
			for key in self._metricValues:
				val = self._metricValues[key] / self._updateCounter
				self._metricValues[key] = 0
				self._client.publish(self._prefix + key, round(val, HWMON_ROUNDING_PRECISION))
			self._updateCounter = 0
				
	def _loop(self):
		"""
		This function handles the MQTT loop for the HwMonitor class.
		If the loop returns an error, it sleeps for 1 second and reconnects.
		Otherwise, it calls the functions to update and send metrics.
		"""
		if self._client.loop() != mqtt.MQTT_ERR_SUCCESS:
			try:
				time.sleep(1.0)
				self.client.reconnect()
			except:
				pass
		else:
			self._maybeUpdateMetrics()
			self._maybeSendMetrics()

	def run(self):
		"""
		Runs the MQTT client and connects to the broker.
		"""
		if self._user is not None:
			self._client.username_pw_set(self._user, self._password)
		
		connected = False
		while not connected:
			try:
				self._client.connect(self._host, HWMON_MQTT_PORT, HWMON_KEEPALIVE_INTERVAL_S)
				connected = True
			except:
				time.sleep(5)
				pass

		self._lastMetricSend = time.time()
		self._lastMetricUpdate = time.time()
		
		while True:
			self._loop()
			time.sleep(0.05)

if __name__ == "__main__":
	print("[HWMON starting]")
	
	cfg = configparser.ConfigParser()
	cfg.read('config.ini')
	
	print("> Parsing config...")
	
	# Get credentials from the config file
	username = cfg.get('credentials', 'user')
	password = cfg.get('credentials', 'pass')
	hostname = cfg.get('credentials', 'host')
	
	print("> MQTT hostname is " + hostname)
	print("> MQTT user is " + username)
	
	# Create and start the hardware monitor
	monitor = HwMonitor(HWMON_MQTT_PREFIX, hostname, username, password, HWMON_METRIC_UPDATE_INTERVAL_S, HWMON_METRIC_SEND_INTERVAL_S)
	
	print("[Monitor starting]")
	monitor.run()
