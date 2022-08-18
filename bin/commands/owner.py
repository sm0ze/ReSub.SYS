import sys
import typing

import bin.log as log
import discord
import git
from bin.shared.consts import COMMANDS_ON, HOST_NAME
from bin.shared.funcs import asleep, dupeMes, getBrief, getDesc, load, save
from discord.ext import commands

logP = log.get_logger(__name__)


class ownerCommands(
    commands.Cog,
    name="Owner Commands",
    description=getDesc("ownerCommands"),
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
        enabled=COMMANDS_ON,
        brief=getBrief("resetPatrol"),
        description=getDesc("resetPatrol"),
    )
    async def resetPatrol(self, ctx: commands.Context):
        cache_file = load(ctx.guild.id)

        for key in cache_file.keys():
            cache_file[key].pop("currPatrol", None)
            cache_file[key].pop("topStatistics", None)
        save(ctx.guild.id, cache_file)
        await ctx.send("Truncated File.")

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["poop", "pp"],
        brief=getBrief("popPeep"),
        description=getDesc("popPeep"),
    )
    async def popPeep(self, ctx: commands.Context, peep: discord.User):
        cache_file = load(ctx.guild.id)
        if peep.id not in cache_file.keys():
            ctx.send(f"{peep.display_name} is not saved in File.")
            return
        haveRemoved = cache_file.pop(peep.id)
        sendMes = f"Have removed {peep.id}: {haveRemoved}"
        logP.debug(sendMes)
        save(ctx.guild.id, cache_file)
        await ctx.send(sendMes)

    @commands.command(
        brief=getBrief("resume"),
        description=getDesc("resume"),
    )
    async def resume(
        self,
        ctx: commands.Context,
        up: typing.Optional[int] = 0,
        host: str = HOST_NAME,
    ):
        logP.debug(f"Command resume called for host: {host}, to update: {up}")
        if host != HOST_NAME:
            return
        if asleep():
            await dupeMes(self.bot, ctx, f"Bot is now awake on {HOST_NAME}")
            asleep(True)
            logP.info("Bot is now awake")
        if up:
            await ctx.invoke(self.bot.get_command("update"))
            await ctx.invoke(self.bot.get_command("restart"))
        logP.debug("command resume completed")

    @commands.command(
        aliases=["sleep"],
        brief=getBrief("pause"),
        description=getDesc("pause"),
    )
    async def pause(self, ctx: commands.Context, host: str = HOST_NAME):
        logP.debug(f"Command pause called for host: {host}")
        if host != HOST_NAME:
            return
        asleep(True)
        await dupeMes(self.bot, ctx, f"Bot is now asleep on {HOST_NAME}")
        logP.info("Bot is now paused")

    @commands.command(
        aliases=["up"],
        brief=getBrief("update"),
        description=getDesc("update"),
    )
    async def update(self, ctx: commands.Context, host: str = HOST_NAME):
        logP.debug(f"Command update called for host: {host}")
        if host != HOST_NAME:
            return
        text1 = f"Update starting on {HOST_NAME}"
        await dupeMes(self.bot, ctx, text1)
        logP.warning(text1)
        git_dir = "/.git/ReSub.SYS"
        g = git.cmd.Git(git_dir)
        text2 = f"{HOST_NAME}\n{g.pull()}"
        await dupeMes(self.bot, ctx, text2)
        logP.warning(text1)
        logP.info("Command update completed")

    @commands.command(
        brief=getBrief("end"),
        description=getDesc("end"),
    )
    async def end(self, ctx: commands.Context, host: str = HOST_NAME):
        logP.debug(f"Command end called for host: {host}")
        if host != HOST_NAME:
            return
        text = f"Bot on {HOST_NAME} is terminating"
        await dupeMes(self.bot, ctx, text)
        await self.bot.close()
        logP.warning("Bot is now offline and terminating")
        sys.exit()

    @commands.command(
        aliases=["tog"],
        brief=getBrief("toggle"),
        description=getDesc("toggle"),
    )
    async def toggle(self, ctx: commands.Context, mes="t", host=HOST_NAME):
        logP.debug(f"command toggle called for host: {host}")
        if host != HOST_NAME:
            return
        getComm = self.bot.get_command(mes)
        if ctx.command == getComm:
            await dupeMes(self.bot, ctx, "Cannot disable this command.")
        elif getComm:
            getComm.enabled = not getComm.enabled
            ternary = "enabled" if getComm.enabled else "disabled"
            message = f"Command '{getComm.name}' {ternary} on {host}."
            await dupeMes(
                self.bot,
                ctx,
                message,
            )
            logP.info(message)
        else:
            await dupeMes(self.bot, ctx, f"Command '{mes}' was not found.")

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("testAll"),
        description=getDesc("testAll"),
    )
    async def testAll(self, ctx: commands.Context, host: str = HOST_NAME):
        logP.debug(f"command testAll called for host: {host}")
        if host != HOST_NAME:
            return
        host = ""
        logP.info("Command testAll starting")
        for cmd in self.bot.commands:
            mes = f"Testing command **{cmd.name}**."
            await ctx.send(mes)
            logP.debug(mes)
            param = cmd.clean_params
            mes = f"clean params: {param}"
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

    @commands.command(
        brief=getBrief("sync"),
        description=getDesc("sync"),
    )
    async def sync(
        self,
        ctx: commands.Context,
        host: str = HOST_NAME,
        all: bool = False,
    ):
        if host != HOST_NAME:
            return
        tree = self.bot.tree
        if not all and ctx.guild:
            syncList = await tree.sync(guild=ctx.guild)
        else:
            syncList = await tree.sync()
        if not syncList:
            syncList = "None"
        await ctx.send(f"Commands Synced: {syncList}")


# function to setup cog
async def setup(bot: commands.Bot):
    await bot.add_cog(ownerCommands(bot))
