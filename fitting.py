import datetime
import time
import requests
import itertools
import yaml

last = None
min_differerence = 5000

# Compute the response to a signal that has been received from the source. Except for their access to the parameters based to the constructor, __call__ and any functions it uses should be pure.
class SignalResponseComputer:
    last = None

    def __init__(self, min_differerence):
        self.min_differerence = min_differerence

    def __call__(self, signal):
     try: 
         difference = signal - self.last
         if difference >= datetime.timedelta(seconds = self.min_differerence):
            self.last = signal
            return signal
         else: 
            return None
     except TypeError as e:
         self.last = signal
         return signal

class Control:
    def __init__(self, eventReceiver, signalResponseComputer, messageSender):
        self.signalResponseComputer = signalResponseComputer 
        self.messageSender = messageSender
        self.eventReceiver = eventReceiver
        self.eventReceiver.setEventHandler(self.handleEvent)
        self.eventReceiver.listen()

    def computeMessage(self, eventValue):
        return datetime.datetime.now()

    def handleEvent(self, eventValue):
        message = self.computeMessage(eventValue)
        response = self.signalResponseComputer(message)
        self.messageSender.send(response)

class EventReceiver:
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

class HttpMessageSender:
    def __init__(self, config):
        self.config = config

    def send(self, message):
        requestContent = [ 
                            ('title', self.config["notification"]["title"])
                         ,  ('message', self.config["notification"]["message"])
                         ,  ('priority', 8)
                         ] 
        url = self.prepareQuery(requestContent)
        requests.post(url)

    def prepareQuery(self, requestContent):
        url =  (self.config["gotify"]["scheme"] 
               + "://" + self.config["gotify"]["server"] 
               + ":" + str(self.config["gotify"]["port"]))
        token = [("token", self.config["gotify"]["token"])]
        query = token + requestContent
        url += "/message"
        if query: 
            url += "?"
            queryAsStrings = map(makeSetting, query)
            url += '&'.join(queryAsStrings)    
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


control = Control(
                    EventReceiver(EventSource()), 
                    SignalResponseComputer(5), 
                    HttpMessageSender(configDictionary)
                )




