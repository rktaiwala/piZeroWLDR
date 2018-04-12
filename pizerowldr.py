import os
import time
import datetime
import sys
import RPi.GPIO as GPIO
import urllib
import json 
import Adafruit_DHT

sensor = Adafruit_DHT.DHT11

from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

GPIO.setmode(GPIO.BCM)
pin=26
pin2=20
dht_pin = 19
GPIO.setup(pin, GPIO.IN)
GPIO.setup(pin2, GPIO.IN)
channel = 'pi-home'
pub_channel='pub_channel'
sub_channel='sub_channel'
pnconfig = PNConfiguration()

lastMotionTime = 0
token = '1e53fe060245429fb7b24522d81598c8'

blynkUpdateUrl = 'http://blynk-cloud.com/%s/update/pin?value=value' %(token)
blynkUrl = 'http://blynk-cloud.com/%s/' %(token)
sleep = 10
#default temperature and humidity
temperature = 18
humidity = 50

pnconfig.subscribe_key = 'sub-c-72ad3b94-2f79-11e8-9e56-1adf9750968b'
pnconfig.publish_key = 'pub-c-04f2bb5c-42fb-4522-81ec-38440739de37'
switches =['socket']
fans = ['fan']
lights = ['tube','tubelight','tube light']
workingSwitch ={}
workingFan ={}
workingLight ={}
pubnub = PubNub(pnconfig)
debug=True

def showDebug(msg):
   if debug:
      print(msg)
def resetlastMotionTime():
   global lastMotionTime
   lastMotionTime = 0
def timebet5pm6pm():
   now = datetime.datetime.now()
   today5pm = now.replace(hour=16, minute=59, second=55, microsecond=0)
   today6pm = now.replace(hour=17, minute=59, second=55, microsecond=0)
   return now > today5pm and now < today6pm
   
def timeCheck(hr=0, mins=0, sec=0, micros=0):
   showDebug('Time check 1')
   now = datetime.datetime.now()
   tom = datetime.datetime.now() + datetime.timedelta(days=1)
   showDebug('Time check 2')
   tom8am = tom.replace(hour=8, minute=0, second=0, microsecond=0)
   today5pm = now.replace(hour=16, minute=59, second=55, microsecond=0)
   showDebug('Time check 3')
   chk = now > today5pm and now<tom8am
   showDebug('Time check %s' % chk)
   return chk
    
def blynkProjects():
   burl=blynkUrl+'project'
   url = urllib.urlopen(burl)
   data = json.loads(url.read().decode())
   for k,v in enumerate(data['widgets']):
      if v['label'].lower() in switches:
          if v['pinType']=='VIRTUAL':
            workingSwitch[v['label'].lower()] = 'V'+str(v['pin'])
      elif v['label'].lower() in fans:
           if v['pinType']=='VIRTUAL':
            workingFan[v['label'].lower()] = 'V'+str(v['pin'])
      elif v['label'].lower() in lights:
           if v['pinType']=='VIRTUAL':
            workingLight[v['label'].lower()] = 'V'+str(v['pin'])
   showDebug(workingSwitch)
   showDebug(workingFan)
   showDebug(workingLight) 
           
def blynkOnOff(pinNumber,onOff):
    burl=blynkUrl+'update/%s?value=%s' %(pinNumber,onOff)
    url = urllib.urlopen(burl)
    url.read()
    #res = json.loads(url.read().decode())
    #showDebug(res)
   
def blynkGet(pinNumber):
    burl=blynkUrl+'get/%s' %(pinNumber)
    url = urllib.urlopen(burl)
    res = json.loads(url.read().decode())
    showDebug(res[0])
    return res[0]
   
def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];
def tsMotioncheck():
    global lastMotionTime
    motion = GPIO.input(pin2)
    if timebet5pm6pm():
       return True
    if motion == 1:
       lastMotionTime = time.time()
       showDebug('motion Detected at: %s'% lastMotionTime)
    return motion

def tsReadDHT():
   global humidity,temperature
   humidity, temperature = Adafruit_DHT.read_retry(sensor, dht_pin)
   #return (humidity,temperature)
def tspublishDataPubnub():
   light = GPIO.input(pin)
   tsReadDHT()
   
   if light==0:
      showDebug('Light intensity is high')
      if tsMotioncheck() ==0:
         last_time = round((int(time.time()) - lastMotionTime) / 60, 2)
         if last_time>5:
            for key, value in workingLight.iteritems():
               if blynkGet(value)=='1':
                  resetlastMotionTime()
                  blynkOnOff(value,0)

   else:
      showDebug('Light intensity is low')
      if timeCheck():
         if tsMotioncheck() ==1:
            #for k in workingLight:
            for key, value in workingLight.iteritems():
               #print(key)
               #print(value)
               if blynkGet(value)=='0':
                  blynkOnOff(value,1)
         else:
            #showDebug('ILM0--LastMotionTime is %s' % lastMotionTime)
            last_time = round((int(time.time()) - lastMotionTime) / 60, 2)
            showDebug(last_time)
            if last_time>4:
               #showDebug('How %s' % last_time>4)
               for key, value in workingLight.iteritems():
                  if blynkGet(value) == '1':
                     blynkOnOff(value,0)
                     resetlastMotionTime()

   pubnub.publish().channel(pub_channel).message([
                                   ['current_time', time.time()],
                                   ['light_intensity', light],
                                   ['motion',tsMotioncheck()],
                                   ['humidity',humidity],
                                   ['temperature',temperature],
                                   ]).async(my_publish_callback)
   pubnub.publish().channel('eon_msg').message({'eon':[temperature]}).async(my_publish_callback)         
      
class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data
    def status(self, pubnub, status):
      if status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc 
         print 'Connected'
    
    def message(self, pubnub, message):
      #pass  # Handle new message stored in message.message
      print "message=", message.message

pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels(sub_channel).execute()
blynkProjects()
while True:
   try:
      tspublishDataPubnub()
      time.sleep(sleep)
   except: urllib.error as err:
      time.sleep(30)

