import asyncio
import typing

import bin.log as log
import discord
from bin.shared.consts import HANGMAN_LIVES
from discord.ext import commands
from random_word import RandomWords

logP = log.get_logger(__name__)


async def hangmanGame(
    ctx: commands.Context,
    bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot],
):
    answer = RandomWords().get_random_word(minLength=5, maxLength=10)
    leftToGuess = list(answer)
    toRemove = [
        x for x in leftToGuess if x not in "abcdefghijklmnopqrstuvwxyz"
    ]
    for char in toRemove:
        while char in leftToGuess:
            leftToGuess.remove(char)
    guesses = []
    countDown = HANGMAN_LIVES

    # create the game embed to send
    gameEmbed = discord.Embed(
        title="Hangman",
        description=hangmanRender(
            countDown, leftToGuess, ini=True, ans=answer
        ),
    )

    gameView = hangmanView()

    def check(interaction: discord.Interaction):
        return (
            interaction.user.id == ctx.author.id
            and interaction.message.id == sentMes.id
        )

    sentMes = await ctx.send(embed=gameEmbed, view=gameView)
    while not gameView.is_finished():
        await sentMes.edit(embed=gameEmbed, view=gameView)
        try:
            interaction: discord.Interaction = await bot.wait_for(
                "interaction", check=check
            )
            move = interaction.data.get("values", None)
            if not move:
                intId = interaction.data.get("custom_id", "None")
                if intId == "HangManExit":
                    await hangmanEnd(
                        answer, leftToGuess, countDown, sentMes, "QUIT"
                    )
                    return
            else:
                move = move[0]
            (
                gameEmbed.description,
                countDown,
                gameView,
                guesses,
            ) = hangmanRender(
                countDown,
                leftToGuess,
                ans=answer,
                guess=move,
                guessList=guesses,
            )
        except asyncio.TimeoutError:
            (
                gameEmbed.description,
                countDown,
            ) = hangmanRender(countDown, leftToGuess, ans=answer)
        if not leftToGuess:
            await hangmanEnd(answer, leftToGuess, countDown, sentMes, "WON")
            return
        if countDown == 0:
            await hangmanEnd(answer, leftToGuess, countDown, sentMes, "LOST")
            return


async def hangmanEnd(
    answer, leftToGuess, countDown, sentMes: discord.Message, endCon
):
    return await sentMes.edit(
        embed=discord.Embed(
            title="Hangman",
            description=hangmanEndMes(answer, leftToGuess, countDown, endCon),
        ),
        view=None,
    )


def hangmanEndMes(answer, leftToGuess, countDown, endCon):
    retMes = (
        f"Game {endCon} at {countDown} lives left.\n"
        f"Correct answer was ***{answer}***.\n"
        f"You guessed: {soFarGuessed(leftToGuess,answer,False)}"
    )
    if endCon == "WON":
        retMes += "Well done!"
    elif endCon == "LOST":
        retMes += "Better luck next time!"
    return retMes


def hangmanView(guessList: list = None):
    # create a list of discord.ui.select.options for the letters a to z
    consonantList = "bcdfghjklmnpqrstvwxyz"
    vowelList = "aeiou"
    exitButton = discord.ui.Button(
        label="Exit",
        custom_id="HangManExit",
        style=discord.ButtonStyle.red,
    )
    consonantOptions = []
    vowelOptions = []
    if not guessList:
        guessList = []
    for char in [x for x in consonantList if x not in guessList]:
        consonantOptions.append(discord.SelectOption(label=char))
    for char in [x for x in vowelList if x not in guessList]:
        vowelOptions.append(discord.SelectOption(label=char))

    # create discord view for interactions
    gameView = discord.ui.View()
    if consonantOptions:
        gameView.add_item(
            discord.ui.Select(
                custom_id="hangmanConsonants",
                options=consonantOptions,
                placeholder="Consonants",
            )
        )
    if vowelOptions:
        gameView.add_item(
            discord.ui.Select(
                custom_id="hangmanVowels",
                options=vowelOptions,
                placeholder="Vowels",
            )
        )
    gameView.add_item(exitButton)

    return gameView


def hangmanRender(
    countDown: int,
    leftToGuess: list,
    guess: str = None,
    ini: bool = False,
    ans: str = None,
    guessList: list = None,
):
    if ini:
        guessStr = genGuessStr(leftToGuess, ans, guessList, countDown)
        return f"Chances left: {countDown}\n{guessStr}"

    if guess is None:
        countDown -= 1
        guessStr = genGuessStr(leftToGuess, ans, guessList, countDown)
        return f"Chances left: {countDown}\n{guessStr}", countDown

    else:
        guessList.append(guess)
        if guess in leftToGuess:
            while guess in leftToGuess:
                leftToGuess.remove(guess)
        else:
            countDown -= 1
        guessStr = genGuessStr(leftToGuess, ans, guessList, countDown)
        return (
            f"Chances left: {countDown}\n{guessStr}",
            countDown,
            hangmanView(guessList),
            guessList,
        )


def genGuessStr(leftToGuess: list, ans: str, guesses: list, livesLeft: int):
    retString = soFarGuessed(leftToGuess, ans)
    if not guesses:
        guesses = []
    retString += f"Guesses: {' '.join(guesses)}\n\n"
    retString += genHangman(livesLeft)
    retString += "```"
    return retString


def soFarGuessed(leftToGuess, ans, strStart=True):
    retString = ""
    if strStart:
        retString += "```\n"
    if not ans:
        ans = []
    for char in ans:
        if char in leftToGuess:
            retString += "_ "
        else:
            retString += f"{char} "
    retString = retString.strip() + "\n"
    return retString


def genHangman(livesLeft: int):
    hangman = ""
    if livesLeft == 0:
        hangman += " ________\n"
        hangman += "|        |\n"
        hangman += "|        O\n"
        hangman += "|       /|\\\n"
        hangman += "|       / \\\n"
        hangman += "|\\\n"
    elif livesLeft == 1:
        hangman += " ________\n"
        hangman += "|        |\n"
        hangman += "|        O\n"
        hangman += "|       /|\\\n"
        hangman += "|       / \n"
        hangman += "|\\\n"
    elif livesLeft == 2:
        hangman += " ________\n"
        hangman += "|        |\n"
        hangman += "|        O\n"
        hangman += "|       /|\\\n"
        hangman += "|\n"
        hangman += "|\\\n"
    elif livesLeft == 3:
        hangman += " ________\n"
        hangman += "|        |\n"
        hangman += "|        O\n"
        hangman += "|       /|\n"
        hangman += "|\n"
        hangman += "|\\\n"
    elif livesLeft == 4:
        hangman += " ________\n"
        hangman += "|        |\n"
        hangman += "|        O\n"
        hangman += "|       /\n"
        hangman += "|\n"
        hangman += "|\\\n"
    elif livesLeft == 5:
        hangman += " ________\n"
        hangman += "|        |\n"
        hangman += "|        O\n"
        hangman += "|\n"
        hangman += "|\n"
        hangman += "|\\\n"
    elif livesLeft == 6:
        hangman += " ________\n"
        hangman += "|        |\n"
        hangman += "|\n"
        hangman += "|\n"
        hangman += "|\n"
        hangman += "|\\\n"
    elif livesLeft == 7:
        hangman += " _\n"
        hangman += "|\n"
        hangman += "|\n"
        hangman += "|\n"
        hangman += "|\n"
        hangman += "|\\\n"
    elif livesLeft == 8:
        hangman += "\n"
        hangman += "\n"
        hangman += "|\n"
        hangman += "|\n"
        hangman += "|\n"
        hangman += "|\\\n"
    elif livesLeft == 9:
        hangman += "\n"
        hangman += "\n"
        hangman += "\n"
        hangman += "\n"
        hangman += "|\n"
        hangman += "|\\\n"
    else:
        hangman += "\n"
        hangman += "\n"
        hangman += "\n"
        hangman += "\n"
        hangman += "\n"
        hangman += "|\n"
    return hangman
