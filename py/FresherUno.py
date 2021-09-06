import serial
from time import sleep
import threading

# Serial signals
SSIG_DISCORD_JOIN = 1
SSIG_SET_DEFAULT_COLOUR = 2

class FresherUno:
        def __init__(self, serPort, serSpeed):
                self.serialCon = serial.Serial(serPort, serSpeed, timeout=1)
                self.lock = threading.Lock()
                # Wait for serial to initialise
                sleep(3)

        def discordBlink(self, times, accentColour):
                self.lock.acquire()
                serialCommand = bytes([SSIG_DISCORD_JOIN, accentColour[0], accentColour[1],
                                       accentColour[2], times])
                self.serialCon.write(serialCommand)
                self.lock.release()

        def setDefaultColour(self, colour):
                self.lock.acquire()
                serialCommand = bytes([SSIG_SET_DEFAULT_COLOUR, colour[0], colour[1], colour[2]])
                self.serialCon.write(serialCommand)
                self.lock.release()
