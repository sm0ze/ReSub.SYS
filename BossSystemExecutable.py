# bot.py
import os

import discord, datetime, time
from discord.ext import commands, tasks
from discord.ext.commands import Bot
from dotenv import load_dotenv

from mee6_py_api import API

import re

import enhancements

DEBUG = 0
TEST = 0

if DEBUG: print("DEBUG TRUE")
#if DEBUG: print()
if TEST: print("TEST TRUE")
#if TEST: print()

# .env variables that are not shared with github and other users.
# Use your own if testing this with your own bot
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CLIENT = os.getenv('DISCORD_CLIENT')
GUILD = os.getenv('DISCORD_GUILD')

mee6API = API(GUILD)

cmdPrefix = '~'
intents = discord.Intents.all()
client = commands.Bot(command_prefix = cmdPrefix, case_insensitive=True, intents=intents)


enhList = [(x,y) for (x,y) in enhancements.powerTypes.items()]
if DEBUG: print("setup - " + "Enhancement list is {}".format(enhList))


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    update_presence.start()
    return


@tasks.loop(seconds=150)
async def update_presence():

    members = len(servList())

    nameSet = "{} users with {} enhancements".format(members, len(enhancements.powerTypes.keys()))

    if DEBUG: print(nameSet)

    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=nameSet))

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        em = discord.Embed(title=f"Error!!!", description=f"Command not found.", color=ctx.author.color)
        await ctx.send(embed=em)
    return


@client.command(brief="Shows target host's spent enhancement points")
async def spent(ctx):
    if DEBUG: print("Points function start")
    if ctx.message.mentions:
        memList = ctx.message.mentions
        if DEBUG: print("Message mentions: {}".format(memList))
    else:
        memList = [ctx.message.author]
        if DEBUG: print("Author is: {}".format(memList))

    pointList = spent(memList)
    for peep,pointCount in pointList:
        await ctx.send("{} has {} enhancements.".format(peep, pointCount))
    return

@client.command(brief="Shows target host's available enhancement points")
async def points(ctx):
    level = []
    if ctx.message.mentions:
        user = ctx.message.mentions
        if DEBUG: print("Message mentions: {}".format(user))
    else:
        user = [ctx.message.author]
        if DEBUG: print("Author is: {}".format(user))
    level = [[user[x], await mee6API.levels.get_user_level(user[x].id)] for x in range(0,len(user))]
    if DEBUG: print("level is: {}".format(level))
    for group in level:
        if DEBUG: print("group in level is: {}".format(group))
        if group[1]:
            pointTot = int(group[1]/5 + 1)
        else:
            pointTot = 0
        if DEBUG: print(group[0].roles)
        for role in group[0].roles:
            if DEBUG: print(role)
            if str(role) in enhancements.patList:
                pointTot += 1
        await ctx.send("{} has {} enhancement points.".format(group[0], pointTot))
    return


@client.command(brief="Lists all available enhancements")
async def list(ctx):
    await ctx.send("Enhancement list is:")
    mes = ""
    for group in enhList:
        if group[0][0:3].lower() == "men":
            shorthand = group[0][7:10]
        else:
            shorthand = group[0][0:3]
        addMes = "{} ({}) of {} rank(s)\n".format(group[0], shorthand.lower(), group[1])
        if DEBUG: print(addMes)
        mes += addMes
        #if DEBUG: print("funcList - " + "message is at {}".format(mes))
    if DEBUG: print("funcList - " + str(mes))
    await ctx.send("{}".format(mes))
    return


@client.command(brief="Total points required and their prerequisite enhancements")
async def build(ctx, *, args = ''):
    if DEBUG: print("Build command start")
    buildList = re.split('; |, |\*|\n|\s',args)
    buildTot = funcBuild(buildList)
    await ctx.send("This build requires {} point(s) for:\n\n {} \n\n{}".format(buildTot[0], buildTot[1], buildTot[2]))
    return

def funcBuild(buildList):
    reqList = []
    nameList = []
    if DEBUG: print("Build command buildList = {}".format(buildList))
    for item in buildList:
        if DEBUG: print("Build command item = {}".format(item))
        temCost = enhancements.cost(item)
        if DEBUG: print("Build command prereq cost = {}".format(temCost))
        reqList.append(temCost[2])
        tempName = enhancements.power[item]['Name']
        reqList.append(tempName)
        nameList.append(tempName)
    if DEBUG: print("build command reqList is: {}".format(reqList))
    temp = enhancements.eleCountUniStr(reqList)
    costTot = temp[0]
    reqList = enhancements.trim([x for x in temp[1] if x not in nameList])
    req = enhancements.reqEnd([costTot, reqList])
    if DEBUG: print("costTot: {}\n reqList: {}\n req: {}".format(costTot, reqList, req))
    return costTot, nameList, req

@client.command(brief="Shows the top ten Supes by their enhancements.")
async def topten(ctx):
    guildList = servList()
    if DEBUG: print("Guild list is: {}".format(guildList))
    supeList = []
    for pers in guildList:
        if DEBUG: print("Pers is {}".format(pers))
        for role in pers.roles:
            if DEBUG: print("role is {}".format(role))
            if str(role) == "Supe":
                supeList.append(pers)
    if DEBUG: print("Supe list is: {}".format(supeList))
    pointList = spent(supeList)
    if DEBUG: print(pointList)
    pointList = sorted(pointList, key= lambda x: x[1], reverse=True)
    if DEBUG: print(pointList)
    i = 1
    blankMessage = ""
    for group in pointList[:10]:
        blankMessage += "**{}** - {} \n\t {} enhancements\n".format( i, [group[0].name if group[0].nick == None else group[0].nick][0], group[1])
        #await ctx.send("{} is number {} with {} enhancements".format(group[0], i, group[1]))
        i += 1
    await ctx.send(blankMessage)


def spent(memList):
    retList = []
    if DEBUG: print("memList is: {}".format(memList))
    for peep in memList:
        supeRoles = []
        if DEBUG: print("current user is: {}".format(peep))
        if DEBUG: print("current user role list: {}".format(peep.roles))

        for roles in peep.roles:
            if str(roles) in [enhancements.power[x]['Name'] for x in enhancements.power.keys()]:
                supeRoles.append([x for x in enhancements.power.keys() if enhancements.power[x]['Name'] == str(roles)][0])
        if DEBUG: print("Supe roles: {}".format(supeRoles))
        pointCount = funcBuild(supeRoles)[0]

        """
        for posEnh in peep.roles:
            posEnh = str(posEnh)
            if DEBUG: print("current role is: {}".format(posEnh))
            if DEBUG: print([enhancements.power[x]['Name'] for x in enhancements.power.keys()])
            if DEBUG: print(posEnh in [enhancements.power[x]['Name'] for x in enhancements.power.keys()])
            if posEnh in [enhancements.power[x]['Name'] for x in enhancements.power.keys()]:
                pointCount += 1
        """
        retList.append([peep, pointCount])
    if DEBUG: print("retlist is: {}".format(retList))
    return retList

def servList():
    guilds = client.guilds
    if DEBUG: print()
    members_set = set()
    for guild in guilds:
        if DEBUG: print("Guild in guilds = {}".format(guild))
        for member in guild.members:
            if DEBUG: print("Member in {} is {}".format(guild,member))
            members_set.add(member)
    return members_set

client.run(TOKEN)
