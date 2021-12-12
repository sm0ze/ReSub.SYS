# ErrorHandler.py

import discord
from discord.ext import commands

from enhancements import dupeError, getSendLoc
from exceptions import notSupeDuel
from sharedVars import ERRORTHREAD


class ErrorHandler(commands.Cog):
    """A cog for global error handling."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global ERTHRD
        ERTHRD = await getSendLoc(ERRORTHREAD, self.bot, "thread")

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """A global error handler cog."""

        # for messy handling without isinstance()
        command = ctx.command
        mes = None
        delaySet = 5
        dupeEr = True

        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.DisabledCommand):
            return

        elif isinstance(error.__cause__, KeyError):
            dupeEr = False
            mes = discord.Embed(
                title="KeyError",
                description="{} is not a recognised option".format(
                    error.__cause__.args
                ),
            )
        elif isinstance(error, commands.CommandOnCooldown):
            dupeEr = False
            cdTime = round(error.retry_after, 2)
            if str(command) == "task":
                mes = discord.Embed(
                    title="No Tasks",
                    description=(
                        "You have no available tasks at this time. "
                        "Please search again in {} minutes or {} seconds."
                    ).format(round(cdTime / 60, 2), cdTime),
                )
            else:
                mes = discord.Embed(
                    title="Error!!!",
                    description=(
                        "Command: {}, on cooldown for {} minutes or {} seconds"
                    ).format(str(command), round(cdTime / 60, 2), cdTime),
                )
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.__cause__, notSupeDuel):
                dupeEr = False
                mes = discord.Embed(
                    title="Civilian", description="You can't fight a civilian!"
                )

        if not mes:
            delaySet = 0
            mes = discord.Embed(
                title="{} Error!!!".format(str(command)), description=error
            )

        if delaySet:
            await ctx.send(embed=mes, delete_after=delaySet)
            await ctx.message.delete(delay=delaySet)
        else:
            await ctx.send(embed=mes)

        if dupeEr:
            await dupeError(mes, ctx, ERTHRD)


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
