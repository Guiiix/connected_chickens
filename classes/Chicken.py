import time
import threading
import random
import grequests
import RPi.GPIO as GPIO

class Chicken:
	def __init__(self, CONF, action_queue):
		print("Initializing object")
		self.CONF = CONF
		self.action = {"id": 0, "time": time.time()}
		self.last_id = 0
		self.action_queue = action_queue
		self.run_script = True
		self.running_actions = []
		self.door_state = "UNKNOWN"

		self.action_method = {
			"OPEN": self.action_open,
			"CLOSE": self.action_close,
			"STOP": self.action_stop
		}

		self.gpio_init()


	"""--------------
	    GPIO methods
	   --------------"""

	def gpio_init(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.CONF["GPIO_PIN"]["GPIO_OUT_ENGINE_1"], GPIO.OUT)
		GPIO.setup(self.CONF["GPIO_PIN"]["GPIO_OUT_ENGINE_2"], GPIO.OUT)
		GPIO.setup(self.CONF["GPIO_PIN"]["GPIO_IN_SWITCH_1"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.setup(self.CONF["GPIO_PIN"]["GPIO_IN_SWITCH_2"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
		GPIO.setup(self.CONF["GPIO_PIN"]["GPIO_IN_THERMO"], GPIO.IN)

	def gpio_engine_clockwise(self):
		print("Engine clockwise")
		GPIO.output(self.CONF["GPIO_PIN"]["GPIO_OUT_ENGINE_1"], 1)
		GPIO.output(self.CONF["GPIO_PIN"]["GPIO_OUT_ENGINE_2"], 0)

	def gpio_engine_anti_clockwise(self):
		print("Engine anti clockwise")
		GPIO.output(self.CONF["GPIO_PIN"]["GPIO_OUT_ENGINE_1"], 0)
		GPIO.output(self.CONF["GPIO_PIN"]["GPIO_OUT_ENGINE_2"], 1)

	def gpio_engine_stop(self):
		print("Engine stop")
		GPIO.output(self.CONF["GPIO_PIN"]["GPIO_OUT_ENGINE_1"], 0)
		GPIO.output(self.CONF["GPIO_PIN"]["GPIO_OUT_ENGINE_2"], 0)

	def gpio_switch1_hit(self):
		return GPIO.input(self.CONF["GPIO_PIN"]["GPIO_IN_SWITCH_1"])

	def gpio_switch2_hit(self):
		return GPIO.input(self.CONF["GPIO_PIN"]["GPIO_IN_SWITCH_2"])


	"""---------------
	    Tools methods
	   ---------------"""
	def tools_generate_action_id(self):
		print("Generating action id")
		self.last_id += 1
		return self.last_id

	def tools_refresh_door_state(self):
		if self.gpio_switch1_hit():
			self.door_state = "OPENED"
		elif self.gpio_switch2_hit():
			self.door_state = "CLOSED"
		else:
			self.door_state = "PARTIAL"

	def tools_send_door_state(self):
		print("Updating Jeedom")
		req = grequests.get("%s%s%s" % (self.CONF["JEEDOM"]["PROTOCOL"], 
			self.CONF["JEEDOM"]["HOST"],
			self.CONF["JEEDOM"]["API_URL"].replace("{key}", 
				self.CONF["JEEDOM"]["API_KEY"]).replace("{id}", 
				self.CONF["JEEDOM"]["CMD_ID"][self.door_state])))
		grequests.send(req, grequests.Pool(1))

	def tools_stop_running(self):
		print("Stopping script")
		self.run_script = False
		self.gpio_engine_stop()
		self.action_queue.put("STOP")
		print("Waiting for all actions to be completed")
		while len(self.running_actions) > 0:
			print(self.running_actions)
			time.sleep(1)

	"""-----------------
	    Actions methods
	   -----------------"""
	def action_open(self, action_id):
		print("Opening door")
		if self.door_state != "OPENED":
			self.gpio_engine_clockwise()
			time.sleep(self.CONF["MAX_CLOSING_TIME"])
			if self.action["id"] == action_id:
				self.gpio_engine_stop()
		self.running_actions.remove(action_id)

	def action_close(self, action_id):
		print("Closing door")
		print(action_id)
		if self.door_state != "CLOSED":
			self.gpio_engine_anti_clockwise()
			time.sleep(self.CONF["MAX_CLOSING_TIME"])
			if self.action["id"] == action_id:
				self.gpio_engine_stop()
		self.running_actions.remove(action_id)

	def action_stop(self, action_id):
		print("Stopping door")
		self.gpio_engine_stop()
		self.running_actions.remove(action_id)


	"""--------------------
	    Background methods
	   --------------------"""
	def bkg_action_fetcher(self):
		print("Starting action fetcher")
		while self.run_script:
			action = self.action_queue.get()
			print("New action: %s" % (action))
			action_id = self.tools_generate_action_id()
			self.running_actions.append(action_id)
			self.action = {"id": action_id, "time": time.time()}
			t = threading.Thread(target = self.action_method[action], args = (action_id,))
			t.start()

	def bkg_door_state_monitoring(self):
		print("Starting state monitoring")
		while self.run_script:
			door_state_ = self.door_state
			self.tools_refresh_door_state()
			if door_state_ != self.door_state:
				if self.door_state in ["OPENED", "CLOSED"]:
					self.tools_send_door_state()
				if time.time() - self.action["time"] > self.CONF["MIN_ACTION_TIME_BEFORE_STOP"]:
					self.gpio_engine_stop()
			time.sleep(self.CONF["SWITCH_CHECK_TIME_INTERVAL"])





