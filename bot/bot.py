import discord
import os

from discord.ext import commands
from dotenv import load_dotenv
from discord_components import DiscordComponents

from cogs.welcomer import Welcomer
from cogs.roleshandler import RolesHandler

## Loading env variables
load_dotenv()
TOKEN = os.getenv("TOKEN")


##intents
intents = discord.Intents.default()
intents.members = True

## bot
description = "Official bot for KUCC discord server"
intents = discord.Intents().default()
intents.members = True
bot = commands.Bot(command_prefix=">", description=description, intents=intents)

@bot.event
async def on_ready():
    DiscordComponents(bot)
    print('Logged in as', bot.user)

# loads all cogs by default
for filename in os.listdir("./bot/cogs"):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

#loads a cog
@commands.has_role('Manager')
@bot.command()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.send("Loaded Successfully")

#unloads a cog
@commands.has_role('Manager')
@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send("Unloaded Successfully")

#reloads a cog
@commands.has_role('Manager')
@bot.command()
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    await ctx.send("Reloaded Successfully")

bot.run(TOKEN)
