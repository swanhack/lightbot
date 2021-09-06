import os
import requests
import threading
from PIL import Image
import discord

from user_vars import UserVars

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
                if message.author.name == UserVars.DISCORD_USER:
                        accentColour = self.__getAccentColour(message.author)
                        if message.content == 'newuser':
                                self.fresherUno.discordBlink(len('newuser'), accentColour)
    
        async def on_member_join(self, member):
                print('member %s joined' % member.display_name)
                # Don't blink if we have collision on the member name
                if self.__addJoinedMember(member.display_name):
                        accentColour = self.__getAccentColour(message.author)
                        self.fresherUno.discordBlink(len(member.display_name))

        # Currently just retrieves the pixel at 4,4
        def __getAccentColour(self, member):
                req = requests.get(member.avatar_url, stream = True)
                if req.status_code == 200:
                        req.raw.decode_content = True
                        with Image.open(req.raw) as avatarImg:
                                avatarPx = avatarImg.load()
                        accentColour = avatarPx[4, 4]
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
