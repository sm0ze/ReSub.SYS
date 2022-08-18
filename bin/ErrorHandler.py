# ErrorHandler.py

import datetime

import discord
from discord.ext import commands

from bin.exceptions import notNPC, notSupeDuel
from bin.shared.consts import CMD_PREFIX, ERROR_THREAD
from bin.shared.funcs import dupeError, getSendLoc


class ErrorHandler(commands.Cog):
    """A cog for global error handling."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global ERTHRD
        ERTHRD = await getSendLoc(ERROR_THREAD, self.bot, "thread")

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
            delaySet = 0
            mes = discord.Embed(
                title="KeyError",
                description=(
                    f"{error.__cause__.args[0]} is not a recognised option"
                ),
            )
        elif isinstance(error, commands.CommandOnCooldown):
            dupeEr = False
            cdTimeStr = str(datetime.timedelta(seconds=int(error.retry_after)))

            if str(command) == "task":
                mes = discord.Embed(
                    title="No Tasks",
                    description=(
                        "You have no available tasks at this time. "
                        f"Please search again in {cdTimeStr}."
                    ),
                )
            else:
                mes = discord.Embed(
                    title="Error!!!",
                    description=(
                        f"Command: {str(command)}, on cooldown for "
                        f"{cdTimeStr}."
                    ),
                )
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.__cause__, notSupeDuel):
                dupeEr = False
                mes = discord.Embed(
                    title="Civilian", description="You can't fight a civilian!"
                )
            if isinstance(error.__cause__, notNPC):
                dupeEr = False
                mes = discord.Embed(
                    title="Non Player Character",
                    description=error.__cause__.args[0],
                )

        elif isinstance(error, commands.CheckFailure):
            dupeEr = False
            mes = discord.Embed(
                title="Role Check Error!!!",
                description=error,
            )
        elif isinstance(error, commands.UserInputError):
            dupeEr = False
            delaySet = 20
            mes = discord.Embed(
                title="Incorrect Input",
                description=(
                    f"""The following error was produced:
                    {error.args[0]}

                    Expected:
                    {CMD_PREFIX}{str(command)} {command.signature}"""
                ),
            )

        if not mes:
            delaySet = 0
            mes = discord.Embed(
                title=f"{str(command)} Error!!!",
                description=(
                    f"Error of type: {type(error)},\n"
                    f"{error.__cause__}\n"
                    f"{error}"
                ),
            )

        if delaySet:
            await ctx.send(embed=mes, delete_after=delaySet)
            await ctx.message.delete(delay=delaySet)
        else:
            await ctx.send(embed=mes)

        if dupeEr:
            await dupeError(mes, ctx, ERTHRD)


async def setup(bot: commands.Bot):
    await bot.add_cog(ErrorHandler(bot))
