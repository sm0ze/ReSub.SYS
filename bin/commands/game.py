import asyncio
import typing

import bin.log as log
from bin.minigame.bullsAndCows import bacGame
from bin.minigame.hangman import hangmanGame
from bin.shared.consts import COMMANDS_ON
from bin.shared.funcs import getBrief, getDesc
from discord.ext import commands

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


# function to setup cog
async def setup(bot: commands.Bot):
    await bot.add_cog(gameCommands(bot))
