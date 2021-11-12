# BossSystemExecutable.py

import asyncio
import datetime
import os
import random
import sys
import time

import discord
import enhancements as enm
import git
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv
from mee6_py_api import API

DEBUG = 0
TEST = 0


def debug(*args):
    if DEBUG:
        print(*args)


# function to grab a discord bot token from user if one is not found in the .env
def askToken(var):
    tempToken = input("Enter your {}: ".format(var))
    with open(".env", "a+") as f:
        f.write("{}={}\n".format(var, tempToken))
    return tempToken


debug("{} DEBUG TRUE".format(os.path.basename(__file__)))


if TEST:
    print("{} TEST TRUE".format(os.path.basename(__file__)))
#if TEST: print("".format())

# .env variables that are not shared with github and other users.
# Use your own if testing this with your own bot
# TOKEN is the discord bot token to authorise this code for the ReSub.SYS bot
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SAVEFILE = os.getenv('SAVEFILE')

if not TOKEN:
    TOKEN = askToken('DISCORD_TOKEN')
if not SAVEFILE:
    SAVEFILE = askToken('SAVEFILE')

SUPEROLE = "Supe"
MANAGER = 'System'  # manager role name for guild
CMDPREFIX = '~'
STARTTIME = time.time()
STARTCHANNEL = 823225800073412698
HIDE = False

global asleep
asleep = False

# need all intents to properly manage user roles and fetch MEE6 level
INTENTS = discord.Intents.all()

# DefaultHelpCommand along with a no_category rename
HELPCOMMAND = commands.DefaultHelpCommand(no_category='\nBasic Options')

bot = commands.Bot(command_prefix=CMDPREFIX,
                   case_insensitive=True, intents=INTENTS, help_command=HELPCOMMAND)


@bot.event
# function called upon bot initilisation
async def on_ready():
    # Generalised login message. Once bot is closer to finished and expected to
    # run 24/7, will add a discord channel message on login
    print('Bot has logged in as {0.user}'.format(bot))
    global loginTime
    loginTime = time.time()

    StrtChannel = bot.get_channel(STARTCHANNEL)
    await StrtChannel.send('Bot has logged in as {0.user}'.format(bot))

    # looped command to update bot's discord presence flavour text
    update_presence.start()

    # bot permissions debugging
    if DEBUG:
        botGuild = get(bot.guilds)
        botMember = botGuild.me

        debug(botGuild)
        debug(botMember)

        botGuildPermissions = botMember.guild_permissions

        for perm in botGuildPermissions:
            debug(perm)
    return


@bot.event
async def on_message(message):
    global asleep
    debug(message.author.id == bot.owner_id, message.author.id, bot.owner_id)

    if message.author.bot:
        # skip message if a bot posted it
        return

    if message.author.id == bot.owner_id:
        if message.content.startswith('{}resume'.format(CMDPREFIX)):
            # wake up the bot if it is asleep
            if asleep:
                await message.channel.send("Bot is now awake")
                asleep = False
            return

    if asleep:
        # stop parsing the message if the bot is asleep
        return

    if message.content.startswith("{}{}".format(CMDPREFIX, CMDPREFIX)):
        return

    """
    # begining implementation for ~start
    if message.content.startswith('{}start'.format(CMDPREFIX)):
        if SUPEROLE not in [x.name for x in message.author.roles]:
            await message.channel.send("You do not have the role {}.\nCome back after you use the command '{}role {}'".format(SUPEROLE, CMDPREFIX, SUPEROLE))
            return
        await message.channel.send("To begin use the command '{}list'".format(CMDPREFIX))

        def check(m):
            return m.author == message.author and m.channel == message.channel and m.content == '{}list'.format(CMDPREFIX)

        try:
            msg = await bot.wait_for('message', check=check, timeout=10.0)
        except asyncio.TimeoutError:
            return await message.channel.send('Sorry, you took too long.')
        await asyncio.sleep(2)
        await message.channel.send(":point_up: These are the enhancements you can pick from. \nEach rank of an enhancement costs one enhancement point and there are prerequisite enhancements for higher ranks. \nFor example, Rank 3 Strength requires 3 enhancement points and Rank 4 Strength requires 7 enhancement points.")
        await message.channel.send("You can see how many enhancement points you have with the command '{}points'".format(CMDPREFIX))
        return
    """

    await bot.process_commands(message)


@bot.event
# bot error handler. Messy global implementation instead of multiple locals
async def on_command_error(ctx, error):
    splitError = str(error).split()  # for messy handling without isinstance()
    print(splitError)  # for debugging

    if isinstance(error, commands.CommandNotFound):
        em = discord.Embed(
            title=f"Error!!!", description=f"Command not found.", color=ctx.author.color)
        # await ctx.send(embed=em)

    elif splitError[4] == 'KeyError:':
        await ctx.send("{} is not a recognised option".format(splitError[-1]))

    elif isinstance(error, commands.CommandOnCooldown):
        cdTime = float(splitError[-1][:-1])
        await ctx.send("You have no available tasks at this time. Please search again in {} minutes or {} seconds.".format(round(cdTime / 60, 2), cdTime))

    else:  # just send the error to discord
        await ctx.send("Error: " + str(error))
    return


@tasks.loop(seconds=150)
# bot's discord rich presence updater
async def update_presence():
    guilds = bot.guilds
    members = sum([len(x.members)
                  for x in [get(y.roles, name=SUPEROLE) for y in guilds]])
    nameSet = "{} users with {} enhancements".format(
        members, len(enm.powerTypes.keys()))

    debug("\t\t" + str(nameSet))

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=nameSet))
    return


@bot.command(aliases=['u'], brief=enm.cmdInf['uptime']['brief'], description=enm.cmdInf['uptime']['description'])
async def uptime(ctx):
    uptimeLogin = str(datetime.timedelta(
        seconds=int(round(time.time() - loginTime))))
    uptimeStartup = str(datetime.timedelta(
        seconds=int(round(time.time() - STARTTIME))))
    await ctx.send("{} has been logged in for {}\nand powered up for {}".format(bot.user.name, uptimeLogin, uptimeStartup))

    return


@bot.command(aliases=['r', 'roles'], brief=enm.cmdInf['role']['brief'], description=enm.cmdInf['role']['description'])
# gives requested role to command caller if it is in enm.freeRoles
async def role(ctx, *, roleToAdd: str = enm.freeRoles[0]):
    member = ctx.message.author
    debug(roleToAdd)
    roleAdd = get(member.guild.roles, name=roleToAdd)
    if not roleAdd:
        await ctx.send("'{}' is not a valid role.".format(roleToAdd))
    elif roleAdd.name not in enm.freeRoles:
        await ctx.send("That is not a role you can add with this command!")
    elif roleAdd not in member.roles:
        await member.add_roles(roleAdd)
        await ctx.send("{} is granted the role: '{}'!".format(nON(member), roleAdd))
    else:
        await member.remove_roles(roleAdd)
        await ctx.send("{} no longer has the role: '{}'!".format(nON(member), roleAdd))
    return


@bot.command(hidden=HIDE, aliases=['re', 'reboot'], brief=enm.cmdInf['restart']['brief'], description=enm.cmdInf['restart']['description'])
@commands.has_any_role(MANAGER)
async def restart(ctx):
    await ctx.send("Restarting bot...")
    restart_bot()
    return


@bot.command(hidden=HIDE, brief=enm.cmdInf['upload']['brief'], description=enm.cmdInf['upload']['description'])
@commands.has_any_role(MANAGER)
async def upload(ctx):
    await ctx.send(file=discord.File(SAVEFILE))


@bot.command(hidden=HIDE, brief=enm.cmdInf['end']['brief'], description=enm.cmdInf['end']['description'])
@commands.is_owner()
async def end(ctx):
    StrtChannel = bot.get_channel(STARTCHANNEL)
    await StrtChannel.send('Bot is terminating')
    await bot.close()
    sys.exit()
    return


@bot.command(hidden=HIDE, aliases=['up'], brief=enm.cmdInf['update']['brief'], description=enm.cmdInf['update']['description'])
@commands.is_owner()
async def update(ctx):
    git_dir = "/.git/ReSub.SYS"
    g = git.cmd.Git(git_dir)
    g.pull()
    return


@bot.command(hidden=HIDE, aliases=['sleep'],  brief=enm.cmdInf['pause']['brief'], description=enm.cmdInf['pause']['description'])
@commands.is_owner()
async def pause(ctx):
    global asleep
    asleep = True
    await ctx.send("Bot is now asleep")
    return

"""
@client.event
async def on_message(self, message):
    if message.author.id == self.user.id:
        return
    if message.content.startswith('{}start'.format(CMDPREFIX)):
        await ctx.send("To begin use the command 'list'")

        def check(m):
            return m.author == message.author and m.channel == message.channel and m.content == '{}list'.format(CMDPREFIX)

        try:
            msg = await self.wait_for('message', check=check, timeout=10.0)
        except asyncio.TimeoutError:
            return await message.channel.send('Sorry, you took too long.')
        await ctx.send("next step")

@bot.command(aliases=['s'], brief=enm.cmdInf['start']['brief'], description=enm.cmdInf['start']['description'])
async def start(self, ctx):
    await ctx.send("To begin use the command 'list'")
    msg = await discord.Client.wait_for('message', author=ctx.message.author, content='list')
    await ctx.send("Next step")
    return
    """


# function to grab the full member list the bot has access to
def servList(bots):
    guilds = bots.guilds
    debug("guilds is: {}".format(guilds))

    # ensure the member list is unique (a set)
    members_set = set()
    for guild in guilds:
        debug("Guild in guilds = {}".format(guild))
        for member in guild.members:
            debug("\tMember in {} is {}".format(guild, member))
            members_set.add(member)
    debug("members_set is: {}".format(members_set))
    return members_set


# dirty little function to avoid 'if user.nick else user.name'
def nON(user):
    if user.nick:
        return user.nick
    else:
        return user.name


def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)
    return


# general import protection
if __name__ == "__main__":

    # discord.py cog importing
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

        # general exception for excluding __pycache__
        # while accounting for generation of other filetypes
        elif filename.endswith('__'):
            continue
        else:
            print(f'Unable to load {filename[:-3]}')

    # and to finish. run the bot
    bot.run(TOKEN, bot=True, reconnect=True)
