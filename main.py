import discord
import requests
from json import loads

file = open("token.secret", "r")
botToken = file.read()
file.close()

APIEndpoint = "http://192.168.4.42:5042"


def getStoryInfo(ID):
    content = requests.get(
        f"{APIEndpoint}/get_info/{ID}/v3stories/title,user(username)"
    )
    if content.status_code == 200:
        return content.text
    raise (ValueError)


def getStoryID(ID):
    content = requests.get(f"{APIEndpoint}/get_info/{ID}/getstoryid/url")
    if content.status_code == 200:
        return content.text
    raise (ValueError)


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):  # Ignore messages sent by the bot
    if message.author == client.user:
        return

    try:  # Is the message content an integer
        int(message.content)
    except:
        return

    try: # Is it a valid Story ID
        metadata = getStoryInfo(message.content)
        isStoryID = True
    except:
        isStoryID = False

    try: # Is it a valid Part ID
        ID = getStoryID(message.content)
        isPartID = True
    except:
        isPartID = False

    if isPartID and not isStoryID: # If it's only a Part ID
        metadata = getStoryInfo(ID)

    if not isStoryID and not isPartID: # If it's isn't a valid Story or Part ID
        return

    if isStoryID and isPartID: # If it's both a Part and Story ID
        isBoth = True
    else:
        isBoth = False

    metadata = loads(metadata)

    title = metadata["title"]
    author = metadata["user"]["username"]

    if not isBoth:
        response = (
            f"`{message.content}` is a "
            + ("Part" if isPartID else "Story")
            + f" ID for the book `{title}` by `{author}`"
        )
    else:
        response = f"`{message.content}` is a Story ID for the book `{title}` by `{author}`"
        
        metadata = getStoryInfo(ID)
        metadata = loads(metadata)
        title = metadata["title"]
        author = metadata["user"]["username"]
        response = response + f" **AND** a Part ID for the book `{title}` by `{author}`"

    await message.channel.send(response)

client.run(botToken)

