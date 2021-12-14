import asyncio
import datetime
import math
import time
import typing
import discord
from discord.ext import commands
from discord.utils import get
from enhancements import nON
import log
from power import cmdInf, freeRoles
from sharedVars import HOSTNAME, STARTTIME

logP = log.get_logger(__name__)


global loginTime
loginTime = time.time()

logP.debug("Bot last login time set as: {}".format(loginTime))


class defaultCommands(
    commands.Cog,
    name="Default Commands",
    description=cmdInf["defaultCommands"]["Description"],
):
    def __init__(
        self, bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot]
    ):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global loginTime
        loginTime = time.time()

        logP.debug("Bot last login time set as: {}".format(loginTime))

    @commands.command(
        brief=cmdInf["emoji"]["Brief"],
        description=cmdInf["emoji"]["Description"],
    )
    async def emoji(self, ctx: commands.Context, idTry=""):
        if idTry:
            emo = await fetchEmoji(ctx, idTry)
            if emo:
                await ctx.send(emo)
            else:
                await ctx.send("Could not find emoji '{}'".format(idTry))
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
                            content="Page {}/{}:\n{}".format(
                                cur_page, pages, linebreak.join(chunk)
                            )
                        )
                        await message.remove_reaction(reaction, user)

                    elif str(reaction.emoji) == "◀️" and cur_page > 1:
                        cur_page -= 1
                        num = (cur_page - 1) * per_page
                        num2 = cur_page * per_page

                        chunk = emo[num:num2]
                        await message.edit(
                            content="Page {}/{}:\n{}".format(
                                cur_page, pages, linebreak.join(chunk)
                            )
                        )
                        await message.remove_reaction(reaction, user)
                except asyncio.TimeoutError:
                    await message.delete()
                    active = False

    @commands.command(
        brief=cmdInf["about"]["Brief"],
        description=cmdInf["about"]["Description"],
    )
    async def about(self, ctx: commands.Context):
        desc = (
            "This initially started as a way to automatically assign roles "
            "for Geminel#1890's novel. At the time Admins were manually "
            "calculating enhancement points and adding roles."
        )
        mes = discord.Embed(
            title="About {}".format(self.bot.user.display_name)
        )
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
            text="{} is currently running on {}.".format(
                self.bot.user.display_name, HOSTNAME
            )
        )
        mes.set_thumbnail(url=self.bot.user.display_avatar)
        await ctx.send(embed=mes)

    @commands.command(
        brief=cmdInf["run"]["Brief"],
        description=cmdInf["run"]["Description"],
    )
    async def run(self, ctx: commands.Context):
        await ctx.send("Bot is running on {}".format(HOSTNAME))

    @commands.command(
        aliases=["r", "roles"],
        brief=cmdInf["role"]["Brief"],
        description=cmdInf["role"]["Description"],
    )
    # gives requested role to command caller if it is in freeRoles
    async def role(
        self, ctx: commands.Context, *, roleToAdd: str = freeRoles[0]
    ):
        member = ctx.message.author
        sendMes = ""
        logP.debug(
            "Trying to toggle the role: {}, for: {}".format(
                roleToAdd, nON(member)
            )
        )
        roleAdd = get(member.guild.roles, name=roleToAdd)
        if not roleAdd:
            sendMes = "'{}' is not a valid role.".format(roleToAdd)
        elif roleAdd.name not in freeRoles:
            sendMes = "That is not a role you can add with this command!"
        elif roleAdd not in member.roles:
            await member.add_roles(roleAdd)
            sendMes = "{} is granted the role: '{}'!".format(
                nON(member), roleAdd
            )
        else:
            await member.remove_roles(roleAdd)
            sendMes = "{} no longer has the role: '{}'!".format(
                nON(member), roleAdd
            )
        await ctx.send(sendMes)
        logP.debug("command role resolution: " + sendMes)

    @commands.command(
        aliases=["u"],
        brief=cmdInf["uptime"]["Brief"],
        description=cmdInf["uptime"]["Description"],
    )
    async def uptime(self, ctx: commands.Context):
        logP.debug("command uptime called")
        uptimeLogin = str(
            datetime.timedelta(seconds=int(round(time.time() - loginTime)))
        )
        uptimeStartup = str(
            datetime.timedelta(seconds=int(round(time.time() - STARTTIME)))
        )
        mes = discord.Embed(title="Uptime")
        mes.add_field(name=uptimeLogin, value="Time since last login.")
        mes.add_field(name=uptimeStartup, value="Time since bot startup.")
        mes.set_footer(
            text="{} is currently running on {}.".format(
                self.bot.user.display_name, HOSTNAME
            )
        )
        mes.set_thumbnail(url=self.bot.user.display_avatar)
        await ctx.send(embed=mes)
        logP.debug(
            "Bot has been logged in for: {}, and powered up for: {}".format(
                uptimeLogin, uptimeStartup
            )
        )
        # "{} has been logged in for {}\nand powered up for {}"
        # .format(bot.user.name, uptimeLogin, uptimeStartup)
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
