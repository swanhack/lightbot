import os
import requests
import threading
from PIL import Image
import discord
import matplotlib.colors as mcolours
import asyncio

from user_vars import UserVars

CUSTOM_COLOUR_DICT = {"swan_hack": (0x00, 0xFF, 0x02),
                      "pink"     : (0xFF, 0x22, 0xCB)}

class FresherBot(discord.Client):
        def __init__(self, dataPath, fresherUno):
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
                
                # run the constructor of our parent (discord.Client) with right permissions
                memberIntent = discord.Intents.default()
                memberIntent.members = True
                super(FresherBot, self).__init__(intents=memberIntent)
                        
        def __del__(self):
                self.joinedMemberFile.close()

                        
        async def on_ready(self):
                print("%s IS ALIVE" % self.user)

        async def on_message(self, message):
                # fresher-bot message
                if str(message.channel.id) == UserVars.DISCORD_BOT_MSG_CHANNEL:
                        await self.__handleChannelMessage(message)

                # Private message from privileged user
                elif str(message.author.id) == UserVars.DISCORD_USER_ID:
                        await self.__handlePrivilegedMessage(message)

                        
    
        async def on_member_join(self, member):
                # Don't do anything if we have collision on the member name
                if self.__addJoinedMember(member):
                        accentColour = self.__getAccentColour(member)
                        await self.fresherUno.setTemporaryColour(accentColour)
                        self.fresherUno.discordBlink(len(member.display_name), accentColour)

        async def __handleChannelMessage(self, message):
                messageDelimited = message.content.split(' ')
                negateNext = False
                colourList = list()
                for word in messageDelimited:
                        if word == "not":
                                negateNext = not negateNext
                        elif self.__validColour(word):
                                colour = self.__translateColour(word)
                                if negateNext:
                                        # randomize colour so its not
                                        # the original
                                        newColour1 = colour[0] ^ int('11111111', 2)
                                        newColour2 = colour[1] ^ int('11111111', 2)
                                        newColour3 = colour[2] ^ int('11111111', 2)
                                        colour = (newColour1, newColour2, newColour3)
                                        negateNext = False
                                await self.fresherUno.setTemporaryColour(colour, totalSec = 5)
                        
        async def __handlePrivilegedMessage(self, message):
                msgContentList = message.content.split(' ')
                if msgContentList[0] == 'newuser':
                        accentColour = self.__getAccentColour(message.author)
                        await self.fresherUno.setTemporaryColour(accentColour)
                        self.fresherUno.discordBlink(len(message.author.name), accentColour)
                elif msgContentList[0] == 'colour':
                        try:
                                newDefaultColour = self.__translateColour(msgContentList[1])
                                self.fresherUno.setDefaultColour(newDefaultColour)
                        except ValueError as ve:
                                await message.author.send("Sorry, I don't know what colour that is.")

        def __validColour(self, colourStr):
                if colourStr in CUSTOM_COLOUR_DICT.keys():
                        return True
                try:
                        colourPercent = mcolours.to_rgb(colourStr)
                        return True
                except ValueError:
                        return False

        def __translateColour(self, colourStr):
                if colourStr in CUSTOM_COLOUR_DICT.keys():
                        return CUSTOM_COLOUR_DICT[colourStr]

                colourPercent = mcolours.to_rgb(colourStr)
                return (int(colourPercent[0] * 255),
                        int(colourPercent[1] * 255),
                        int(colourPercent[2] * 255))
                        
        
        # Currently just retrieves the pixel at arbitrary pixel
        def __getAccentColour(self, member):
                req = requests.get(member.avatar_url, stream = True)
                if req.status_code == 200:
                        req.raw.decode_content = True
                        with Image.open(req.raw) as avatarImg:
                                avatarPx = avatarImg.load()
                        accentColour = avatarPx[50, 50]
                else:
                        print('error: FresherBot: failed to download image for user %s at %s' %
                              (member.name, imageURL))
                        accentcolour = (0, 0, 0)

                if not isinstance(accentColour, tuple):
                        accentColour = (0, 0, 0)
                return accentColour
            
        def __addJoinedMember(self, member):
                memberUniqueName = "%s#%s" % (member.name, member.discriminator)
                if memberUniqueName not in self.joinedMemberSet:
                        print('FresherBot: added ' + memberUniqueName)
                        self.joinedMemberSet.add(memberUniqueName)
                        self.joinedMemberFile.write(memberUniqueName + '\n')
                        self.joinedMemberFile.flush()
                        return True
                return False
