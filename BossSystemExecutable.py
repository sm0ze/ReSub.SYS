# BossSystemExecutable.py

import datetime
import os
import sys
import time
import typing

import discord
import git
from discord.ext import commands, tasks
from discord.utils import get
from pretty_help import DefaultMenu, PrettyHelp
import log
from enhancements import nON
from power import cmdInf, freeRoles, powerTypes
from sharedVars import (
    CMDPREFIX,
    HIDE,
    HOSTNAME,
    MANAGER,
    SAVEFILE,
    STARTCHANNEL,
    STARTTIME,
    SUPEROLE,
    TOKEN,
)

logP = log.get_logger(__name__)

runBot = True
logP.info(
    "Bot will attempt to connect to discord on host: {}, {}".format(
        HOSTNAME, runBot
    )
)


logP.debug("Bot start time set as: {}".format(STARTTIME))

cogList = ["options.py", "ErrorHandler.py"]

global asleep
asleep = False

# need all intents to properly manage user roles and fetch MEE6 level
INTENTS = discord.Intents.all()


# ":discord:743511195197374563" is a custom discord emoji format.
# Adjust to match your own custom emoji.
menu = DefaultMenu(
    page_left="⬅️",
    page_right="➡️",
    remove="⏹️",
    active_time=60,
)

# Custom ending note
ending_note = "{ctx.bot.user.name}"

bot = commands.Bot(command_prefix="!")


# DefaultHelpCommand along with a no_category rename
HELPCOMMAND = commands.DefaultHelpCommand(no_category="\nBasic Options")

bot = commands.Bot(
    command_prefix=CMDPREFIX,
    case_insensitive=True,
    intents=INTENTS,
)

bot.help_command = PrettyHelp(
    menu=menu,
    ending_note=ending_note,
    delete_after_timeout=True,
    no_category="Basic Options",
)

logP.info("Bot initialised")


@bot.event
# function called upon bot initilisation
async def on_ready():
    # Generalised login message. Once bot is closer to finished and expected to
    # run 24/7, will add a discord channel message on login
    global STRCHNL
    global ERTHRD
    channelList = [x for y in bot.guilds for x in y.channels]
    threadList = [x for y in bot.guilds for x in y.threads]
    logP.debug(
        "Bot has access to {} servers, {} channels and {} threads.".format(
            len(bot.guilds), len(channelList), len(threadList)
        )
    )
    startChannelCheck = [int(x.id) == int(STARTCHANNEL) for x in channelList]
    logP.debug(
        (
            "While searching for StartChannel, {} channels were checked and {}"
            " channels were found to match the given ID"
        ).format(len(startChannelCheck), startChannelCheck.count(True))
    )

    STRCHNL = [x for x in channelList if int(x.id) == int(STARTCHANNEL)]
    if STRCHNL:
        STRCHNL = STRCHNL[0]

    logP.debug("Start channel by the name of {} found".format(STRCHNL.name))

    strtMes = "Bot has logged in as {} on {}".format(bot.user, HOSTNAME)
    logP.info(strtMes)
    global loginTime
    loginTime = time.time()

    logP.debug("Bot last login time set as: {}".format(loginTime))

    await STRCHNL.send(strtMes)

    # looped command to update bot's discord presence flavour text
    update_presence.start()

    # bot permissions logP.debugging
    for guild in bot.guilds:
        botMember = guild.me
        botGuildPermissions = botMember.guild_permissions
        permList = []
        i = 0
        for perm in botGuildPermissions:
            permList.append(perm)
            if perm[1]:
                i += 1
        logP.debug(
            "Bot: {}, in guild: {}, has {}/{} permissions".format(
                nON(botMember), guild.name, i, len(permList)
            )
        )
    logP.info("Bot is now waiting for commands")


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


@tasks.loop(seconds=300)
# bot's discord rich presence updater
async def update_presence():
    guilds = bot.guilds
    members = sum(
        [len(x.members) for x in [get(y.roles, name=SUPEROLE) for y in guilds]]
    )
    nameSet = "{} users with {} enhancements".format(
        members, len(powerTypes.keys())
    )

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name=nameSet
        )
    )
    logP.debug("Rich presence set to: " + nameSet)
    return


@bot.command(
    aliases=["u"],
    brief=cmdInf["uptime"]["brief"],
    description=cmdInf["uptime"]["description"],
)
async def uptime(ctx: commands.Context):
    logP.debug("command uptime called")
    uptimeLogin = str(
        datetime.timedelta(seconds=int(round(time.time() - loginTime)))
    )
    uptimeStartup = str(
        datetime.timedelta(seconds=int(round(time.time() - STARTTIME)))
    )
    mes = discord.Embed(title="Uptime")
    mes.add_field(name=uptimeLogin, value="Time since last login.")
    mes.add_field(name=uptimeStartup, value="Time since bot startup.")
    mes.set_footer(
        text="{} is currently running on {}.".format(
            bot.user.display_name, HOSTNAME
        )
    )
    mes.set_thumbnail(url=bot.user.display_avatar)
    await ctx.send(embed=mes)
    logP.debug(
        "Bot has been logged in for: {}, and powered up for: {}".format(
            uptimeLogin, uptimeStartup
        )
    )
    # "{} has been logged in for {}\nand powered up for {}"
    # .format(bot.user.name, uptimeLogin, uptimeStartup)
    logP.debug("command uptime completed")


@bot.command()
@commands.is_owner()
async def resume(
    ctx: commands.Context, up: typing.Optional[int] = 0, host: str = HOSTNAME
):
    global asleep
    logP.debug(
        "Command resume called for host: {}, to update: {}".format(host, up)
    )
    if host != HOSTNAME:
        return
    if asleep:
        await dupeMes(ctx, "Bot is now awake on {}".format(HOSTNAME))
        asleep = False
        logP.info("Bot is now awake")
    if up:
        await ctx.invoke(bot.get_command("update"))
        await ctx.invoke(bot.get_command("restart"))
    logP.debug("command resume completed")


@bot.command(
    aliases=["r", "roles"],
    brief=cmdInf["role"]["brief"],
    description=cmdInf["role"]["description"],
)
# gives requested role to command caller if it is in freeRoles
async def role(ctx: commands.Context, *, roleToAdd: str = freeRoles[0]):
    member = ctx.message.author
    sendMes = ""
    logP.debug(
        "Trying to toggle the role: {}, for: {}".format(roleToAdd, nON(member))
    )
    roleAdd = get(member.guild.roles, name=roleToAdd)
    if not roleAdd:
        sendMes = "'{}' is not a valid role.".format(roleToAdd)
    elif roleAdd.name not in freeRoles:
        sendMes = "That is not a role you can add with this command!"
    elif roleAdd not in member.roles:
        await member.add_roles(roleAdd)
        sendMes = "{} is granted the role: '{}'!".format(nON(member), roleAdd)
    else:
        await member.remove_roles(roleAdd)
        sendMes = "{} no longer has the role: '{}'!".format(
            nON(member), roleAdd
        )
    await ctx.send(sendMes)
    logP.debug("command role resolution: " + sendMes)


@bot.command(
    hidden=HIDE,
    aliases=["re", "reboot"],
    brief=cmdInf["restart"]["brief"],
    description=cmdInf["restart"]["description"],
)
@commands.has_any_role(MANAGER)
async def restart(ctx: commands.Context, host: str = HOSTNAME):
    logP.debug("Command restart called for host: {}".format(host))
    if host != HOSTNAME:
        return
    text = "Restarting bot on {}...".format(HOSTNAME)
    await dupeMes(ctx, text)
    logP.warning("Bot is now restarting")
    restart_bot()


@bot.command(
    hidden=HIDE,
    brief=cmdInf["upload"]["brief"],
    description=cmdInf["upload"]["description"],
)
@commands.has_any_role(MANAGER)
async def upload(ctx: commands.Context, host: str = HOSTNAME):
    logP.debug("Command upload called for host: {}".format(host))
    if host != HOSTNAME:
        return
    currTime = time.localtime()
    currTimeStr = "{0:04d}.{1:02d}.{2:02d}_{3:02d}.{4:02d}.{5:02d}".format(
        currTime.tm_year,
        currTime.tm_mon,
        currTime.tm_mday,
        currTime.tm_hour,
        currTime.tm_min,
        currTime.tm_sec,
    )
    logP.debug("currTime: {}".format(currTime))
    logP.debug("currTimeStr: " + currTimeStr)
    nameStamp = "{}_{}".format(
        SAVEFILE,
        currTimeStr,
    )
    await ctx.send(
        "File {} from {}".format(SAVEFILE, HOSTNAME),
        file=discord.File(SAVEFILE, filename=nameStamp),
    )
    logP.debug("command upload completed")


@bot.command(
    hidden=HIDE,
    brief=cmdInf["end"]["brief"],
    description=cmdInf["end"]["description"],
)
@commands.is_owner()
async def end(ctx: commands.Context, host: str = HOSTNAME):
    logP.debug("Command end called for host: {}".format(host))
    if host != HOSTNAME:
        return
    text = "Bot on {} is terminating".format(HOSTNAME)
    await dupeMes(ctx, text)
    await bot.close()
    logP.warning("Bot is now offline and terminating")
    sys.exit()


@bot.command(
    hidden=HIDE,
    aliases=["up"],
    brief=cmdInf["update"]["brief"],
    description=cmdInf["update"]["description"],
)
@commands.is_owner()
async def update(ctx: commands.Context, host: str = HOSTNAME):
    logP.debug("Command update called for host: {}".format(host))
    if host != HOSTNAME:
        return
    text1 = "Update starting on {}".format(HOSTNAME)
    await dupeMes(ctx, text1)
    logP.warning(text1)
    git_dir = "/.git/ReSub.SYS"
    g = git.cmd.Git(git_dir)
    text2 = "{}\n{}".format(HOSTNAME, g.pull())
    await dupeMes(ctx, text2)
    logP.warning(text1)
    logP.info("Command update completed")


@bot.command(
    hidden=HIDE,
    aliases=["sleep"],
    brief=cmdInf["pause"]["brief"],
    description=cmdInf["pause"]["description"],
)
@commands.is_owner()
async def pause(ctx: commands.Context, host: str = HOSTNAME):
    logP.debug("Command pause called for host: {}".format(host))
    if host != HOSTNAME:
        return
    global asleep
    asleep = True
    await dupeMes(ctx, "Bot is now asleep on {}".format(HOSTNAME))
    logP.info("Bot is now paused")


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
    logP.debug("command testAll called for host: {}".format(host))
    if host != HOSTNAME:
        return
    host = ""
    logP.info("Command testAll starting")
    for cmd in bot.commands:
        mes = "Testing command **{}**.".format(cmd.name)
        await ctx.send(mes)
        logP.debug(mes)
        param = cmd.clean_params
        mes = "clean params: {}".format(param)
        await ctx.send(mes)
        logP.debug(mes)
        if "host" in param.keys():
            logP.debug("Skipping command")
            continue
        if cmd.name in ["hhelp", "help"]:
            logP.debug("Skipping command")
            continue
        if cmd.can_run:
            logP.debug("Running command")
            await cmd.__call__(ctx)
    await ctx.send("Testing Done")
    logP.info("Command testAll finished")


@bot.command(aliases=["tog"])
@commands.is_owner()
async def toggle(ctx: commands.Context, mes="t", host=HOSTNAME):
    logP.debug("command toggle called for host: {}".format(host))
    if host != HOSTNAME:
        return
    getComm = bot.get_command(mes)
    if ctx.command == getComm:
        await dupeMes(ctx, "Cannot disable this command.")
    elif getComm:
        getComm.enabled = not getComm.enabled
        ternary = "enabled" if getComm.enabled else "disabled"
        message = "Command '{}' {} on {}.".format(getComm.name, ternary, host)
        await dupeMes(
            ctx,
            message,
        )
        logP.info(message)
    else:
        await dupeMes(ctx, "Command '{}' was not found.".format(mes))


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
            logP.debug("Loading Cog: {}".format(filename))
            bot.load_extension(f"{filename[:-3]}")

        # general exception for excluding __pycache__
        # while accounting for generation of other filetypes
        elif filename.endswith("__"):
            continue
        else:
            print(f"Unable to load {filename[:-3]}")

    # and to finish. run the bot
    if runBot:
        logP.info("Bot connection starting....")
        bot.run(TOKEN, reconnect=True)
logP.critical("Bot has reached end of file")
