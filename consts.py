# -*-coding:Latin-1 -*

# Define GPIO BCM settings here
CONF = {
	"GPIO_PIN": {
		# Engine control
		"GPIO_OUT_ENGINE_1": 27,
		"GPIO_OUT_ENGINE_2": 22,
		# Door position
		"GPIO_IN_SWITCH_1": 23,
		"GPIO_IN_SWITCH_2": 24,
		# Temperature
		"GPIO_IN_THERMO": 25
	},
	"MAX_CLOSING_TIME": 40,
	"SWITCH_CHECK_TIME_INTERVAL": 0.2,
	"JEEDOM": {
		"PROTOCOL": "http://",
		"HOST": "192.168.1.6",
		"API_URL": "/core/api/jeeApi.php?apikey={key}&type=cmd&id={id}",
		"API_KEY": "u8dNVQfeCWJcaspsC6Ln1pRLhXWTtewELBN9OqNVkgNVBbcy",
		"CMD_ID": {"OPENED": "2550", "CLOSED": "2554"}
	},
	"MIN_ACTION_TIME_BEFORE_STOP": 2,
	"SOCKET_PATH": "/var/www/chicken.sock"
}
