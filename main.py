# ===== SETUP =====
import os # allows use of environment variables
import discord
from replit import db
import random, re
from collections import defaultdict
from stayawake import stayawake

activity = discord.Activity(name="the game (you know, the one you just lost)", type=discord.ActivityType.playing)
client = discord.Client(activity=activity)

@client.event
async def on_ready():
  print("Kenku is listening as {0.user}".format(client))

# ===== DEFINING FUNCTIONS =====

#TBA: called when an opted-in user sends a message
# def addUserMessage(user, message):
#   userContent = db[user]
#   userContent.append(message)
#   db[user] = userContent

def addGlobalMessage(message):
  if "serverContent" in db.keys():
    serverContent = db["serverContent"]
    serverContent.append(message)
    db["serverContent"] = serverContent
  else:
    db["serverContent"] = [message]

# add user to db.keys()
def userOptIn(user):
  db[user] = []
  print(str(user) + " opted in")

# removes user from db.keys()
def userOptOut(user):
  del db[user]
  print(str(user) + " opted out")

# markov's chain setup:
class LString:
  def __init__(self):
    self._total = 0
    self._successors = defaultdict(int)

  def put(self, word):
    self._successors[word] += 1
    self._total += 1

  def get_random(self):
    ran = random.randint(0, self._total - 1)
    for key, value in self._successors.items():
      if ran < value:
        return key
      else:
        ran -= value

# server-specific markov's chain setup commands
serverCoupleWords = defaultdict(LString) # stores the chain

def serverLoad():
  serverContent = db["serverContent"]
  for message in serverContent:
    serverAddMessage(message)

def serverAddMessage(message):
  message = re.sub(r'[^\w\s\/\:\-\#\@]', '', message).lower().strip()
  words = message.split()
  if len(words)!= 0 :
    for i in range(2, len(words)):
      serverCoupleWords[(words[i - 2], words[i - 1])].put(words[i])
     serverCoupleWords[(words[-2], words[-1])].put("")

def serverGenerate():
  result = []
  while len(result) < 5 or len(result) > 20:
    result = []
    s = random.choice(list(serverCoupleWords.keys()))
    result.extend(s)
    while result[-1]:
      w = serverCoupleWords[(result[-2], result[-1])].get_random()
      result.append(w)

  return " ".join(result)

# TBA: user-specific markov's chain setup commands
# userCoupleWords = defaultdict(LString)

# def userLoad(user):
#   userContent = db[user]
#   for message in userContent:
#     userAddMessage(message)

# def userAddMessage(message):
#   message = re.sub(r'[^\w\s\/\:]', '', message).lower().strip()
#   words = message.split()
#   for i in range(2, len(words)):
#     userCoupleWords[(words[i - 2], words[i - 1])].put(words[i])
#   userCoupleWords[(words[-2], words[-1])].put("")

# def userGenerate():
#   result = []
#   while len(result) < 5 or len(result) > 20:
#     result = []
#     s = random.choice(list(userCoupleWords.keys()))
#     result.extend(s)
#     while result[-1]:
#       w = userCoupleWords[(result[-2], result[-1])].get_random()
#       result.append(w)

#   return " ".join(result)

# ===== COMMANDS =====

mimicTriggers = ["kenku"]
blacklist = ["suicide", "god", "pregnant", "pregnancy", "choke", "choking", "strangle", "strangling", "killing stalking", "hospital", "holy spirit", "trinity", "touch tone telephone", "cult", "cannibal", "fatphobia", "fatphobic", "shoplift", "arrest", "heaven", "drown", "!p", "||", "!s", "!fs", "!q", "!shuffle", "http", "hamilton", "henry", "tempoptout"]
serverLoad()

@client.event
async def on_message(message):
  # ignore messages from the bot
  if message.author == client.user: 
    return
  
  # ignore messages in the #serious-talk channel
  if message.channel.id == 737263667459915848:
    return

  # sends command list
  elif message.content.startswith("<(help") or message.content.startswith("<( help"):
    await message.channel.send("Hi, I'm Kenku! <:nevermore:878824017602170890> Want to hear me do an impression? I only know how to imitate words and phrases I've heard others say, so I might spit out nonsense for a while, but the more I learn the better I'll get!\n \n> **<(help:** Displays this list of commands \n> \n> **<(optin:** Start teaching me with your messages!\n> \n> **<(optout:** Stop teaching me with your messages (note that messages previously sent while opted in will remain in my memory)\n> \n> **<(mimic:** Generates a message! (I'll also respond to mentions of my name, Kenku!)") #<:nevermore:878822378463957012> # TBA: **<(mimicme:** Generates a message exclusive to you (only works if you've opted in); opting out will clear your personalized message data, although your messages will remain in server-wide memory
  
  # allows users to opt in to have their messages collected
  elif message.content.startswith("<(optin") or message.content.startswith("<( optin"):
    if message.author.name in db.keys():
      await message.channel.send("**{},** you are already opted in!".format(message.author.name))
    else:
      userOptIn(message.author.name)
      await message.channel.send("Now listening to **{}** :loud_sound:".format(message.author.name))

  # allows opted-in users to change their mind and stop having their messages collected
  elif message.content.startswith("<(optout") or message.content.startswith("<( optout"):
    if message.author.name in db.keys():
      userOptOut(message.author.name)
      await message.channel.send("No longer listening to **{}** :mute:".format(message.author.name))
    else:
      await message.channel.send("**{},** you are already opted out!".format(message.author.name))

  # TBA: per-user mimicry
  # elif message.content.startswith("<(mimicme") or message.content.startswith("<( mimicme"):
  #   if message.author.name in db.keys():
  #     userCoupleWords = defaultdict(LString)
  #     userLoad(message.author.name)
  #     await message.channel.send("Okay, here's my {} impression: ".format(message.author.name) + userGenerate())    
  #   else:
  #     await message.channel.send("Sorry, I can only do impressions of users who have performed the `<(optin` command <:oops:827011805099589653>")

# ignores messages containing blacklisted words
  elif any(word in message.content for word in blacklist):
    return

# sends mimicry
  elif message.content.startswith("<(mimic") or message.content.startswith("<( mimic") or any(word in message.content.lower() for word in mimicTriggers):
    serverLoad()
    await message.channel.send(serverGenerate())


  # moderation commands for status checks/debugging
  elif message.author.id == 233752195768647680 and message.content.startswith("<(clearall"):
    db["serverContent"] = []
  elif message.content.startswith("<(listdb"):
    print(db.keys())
  elif message.content.startswith("<(getdb"):
    print(db["serverContent"])

  # adds all non-command messages sent by opted-in users to the message database
  elif message.author.name in db.keys() and len(message.content.split()) > 3:
    #addUserMessage(message.author.name, message.content)
    addGlobalMessage(message.content)
  
  else:
    return

stayawake() # sends periodic pings to keep the bot running
client.run(os.environ["kenkuToken"]) # uses an environment variable to keep the bot token hidden