import discord
import serial
from time import sleep
import os
import datetime
# User-defined variables file
from user_vars import UserVars

# Definitions
DATA_DIR_PATH = "./data"
ARDUINO_SERIAL_PORT = "/dev/ttyACM0"
ARDUINO_SERIAL_SPEED = 9600

class FresherBot(discord.Client):
    def __init__(self, dataPath, fresherUno):
        self.dataPath = dataPath
        self.fresherUno = fresherUno
        # run the constructor of our parent (discord.Client)
        super(FresherBot, self).__init__()

        
    async def on_ready(self):
        print("%s IS ALIVE" % self.user)

    async def on_message(self, message):
        if message.author.name == UserVars.DISCORD_USER:
            if message.content == 'newuser':
                self.fresherUno.discordBlink(len('newuser'))

#    async def on_member_join(self, member):

class FresherUno:
    def __init__(self, serPort, serSpeed):
        self.serialCon = serial.Serial(serPort, serSpeed, timeout=1)
        # Wait for serial to initialise
        sleep(3)

    def discordBlink(self, times):
        self.serialCon.write(b'Q')
        self.serialCon.write(bytes(str(times), 'ascii'))


def main():
    # Verify user variables have been filled
    # Yes, there is a better way to do this
    # No, that does not mean I'm not going to be lazy
    if not UserVars.DISCORD_API:
        print("error: py/user_vars.py: DISCORD_API not filled in, fill in with your Discord bot's API key")
        exit()
    if not UserVars.DISCORD_USER:
        print("error: py/user_vars.py: DISCORD_USER not filled in, please fill in with your user name")
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
