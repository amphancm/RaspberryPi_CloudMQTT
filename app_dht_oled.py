import paho.mqtt.client as mqtt , os, urlparse
import time
from time import sleep
import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
import Adafruit_DHT

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)


# Define event callbacks  
def on_connect(mosq, obj, rc):
    print ("on_connect:: Connected with result code "+ str ( rc ) )
    print("rc: " + str(rc))

def on_message(mosq, obj, msg):
    print ("on_message:: this means  I got a message from brokerfor this topic")
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    if ( msg.payload == "on" ): 	  	
		#disp.clear()
		#disp.display()
		draw.rectangle((0,0,width,height), outline=0, fill=0)				
		draw.text((x, top),    ' CloudMQTT',  font=font, fill=255)
		draw.text((x+20, top+16), ' ON', font=font42, fill=255)
		disp.image(image)
		disp.display()	
		print "Lights on" 
		GPIO.output(18,GPIO.HIGH)
    else :
		if ( msg.payload == "off" ):
			print "Lights off"
			GPIO.output(18,GPIO.LOW)
			draw.rectangle((0,0,width,height), outline=0, fill=0)
			#disp.clear()
			#disp.display()		
			draw.text((x, top),    ' CloudMQTT',  font=font, fill=255)
			draw.text((x, top+16), ' OFF', font=font42, fill=255)
			disp.image(image)
			disp.display()
    	#print "Lights off"
    	#GPIO.output(17,GPIO.LOW)
		

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("This means broker has acknowledged my subscribe request")
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)


# Raspberry Pi pin configuration:
RST = 24
# Note the following are only used with SPI:
DC = 23
SPI_PORT = 0
SPI_DEVICE = 0

# Note you can change the I2C address by passing an i2c_address parameter like:
# disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)


# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = 2
shape_width = 20
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = padding


# Load default font.
font = ImageFont.load_default()
font10 = ImageFont.truetype('Minecraftia.ttf', 10)
font18 = ImageFont.truetype('Minecraftia.ttf', 18)
font20 = ImageFont.truetype('Minecraftia.ttf', 20)
font42 = ImageFont.truetype('Minecraftia.ttf', 42)

# Write two lines of text.
draw.text((x, top),    ' CloudMQTT',  font=font, fill=255)
draw.text((x, top+20), 'CONTROL', font=font20, fill=255)

# Display image.
disp.image(image)
disp.display()

# Sensor should be set to Adafruit_DHT.DHT11,
# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
sensor = Adafruit_DHT.DHT11

# Example using a Beaglebone Black with DHT sensor
# connected to pin P8_11.
pin = 4



client = mqtt.Client()
# Assign event callbacks
client.on_message = on_message
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe

# Uncomment to enable debug messages
client.on_log = on_log


# user name has to be called before connect - my notes.
client.username_pw_set("dvzsscye", "7Q9_jhZajID5")
client.connect('m13.cloudmqtt.com', 11591, 60)

# Continue the network loop, exit when an error occurs
#rc = 0
#while rc == 0:
#    rc = client.loop()
#print("rc: " + str(rc))

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
#client.loop_forever()

client.loop_start()
client.subscribe ("dht11" ,0 )


run = True
while run:
	humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
	if humidity is not None and temperature is not None:
		sleep(5)
		str_temp = ' {0:0.2f} *C '.format(temperature)	
		str_hum  = ' {0:0.2f} %'.format(humidity)
		print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))	
		draw.rectangle((0,0,width,height), outline=0, fill=0)
		#disp.clear()
		#disp.display()		
		draw.text((3, top),    'Temperature/Humidity',  font=font, fill=255)
		draw.text((x, top+16), str_temp, font=font18, fill=255)
		draw.text((x, top+36), str_hum, font=font18, fill=255)
		disp.image(image)
		disp.display()
		client.publish ( "dht11", str_temp +","+ str_hum)
		
	else:
		print('Failed to get reading. Try again!')	
		sleep(10)
