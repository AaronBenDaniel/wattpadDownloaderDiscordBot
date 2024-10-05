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
    content = content.text
    if content == "HTTP Error 400: Bad Request":
        raise (ValueError)
        return
    return content


def getStoryID(ID):
    content = requests.get(f"{APIEndpoint}/get_info/{ID}/getstoryid/url")
    content = content.text
    if content == "HTTP Error 400: Bad Request":
        raise (ValueError)
        return
    return content


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

    try:  # Try to get story info
        metadata = getStoryInfo(message.content)
        isPartID = False
        ID = message.content
    except:  # Maybe it's a Part ID
        try:
            ID = getStoryID(message.content)
            metadata = getStoryInfo(ID)
            isPartID = True
        except:  # It's just a random number
            return

    metadata = loads(metadata)

    title = metadata["title"]
    author = metadata["user"]["username"]

    response = (
        f"`{message.content}` is a "
        + ("Part" if isPartID else "Story")
        + f" ID for the book `{title}` by `{author}`"
    )

    await message.channel.send(response)


client.run(botToken)
