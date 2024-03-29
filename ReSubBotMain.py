# ReSubBotMain.py

import asyncio
import discord
from discord.ext import commands, tasks
from discord.utils import get
import pretty_help

import bin.log as log
from bin.shared.consts import (
    CMD_PREFIX,
    HOST_NAME,
    START_TIME,
    SUPE_ROLE,
    TOKEN,
)
from bin.shared.dicts import notLoaded, powerTypes
from bin.shared.funcs import asleep, dupeMes

logP = log.get_logger(__name__)

runBot = True
logP.info(
    f"Bot will attempt to connect to discord on host: {HOST_NAME}, {runBot}"
)


logP.debug(f"Bot start time set as: {START_TIME}")

cogList = [
    "commands.author.py",
    "commands.default.py",
    "commands.game.py",
    "commands.manager.py",
    "commands.owner.py",
    "commands.role.py",
    "ErrorHandler.py",
]


# need all intents to properly manage user roles and fetch MEE6 level
INTENTS = discord.Intents.all()


# ":discord:743511195197374563" is a custom discord emoji format.
# Adjust to match your own custom emoji.
menu = pretty_help.EmojiMenu(
    page_left="⬅️",
    page_right="➡️",
    remove="⏹️",
    active_time=60,
)

# Custom ending note
ending_note = "{ctx.bot.user.name}"

bot = commands.Bot(
    command_prefix=CMD_PREFIX,
    case_insensitive=True,
    intents=INTENTS,
)

bot.help_command = pretty_help.PrettyHelp(
    menu=menu,
    ending_note=ending_note,
    delete_after_timeout=True,
    no_category="Basic Commands",
    index_title="Command Lists",
)

logP.info("Bot initialised")


@bot.event
# function called upon bot initilisation
async def on_ready():
    # Generalised login message. Once bot is closer to finished and expected to
    # run 24/7, will add a discord channel message on login
    channelList = [x for y in bot.guilds for x in y.channels]
    threadList = [x for y in bot.guilds for x in y.threads]
    logP.debug(
        (
            f"Bot has access to {len(bot.guilds)} servers, {len(channelList)}"
            f" channels and {len(threadList)} threads."
        )
    )
    strtMes = f"Bot has logged in as {bot.user} on {HOST_NAME}.\n"
    strtMes += f"Loaded {notLoaded[2]} of {notLoaded[1]} URLs.\n"
    if notLoaded[0]:
        strtMes += f"Failed to load these URLs: {notLoaded}"
    logP.info(strtMes)

    await dupeMes(bot, None, strtMes)

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
            (
                f"Bot: {botMember.display_name}, in guild: {guild.name}, "
                f"has {i}/{len(permList)} permissions"
            )
        )
    logP.info("Bot is now waiting for commands")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        # skip message if a bot posted it
        return

    if message.author.id == bot.owner_id:
        if message.content.startswith(f"{CMD_PREFIX}resume"):
            # wake up the bot if it is asleep
            await bot.process_commands(message)
            return

    if asleep():
        # stop parsing the message if the bot is asleep
        return

    if message.content.startswith(f"{CMD_PREFIX}{CMD_PREFIX}"):
        return

    await bot.process_commands(message)


@tasks.loop(seconds=300)
# bot's discord rich presence updater
async def update_presence():
    guilds = bot.guilds
    members = sum(
        [
            len(x.members)
            for x in [get(y.roles, name=SUPE_ROLE) for y in guilds]
        ]
    )
    nameSet = f"{members} users with {len(powerTypes.keys())} " "enhancements"

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name=nameSet
        )
    )
    logP.debug("Rich presence set to: " + nameSet)
    return


async def load_extensions():
    for filename in cogList:
        if filename.endswith(".py"):
            logP.debug(f"Loading Cog: {filename}")
            await bot.load_extension(f"bin.{filename[:-3]}")

        # general exception for excluding __pycache__
        # while accounting for generation of other filetypes
        elif filename.endswith("__"):
            continue
        else:
            print(f"Unable to load {filename[:-3]}")


async def main():
    async with bot:
        # discord.py cog importing
        await load_extensions()

        logP.debug(bot.tree)

        # and to finish. run the bot
        if runBot:
            logP.info("Bot connection starting....")
            await bot.start(TOKEN, reconnect=True)


# general import protection
if __name__ == "__main__":
    asyncio.run(main())

logP.critical("Bot has reached end of file")
