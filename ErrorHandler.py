import discord
from discord.ext import commands

from BossSystemExecutable import debug


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

        elif isinstance(error, KeyError):
            mes = discord.Embed(
                title="KeyError",
                description="{} is not a recognised option".format(
                    KeyError.args
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
        await ctx.message.delete(delay=4)
        print(mes.to_dict())


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
