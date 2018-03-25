import os
import time
import sys
import RPi.GPIO as GPIO

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

GPIO.setmode(GPIO.BCM)
pin=26
GPIO.setup(pin, GPIO.IN)
channel = 'pi-home'
pnconfig = PNConfiguration()
 
pnconfig.subscribe_key = 'sub-c-72ad3b94-2f79-11e8-9e56-1adf9750968b'
pnconfig.publish_key = 'pub-c-04f2bb5c-42fb-4522-81ec-38440739de37'
 
pubnub = PubNub(pnconfig)
 
 
def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];
 
while True: 
class MySubscribeCallback(SubscribeCallback):
   
    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            
                light = GPIO.input(pin)
                if light==0:
                  print 'Light intensity is high'
                else:
                  print 'Light intensity is low'
                pubnub.publish().channel(channel).message([
                                                ['x', time.time()],
                                                ['light_intensity', light]
                                                ]).async(my_publish_callback)
 
pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels(channel).execute()

