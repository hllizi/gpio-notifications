import datetime
import time

last = None
min_differerence = 5000

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
        event = self.eventSource(True)
        self.handler(event)
        self.listen()

class MessageSender:
    def send(self, message):
        print(message)

control = Control(
                    EventReceiver(lambda a: input("Type message: ")), 
                    SignalResponseComputer(5), 
                    MessageSender()
                )




