# bot.py
import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from mee6_py_api import API

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CLIENT = os.getenv('DISCORD_CLIENT')
GUILD = os.getenv('DISCORD_GUILD')
mee6API = API(GUILD)



client = commands.Bot(command_prefix = '$')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    leaderboard_page = await mee6API.levels.get_leaderboard_page(0)
    print(leaderboard_page)

@client.command()
async def point(ctx):
    level = await API(ctx.guild).levels.get_user_level(ctx.message.author.id)
    await ctx.send("Your level is {}.".format(level))


client.run(TOKEN)