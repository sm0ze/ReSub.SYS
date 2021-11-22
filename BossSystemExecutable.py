# BossSystemExecutable.py

# import asyncio
# import random
import datetime
import os
import socket
import sys
import time
import typing

import discord
import git
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv

from power import cmdInf, freeRoles, powerTypes

DEBUG = 0
TEST = 0
HOSTNAME = socket.gethostname()


def debug(*args):
    if DEBUG:
        print(*args)


# function to grab a discord bot token
# from user if one is not found in the .env
def askToken(var: str) -> str:
    tempToken = input("Enter your {}: ".format(var))
    with open(".env", "a+") as f:
        f.write("{}={}\n".format(var, tempToken))
    return tempToken


debug("DEBUG TRUE")
if TEST:
    print("TEST TRUE")

# .env variables that are not shared with github and other users.
# Use your own if testing this with your own bot
# TOKEN is the discord bot token to authorise this code for the ReSub.SYS bot
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SAVEFILE = os.getenv("SAVEFILE")
STARTCHANNEL = os.getenv("STARTCHANNEL")

if not TOKEN:
    TOKEN = askToken("DISCORD_TOKEN")
if not SAVEFILE:
    SAVEFILE = askToken("SAVEFILE")
if not STARTCHANNEL:
    STARTCHANNEL = askToken("STARTCHANNEL")

SUPEROLE = "Supe"
MANAGER = "System"  # manager role name for guild
CMDPREFIX = "~"
STARTTIME = time.time()
HIDE = False

cogList = ["options.py", "ErrorHandler.py"]

global asleep
asleep = False

# need all intents to properly manage user roles and fetch MEE6 level
INTENTS = discord.Intents.all()

# DefaultHelpCommand along with a no_category rename
HELPCOMMAND = commands.DefaultHelpCommand(no_category="\nBasic Options")

bot = commands.Bot(
    command_prefix=CMDPREFIX,
    case_insensitive=True,
    intents=INTENTS,
    help_command=HELPCOMMAND,
)


@bot.event
# function called upon bot initilisation
async def on_ready():
    # Generalised login message. Once bot is closer to finished and expected to
    # run 24/7, will add a discord channel message on login
    global STRCHNL
    channelList = [x for y in bot.guilds for x in y.channels]
    debug(channelList)
    debug(
        [
            [
                "{} == {}".format(x.id, STARTCHANNEL),
                int(x.id) == int(STARTCHANNEL),
            ]
            for x in channelList
        ]
    )

    debug("STARTCHANNEL: ", STARTCHANNEL)
    STRCHNL = [x for x in channelList if int(x.id) == int(STARTCHANNEL)]
    if STRCHNL:
        STRCHNL = STRCHNL[0]
    debug("STRCHNL: ", STRCHNL)
    print("Bot has logged in as {} on {}".format(bot.user, HOSTNAME))
    global loginTime
    loginTime = time.time()

    await STRCHNL.send(
        "Bot has logged in as {} on {}".format(bot.user, HOSTNAME)
    )

    # looped command to update bot's discord presence flavour text
    update_presence.start()

    # bot permissions debugging
    if DEBUG:
        botGuild = get(bot.guilds)
        botMember = botGuild.me

        debug("botGuild = ", botGuild)
        debug("botMember = ", botMember)

        botGuildPermissions = botMember.guild_permissions

        for perm in botGuildPermissions:
            debug(perm)


@bot.event
async def on_thread_update(before, after):
    debug("before = ", before)
    debug("after = ", after)


@bot.event
async def on_message(message: discord.Message):
    global asleep

    if message.author.bot:
        # skip message if a bot posted it
        return

    if message.author.id == bot.owner_id:
        if message.content.startswith("{}resume".format(CMDPREFIX)):
            # wake up the bot if it is asleep
            await bot.process_commands(message)
            return

    if asleep:
        # stop parsing the message if the bot is asleep
        return

    if message.content.startswith("{}{}".format(CMDPREFIX, CMDPREFIX)):
        return

    # # begining implementation for ~start
    # if message.content.startswith("{}start".format(CMDPREFIX)):
    #     if SUPEROLE not in [x.name for x in message.author.roles]:
    #         await message.channel.send(
    #             "You do not have the role {}.\nCome back after you use the "
    #             "command '{}role {}'".format(
    #                 SUPEROLE, CMDPREFIX, SUPEROLE
    #             )
    #         )
    #         return
    #     await message.channel.send(
    #         "To begin use the command '{}list'".format(CMDPREFIX)
    #     )

    #     def check(m):
    #         return (
    #             m.author == message.author
    #             and m.channel == message.channel
    #             and m.content == "{}list".format(CMDPREFIX)
    #         )

    #     try:
    #         msg = await bot.wait_for("message", check=check, timeout=10.0)
    #     except asyncio.TimeoutError:
    #         return await message.channel.send("Sorry, you took too long.")
    #     await asyncio.sleep(2)
    #     await message.channel.send(
    #         (
    #             ":point_up: These are the enhancements you can pick from. \n"
    #             "Each rank of an enhancement costs one enhancement point and"
    #             " there are prerequisite enhancements for higher ranks. \n"
    #             "For example, Rank 3 Strength requires 3 enhancement points "
    #             "and Rank 4 Strength requires 7 enhancement points."
    #             )
    #     )
    #     await message.channel.send(
    #         ("You can see how many enhancement points you "
    #          "have with the command '{}points'").format(
    #             CMDPREFIX
    #         )
    #     )
    #     return

    await bot.process_commands(message)


@tasks.loop(seconds=150)
# bot's discord rich presence updater
async def update_presence():
    guilds = bot.guilds
    members = sum(
        [len(x.members) for x in [get(y.roles, name=SUPEROLE) for y in guilds]]
    )
    nameSet = "{} users with {} enhancements".format(
        members, len(powerTypes.keys())
    )

    debug("\t\t" + str(nameSet))

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name=nameSet
        )
    )


@bot.command(
    aliases=["u"],
    brief=cmdInf["uptime"]["brief"],
    description=cmdInf["uptime"]["description"],
)
async def uptime(ctx: commands.Context):
    uptimeLogin = str(
        datetime.timedelta(seconds=int(round(time.time() - loginTime)))
    )
    uptimeStartup = str(
        datetime.timedelta(seconds=int(round(time.time() - STARTTIME)))
    )
    mes = discord.Embed(title="Uptime")
    mes.add_field(name=uptimeLogin, value="Time since last login.")
    mes.add_field(name=uptimeStartup, value="Time since bot startup.")
    mes.set_thumbnail(url=bot.user.display_avatar)
    await ctx.send(embed=mes)
    # "{} has been logged in for {}\nand powered up for {}"
    # .format(bot.user.name, uptimeLogin, uptimeStartup)


@bot.command()
@commands.is_owner()
async def resume(
    ctx: commands.Context, up: typing.Optional[int] = 0, host: str = HOSTNAME
):
    global asleep
    debug("cmd:", "resume", "ctx:", ctx, "host:", host, "up:", up)
    if host != HOSTNAME:
        return
    if asleep:
        await dupeMes(ctx, "Bot is now awake on {}".format(HOSTNAME))
        asleep = False
    if up:
        await ctx.invoke(bot.get_command("update"))
        await ctx.invoke(bot.get_command("restart"))


@bot.command(
    aliases=["r", "roles"],
    brief=cmdInf["role"]["brief"],
    description=cmdInf["role"]["description"],
)
# gives requested role to command caller if it is in freeRoles
async def role(ctx: commands.Context, *, roleToAdd: str = freeRoles[0]):
    member = ctx.message.author
    debug(roleToAdd)
    roleAdd = get(member.guild.roles, name=roleToAdd)
    if not roleAdd:
        await ctx.send("'{}' is not a valid role.".format(roleToAdd))
    elif roleAdd.name not in freeRoles:
        await ctx.send("That is not a role you can add with this command!")
    elif roleAdd not in member.roles:
        await member.add_roles(roleAdd)
        await ctx.send(
            "{} is granted the role: '{}'!".format(nON(member), roleAdd)
        )
    else:
        await member.remove_roles(roleAdd)
        await ctx.send(
            "{} no longer has the role: '{}'!".format(nON(member), roleAdd)
        )


@bot.command(
    hidden=HIDE,
    aliases=["re", "reboot"],
    brief=cmdInf["restart"]["brief"],
    description=cmdInf["restart"]["description"],
)
@commands.has_any_role(MANAGER)
async def restart(ctx: commands.Context, host: str = HOSTNAME):
    debug("cmd:", "restart", "ctx:", ctx, "host:", host)
    if host != HOSTNAME:
        return
    text = "Restarting bot on {}...".format(HOSTNAME)
    await dupeMes(ctx, text)
    restart_bot()


@bot.command(
    hidden=HIDE,
    brief=cmdInf["upload"]["brief"],
    description=cmdInf["upload"]["description"],
)
@commands.has_any_role(MANAGER)
async def upload(ctx: commands.Context, host: str = HOSTNAME):
    debug("cmd:", "upload", "ctx:", ctx, "host:", host)
    if host != HOSTNAME:
        return
    await ctx.send(
        "File {} from {}".format(SAVEFILE, HOSTNAME),
        file=discord.File(SAVEFILE),
    )


@bot.command(
    hidden=HIDE,
    brief=cmdInf["end"]["brief"],
    description=cmdInf["end"]["description"],
)
@commands.is_owner()
async def end(ctx: commands.Context, host: str = HOSTNAME):
    debug("cmd:", "end", "ctx:", ctx, "host:", host)
    if host != HOSTNAME:
        return
    text = "Bot on {} is terminating".format(HOSTNAME)
    await dupeMes(ctx, text)
    await bot.close()
    sys.exit()


@bot.command(
    hidden=HIDE,
    aliases=["up"],
    brief=cmdInf["update"]["brief"],
    description=cmdInf["update"]["description"],
)
@commands.is_owner()
async def update(ctx: commands.Context, host: str = HOSTNAME):
    debug("cmd:", "update", "ctx:", ctx, "host:", host)
    if host != HOSTNAME:
        return
    text1 = "Update starting on {}".format(HOSTNAME)
    await dupeMes(ctx, text1)
    git_dir = "/.git/ReSub.SYS"
    g = git.cmd.Git(git_dir)
    text2 = "{}\n{}".format(HOSTNAME, g.pull())
    await dupeMes(ctx, text2)


@bot.command(
    hidden=HIDE,
    aliases=["sleep"],
    brief=cmdInf["pause"]["brief"],
    description=cmdInf["pause"]["description"],
)
@commands.is_owner()
async def pause(ctx: commands.Context, host: str = HOSTNAME):
    debug("cmd:", "pause", "ctx:", ctx, "host:", host)
    if host != HOSTNAME:
        return
    global asleep
    asleep = True
    await dupeMes(ctx, "Bot is now asleep on {}".format(HOSTNAME))


@bot.command(
    brief=cmdInf["about"]["brief"],
    description=cmdInf["about"]["description"],
)
async def about(ctx: commands.Context):
    desc = (
        "This initially started as a way to automatically assign roles "
        "for Geminel#1890's novel. At the time Admins were manually "
        "calculating enhancement points and adding roles."
    )
    mes = discord.Embed(title="About {}".format(bot.user.display_name))
    mes.set_author(
        name="Creator: sm0ze#3542",
        icon_url="https://avatars.githubusercontent.com/u/31851788",
    )
    mes.add_field(inline=False, name="Why does this bot exist?", value=desc)
    mes.add_field(
        inline=False,
        name="What can the bot do?",
        value=(
            "Now the bot is capable enough to allow users to gain bot "
            "specific experience, level up their GDV and gain system "
            "enhancements through the use of commands."
        ),
    )
    mes.add_field(
        inline=False,
        name="More Info",
        value=(
            "You can find the code [here](https://github.com/sm0ze/ReSub.SYS)"
        ),
    )
    mes.set_footer(
        text="{} is currently running on {}.".format(
            bot.user.display_name, HOSTNAME
        )
    )
    mes.set_thumbnail(url=bot.user.display_avatar)
    await ctx.send(embed=mes)


@bot.command(
    brief=cmdInf["run"]["brief"],
    description=cmdInf["run"]["description"],
)
async def run(ctx: commands.Context):
    await ctx.send("Bot is running on {}".format(HOSTNAME))


@bot.command()
@commands.has_any_role(MANAGER)
async def testAll(ctx: commands.Context, host: str = HOSTNAME):
    debug("cmd:", "debug", "ctx:", ctx, "host:", host)
    if host != HOSTNAME:
        return
    host = ""
    for cmd in bot.commands:
        await ctx.send("Testing command **{}**.".format(cmd.name))
        param = cmd.clean_params
        await ctx.send("clean params: {}".format(param))
        if "host" in param.keys():
            continue
        if cmd.name in ["hhelp", "help"]:
            continue
        if cmd.can_run:
            await cmd.__call__(ctx)
    await ctx.send("Testing Done")


"""
@client.event
async def on_message(self, message):
    if message.author.id == self.user.id:
        return
    if message.content.startswith('{}start'.format(CMDPREFIX)):
        await ctx.send("To begin use the command 'list'")

        def check(m):
            return (m.author == message.author and
            m.channel == message.channel and m.content == ('{}list'
            ).format(CMDPREFIX))

        try:
            msg = await self.wait_for('message', check=check, timeout=10.0)
        except asyncio.TimeoutError:
            return await message.channel.send('Sorry, you took too long.')
        await ctx.send("next step")

@bot.command(
    aliases=['s'],
    brief=cmdInf['start']['brief'],
    description=cmdInf['start']['description'])
async def start(self, ctx):
    await ctx.send("To begin use the command 'list'")
    msg = await discord.Client.wait_for('message',
    author=ctx.message.author,
    content='list')
    await ctx.send("Next step")
    return
    """


# dirty little function to avoid 'if user.nick else user.name'
def nON(user: discord.Member) -> str:
    if user.nick:
        return user.nick
    else:
        return user.name


def restart_bot() -> None:
    os.execv(sys.executable, ["python"] + sys.argv)


async def dupeMes(channel, mes):
    if isinstance(channel, commands.Context):
        channel = channel.channel
    print(mes)
    await STRCHNL.send(mes)
    if not STRCHNL == channel:
        await channel.send(mes)


# general import protection
if __name__ == "__main__":

    # discord.py cog importing
    for filename in cogList:
        if filename.endswith(".py"):
            bot.load_extension(f"{filename[:-3]}")

        # general exception for excluding __pycache__
        # while accounting for generation of other filetypes
        elif filename.endswith("__"):
            continue
        else:
            print(f"Unable to load {filename[:-3]}")

    # and to finish. run the bot
    bot.run(TOKEN, reconnect=True)
