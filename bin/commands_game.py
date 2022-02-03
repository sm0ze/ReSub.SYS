import asyncio
import random
import typing

import discord
from discord.ext import commands

import bin.log as log
from bin.shared_consts import COMMANDS_ON, MAX_BAC_ROUNDS
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
        aliases=["bac"],
        brief=getBrief("bullsAndCows"),
        description=getDesc("bullsAndCows"),
    )
    async def bullsAndCows(
        self,
        ctx: commands.Context,  # *, memberList: str = ""
    ):
        # users = await memGrab(ctx, memberList)

        digitList = "0123456789"
        emojiList = [
            "0️⃣",
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
            "8️⃣",
            "9️⃣",
        ]
        numToGuess = random.choices(digitList, k=5)
        currRound = MAX_BAC_ROUNDS

        gameView = self.gameViewButtons(emojiList)
        gameEmbed = discord.Embed(
            title="Bulls and Cows (5 Digits)",
            description=self.roundText(currRound),
        )
        gameEmbed.add_field(
            name="Previous Guesses",
            value="[]",
        )
        gameEmbed.add_field(
            name="Current Guess",
            value="[]",
        )

        gameMes = await ctx.send(embed=gameEmbed)

        def check(interaction: discord.Interaction):
            return interaction.user.id == ctx.author.id

        prevGuesses: list[tuple[tuple[int, int], list[int]]] = []
        while currRound > 0:
            guessedNum: list[int] = []
            await gameMes.edit(embed=gameEmbed, view=gameView)

            while not gameView.is_finished():
                try:
                    interaction: discord.Interaction = await self.bot.wait_for(
                        "interaction",
                        check=check,
                    )
                    press = interaction.data["custom_id"]
                    if str(press) in digitList:
                        guessedNum.append(str(press))
                    elif str(press) == "b":
                        if guessedNum:
                            guessedNum.pop()
                    elif str(press) == "x":
                        guessedNum = [-1] * len(numToGuess)
                    gameEmbed.set_field_at(
                        index=1,
                        name="Current Guess",
                        value=guessedNum,
                    )
                    await gameMes.edit(embed=gameEmbed)

                    if len(guessedNum) == len(numToGuess):
                        gameView.stop()
                        await gameMes.edit(view=None)

                except asyncio.TimeoutError:
                    gameView.stop()
                    await gameMes.edit(view=None)
            if guessedNum == [-1] * len(numToGuess):
                await self.bacExitFail(numToGuess, gameEmbed, gameMes)
                break
            gameView = self.gameViewButtons(emojiList)
            currRound -= 1
            gameEmbed.description = self.roundText(currRound)
            gameEmbed.set_field_at(
                index=1,
                name="Current Guess",
                value="[]",
            )
            prevGuesses.append(
                ((self.countBAC(numToGuess, guessedNum)), guessedNum)
            )
            prevGuessStr = ""
            for hit, guess in prevGuesses:
                prevGuessStr += f"B{hit[0]} C{hit[1]}: {guess}\n"
            gameEmbed.set_field_at(
                index=0,
                name="Previous Guesses",
                value=f"{prevGuessStr}",
            )
            if prevGuesses[-1][0][0] == len(numToGuess):
                gameEmbed.set_field_at(
                    index=1,
                    name="Correct Guess",
                    value=guessedNum,
                )
                await gameMes.edit(embed=gameEmbed, view=None)
                currRound = 0
            elif not currRound > 0:
                await self.bacExitFail(numToGuess, gameEmbed, gameMes)

    async def bacExitFail(
        self,
        numToGuess: list,
        gameEmbed: discord.Embed,
        gameMes: discord.Message,
    ):
        gameEmbed.set_field_at(
            index=1,
            name="Correct Guess",
            value=f"Not Guessed:\n{numToGuess}",
        )
        await gameMes.edit(embed=gameEmbed, view=None)

    def roundText(self, currRound):
        roundText = (
            "Number has been chosen, make your guess.\n"
            f"Round {MAX_BAC_ROUNDS-currRound}/{MAX_BAC_ROUNDS}"
        )
        return roundText

    def gameViewButtons(self, emojiList: list):
        gameView = discord.ui.View()
        for count, numEmoji in enumerate(emojiList):
            gameView.add_item(
                discord.ui.Button(
                    emoji=numEmoji,
                    style=discord.ButtonStyle.blurple,
                    custom_id=str(count),
                )
            )
        gameView.add_item(
            discord.ui.Button(
                label="Backspace",
                style=discord.ButtonStyle.grey,
                custom_id="b",
            )
        )
        gameView.add_item(
            discord.ui.Button(
                label="Give Up",
                style=discord.ButtonStyle.red,
                custom_id="x",
            )
        )
        return gameView

    def countBAC(self, answer: list[int], guess: list[int]):
        bulls = 0
        cows = 0
        possibleCow = answer.copy()
        indexToCheck = list(range(len(answer)))
        for count in range(len(answer)):
            if answer[count] == guess[count]:
                bulls += 1
                possibleCow.remove(guess[count])
                indexToCheck.remove(count)

        for count in indexToCheck:
            if guess[count] in possibleCow:
                cows += 1
                possibleCow.remove(guess[count])

        return bulls, cows


# function to setup cog
def setup(bot: commands.Bot):
    bot.add_cog(gameCommands(bot))
