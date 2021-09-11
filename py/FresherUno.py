import serial
import time
from time import sleep
import threading
import asyncio

# Serial signals
SSIG_DISCORD_JOIN = 1
SSIG_SET_DEFAULT_COLOUR = 2
SSIG_QUERY_STATE = 3

# Colour Macros
SWAN_HACK_GREEN = (0x00, 0xFF, 0x02)
class FresherUno:
        def __init__(self, serPort, serSpeed):
                self.serialCon = serial.Serial(serPort, serSpeed, timeout=15, write_timeout=15)
                # Wait for serial to initialise
                sleep(3)
                self.lock = threading.Lock()
                self.defaultColour = SWAN_HACK_GREEN
                self.__sendSetDefaultColour(self.defaultColour[0],
                                                  self.defaultColour[1],
                                                  self.defaultColour[2])

        def discordBlink(self, times, accentColour):
                self.__sendDiscordBlink(accentColour[0], accentColour[1], accentColour[2], times)
                
        def setDefaultColour(self, colour):
                self.defaultColour = colour
                self.__sendSetDefaultColour(colour[0], colour[1], colour[2])

        async def setTemporaryColour(self, colour, totalSec = 30):
                self.__sendSetDefaultColour(colour[0], colour[1], colour[2])
                # Run the wait asynchronously
                loop = asyncio.get_running_loop()
                out = loop.run_in_executor(None, self.__waitAndResetDefaultColour, totalSec)

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

        def __waitAndResetDefaultColour(self, timeout):
                knownTimeWhenDefaultChangedLast = self.__timeDefaultChangedLast
                sleep(timeout)
                if self.__timeDefaultChangedLast == knownTimeWhenDefaultChangedLast:
                        self.__sendSetDefaultColour(self.defaultColour[0],
                                                    self.defaultColour[1],
                                                    self.defaultColour[2])

        def __sendDiscordBlink(self, accentR, accentG, accentB, times):
                self.lock.acquire()
                self.serialCon.write(bytearray([SSIG_DISCORD_JOIN,
                                           accentR,
                                           accentG,
                                           accentB,
                                           times]))
                self.lock.release()
                
        def __sendSetDefaultColour(self, r, g, b):
                self.lock.acquire()
                self.__timeDefaultChangedLast = int(time.time())
                self.serialCon.write(bytearray([SSIG_SET_DEFAULT_COLOUR,
                                                r,
                                                g,
                                                b]))
                self.lock.release()
                     
