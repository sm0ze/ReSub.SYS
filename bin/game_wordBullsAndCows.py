import typing

from discord.ext import commands
from random_word import RandomWords

import bin.log as log

logP = log.get_logger(__name__)


async def wbacGame(
    ctx: commands.Context,
    bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot],
):
    answerFound = False
    while not answerFound:
        answer: str = RandomWords().get_random_word(
            minLength=5,
            maxLength=5,
        )
        notABC = [
            x for x in answer.lower() if x not in "abcdefghijklmnopqrstuvwxyz"
        ]
        if not notABC:
            answerFound = True
