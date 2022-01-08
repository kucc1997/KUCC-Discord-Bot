import discord
import os

from discord.ext import commands
from dotenv import load_dotenv

from cogs.welcomer import Welcomer

## Loading env variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

## bot
description = "Official bot for KUCC discord server"
bot = commands.Bot(command_prefix=">", description=description)

# run
@bot.event
async def on_ready():
    print('Logged in as', bot.user)
    # channel = bot.get_channel(929217867642187826)
    # await channel.send("Up and running :)")

# cogs
bot.add_cog(Welcomer(bot))

bot.run(TOKEN)
