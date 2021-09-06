import serial
from time import sleep
import threading

class FresherUno:
        def __init__(self, serPort, serSpeed):
                self.serialCon = serial.Serial(serPort, serSpeed, timeout=1)
                self.lock = threading.Lock()
                # Wait for serial to initialise
                sleep(3)

        def discordBlink(self, times, accentColour):
                self.lock.acquire()
                serialCommand = bytes([1, accentColour[0], accentColour[1],
                                       accentColour[2], times])
                self.serialCon.write(serialCommand)
                self.lock.release()
