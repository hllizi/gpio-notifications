import datetime
import signal
import time
import requests
import itertools
import yaml
import RPi.GPIO as GPIO

BELL = 17

last = None

# Compute the response to a signal that has been received from the source. Except for their access to the parameters based to the constructor, __call__ and any functions it uses should be pure.
class SignalResponseComputer:
    last = None

    def __init__(self, config):
        self.min_differerence = min_differerence

    def __call__(self, signal):
     try: 
         difference = signal - self.last
         if difference >= datetime.timedelta(seconds = self.config["waiting_time"] * 1000):
            self.last = signal
            return signal
         else: 
            return None
     except TypeError as e:
         self.last = signal
         return signal

class Control:
    def __init__(self, eventListener, signalResponseComputer, messageSender):
        self.signalResponseComputer = signalResponseComputer 
        self.messageSender = messageSender
        self.eventListener = eventListener
        self.eventListener.setEventHandler(self.handleEvent)
        self.eventListener.listen()

    def computeMessage(self, eventValue):
        return datetime.datetime.now()

    def handleEvent(self, eventValue):
        message = self.computeMessage(eventValue)
        response = self.signalResponseComputer(message)
        self.messageSender.send(response)

class EventLstener:
    handler = None
    eventSource = None

    def __init__(self, eventSource):
        self.eventSource = eventSource

    def setEventHandler(self, handler):
        self.handler = handler

    def listen(self):
        event = self.eventSource()
        self.handler(event)
        self.listen()

class InterruptReceiver:
    handler = None
    interruptManager = None

    def __init__(interruptManager):
        self.interruptManager = interruptManager

    def setEventHandler(self, handler):
        self.handler = handler

    def listen(self):
        self.interruptManager(handler)



class HttpMessageSender:
    def __init__(self, config):
        self.config = config

    def send(self, message):
        requestContent = [ 
                            ( 'title', 
                              self.config["notification"]["title"]
                             )
                         ,  ( 'message', 
                              self.config["notification"]["message"]
                             )
                         ,  ( 
                              'priority', 
                              8
                            )
                         ] 
        url = self.prepareQuery(requestContent)
        requests.post(url)

    def prepareQuery(self, requestContent):
        url = self.urlBase() 
        token = [("token", self.config["gotify"]["token"])]
        query = token + requestContent
        url += "/message"
        if query: 
            url += "?"
            queryAsStrings = map(makeSetting, query)
            url += '&'.join(queryAsStrings)    
        return url 

    def urlBase(self):
          url =  (self.config["gotify"]["scheme"] 
                 + "://" + self.config["gotify"]["server"] 
                 + ":" + str(self.config["gotify"]["port"]))
          return url

def makeSetting(paramAndValue):
     print(paramAndValue)
     (param, value) = paramAndValue
     return param + "=" + str(value)

class EventSource:
    def __call__(self,):
        input("Type message: ")

    
with open("./config.yaml", 'r') as file:
           configDictionary = yaml.safe_load(file)


class GpioInterruptManager:
    def __init__(self, button):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.button = button

    def __call__(callback):
        GPIO.add_event_detect(self.button, GPIO.RISING, callback=callback, bouncetime=100)

control = Control(
                    EventListener(EventSource()), 
                    SignalResponseComputer(configDictionary), 
                    HttpMessageSender(configDictionary)
                )

def cleanup(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)




