import discord
from discord.ext import commands

from BossSystemExecutable import ERRORTHREAD
from enhancements import dupeError, getSendLoc
from exceptions import notSupeDuel


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

        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.DisabledCommand):
            return

        elif isinstance(error, KeyError):
            mes = discord.Embed(
                title="KeyError",
                description="{} is not a recognised option".format(
                    KeyError.args
                ),
            )
        elif isinstance(error, commands.CommandOnCooldown):
            cdTime = round(error.retry_after, 2)
            if command == "task":
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
                        "Command on cooldown for" "{} minutes or {} seconds"
                    ).format(round(cdTime / 60, 2), cdTime),
                )
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.__cause__, notSupeDuel):
                mes = discord.Embed(
                    title="Civilian", description="You can't fight a civilian!"
                )

        if not mes:
            mes = discord.Embed(title="Error!!!", description=error)
        await ctx.send(embed=mes, delete_after=5)
        await ctx.message.delete(delay=4)
        print(mes.to_dict())
        await dupeError(mes, ctx, ERTHRD)


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
