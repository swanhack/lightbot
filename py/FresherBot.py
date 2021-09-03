import os
import requests
import threading
from PIL import Image
import discord

from user_vars import UserVars

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
                # run the constructor of our parent (discord.Client)
                super(FresherBot, self).__init__()
                        
        def __del__(self):
                self.joinedMemberFile.close()
                                
        async def on_ready(self):
                print("%s IS ALIVE" % self.user)
 
        async def on_message(self, message):
                self.lock.acquire()
                if message.author.name == UserVars.DISCORD_USER:
                        accentColour = self.__getMostCommonPixel(message.author)
                        if message.content == 'newuser':
                                self.fresherUno.discordBlink(len('newuser'), accentColour)
                self.lock.release()
    
        async def on_member_join(self, member):
                self.lock.acquire()
                print('member %s joined' % member.display_name)
                # Don't blink if we have collision on the member name
                if self.__addJoinedMember(member.display_name):
                        accentColour = self.__getMostCommonPixel(message.author)
                        self.fresherUno.discordBlink(len(member.display_name))
                self.lock.release()

        def __getMostCommonPixel(self, member):
                req = requests.get(member.avatar_url, stream = True)
                if req.status_code == 200:
                        req.raw.decode_content = True
                        with Image.open(req.raw) as avatarImg:
                                avatarPx = avatarImg.load()
                        return avatarPx[4, 4]
                else:
                        print('error: FresherBot: failed to download image for user %s at %s' %
                              (member.name, imageURL))
                        return (0, 0, 0)
            
        def __addJoinedMember(self, memberName):
                if memberName not in self.joinedMemberSet:
                        print('FresherBot: added ' + memberName)
                        self.joinedMemberSet.add(memberName)
                        self.joinedMemberFile.write(memberName + '\n')
                        self.joinedMemberFile.flush()
