import os

import discord
from discord.ext import commands

DEBUG = 0
TEST = 0


def debug(*args):
    if DEBUG:
        print(*args)


debug("{} DEBUG TRUE".format(os.path.basename(__file__)))
if TEST:
    print("{} TEST TRUE".format(os.path.basename(__file__)))


class ErrorHandler(commands.Cog):
    """A cog for global error handling."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """A global error handler cog."""
        localHandlers = ["task"]

        # for messy handling without isinstance()
        splitError = str(error).split()
        command = ctx.command

        debug(
            "{} in {}".format(command, localHandlers),
            str(command) in localHandlers,
        )
        if str(command) in localHandlers:
            return

        if isinstance(error, commands.CommandNotFound):
            return
            mes = discord.Embed(
                title="Error!!!",
                description="Command not found.",
                color=ctx.author.color,
            )

        elif splitError[4] == "KeyError:":
            mes = discord.Embed(
                title=splitError[4],
                description="{} is not a recognised option".format(
                    splitError[-1]
                ),
            )
        elif isinstance(error, commands.CommandOnCooldown):
            cdTime = round(error.retry_after, 2)
            mes = discord.Embed(
                title="Error!!!",
                description=(
                    "Command on cooldown for" "{} minutes or {} seconds"
                ).format(round(cdTime / 60, 2), cdTime),
            )

        else:  # just send the error to discord
            mes = discord.Embed(title="Error!!!", description=error)
        await ctx.send(embed=mes, delete_after=5)
        await ctx.message.delete(delay=5)
        print(mes.to_dict())


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
