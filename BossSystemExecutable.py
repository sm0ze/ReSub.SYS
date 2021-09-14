# bot.py
import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import enhancments

DEBUG = 0
TEST = 0

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
async def points(ctx, *, member = 0):
    #level = await API(ctx.guild).levels.get_user_level(ctx.message.author.id)

    member = discord.utils.get(client.get_all_members(), id=member)
    if not member:
        level = len(ctx.message.author.roles)
        member = ctx.message.author
    else:
        level = len(member.roles)
    await ctx.send("{} has {} points.".format(member, level))

@client.command()
async def cost(ctx, *, args = ''):
    if not args:
        await ctx.send("Enhancment not specified")
        return
    elif args in enhancments.power.keys():
        name = enhancments.power[args]['Name']
        weight = enhancments.cost(args)
    elif args in [enhancments.power[x]['Name'] for x in enhancments.power.keys() if args == enhancments.power[x]['Name']]:
        name = args
        key = [x for x in enhancments.power.keys() if args == enhancments.power[x]['Name']][0]
        if DEBUG: print('Args = {}, key is {}'.format(args, key))
        weight = enhancments.cost(key)
    else:
        await ctx.send("Enhancment not found")
        return

    if weight[1] == []:
        req = 'no'
    else:
        req = weight[1]
    await ctx.send("Enhancment {} costs {} points and has {} requirements".format(name, weight[0], req))

client.run(TOKEN)
