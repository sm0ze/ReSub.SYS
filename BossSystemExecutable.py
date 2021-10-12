# BossSystemExecutable.py

import datetime
import os
import random
import sys
import time

import discord
import enhancements
import git
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv
from mee6_py_api import API

DEBUG = 1
TEST = 0


def debug(*args):
    if DEBUG:
        print(*args)


# function to grab a discord bot token from user if one is not found in the .env
def askToken():
    tempToken = input("Enter your discord bot TOKEN: ")
    with open(".env", "a+") as f:
        f.write("DISCORD_TOKEN={}\n".format(tempToken))
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
if not TOKEN:
    TOKEN = askToken()

SUPEROLE = "Supe"
MANAGER = 'System'  # manager role name for guild
CMDPREFIX = '~'
STARTTIME = time.time()
STARTCHANNEL = 823225800073412698

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
    if message.author.id == bot.owner_id:
        if message.content.startswith('{}resume'.format(CMDPREFIX)):
            asleep = False
            return
    if not asleep:
        await bot.process_commands(message)


@bot.event
# bot error handler. Messy global implementation instead of multiple locals
async def on_command_error(ctx, error):
    splitError = str(error).split()  # for messy handling without isinstance()
    print(splitError)  # for debugging

    if isinstance(error, commands.CommandNotFound):
        em = discord.Embed(
            title=f"Error!!!", description=f"Command not found.", color=ctx.author.color)
        await ctx.send(embed=em)

    elif splitError[4] == 'KeyError:':
        await ctx.send("{} is not a recognised option".format(splitError[-1]))

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
        members, len(enhancements.powerTypes.keys()))

    debug("\t\t" + str(nameSet))

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=nameSet))
    return


@bot.command(brief=enhancements.commandInfo['uptime']['brief'], description=enhancements.commandInfo['uptime']['description'])
async def uptime(ctx):
    uptimeLogin = str(datetime.timedelta(
        seconds=int(round(time.time() - loginTime))))
    uptimeStartup = str(datetime.timedelta(
        seconds=int(round(time.time() - STARTTIME))))
    await ctx.send("{} has been logged in for {}\nand powered up for {}".format(bot.user.name, uptimeLogin, uptimeStartup))

    return


@bot.command(aliases=['r', 'roles'], brief=enhancements.commandInfo['role']['brief'], description=enhancements.commandInfo['role']['description'])
# gives requested role to command caller if it is in enhancements.freeRoles
async def role(ctx, *, roleToAdd: str = enhancements.freeRoles[0]):
    member = ctx.message.author
    debug(roleToAdd)
    roleAdd = get(member.guild.roles, name=roleToAdd)
    if not roleAdd:
        await ctx.send("'{}' is not a valid role.".format(roleToAdd))
    elif roleAdd.name not in enhancements.freeRoles:
        await ctx.send("That is not a role you can add with this command!")
    elif roleAdd not in member.roles:
        await member.add_roles(roleAdd)
        await ctx.send("{} is granted the role: '{}'!".format(nON(member), roleAdd))
    else:
        await member.remove_roles(roleAdd)
        await ctx.send("{} no longer has the role: '{}'!".format(nON(member), roleAdd))
    return


@bot.command(hidden=True, aliases=['re'])
@commands.has_any_role(MANAGER)
async def restart(ctx):
    await ctx.send("Restarting bot...")
    restart_bot()
    return


@bot.command(hidden=True)
@commands.is_owner()
async def end(ctx):
    StrtChannel = bot.get_channel(STARTCHANNEL)
    await StrtChannel.send('Bot is terminating')
    await bot.close()
    sys.exit()
    return


@bot.command(hidden=True)
@commands.is_owner()
async def update(ctx):
    git_dir = "/.git/ReSub.SYS"
    g = git.cmd.Git(git_dir)
    g.pull()
    return


@bot.command(hidden=True)
@commands.is_owner()
async def pause(ctx):
    asleep = True
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

@bot.command(aliases=['s'], brief=enhancements.commandInfo['start']['brief'], description=enhancements.commandInfo['start']['description'])
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
