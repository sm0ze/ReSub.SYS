# authorCommands.py
import typing

import discord
from discord.ext import commands

import log
from sharedConsts import COMON, GEMDIFF, setGemDiff
from sharedFuncs import getBrief, getDesc, sendMessage

logP = log.get_logger(__name__)


class authorCommands(
    commands.Cog,
    name="Author Commands",
    description=getDesc("authorCommands"),
):
    def __init__(
        self, bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot]
    ):
        self.bot = bot

    # Check if user has guild role
    async def cog_check(self, ctx: commands.Context):
        async def predicate(ctx: commands.Context):
            passCheck = True
            if int(ctx.message.author.id) not in [
                213090220147605506,
                277041901776142337,
            ]:
                mes = discord.Embed(title="You have no power here.")
                mes.set_image(
                    url=(
                        "https://www.greatmanagers.com.au/wp-content/"
                        "uploads/2018/03/talktohand_trans.png"
                    )
                )
                await sendMessage(mes, ctx)
                passCheck = False
            return passCheck

        # messy implementation for Supe
        return commands.check(await predicate(ctx))

    @commands.command(
        enabled=COMON,
        brief=getBrief("diffGem"),
        description=getDesc("diffGem"),
    )
    async def diffGem(
        self, ctx: commands.Context, var: float = float(GEMDIFF)
    ):
        if var < 0.0:
            var = 0.0
        if var > 1.0:
            var = 1.0
        GEMDIFF = var
        setGemDiff(var)

        await sendMessage(
            f"Gem diff is now {GEMDIFF} times total XP or {100 * GEMDIFF}%",
            ctx,
        )


# function to setup cog
def setup(bot: commands.Bot):
    bot.add_cog(authorCommands(bot))
