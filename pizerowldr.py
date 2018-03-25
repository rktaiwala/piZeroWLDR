import os
import time
import sys
import RPi.GPIO as GPIO
from pubnub import Pubnub
GPIO.setmode(GPIO.BOARD)
pin=25
GPIO.setup(pin, GPIO.IN)

pubnub = Pubnub(publish_key='pub-c-04f2bb5c-42fb-4522-81ec-38440739de37', subscribe_key='sub-c-72ad3b94-2f79-11e8-9e56-1adf9750968b')
channel = 'pi-home'

def callback(message):
    print(message)

#published in this fashion to comply with Eon
while True:
    light = GPIO.input(pin)
    if light==0:
      print 'Light intensity is high'
    else:
      print 'Light intensity is low'
    
    pubnub.publish(channel, {
        'columns': [
            ['x', time.time()],
            ['light_intensity', light]
            ]

        })
    
