from typing import Tuple
from dotenv import load_dotenv

load_dotenv()
from os import environ
import re
from datetime import datetime
import disnake
from disnake.ext import commands
import aiohttp


intents = disnake.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    intents=intents,
    case_insensitive=True,
)
bot.load_extension("jishaku")


class MessageToStoryCog(commands.Cog):
    """Check message content for Story or Part IDs/URLs."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.pattern = re.compile(r"\d+")
        self.headers = {"user-agent": "WPDBot"}
        self.host = "https://wpd.rambhat.la"  # Note: If you're selfhosting a wpd instance, place its URL here
        self.host = self.host.rstrip("/")  # Remove trailing slash

    async def get_story_from_part(self, part_id: int) -> dict:
        """Retrieve a Story from a Part ID."""
        async with aiohttp.ClientSession(
            headers=self.headers, raise_for_status=True
        ) as session:
            async with session.get(
                f"https://www.wattpad.com/api/v3/story_parts/{part_id}?fields=groupId,group"
            ) as response:
                data = await response.json()
                return data

    async def get_story(self, story_id: int) -> dict:
        """Retrieve a Story from a Story ID."""
        async with aiohttp.ClientSession(
            headers=self.headers, raise_for_status=True
        ) as session:
            async with session.get(
                f"https://www.wattpad.com/api/v3/stories/{story_id}"
            ) as response:
                data = await response.json()
                return data

    def create_embed(self, story: dict) -> Tuple[disnake.Embed, str]:
        short = f"👀 {story['readCount']} Reads  |  ⭐ {story['voteCount']} Votes |  🗨️ {story['commentCount']} Comments\n"
        short += f"🔖 {story['numParts']} Parts\n"

        short += f"🌏 {story['language']['name']}\n"

        last_updated = int(
            datetime.strptime(story["modifyDate"], "%Y-%m-%dT%H:%M:%SZ").strftime("%s")
        )
        if story["completed"]:
            short += f"✅ Completed on <t:{last_updated}:D>\n"
        else:
            short += f"🚧 Updated on <t:{last_updated}:D>\n"
        if story["mature"]:
            short += "🚸 Mature\n"

        short += f"👤 {story['user']['name']}\n"

        embed = disnake.Embed(
            title=story["title"],
            description=short,
            color=disnake.Color.orange(),  # Would be sick if I could get the dominant color of the cover, but that's a lot of work (download the cover and additional dependency: PIL)
        )
        # embed.add_field(name="Description", value=story["description"])  # Too much variation, doesn't look good

        embed.set_image(url=story["cover"])

        # embed.set_author(name=story["user"]["name"], icon_url=story["user"]["avatar"])

        embed.set_footer(text="")

        embed.add_field(name="\u200b", value="Was this helpful? React with 👍 or 👎")

        return embed, f"{self.host}/download/{story['id']}"

    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: disnake.Message):
        if message.author.bot:
            return

        matches = [int(i) for i in re.findall(self.pattern, message.content)]
        if not matches:
            return

        for match in matches:

            try:
                # Part
                data = (await self.get_story_from_part(match))["group"]
                embed, download_url = self.create_embed(data)
                to_react = await message.reply(
                    embed=embed,
                    components=[
                        disnake.ui.Button(
                            label="Download",
                            url=download_url,
                            style=disnake.ButtonStyle.primary,
                        ),
                        disnake.ui.Button(
                            label="Add the Bot",
                            url="https://discord.com/oauth2/authorize?client_id=1292173380065296395&permissions=274878285888&scope=bot%20applications.commands",
                            style=disnake.ButtonStyle.green,
                        ),
                    ],
                )
                await to_react.add_reaction("👍")
                await to_react.add_reaction("👎")

            except aiohttp.ClientResponseError:
                pass

            try:
                # Story
                data = await self.get_story(match)
                embed, download_url = self.create_embed(data)
                to_react = await message.reply(
                    embed=embed,
                    components=[
                        disnake.ui.Button(
                            label="Download",
                            url=download_url,
                            style=disnake.ButtonStyle.primary,
                        ),
                        disnake.ui.Button(
                            label="Add the Bot",
                            url="https://discord.com/oauth2/authorize?client_id=1292173380065296395&permissions=274878285888&scope=bot%20applications.commands",
                            style=disnake.ButtonStyle.green,
                        ),
                    ],
                )
                await to_react.add_reaction("👍")
                await to_react.add_reaction("👎")

            except aiohttp.ClientResponseError:
                pass


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="info",
        description="Information on the Bot",
    )
    async def info(self, interaction: disnake.GuildCommandInteraction):
        """Slash Command Handler for the Info Command."""
        embed = disnake.Embed(title="WPD Bot", color=disnake.Color.dark_magenta())
        description = "Big thanks to <@719663601060806736> for the idea and original implementation. Star his work [here](<https://github.com/AaronBenDaniel/wattpadDownloaderDiscordBot>).\n\nIf you'd like to support me, star the code [here](<https://github.com/TheOnlyWayUp/WPDBot>) and add the bot to your server!"

        embed.description = description

        embed.set_footer(text="TheOnlyWayUp ©️ 2024")

        await interaction.send(
            embed=embed,
            components=[
                disnake.ui.Button(
                    label="Add the Bot",
                    url="https://discord.com/oauth2/authorize?client_id=1292173380065296395&permissions=274878285888&scope=bot%20applications.commands",
                    style=disnake.ButtonStyle.green,
                )
            ],
        )


bot.add_cog(MessageToStoryCog(bot))
bot.add_cog(Commands(bot))


@bot.event
async def on_ready():
    print("ready", bot.user)


bot.run(environ["TOKEN"])
