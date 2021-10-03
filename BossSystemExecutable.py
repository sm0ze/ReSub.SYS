# BossSystemExecutable.py

import datetime
import os
import random
import time

import discord
import enhancements
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv
from mee6_py_api import API

DEBUG = 0
TEST = 0
STARTTIME = time.time()


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
CMDPREFIX = '~'

# need all intents to properly manage user roles and fetch MEE6 level
INTENTS = discord.Intents.all()

# DefaultHelpCommand along with a no_category rename
HELPCOMMAND = commands.DefaultHelpCommand(no_category='Basic Options')

bot = commands.Bot(command_prefix=CMDPREFIX,
                   case_insensitive=True, intents=INTENTS, help_command=HELPCOMMAND)


@bot.event
# function called upon bot initilisation
async def on_ready():
    # Generalised login message. Once bot is closer to finished and expected to
    # run 24/7, will add a discord channel message on login
    print('We have logged in as {0.user}'.format(bot))
    global loginTime
    loginTime = time.time()

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


@bot.command()
async def uptime(ctx):
    uptimeLogin = str(datetime.timedelta(
        seconds=int(round(time.time() - loginTime))))
    uptimeStartup = str(datetime.timedelta(
        seconds=int(round(time.time() - STARTTIME))))
    await ctx.send("{} has been logged in for {}\nand powered up for {}".format(bot.user.name, uptimeLogin, uptimeStartup))

    return


@bot.command(brief="-Gives the Supe role so host can recieve enhancements.")
# gives SUPERROLE to command caller
async def super(ctx):
    member = ctx.message.author
    supeRoleId = get(member.guild.roles, name=SUPEROLE)
    if supeRoleId not in member.roles:
        await member.add_roles(supeRoleId)
        await ctx.send("{} is now a {}!".format(nON(member), supeRoleId))
    else:
        await ctx.send("{} is already a {}!".format(nON(member), supeRoleId))
    return


@bot.command(brief="-Removes the Supe role and clears host of their existing enhancements.")
# removes SUPERROLE and all unrestricted matching roles in power.power
async def noSuper(ctx):
    member = ctx.message.author
    supeRoleId = get(member.guild.roles, name=SUPEROLE)
    if supeRoleId in member.roles:
        await member.remove_roles(supeRoleId)
        await ctx.send("{} is no longer a {} \n{}".format(nON(member), supeRoleId, random.choice(enhancements.remList)))

    # run clean command to remova all Supe roles as well
    # due to command being in a cog, it needs to be fetched
    toRun = bot.get_command('clean')
    await toRun(ctx)
    return


@bot.command(hidden=True)
@commands.is_owner()
# hidden owner function to test load a cog
async def load(ctx, extension_name: str):
    try:
        bot.load_extension("cogs.{}".format(extension_name))
    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.send("{} loaded.".format(extension_name))


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
