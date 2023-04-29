import datetime
import signal
import time
import requests
import itertools
import yaml
import RPi.GPIO as GPIO
import datetime
from datetime import date

BELL = 17

last = None

# Compute the response to a signal that has been received from the source. Except for their access to the parameters based to the constructor, __call__ and any functions it uses should be pure.
class SignalResponseComputer:
    last = None

    def __init__(self, config):
        self.waitingTime = config["notification"]["waiting_time"]

    def __call__(self, signal):
     try: 
         difference = signal - self.last
         if difference >= datetime.timedelta(
                                seconds = self.waitingTime):
            self.last = signal
            return signal
         else: 
            return None
     except TypeError as e:
         self.last = signal
         return signal

class Control:
    messageTemplate = None
    def __init__(self, eventListener, signalResponseComputer, messageSender, config):
        self.signalResponseComputer = signalResponseComputer 
        self.messageSender = messageSender
        self.eventListener = eventListener
        self.messageTemplate = config["notification"]["message_template"]
        self.eventListener.setEventHandler(self.handleEvent)
        self.eventListener.listen()

    def computeMessage(self, eventValue):
        return datetime.datetime.now()

    def handleEvent(self, eventValue):
        print(eventValue)
        (eventContent, time) = eventValue
        message = self.computeMessage(eventContent)
        response = self.signalResponseComputer(message)
        if response:
            self.messageSender.send(response)
    
class EventListener:
    handler = None
    eventSource = None

    def __init__(self, eventSource):
        self.eventSource = eventSource

    def setEventHandler(self, handler):
        self.handler = handler

    def listen(self):
        event = self.eventSource(self.handler)


class HttpMessageSender:
    def __init__(self, config, formatter):
        self.config = config
        self.formatter = formatter

    def send(self, message):
        requestContent = [ 
                            ( 'title', 
                              self.config["notification"]["title"]
                             )
                         ,  ( 'message', 
                              self.formatter(message)
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
     (param, value) = paramAndValue
     return param + "=" + str(value)

class EventSource:
    def __call__(self, handler):
        userInput = input("Type message: ")
        handler(input)
        self(handler)

class MessageFormatter:
        def __init__(self, template):
            self.template = template

        def __call__(self, input):
            return self.template.replace(
                    "%time%", date.ctime(input)
                    )



    
with open("./config.yaml", 'r') as file:
           configDictionary = yaml.safe_load(file)


class GpioInterruptManager:
    lastEventTime = None
    def __init__(self, button):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.button = button

    def wrapCallback(self, callback):
        def modifyEvent(event):
            timeNow = datetime.datetime.now()
            if not GPIO.input(self.button):
                if self.lastEventTime:
                    timeAnnotatedEvent = (event, timeNow - self.lastEventTime)
                else: 
                    timeAnnotatedEvent = (event, None)
                result = callback(timeAnnotatedEvent)
            else: self.lastEventTime = timeNow
        return modifyEvent

    def __call__(self, callback):
        GPIO.add_event_detect(
            self.button, 
            GPIO.BOTH, 
            callback=self.wrapCallback(callback), 
            bouncetime=300)


class Messenger:
    def __init__(self, formatter):
        self.formatter = formatter
    def send(self, message):
        print(self.formatter(message))

def cleanup(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

control = Control(
                    EventListener(GpioInterruptManager(BELL)), 
                    SignalResponseComputer(configDictionary), 
                    HttpMessageSender(configDictionary, MessageFormatter(configDictionary["notification"]["message_template"])),
                    configDictionary 
                )

signal.signal(signal.SIGINT, cleanup)
signal.pause()




