import discord
import serial
from time import sleep
import os
import datetime
import requests
import shutil
import threading
from PIL import Image
# User-defined variables file
from user_vars import UserVars

# Definitions
DATA_DIR_PATH = "./data"
ARDUINO_SERIAL_PORT = "/dev/ttyACM0"
ARDUINO_SERIAL_SPEED = 9600

class FresherBot(discord.Client):
    def __init__(self, dataPath, fresherUno):
        self.lock = threading.Lock()
        self.fresherUno = fresherUno

        # New member storage
        memberPath = dataPath + '/joinedMembers.txt'
        self.joinedMemberSet = set()
        try: 
            with open(memberPath, 'r') as joinedMembersFile:
                for joinedMember in joinedMembersFile.read().split('\n'):
                    self.joinedMemberSet.add(joinedMember)
        except FileNotFoundError:
            print("warn: joinedMembers.txt not found")

        self.joinedMemberFile = open(memberPath, 'a')

        # Profile picture storage
        self.joinedMemberImgs = dataPath + '/img'
        if not os.path.isdir(self.joinedMemberImgs):
            os.mkdir(self.joinedMemberImgs)
        
        # run the constructor of our parent (discord.Client)
        super(FresherBot, self).__init__()

#    def __del__(self):
        #self.joinedMemberFile.close()
        
    async def on_ready(self):
        print("%s IS ALIVE" % self.user)
 
    async def on_message(self, message):
        self.lock.acquire()
        if message.author.name == UserVars.DISCORD_USER:
            accentColour = self.__getMostCommonPixel(message.author)
            
            if message.content == 'newuser':
                self.__addJoinedMember('newuser')
                self.fresherUno.discordBlink(len('newuser'), accentColour)
        self.lock.release()
    
    async def on_member_join(self, member):
        self.lock.acquire()
        print('member %s joined' % member.display_name)
        self.__addJoinedMember(member.display_name)
#        self.fresherUno.discordBlink(len(member.display_name))
        self.lock.release()

    def __getMostCommonPixel(self, member):
        req = requests.get(member.avatar_url, stream = True)
        if req.status_code == 200:
            req.raw.decode_content = True
            with Image.open(req.raw) as avatarImg:
                avatarPx = avatarImg.load()
            return avatarPx[4, 4]
        else:
            print('error: FresherBot: failed to download image for user %s at %s' % (member.name, imageURL))
            return (0, 0, 0)
            
    def __addJoinedMember(self, memberName):
        if memberName not in self.joinedMemberSet:
            print('FresherBot: added ' + memberName)
            self.joinedMemberSet.add(memberName)
            self.joinedMemberFile.write(memberName + '\n')
            self.joinedMemberFile.flush()

class FresherUno:
    def __init__(self, serPort, serSpeed):
        self.serialCon = serial.Serial(serPort, serSpeed, timeout=1)
        # Wait for serial to initialise
        sleep(3)

    def discordBlink(self, times, accentColour):
        serialCommand = bytes([1, accentColour[0], accentColour[1], accentColour[2], times])
        self.serialCon.write(serialCommand)


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
