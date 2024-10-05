import discord
import requests
from json import loads

file = open("token.secret", "r")
botToken = file.read()
file.close()

APIEndpoint = "https://wpd.abendaniel.top"


def getStoryInfo(ID):
    content = requests.get(
        f"{APIEndpoint}/get_info/{ID}/v3stories/title,user(username),cover"
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

        # determine what type of ID the number is
        try:  # Is it a valid Story ID
            metadata = getStoryInfo(message.content)
            storyID = message.content
            isStoryID = True
        except:
            isStoryID = False

        try:  # Is it a valid Part ID
            getStoryID(message.content)
            partID = message.content
            isPartID = True
        except:
            isPartID = False

    except:  # Maybe it's a Wattpad link
        try:
            link = message.content[message.content.find("wattpad.com/") + 12 :]
            link = link[: link.find("-")]
        except:  # Not a valid link
            return
        try:  # Is it a Part Link
            int(link)
            partID = link
            isPartID = True
            isStoryID = False
        except:  # Maybe it's a Story Link
            try:
                link = link[6:]
                storyID = link
                isPartID = False
                isStoryID = True
                metadata = getStoryInfo(storyID)
            except:  # Catch-all
                print("test")
                return

    def constructButtons(ID):
        downloadButton = discord.ui.Button(
            label="Download this story",
            style=discord.ButtonStyle.primary,
            url=APIEndpoint + "/download/" + ID,
        )
        linkButton = discord.ui.Button(
            label="View this story on Wattpad",
            url="https://wattpad.com/story/" + ID,
        )
        return [downloadButton, linkButton]

    def constructEmbed(isPart, metadata):
        metadata = loads(metadata)
        title = metadata["title"]
        author = metadata["user"]["username"]
        cover = metadata["cover"]

        embedVar = discord.Embed(
            title="Part ID" if isPart else "Story ID",
            description="",
            color=0xFF6122,
        )
        embedVar.set_thumbnail(url=cover)
        embedVar.add_field(name="Title", value=title, inline=True)
        embedVar.add_field(name="Author", value=author, inline=True)

        return embedVar

    if isStoryID:

        # Send embed
        await message.channel.send(embed=constructEmbed(False,metadata))

        # Send buttons
        buttons = constructButtons(storyID)
        await message.channel.send(
            view=discord.ui.View().add_item(buttons[0]).add_item(buttons[1])
        )

    if isPartID:

        # Get info
        partID = getStoryID(partID)
        metadata = getStoryInfo(partID)

        # Send embed
        await message.channel.send(embed=constructEmbed(True,metadata))

        # Send buttons
        buttons = constructButtons(partID)
        await message.channel.send(
            view=discord.ui.View().add_item(buttons[0]).add_item(buttons[1])
        )


client.run(botToken)
