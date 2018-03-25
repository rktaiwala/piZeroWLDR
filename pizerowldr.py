import os
import time
import datetime
import sys
import RPi.GPIO as GPIO
import urllib
import json 
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

GPIO.setmode(GPIO.BCM)
pin=26
pin2=20
GPIO.setup(pin, GPIO.IN)
GPIO.setup(pin2, GPIO.IN)
channel = 'pi-home'
pnconfig = PNConfiguration()

lastMotionTime = 0
token = '1e53fe060245429fb7b24522d81598c8'

blynkUpdateUrl = 'http://blynk-cloud.com/%s/update/pin?value=value' %(token)
blynkUrl = 'http://blynk-cloud.com/%s/' %(token)
sleep = 30

pnconfig.subscribe_key = 'sub-c-72ad3b94-2f79-11e8-9e56-1adf9750968b'
pnconfig.publish_key = 'pub-c-04f2bb5c-42fb-4522-81ec-38440739de37'
switches =['socket']
fans = ['fan']
lights = ['tube','tubelight','tube light']
workingSwitch ={}
workingFan ={}
workingLight ={}
pubnub = PubNub(pnconfig)

def timeCheck(hr=16, mins=59, sec=55, micros=0):
   now = datetime.datetime.now()
   today5pm = now.replace(hour=hr, minute=mins, second=sec, microsecond=micros)
   return now > today5pm
    
def blynkProjects():
   burl=blynkUrl+'project'
   url = urllib.urlopen(burl)
   data = json.loads(url.read().decode())
   for k,v in enumerate(data['widgets']):
      if v['label'].lower() in switches:
          if v['pinType']=='VIRTUAL':
            workingSwitch[v['label'].lower()] = 'V'+v['pin']
      elif v['label'].lower() in fans:
           if v['pinType']=='VIRTUAL':
            workingFan[v['label'].lower()] = 'V'+v['pin']
      elif v['label'].lower() in lights:
           if v['pinType']=='VIRTUAL':
            workingLight[v['label'].lower()] = 'V'+v['pin']
   print(workingSwitch)
   print(workingFan)
   print(workingLight) 
           
def blynkOnOff(pinNumber,onOff):
    burl=blynkUrl+'update/%s?value=%s' %(pinNumber,onOff)
    url = urllib.urlopen(burl)
    print(burl)
   
def blynkGet(pinNumber):
    burl=blynkUrl+'get/%s' %(pinNumber)
    url = urllib.urlopen(burl)
    print(burl)
   
def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];
def tsMotioncheck():
    motion = GPIO.input(pin2)
    if motion == 1:
       lastMotionTime = time.time()
    else:
       lastMotionTime = 0
    return motion
class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data
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
              if timeCheck():
                  if tsMotioncheck() ==1:
                     #for k in workingLight:
                     for key, value in workingLight.iteritems():
                        #print(key)
                        #print(value)
                        blynkOnOff(value,1)
                  else:
                     last_time = round((int(time.time()) - lastMotionTime) / 60, 2)
                     if last_time>4:
                        for key, value in workingLight.iteritems():
                           blynkOnOff(value,0)
            pubnub.publish().channel(channel).message([
                                            ['current_time', time.time()],
                                            ['light_intensity', light]
                                            ]).async(my_publish_callback)
    def message(self, pubnub, message):
        pass  # Handle new message stored in message.message
 
pubnub.add_listener(MySubscribeCallback())
blynkProjects()
while True:
 pubnub.subscribe().channels(channel).execute()
 time.sleep(sleep)

