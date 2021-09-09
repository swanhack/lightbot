import serial
from time import sleep
import threading

# Serial signals
SSIG_DISCORD_JOIN = 1
SSIG_SET_DEFAULT_COLOUR = 2
SSIG_QUERY_STATE = 3
class FresherUno:
        def __init__(self, serPort, serSpeed):
                self.serialCon = serial.Serial(serPort, serSpeed, timeout=15, write_timeout=15)
                self.lock = threading.Lock()
                # Wait for serial to initialise
                sleep(3)

        def discordBlink(self, times, accentColour):
                self.lock.acquire()
                serialCommand = bytearray([SSIG_DISCORD_JOIN, accentColour[0], accentColour[1],
                                       accentColour[2], times])
                self.serialCon.write(serialCommand)
                self.lock.release()

        def setDefaultColour(self, colour):
                self.lock.acquire()
                serialCommand = bytearray([SSIG_SET_DEFAULT_COLOUR, colour[0], colour[1], colour[2]])
                self.serialCon.write(serialCommand)
                self.lock.release()

        def queryCurrentColour(self):
                self.lock.acquire()
                self.serialCon.write(bytearray([SSIG_QUERY_STATE]))
                RGB_BYTE_SIZE = 3
                currentStateBytes = self.serialCon.read(RGB_BYTE_SIZE)
                self.lock.release()
                if not len(currentStateBytes) == RGB_BYTE_SIZE:
                        raise RuntimeError("didn't read full rgb state string from arduino")
                currentState = (currentStateBytes[0], currentStateBytes[1],
                                currentStateBytes[2])
                return currentState
                     
