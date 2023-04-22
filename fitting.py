import datetime
import time

last = None
min_differerence = 5000

class SignalResponseComputer:
    last = None

    def __init__(self, min_differerence):
        self.min_differerence = min_differerence

    def computeSignalResponse(self, signal):
     try: 
         difference = signal - self.last
         if difference >= datetime.timedelta(seconds = self.min_differerence):
            self.last = signal
            return signal
     except TypeError as e:
         self.last = signal
         return signal

src = SignalResponseComputer(5)

current_time = datetime.datetime.now()
print(src.computeSignalResponse(current_time))
time.sleep(4)
current_time = datetime.datetime.now()
print("No time output now.")
print(src.computeSignalResponse(current_time))
time.sleep(6)
current_time = datetime.datetime.now()
print("Another time output now.")
print(src.computeSignalResponse(current_time))
