import asyncio
import datetime
import math
import time
import typing

import bin.log as log
import discord
from bin.shared.consts import CMD_PREFIX, COMMANDS_ON, HOST_NAME, START_TIME
from bin.shared.dicts import freeRoles, tutDict
from bin.shared.funcs import (
    getBrief,
    getDesc,
    histUptime,
    load,
    save,
    saveTime,
    sendMessage,
)
from discord.ext import commands, tasks
from discord.utils import get

logP = log.get_logger(__name__)


global loginTime
loginTime = time.time()

logP.debug(f"Bot last login time set as: {loginTime}")


class defaultCommands(
    commands.Cog,
    name="Default Commands",
    description=getDesc("defaultCommands"),
):
    def __init__(
        self, bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot]
    ):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global loginTime
        loginTime = time.time()

        self.online_time.start()

        logP.debug(f"Bot last login time set as: {loginTime}")

    @tasks.loop(minutes=1)
    async def online_time(self):
        currTime = time.time()
        if self.bot.ws:
            saveTime(currTime)
            logP.debug(f"Saved uptime ping to file at: {currTime}")
        else:
            logP.debug(f"websocket down at: {currTime}")

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["tut"],
        brief=getBrief("tutorial"),
        description=getDesc("tutorial"),
    )
    async def tutorial(self, ctx: commands.Context, res: int = 0):
        memDict = load(ctx.guild.id)
        defTut = sorted(list(tutDict.keys()))
        memDict.setdefault(ctx.author.id, {"Name": ctx.author.name})
        memDict[ctx.author.id].setdefault("tut", defTut.copy())
        if res == 1:
            memDict[ctx.author.id]["tut"] = defTut.copy()
        elif res == -1:
            memDict[ctx.author.id]["tut"] = []
        if not memDict[ctx.author.id]["tut"]:
            await ctx.send("Tutorial Complete")
            save(ctx.guild.id, memDict)
            return
        retEmb = discord.Embed(
            title=f"Step {memDict[ctx.author.id]['tut'][0]} of {len(defTut)}."
        )

        step: dict[str] = tutDict[memDict[ctx.author.id]["tut"][0]]
        mes = f"{CMD_PREFIX}{step.get('cmd', 'N/A')} {step.get('arg', '')}"
        retEmb.add_field(name="Command", value=mes)
        retEmb.add_field(name="Explanation", value=step.get("txt", "N/A"))
        await sendMessage(ctx, retEmb)
        memDict[ctx.author.id]["tut"] = memDict[ctx.author.id]["tut"][1:]
        save(ctx.guild.id, memDict)

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("emoji"),
        description=getDesc("emoji"),
    )
    async def emoji(self, ctx: commands.Context, idTry=""):
        if idTry:
            emo = await fetchEmoji(ctx, idTry)
            if emo:
                await ctx.send(emo)
            else:
                await ctx.send(f"Could not find emoji '{idTry}'")
        else:
            emo = [str(m) for m in self.bot.emojis]
            per_page = 10  # 10 members per page
            pages = math.ceil(len(emo) / per_page)
            cur_page = 1
            chunk = emo[:per_page]
            linebreak = "\n"
            message = await ctx.send(
                f"Page {cur_page}/{pages}:\n{linebreak.join(chunk)}"
            )
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")
            active = True

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [
                    "◀️",
                    "▶️",
                ]
                # or you can use unicodes, respectively: "\u25c0" or "\u25b6"

            while active:
                try:
                    reaction, user = await self.bot.wait_for(
                        "reaction_add", timeout=60, check=check
                    )

                    if str(reaction.emoji) == "▶️" and cur_page != pages:
                        cur_page += 1
                        if cur_page != pages:
                            num = (cur_page - 1) * per_page
                            num2 = cur_page * per_page
                            chunk = emo[num:num2]
                        else:
                            num = (cur_page - 1) * per_page
                            chunk = emo[num:]
                        await message.edit(
                            content=(
                                f"Page {cur_page}/{pages}:\n"
                                f"{linebreak.join(chunk)}"
                            )
                        )
                        await message.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "◀️" and cur_page > 1:
                        cur_page -= 1
                        num = (cur_page - 1) * per_page
                        num2 = cur_page * per_page

                        chunk = emo[num:num2]
                        await message.edit(
                            content=(
                                f"Page {cur_page}/{pages}:\n"
                                f"{linebreak.join(chunk)}"
                            )
                        )
                        await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    await message.delete()
                    active = False

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("about"),
        description=getDesc("about"),
    )
    async def about(self, ctx: commands.Context):
        desc = (
            "This initially started as a way to automatically assign roles "
            "for Geminel#1890's novel. At the time Admins were manually "
            "calculating enhancement points and adding roles."
        )
        mes = discord.Embed(title=f"About {self.bot.user.display_name}")
        mes.set_author(
            name="Creator: sm0ze#3542",
            icon_url="https://avatars.githubusercontent.com/u/31851788",
        )
        mes.add_field(
            inline=False, name="Why does this bot exist?", value=desc
        )
        mes.add_field(
            inline=False,
            name="What can the bot do?",
            value=(
                "Now the bot is capable enough to allow users to gain bot "
                "specific experience, level up their GDV and gain system "
                "enhancements through the use of commands."
            ),
        )
        mes.add_field(
            inline=False,
            name="More Info",
            value=(
                "You can find the code "
                "[here](https://github.com/sm0ze/ReSub.SYS)"
            ),
        )
        mes.set_footer(
            text=(
                f"{self.bot.user.display_name} is currently "
                f"running on {HOST_NAME}."
            )
        )
        mes.set_thumbnail(url=self.bot.user.display_avatar)
        await ctx.send(embed=mes)

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("run"),
        description=getDesc("run"),
    )
    async def run(self, ctx: commands.Context):
        await ctx.send(f"Bot is running on {HOST_NAME}")

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["r", "roles"],
        brief=getBrief("role"),
        description=getDesc("role"),
    )
    # gives requested role to command caller if it is in freeRoles
    async def role(
        self, ctx: commands.Context, *, roleToAdd: str = freeRoles[0]
    ):
        member = ctx.author
        sendMes = ""
        logP.debug(
            (
                f"Trying to toggle the role: {roleToAdd}, "
                f"for: {member.display_name}"
            )
        )
        roleAdd = get(member.guild.roles, name=roleToAdd)
        if not roleAdd:
            sendMes = f"'{roleToAdd}' is not a valid role."
        elif roleAdd.name not in freeRoles:
            sendMes = "That is not a role you can add with this command!"
        elif roleAdd not in member.roles:
            await member.add_roles(roleAdd)
            sendMes = (
                f"{member.display_name} is granted the role: '{roleAdd}'!"
            )
        else:
            await member.remove_roles(roleAdd)
            sendMes = (
                f"{member.display_name} no longer has the role: '{roleAdd}'!"
            )
        await ctx.send(sendMes)
        logP.debug("command role resolution: " + sendMes)

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["uh", "hist"],
        brief=getBrief("uptimeHistory"),
        description=getDesc("uptimeHistory"),
    )
    async def uptimeHistory(self, ctx: commands.Context, squares: int = 100):
        mes = histUptime(squares)
        await sendMessage(ctx, mes)

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["u"],
        brief=getBrief("uptime"),
        description=getDesc("uptime"),
    )
    async def uptime(self, ctx: commands.Context):
        logP.debug("command uptime called")
        uptimeLogin = str(
            datetime.timedelta(seconds=int(round(time.time() - loginTime)))
        )
        uptimeStartup = str(
            datetime.timedelta(seconds=int(round(time.time() - START_TIME)))
        )
        mes = discord.Embed(title="Uptime")
        mes.add_field(name=uptimeLogin, value="Time since last login.")
        mes.add_field(name=uptimeStartup, value="Time since bot startup.")
        mes.set_footer(
            text=(
                f"{self.bot.user.display_name} is "
                f"currently running on {HOST_NAME}."
            )
        )
        mes.set_thumbnail(url=self.bot.user.display_avatar)
        await ctx.send(embed=mes)
        logP.debug(
            (
                f"Bot has been logged in for: {uptimeLogin}, "
                f"and powered up for: {uptimeStartup}"
            )
        )
        logP.debug("command uptime completed")


async def fetchEmoji(ctx: commands.Context, emojiStr):
    foundEmoji = None
    convertEmoji = await commands.EmojiConverter().convert(
        ctx=ctx, argument=emojiStr
    )
    if convertEmoji:
        foundEmoji = convertEmoji
    return foundEmoji


# function to setup cog
def setup(bot: commands.Bot):
    bot.add_cog(defaultCommands(bot))
