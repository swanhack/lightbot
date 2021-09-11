import datetime
import os
import serial
import asyncio

from FresherBot import FresherBot
from FresherUno import FresherUno
from user_vars import UserVars

# Definitions
DATA_DIR_PATH = "./data"
ARDUINO_SERIAL_PORT = "/dev/ttyACM0"
ARDUINO_SERIAL_SPEED = 9600


def main():
        # Verify user variables have been filled
        # Yes, there is a better way to do this
        # No, that does not mean I'm not going to be lazy
        if not UserVars.DISCORD_API:
                print("error: py/user_vars.py: DISCORD_API not filled in, please visit the file")
                exit()
        if not UserVars.DISCORD_USER:
                print("error: py/user_vars.py: DISCORD_USER not filled in, please visit the file")
                exit()

        try:
                fUno = FresherUno(ARDUINO_SERIAL_PORT, ARDUINO_SERIAL_SPEED)
        except serial.serialutil.SerialException as se:
                print('error: could not connect to serial: %s' % se)
                quit(1)

        path = "%s/%s" % (DATA_DIR_PATH, str(datetime.date.today()))
        if not os.path.isdir(path):
                os.makedirs(path)
        
        discordBot = FresherBot(path, fUno)
        discordBot.run(UserVars.DISCORD_API)

    
if __name__ == "__main__":
        main()
