import discord
import serial
from time import sleep
import os
import datetime
# User-defined variables file
from user_vars import UserVars

# Definitions
DATA_DIR_PATH = "./data"

class FresherBot(discord.Client):
    def initialise(self, dataPath, serialCon):
        self.dataPath = dataPath
        self.serialCon = serialCon
        
    async def on_ready(self):
        print("%s IS ALIVE" % self.user)

    async def on_message(self, message):
        if message.author.name == UserVars.DISCORD_USER:
            if message.content == 'newuser':
                self.serialCon.write(b'Q')
                self.serialCon.write(bytes(str(len('newuser')), 'ascii'))

#    async def on_member_join(self, member):
        

        



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
        
    serialCon = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    # Wait for serial to initialise
    sleep(3)

    path = "%s/%s" % (DATA_DIR_PATH, str(datetime.date.today()))
    if not os.path.isdir(path):
        os.makedirs(path)

    discordBot = FresherBot()
    discordBot.initialise(path, serialCon)
    discordBot.run(UserVars.DISCORD_API)

    
if __name__ == "__main__":
    main()
