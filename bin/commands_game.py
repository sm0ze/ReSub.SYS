import asyncio
import typing

from discord.ext import commands
from bin.game_bullsAndCows import bacGame
from bin.game_wordBullsAndCows import wbacGame

import bin.log as log
from bin.game_hangman import hangmanGame
from bin.shared_consts import COMMANDS_ON
from bin.shared_funcs import getBrief, getDesc

logP = log.get_logger(__name__)


class gameCommands(
    commands.Cog,
    name="Game Commands",
    description=getDesc("gameCommands"),
):
    def __init__(
        self, bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot]
    ):
        self.bot = bot

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["hman"],
        brief=getBrief("hangman"),
        description=getDesc("hangman"),
    )
    async def hangman(self, ctx: commands.Context):
        asyncio.create_task(hangmanGame(ctx, self.bot))

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["bac"],
        brief=getBrief("bullsAndCows"),
        description=getDesc("bullsAndCows"),
    )
    async def bullsAndCows(
        self,
        ctx: commands.Context,
    ):
        asyncio.create_task(bacGame(ctx, self.bot))

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["wbac"],
        brief=getBrief("wordBullsAndCows"),
        description=getDesc("wordBullsAndCows"),
    )
    async def wordBullsAndCows(
        self,
        ctx: commands.Context,
    ):
        asyncio.create_task(wbacGame(ctx, self.bot))


# function to setup cog
def setup(bot: commands.Bot):
    bot.add_cog(gameCommands(bot))
