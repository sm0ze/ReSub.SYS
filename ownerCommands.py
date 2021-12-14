import sys
import typing
from discord.ext import commands
import git
from sharedFuncs import dupeMes
import log
from power import cmdInf
from sharedVars import HOSTNAME

logP = log.get_logger(__name__)


class ownerCommands(
    commands.Cog,
    name="Owner Commands",
    description=cmdInf["ownerCommands"]["Description"],
):
    def __init__(
        self, bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot]
    ):
        self.bot = bot

    # Check if user has guild role
    async def cog_check(self, ctx: commands.Context):
        async def predicate(ctx: commands.Context):
            ownerCheck = await self.bot.is_owner(ctx.author)
            return ownerCheck

        # messy implementation for Supe
        return commands.check(await predicate(ctx))

    @commands.command(
        brief=cmdInf["resume"]["Brief"],
        description=cmdInf["resume"]["Description"],
    )
    async def resume(
        self,
        ctx: commands.Context,
        up: typing.Optional[int] = 0,
        host: str = HOSTNAME,
    ):
        global asleep
        logP.debug(
            "Command resume called for host: {}, to update: {}".format(
                host, up
            )
        )
        if host != HOSTNAME:
            return
        if asleep:
            await dupeMes(
                self.bot, ctx, "Bot is now awake on {}".format(HOSTNAME)
            )
            asleep = False
            logP.info("Bot is now awake")
        if up:
            await ctx.invoke(self.bot.get_command("update"))
            await ctx.invoke(self.bot.get_command("restart"))
        logP.debug("command resume completed")

    @commands.command(
        aliases=["sleep"],
        brief=cmdInf["pause"]["Brief"],
        description=cmdInf["pause"]["Description"],
    )
    async def pause(self, ctx: commands.Context, host: str = HOSTNAME):
        logP.debug("Command pause called for host: {}".format(host))
        if host != HOSTNAME:
            return
        global asleep
        asleep = True
        await dupeMes(
            self.bot, ctx, "Bot is now asleep on {}".format(HOSTNAME)
        )
        logP.info("Bot is now paused")

    @commands.command(
        aliases=["up"],
        brief=cmdInf["update"]["Brief"],
        description=cmdInf["update"]["Description"],
    )
    async def update(self, ctx: commands.Context, host: str = HOSTNAME):
        logP.debug("Command update called for host: {}".format(host))
        if host != HOSTNAME:
            return
        text1 = "Update starting on {}".format(HOSTNAME)
        await dupeMes(self.bot, ctx, text1)
        logP.warning(text1)
        git_dir = "/.git/ReSub.SYS"
        g = git.cmd.Git(git_dir)
        text2 = "{}\n{}".format(HOSTNAME, g.pull())
        await dupeMes(self.bot, ctx, text2)
        logP.warning(text1)
        logP.info("Command update completed")

    @commands.command(
        brief=cmdInf["end"]["Brief"],
        description=cmdInf["end"]["Description"],
    )
    async def end(self, ctx: commands.Context, host: str = HOSTNAME):
        logP.debug("Command end called for host: {}".format(host))
        if host != HOSTNAME:
            return
        text = "Bot on {} is terminating".format(HOSTNAME)
        await dupeMes(self.bot, ctx, text)
        await self.bot.close()
        logP.warning("Bot is now offline and terminating")
        sys.exit()

    @commands.command(
        aliases=["tog"],
        brief=cmdInf["toggle"]["Brief"],
        description=cmdInf["toggle"]["Description"],
    )
    async def toggle(self, ctx: commands.Context, mes="t", host=HOSTNAME):
        logP.debug("command toggle called for host: {}".format(host))
        if host != HOSTNAME:
            return
        getComm = self.bot.get_command(mes)
        if ctx.command == getComm:
            await dupeMes(self.bot, ctx, "Cannot disable this command.")
        elif getComm:
            getComm.enabled = not getComm.enabled
            ternary = "enabled" if getComm.enabled else "disabled"
            message = "Command '{}' {} on {}.".format(
                getComm.name, ternary, host
            )
            await dupeMes(
                self.bot,
                ctx,
                message,
            )
            logP.info(message)
        else:
            await dupeMes(
                self.bot, ctx, "Command '{}' was not found.".format(mes)
            )

    @commands.command(
        brief=cmdInf["testAll"]["Brief"],
        description=cmdInf["testAll"]["Description"],
    )
    async def testAll(self, ctx: commands.Context, host: str = HOSTNAME):
        logP.debug("command testAll called for host: {}".format(host))
        if host != HOSTNAME:
            return
        host = ""
        logP.info("Command testAll starting")
        for cmd in self.bot.commands:
            mes = "Testing command **{}**.".format(cmd.name)
            await ctx.send(mes)
            logP.debug(mes)
            param = cmd.clean_params
            mes = "clean params: {}".format(param)
            await ctx.send(mes)
            logP.debug(mes)
            if "host" in param.keys():
                mes = "Skipping command"
                logP.debug(mes)
                await ctx.send(mes)
                continue
            if cmd.name in ["help"]:
                mes = "Skipping command"
                logP.debug(mes)
                await ctx.send(mes)
                continue
            if cmd.can_run:
                mess = "Running command"
                logP.debug(mess)
                await ctx.send(mess)
                await cmd.__call__(ctx)
        await ctx.send("Testing Done")
        logP.info("Command testAll finished")


# function to setup cog
def setup(bot: commands.Bot):
    bot.add_cog(ownerCommands(bot))
