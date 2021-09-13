# bot.py
import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from enhancments import power

# .env variables that are not shared with github and other users.
# Use your own if testing this with your own bot
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CLIENT = os.getenv('DISCORD_CLIENT')
GUILD = os.getenv('DISCORD_GUILD')

client = commands.Bot(command_prefix = '$')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command()
async def points(ctx):
    #level = await API(ctx.guild).levels.get_user_level(ctx.message.author.id)
    level = len(ctx.message.author.roles)
    await ctx.send("You have {} points.".format(level))

async def unspent(ctx):

client.run(TOKEN)
