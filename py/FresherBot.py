import os
import requests
import threading
from PIL import Image
import discord
import matplotlib.colors as mcolours
import asyncio
import random
import time

from user_vars import UserVars

CUSTOM_COLOUR_DICT = {"swan_hack": (0x00, 0xFF, 0x02),
                      "pink"     : (0xFF, 0x22, 0xCB),
                      "blurple"  : (0x55, 0x39, 0xcc)}


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

                # Set of member members that messaged the channel for timeout reasons
                self.messagedMemberSet = set()

                # Set the random seed to system time
                random.seed(int(time.time() * 1000))

                # Function to respond to requests (based on mood)
                self.__responseFunction = self.__simpResponse
                # Last time we changed the sassMode
                self.__sassLastChanged = 0
                # How frequently we change moods
                self.__SASS_CHANGE_FREQUENCY_SECONDS = 60

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
                if str(message.channel.id) == UserVars.DISCORD_BOT_MSG_CHANNEL and not message.author.bot:
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

        def colourNOT(colour):
                newColour0 = colour[0] ^ int('11111111', 2)
                newColour1 = colour[1] ^ int('11111111', 2)
                newColour2 = colour[2] ^ int('11111111', 2)
                return (newColour0, newColour1, newColour2)
        
        async def __handleChannelMessage(self, message):
                messageDelimited = message.content.split(' ')
                helpString = \
                ("I am the one who controls the lights you see at the swan_hack " + \
                "Freshers' Fayre stall!\nI am capable of rudimentary " + \
                "communication and my mood changes every %d seconds!\n" + \
                "You can find out exactly how I work here: " + \
                "https://github.com/swanhack/lightbot/blob/main/py/FresherBot.py\n\n" + \
                "Now, ask me to display a *colour*!") % self.__SASS_CHANGE_FREQUENCY_SECONDS
                
                negateNext = False
                polite = False
                colourQueue = list()
                if message.content == "who are you?":
                        await message.reply(helpString)
                        return
                
                for word in messageDelimited:
                        if word == "not":
                                negateNext = True
                        elif word == "please":
                                polite = True
                        elif self.__validColour(word):
                                colour = self.__translateColour(word)
                                if negateNext:
                                        colour = FresherBot.colourNOT(colour)
                                colourDict = {"word"   : word,
                                              "negated": negateNext,
                                              "colour" : colour}
                                colourQueue.append(colourDict)
                                negateNext = False
                        else:
                                negateNext = False

                # Update the mood if necessary and run the necessary function
                self.__updateSassMode()
                # Uncomment when you can take the sass
                await self.__responseFunction(message, colourQueue, polite)



        def __updateSassMode(self):
                # Race conditions? Never heard of 'em.
                if int(time.time()) - self.__sassLastChanged < self.__SASS_CHANGE_FREQUENCY_SECONDS:
                        return
                sass = random.random()
                # Determine sass coefficient
                if sass > 0.75:
                        self.__responseFunction = self.__assholeResponse
                elif sass > 0.50:
                        self.__responseFunction = self.__politenessRequiredResponse
                elif sass > 0.25:
                        self.__responseFunction = self.__semiSassResponse
                else:
                        self.__responseFunction = self.__simpResponse

                self.__sassLastChanged = int(time.time())
                
                
        async def __simpResponse(self, message, colourQueue, polite):
                colourResponses = ("haha that's crazy I love %s as well, look what I can do for you queen!",
                                   "good choice king, i'll make sure to give you a nice shade of %s",
                                   "alright i'll change it to %s... but like..." +
                                   " haha but what if I was like there right now instead of changing" +
                                   " lights for you...haha jk!!!!! unless... 👉👈")
                negatedResponses = ("i'll erase all the %s in the world for you, m'lady",
                                    "woah thats crazy I hate %s just like you hehe woah",
                                    "%s? yeah, screw that colour, it sucks.")
                colourlessResponses = ("i'm sorry I didn't get that, I swear i'll try harder next time uwu",
                                       "i have no idea what you are saying but I love the way you talk",
                                       "i'm an idiot but I still love you")
                                       
                response = "something went wrong with my programming and I am left sad :("
                if colourQueue:
                        colour = colourQueue.pop()
                        if colour["negated"]:
                                response = negatedResponses[int(random.random() * 3)] % colour["word"]
                        else:
                                response = colourResponses[int(random.random() * 3)] % colour["word"]
                        await self.fresherUno.setTemporaryColour(colour["colour"], totalSec = 5)
                else:
                        response = colourlessResponses[int(random.random() * 3)]
                await message.reply(response)
                

        async def __semiSassResponse(self, message, colourQueue, polite):
                colourResponses = ("%s? If you say so.",
                                   "I don't think %s is the best choice, but I guess I have no say in the matter.",
                                   "Fine, i'll give you %s, but you might like the second one a bit more.")
                negatedResponses = ("I'll tend to agree with you that %s is pretty bad.",
                                    "Yeah, I could see why you say that, %s really is a colour that only " +
                                    "a mother could love.",
                                    "I HATE %s")
                colourlessResponses = ("I know you'd like to think I'm dumb, but I like to think you just " +
                                       "don't know how to speak to me.",
                                       "I understand, but at the same time I don't.",
                                       "I don't understand, so have blurple instead.")
                
                response = "something went wrong with my programming and I am left sad :(\nYou are free to blame anyone on committee for this henious crime."
                choice = int(random.random() * 3)
                if colourQueue:
                        colour = colourQueue.pop()
                        if colour["negated"]:
                                response = negatedResponses[choice] % colour["word"]
                                await message.reply(response)
                                await self.fresherUno.setTemporaryColour(colour["colour"],
                                                                         totalSec = 5)
                        else:
                                response = colourResponses[choice] % colour["word"]
                                await message.reply(response)
                                await self.fresherUno.setTemporaryColour(colour["colour"],
                                                                         totalSec = 5)
                                if choice == 2:
                                        colourNOTed = FresherBot.colourNOT(colour["colour"])
                                        time.sleep(5)
                                        await self.fresherUno.setTemporaryColour(colourNOTed,
                                                                                 totalSec = 5)
                else:
                        response = colourlessResponses[int(random.random() * 3)]
                        await message.reply(response)
                        if choice == 2:
                                await self.fresherUno.setTemporaryColour(CUSTOM_COLOUR_DICT["blurple"],
                                                                         totalSec = 5)
                                

        async def __politenessRequiredResponse(self, message, colourQueue, polite):
                politeColourResponses = ("Ah shucks, of course I'll set the colour to %s, you're welcome sonny.",
                                         "Sure thing friendolino! I appreciate the politeness! Take a look at %s!",
                                         "Geez you're so nice, how can I resist? Here you go! %s!")
                rudeResponse = ("Ah-ah-ah, you didn't say the magic word!",
                                "Yeah I'm sorry I cannot handle your rudeness rn, consider " +
                                "being a bit more polite next time.",
                                "Can I get a \"please\" in the chat?")
                politeNegatedResponses = ("I'd tend to disagree on the matter of whether %s is " +
                                          "unfavourable, however unfortunately due to your politeness" +
                                          " I simply do not have the heart to refuse such a request, " +
                                          " as it seems you are a natural-born charmer and very nice :)",
                                          "Of course! I hope my replacement for %s will be satisfactory.",
                                          "You're welcome! Here you go fellow human being who dislikes %s.")
                colourlessResponses = ("That's good and all, but I am apologetic to admit that I simply " +
                                       "cannot parse your request",
                                       "Hmm, interesting, tell me more.",
                                       "I am definitely capable interpreting everything you are saying and capable " +
                                       "of understanding it, I just don't want to.")
                
                response = "something went wrong with my programming and I am left sad :(\nYou are free to blame anyone on committee for this henious crime."
                choice = int(random.random() * 3)
                if colourQueue:
                        colour = colourQueue.pop()
                        if not polite:
                                await message.reply(rudeResponse[choice])        
                        elif colour["negated"]:
                                response = politeNegatedResponses[choice] % colour["word"]
                                await message.reply(response)
                                await self.fresherUno.setTemporaryColour(FresherBot.colourNOT(colour["colour"]),
                                                                         totalSec = 5)
                        else:
                                response = politeColourResponses[choice] % colour["word"]
                                await message.reply(response)
                                await self.fresherUno.setTemporaryColour(colour["colour"],
                                                                         totalSec = 5)


                else:
                        response = colourlessResponses[choice]
                        await message.reply(response)
                
        async def __assholeResponse(self, message, colourQueue, polite):
                colourResponses = ("Really? %s? I'm not setting that.",
                                   "I'm sorry but I really can't be asked and do not care enough about " +
                                   "any of this to change the colour to %s.",
                                   "And why should I listen to you? You can't come up with anything better " +
                                   "than %s?")
                negatedResponses = ("Why not %s? Are you afraid or something?",
                                    "I'm not going to do any colour actually, not just %s.",
                                    "Really, you don't want %s?")
                colourlessResponses = ("Okay, and your point being?",
                                       "I didn't care when you were typing and I care even less now.",
                                       "Listen, all I'm saying is that one of us is making the situation " +
                                       "awkward and annoying, but I'm also saying thats not me.")
                
                response = "something went wrong with my programming and I am left sad :("
                if colourQueue:
                        colour = colourQueue.pop()
                        if colour["negated"]:
                                choice = int(random.random() * 3)
                                response = negatedResponses[choice] % colour["word"]
                                await message.reply(response)
                                if choice == 2:
                                        notNegated = FresherBot.colourNOT(colour["colour"])
                                        await message.reply("Too bad, you're getting it.")
                                        
                                        await self.fresherUno.setTemporaryColour(notNegated,
                                                                                 totalSec = 5)
                        else:
                                choice = int(random.random() * 3)
                                response = colourResponses[choice] % colour["word"]
                                await message.reply(response)
                                if choice == 2:
                                        colourNOTed = FresherBot.colourNOT(colour["colour"])
                                        await message.reply("I think this looks much better.")
                                        await self.fresherUno.setTemporaryColour(colourNOTed,
                                                                                 totalSec = 5)

                else:
                        response = colourlessResponses[int(random.random() * 3)]
                        await message.reply(response)

                
                
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
                elif msgContentList[0] == 'simp':
                        self.__responseFunction = self.__simpResponse
                        self.__sassLastChanged = int(time.time())
                elif msgContentList[0] == 'semi':
                        self.__responseFunction = self.__semiSassResponse
                        self.__sassLastChanged = int(time.time())
                elif msgContentList[0] == 'polite':
                        self.__responseFunction = self.__politenessRequiredResponse
                        self.__sassLastChanged = int(time.time())
                elif msgContentList[0] == 'ass':
                        self.__responseFunction = self.__assholeResponse
                        self.__sassLastChanged = int(time.time())

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
