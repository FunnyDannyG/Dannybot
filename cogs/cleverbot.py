import os

import discord
from cleverwrap import CleverWrap
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
cw = CleverWrap(os.getenv("CLEVERBOT_KEY"))


class cleverbot(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, input: discord.Message):
        if "talk-to-dannybot" in str(input.channel.name):
            if not input.author.bot:
                if "new conversation" in input.content:
                    cw.reset()
                elif "> " in input.content:
                    return
                else:
                    await input.channel.send(cw.say(input.content), reference=input)


async def setup(bot: commands.Bot):
    await bot.add_cog(cleverbot(bot))