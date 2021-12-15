import os
import sys
import time
import typing
import discord
from discord.ext import commands
from sharedFuncs import dupeMes, load, memGrab, nON, pluralInt, save, topEnh
import log
from power import cmdInf, power, leader
from sharedVars import HOSTNAME, LOWESTROLE, MANAGERROLES, SAVEFILE, SUPEROLE
from discord.utils import get

logP = log.get_logger(__name__)


class managerCommands(
    commands.Cog,
    name="Manager Commands",
    description=cmdInf["managerCommands"]["Description"],
):
    def __init__(
        self, bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot]
    ):
        self.bot = bot

    # Check if user has guild role
    async def cog_check(self, ctx: commands.Context):
        async def predicate(ctx: commands.Context):
            for role in MANAGERROLES:
                chkRole = get(ctx.guild.roles, name=role)
                if chkRole in ctx.message.author.roles:
                    return chkRole
            raise commands.CheckFailure(
                (
                    "You do not have permission as you are missing a role in "
                    f"this list: {MANAGERROLES}"
                )
            )

        # messy implementation for Supe
        return commands.check(await predicate(ctx))

    @commands.command(
        brief=cmdInf["roleInf"]["Brief"],
        description=cmdInf["roleInf"]["Description"],
    )
    # manager command to check if guild has role and messages
    # some information of the role
    async def roleInf(self, ctx: commands.Context, *, roleStr: str = SUPEROLE):
        supeGuildRoles = await orderRole(ctx)
        roleStrId = [x for x in supeGuildRoles if roleStr == x.name]
        logP.debug(f"Role string ID is: {roleStrId[0].id}")
        if roleStrId:
            roleStrId = roleStrId[0]
            await ctx.send(
                (
                    f"{roleStrId.name} has: \n"
                    f"position - {roleStrId.position}\n"
                    f"colour - {roleStrId.colour}"
                )
            )
        return

    @commands.command(
        aliases=["re", "reboot"],
        brief=cmdInf["restart"]["Brief"],
        description=cmdInf["restart"]["Description"],
    )
    async def restart(self, ctx: commands.Context, host: str = HOSTNAME):
        logP.debug(f"Command restart called for host: {host}")
        if host != HOSTNAME:
            return
        text = f"Restarting bot on {HOSTNAME}..."
        await dupeMes(self.bot, ctx, text)
        logP.warning("Bot is now restarting")
        restart_bot()

    @commands.command(
        brief=cmdInf["upload"]["Brief"],
        description=cmdInf["upload"]["Description"],
    )
    async def upload(
        self,
        ctx: commands.Context,
        logg: typing.Optional[int] = 0,
        host: str = HOSTNAME,
    ):
        logP.debug(f"Command upload called for host: {host}")
        if host != HOSTNAME:
            return
        currTime = time.localtime()
        currTimeStr = (
            f"{currTime.tm_year:04d}.{currTime.tm_mon:02d}."
            f"{currTime.tm_mday:02d}_{currTime.tm_hour:02d}."
            f"{currTime.tm_min:02d}.{currTime.tm_sec:02d}"
        )
        logP.debug(f"currTime: {currTime}")
        logP.debug("currTimeStr: " + currTimeStr)
        nameStamp = f"{SAVEFILE}_{currTimeStr}"
        if logg:
            await ctx.send(
                f"Log File from {HOSTNAME} at: {currTimeStr}",
                file=discord.File(log.LOG_FILE),
            )
        else:
            await ctx.send(
                f"File {SAVEFILE} from {HOSTNAME}",
                file=discord.File(SAVEFILE, filename=nameStamp),
            )
        logP.debug("command upload completed")

    @commands.command(
        brief=cmdInf["xpAdd"]["Brief"],
        description=cmdInf["xpAdd"]["Description"],
    )
    async def xpAdd(
        self,
        ctx: commands.Context,
        val: typing.Union[float, int] = 0.0,
        *,
        mem: str = "",
    ):
        val = round(val, 2)
        logP.debug(f"val to add is: {val}")
        memList = await memGrab(self, ctx, mem)
        logP.debug(f"memList is: {memList}")
        peep = memList[0]

        infGrab = load(peep.guild.id)
        if not infGrab:
            infGrab = {}
        if peep.id not in infGrab.keys():
            infGrab[peep.id] = {"Name": peep.name, "invXP": [0, 0, 0]}
        iniVal = infGrab[peep.id]["invXP"][-1]
        sum = iniVal + val
        if sum < 0.0:
            sum = 0.0
        infGrab[peep.id]["invXP"][-1] = sum
        save(ctx.message.author.guild.id, infGrab)
        await ctx.send(f"Host {nON(peep)}: {iniVal} -> {sum}")

    @commands.command(
        brief=cmdInf["average"]["Brief"],
        description=cmdInf["average"]["Description"],
    )
    async def average(self, ctx: commands.Context):
        mes = discord.Embed(title="Average Enhancment Points")
        totSumPeeps = 0
        totLenPeeps = 0
        getSupe = [x for x in ctx.guild.roles if str(x.name) == SUPEROLE]
        if not getSupe:
            await ctx.send(f"No users of role: {SUPEROLE}")
        else:
            getSupe = getSupe[0]
        for val in leader.values():
            peepDict = topEnh(ctx, val)

            sumPeep = sum(peepDict.values())
            lenPeep = len(peepDict.keys())
            avPeep = round(sumPeep / len(getSupe.members), 4)

            totSumPeeps += sumPeep

            mes.add_field(
                name=f"{val}",
                value=(
                    f"{lenPeep} host{pluralInt(lenPeep)} for a total of "
                    f"{sumPeep} point{pluralInt(sumPeep)}.\n Serverwide "
                    f"average of {avPeep}."
                ),
            )
        totLenPeeps = len(getSupe.members)
        totAvPeep = round(totSumPeeps / totLenPeeps, 2)
        mes.add_field(
            name=SUPEROLE,
            value=(
                f"There is a total of {totLenPeeps} "
                f"host{pluralInt(totLenPeeps)} with a sum of {totSumPeeps} "
                f"enhancement point{pluralInt(totSumPeeps)} spent.\n "
                f"Serverwide average of {totAvPeep}."
            ),
        )
        mes.set_footer(text=HOSTNAME, icon_url=self.bot.user.display_avatar)
        await ctx.send(embed=mes)

    @commands.command(
        brief=cmdInf["moveRoles"]["Brief"],
        description=cmdInf["moveRoles"]["Description"],
    )
    # manager command to correct role position for roles that
    # have been created by bot
    async def moveRoles(self, ctx: commands.Context):
        managed = await manageRoles(ctx)
        await ctx.send(embed=managed)
        return

    """@commands.command(
        hidden=HIDE,
        brief=cmdInf["trimAll"]["Brief"],
        description=cmdInf["trimAll"]["Description"],
    )
    @commands.has_any_role(MANAGER)
    # manager command to role trim all users bot has access to
    async def trimAll(self, ctx: commands.Context):
        debug("funcTrimAll START")

        memberList = isSuper(self, self.bot.users)
        debug("\tmemberlist to cut = {}".format([x.name for x in memberList]))

        await cut(ctx, memberList)
        debug("funcTrimAll END")
        return"""


def restart_bot() -> None:
    os.execv(sys.executable, ["python"] + sys.argv)


# function to fetch all guild roles that are managed by bot
async def orderRole(ctx: commands.Context):
    logP.debug(power.values())

    supeList = [
        x
        for x in ctx.message.author.guild.roles
        if str(x) in [y["Name"] for y in power.values()]
    ]

    logP.debug(supeList)
    return supeList


# function to move roles to correct rank positions
async def manageRoles(ctx: commands.Context):

    # spam message negation
    movedRoles = discord.Embed(title="Moving Roles")
    toMove = {}

    # iterate through all guild roles
    for role in ctx.message.guild.roles:
        logP.debug(f"Looking at role: {role.name}")

        # grab shorthand for enhancement
        roleShort = [x for x in power.keys() if power[x]["Name"] == role.name]
        logP.debug(f"roleShort = {roleShort}")

        # check to ensure role is one overseen by this bot
        if roleShort == []:
            logP.debug("Role not Supe")
            continue

        # check for intelligence roles as they are the rank position constants
        # and should not be changed by this command
        elif "Intelligence" == power[roleShort[0]]["Type"]:
            logP.debug("Role type intelligence")
            continue

        # fetch enhancement rank
        roleRank = power[roleShort[0]]["Rank"]
        logP.debug(f"Role rank is: {roleRank}")

        # check for restricted roles
        if not roleRank:
            logP.debug("Role rank zero")
            continue

        # check for rank 1 roles that do not have a lowerbound intelligence
        # role for positioning
        elif roleRank == 1:
            roleRankLower = LOWESTROLE

        else:
            roleRankLower = [
                x.position
                for x in ctx.message.guild.roles
                if x.name
                == f"Rank {roleRank - 1} Intelligence (only for Systems)"
            ][0]

        # fetch upperbound intelligence rank position
        roleRankUpper = [
            x.position
            for x in ctx.message.guild.roles
            if x.name == f"Rank {roleRank} Intelligence (only for Systems)"
        ][0]

        # roleDiff = roleRankUpper - roleRankLower

        # check for if role is already in postion
        if role.position < roleRankUpper:
            if role.position >= roleRankLower:
                logP.debug(
                    f"Role within bounds {roleRankUpper} - {roleRankLower}"
                )
                continue

        # move role to current upperbound intelligence position,
        # forcing intelligence position to increase
        # ASSUMES current role position is lower than intelligence position
        # TODO remove assumption
        logP.debug(
            f"Role to be moved from {role.position} to {roleRankUpper - 1}"
        )

        movedRoles.add_field(
            name=role.name,
            value=f"{role.position} -> {roleRankUpper}",
        )

        toMove[role] = roleRankUpper
    await ctx.message.guild.edit_role_positions(positions=toMove)

    # return moved roles as single message to function call
    if not movedRoles.fields:
        movedRoles.description = "No roles moved"
    return movedRoles


# function to setup cog
def setup(bot: commands.Bot):
    bot.add_cog(managerCommands(bot))
