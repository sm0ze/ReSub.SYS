# BossSystemExecutable.py

import os
import enhancements
import discord

from discord.ext import commands, tasks
from dotenv import load_dotenv
from mee6_py_api import API
from discord.utils import get

DEBUG = 0
TEST = 0

if DEBUG:
    print("{} DEBUG TRUE".format(os.path.basename(__file__)))
#if DEBUG: print()
if TEST:
    print("{} TEST TRUE".format(os.path.basename(__file__)))
#if TEST: print()

# .env variables that are not shared with github and other users.
# Use your own if testing this with your own bot
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CLIENT = os.getenv('DISCORD_CLIENT')
GUILD = os.getenv('DISCORD_GUILD')

mee6API = API(GUILD)

supeRole = "Supe"
startup_extensions = ["options.py"]
cmdPrefix = '~'
intents = discord.Intents.all()

helpCommand = commands.DefaultHelpCommand(no_category='Basic Options')

bot = commands.Bot(command_prefix=cmdPrefix,
                   case_insensitive=True, intents=intents, help_command=helpCommand)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    update_presence.start()

    botGuild = get(bot.guilds)
    if DEBUG:
        print(botGuild)

    botMember = botGuild.me
    if DEBUG:
        print(botMember)

    botGuildPermissions = botMember.guild_permissions
    for perm in botGuildPermissions:
        if DEBUG:
            print(perm)
    return


@bot.event
async def on_command_error(ctx, error):
    splitError = str(error).split()
    print(splitError)
    if isinstance(error, commands.CommandNotFound):
        em = discord.Embed(
            title=f"Error!!!", description=f"Command not found.", color=ctx.author.color)
        await ctx.send(embed=em)
    elif splitError[4] == 'KeyError:':
        await ctx.send("{} is not a recognised option".format(splitError[-1]))
    else:
        await ctx.send("Error: " + str(error))
    return


@tasks.loop(seconds=150)
async def update_presence():
    members = len(servList(bot))
    nameSet = "{} users with {} enhancements".format(
        members, len(enhancements.powerTypes.keys()))

    if DEBUG:
        print("\t\t" + str(nameSet))

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=nameSet))
    return


@bot.command(brief="-Gives the Supe role so host can recieve enhancements.")
async def super(ctx):
    member = ctx.message.author
    supeRoleId = get(member.guild.roles, name=supeRole)
    if supeRoleId not in member.roles:
        await member.add_roles(supeRoleId)
        await ctx.send("{} is now a {}!".format(nickOrName(member), supeRoleId))
    else:
        await ctx.send("{} is already a {}!".format(nickOrName(member), supeRoleId))
    return


@bot.command(brief="-Removes the Supe role and clears host of their existing enhancements.")
async def noSuper(ctx):
    member = ctx.message.author
    supeRoleId = get(member.guild.roles, name=supeRole)
    if supeRoleId in member.roles:
        await member.remove_roles(supeRoleId)
        await ctx.send("{} is no longer a {} \n( ╥﹏╥) ノシ".format(nickOrName(member), supeRoleId))
    toRun = bot.get_command('clean')
    await toRun(ctx)
    return


@bot.command(hidden=True)
@commands.is_owner()
async def load(ctx, extension_name: str):
    """Loads an extension."""
    try:
        bot.load_extension("cogs.{}".format(extension_name))
    except (AttributeError, ImportError) as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.send("{} loaded.".format(extension_name))


def servList(bots):
    guilds = bots.guilds
    if DEBUG:
        print("guilds is: {}".format(guilds))
    members_set = set()
    for guild in guilds:
        if DEBUG:
            print("Guild in guilds = {}".format(guild))
        for member in guild.members:
            if DEBUG:
                print("\tMember in {} is {}".format(guild, member))
            members_set.add(member)
    if DEBUG:
        print("members_set is: {}".format(members_set))
    return members_set


def nickOrName(user):
    if user.nick:
        return user.nick
    else:
        return user.name


if __name__ == "__main__":
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

        else:
            print(f'Unable to load {filename[:-3]}')

    bot.run(TOKEN, bot=True, reconnect=True)
