import os
import sys
import time
import typing
import discord
from discord.ext import commands
from enhancements import dupeMes
import log
from power import cmdInf
from sharedVars import HOSTNAME, MANAGERROLES, SAVEFILE
from discord.utils import get

logP = log.get_logger(__name__)


class managerCommands(
    commands.Cog,
    name="Manager Commands",
    description=cmdInf["managerCommands"]["Description"],
):
    def __init__(
        self, bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot]
    ):
        self.bot = bot

    # Check if user has guild role
    async def cog_check(self, ctx: commands.Context):
        async def predicate(ctx: commands.Context):
            for role in MANAGERROLES:
                chkRole = get(ctx.guild.roles, name=role)
                if chkRole in ctx.message.author.roles:
                    return chkRole
            raise commands.CheckFailure(
                (
                    "You do not have permission as you are missing a role in "
                    "this list: {}"
                ).format(MANAGERROLES)
            )

        # messy implementation for Supe
        return commands.check(await predicate(ctx))

    @commands.command(
        aliases=["re", "reboot"],
        brief=cmdInf["restart"]["Brief"],
        description=cmdInf["restart"]["Description"],
    )
    async def restart(self, ctx: commands.Context, host: str = HOSTNAME):
        logP.debug("Command restart called for host: {}".format(host))
        if host != HOSTNAME:
            return
        text = "Restarting bot on {}...".format(HOSTNAME)
        await dupeMes(self.bot, ctx, text)
        logP.warning("Bot is now restarting")
        restart_bot()

    @commands.command(
        brief=cmdInf["upload"]["Brief"],
        description=cmdInf["upload"]["Description"],
    )
    async def upload(
        self,
        ctx: commands.Context,
        logg: typing.Optional[int] = 0,
        host: str = HOSTNAME,
    ):
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
        if logg:
            await ctx.send(
                "File {} from {} at: {}".format(
                    SAVEFILE, HOSTNAME, currTimeStr
                ),
                file=discord.File(log.LOG_FILE),
            )
        else:
            await ctx.send(
                "File {} from {}".format(SAVEFILE, HOSTNAME),
                file=discord.File(SAVEFILE, filename=nameStamp),
            )
        logP.debug("command upload completed")


def restart_bot() -> None:
    os.execv(sys.executable, ["python"] + sys.argv)


# function to setup cog
def setup(bot: commands.Bot):
    bot.add_cog(managerCommands(bot))
