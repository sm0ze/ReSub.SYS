# ReSubBotMain.py

import discord
from discord.ext import commands, tasks
from discord.utils import get
from pretty_help import DefaultMenu, PrettyHelp

import log
from sharedConsts import CMDPREFIX, HOSTNAME, STARTTIME, SUPEROLE, TOKEN
from sharedDicts import powerTypes
from sharedFuncs import asleep, dupeMes, nON

logP = log.get_logger(__name__)

runBot = True
logP.info(
    f"Bot will attempt to connect to discord on host: {HOSTNAME}, {runBot}"
)


logP.debug(f"Bot start time set as: {STARTTIME}")

cogList = [
    "defaultCommands.py",
    "roleCommands.py",
    "managerCommands.py",
    "ownerCommands.py",
    "ErrorHandler.py",
    "authorCommands.py",
]


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

    strtMes = f"Bot has logged in as {bot.user} on {HOSTNAME}"
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
                f"Bot: {nON(botMember)}, in guild: {guild.name}, "
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
        if message.content.startswith(f"{CMDPREFIX}resume"):
            # wake up the bot if it is asleep
            await bot.process_commands(message)
            return

    if asleep():
        # stop parsing the message if the bot is asleep
        return

    if message.content.startswith(f"{CMDPREFIX}{CMDPREFIX}"):
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
    nameSet = f"{members} users with {len(powerTypes.keys())} " "enhancements"

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name=nameSet
        )
    )
    logP.debug("Rich presence set to: " + nameSet)
    return


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
    brief=getBrief('start'),
    description=getDesc('start')
    )
async def start(self, ctx):
    await ctx.send("To begin use the command 'list'")
    msg = await discord.Client.wait_for('message',
    author=ctx.author,
    content='list')
    await ctx.send("Next step")
    return
    """


# general import protection
if __name__ == "__main__":

    # discord.py cog importing
    for filename in cogList:
        if filename.endswith(".py"):
            logP.debug(f"Loading Cog: {filename}")
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
