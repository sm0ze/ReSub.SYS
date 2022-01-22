import os
import sys
import time
import typing

import discord
from discord.ext import commands
from discord.utils import get

import log
from sharedConsts import (
    COMMANDS_ON,
    HOST_NAME,
    LOWEST_ROLE,
    MANAGER_ROLES,
    ROLE_ID_CALL,
    ROLE_ID_PATROL,
    SAVE_FILE,
    STREAKER,
    SUPE_ROLE,
    TIME_TILL_ON_CALL,
)
from sharedDicts import leader, masterEhnDict
from sharedFuncs import (
    cut,
    dupeMes,
    getBrief,
    getDesc,
    isSuper,
    load,
    memGrab,
    pluralInt,
    pointsLeft,
    rAddFunc,
    remOnPatrol,
    save,
    sendMessage,
    topEnh,
)

logP = log.get_logger(__name__)


class managerCommands(
    commands.Cog,
    name="Manager Commands",
    description=getDesc("managerCommands"),
):
    def __init__(
        self, bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot]
    ):
        self.bot = bot

    # Check if user has guild role
    async def cog_check(self, ctx: commands.Context):
        async def predicate(ctx: commands.Context):
            for role in MANAGER_ROLES:
                chkRole = get(ctx.guild.roles, name=role)
                if chkRole in ctx.author.roles:
                    return chkRole
            raise commands.CheckFailure(
                (
                    "You do not have permission as you are missing a role in "
                    f"this list: {MANAGER_ROLES}"
                )
            )

        # messy implementation for Supe
        return commands.check(await predicate(ctx))

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("wipe"),
        description=getDesc("wipe"),
    )
    # manager command to check if guild has role and messages
    # some information of the role
    async def wipe(self, ctx: commands.Context, *, memberList: str = ""):
        if not memberList:
            await ctx.send("Give me a peep to wipe next time...")
            return
        members = await memGrab(ctx, memberList)
        await ctx.send(f"Wiping {len(members)} peeps.")
        for peep in members:
            toCut = [
                x.name
                for x in peep.roles
                if x.name
                in [
                    masterEhnDict[y]["Name"]
                    for y in masterEhnDict.keys()
                    if masterEhnDict[y]["Rank"] > 0
                ]
            ]
            logP.debug(toCut)
            await cut(ctx, [peep], toCut)
        await ctx.send(f"Finished wiping {len(members)} peeps.")

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("roleCall"),
        description=getDesc("roleCall"),
    )
    # manager command to check if guild has role and messages
    # some information of the role
    async def roleCall(self, ctx: commands.Context, hideFull: bool = True):
        supeRole = get(ctx.guild.roles, name=SUPE_ROLE)
        await pointsLeft(ctx, supeRole.members, hideFull)

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["fra"],
        brief=getBrief("forceRAdd"),
        description=getDesc("forceRAdd"),
    )
    async def forceRAdd(
        self,
        ctx: commands.Context,
        incNum: typing.Optional[int] = 1,
        *,
        memberList="",
    ):
        memList = await memGrab(ctx, memberList)
        superList = isSuper(self.bot, memList)
        await ctx.send(
            (
                f"Adding to {len(superList)} supes of {len(memList)} "
                "originally selected."
            )
        )
        await rAddFunc(ctx, superList, incNum)
        await ctx.send("Finished forcefully rAdd-ing")

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("roleInf"),
        description=getDesc("roleInf"),
    )
    # manager command to check if guild has role and messages
    # some information of the role
    async def roleInf(
        self,
        ctx: commands.Context,
        *,
        roleStr: str = SUPE_ROLE,
    ):
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
        brief=getBrief("restart"),
        description=getDesc("restart"),
    )
    async def restart(self, ctx: commands.Context, host: str = HOST_NAME):
        logP.debug(f"Command restart called for host: {host}")
        if host != HOST_NAME:
            return
        text = f"Restarting bot on {HOST_NAME}..."
        await dupeMes(self.bot, ctx, text)
        logP.warning("Bot is now restarting")
        restart_bot()

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("upload"),
        description=getDesc("upload"),
    )
    async def upload(
        self,
        ctx: commands.Context,
        logg: typing.Optional[int] = 0,
        host: str = HOST_NAME,
    ):
        logP.debug(f"Command upload called for host: {host}")
        if host != HOST_NAME:
            return
        currTime = time.localtime()
        currTimeStr = (
            f"{currTime.tm_year:04d}.{currTime.tm_mon:02d}."
            f"{currTime.tm_mday:02d}_{currTime.tm_hour:02d}."
            f"{currTime.tm_min:02d}.{currTime.tm_sec:02d}"
        )
        logP.debug(f"currTime: {currTime}")
        logP.debug("currTimeStr: " + currTimeStr)
        nameStamp = f"{SAVE_FILE}_{currTimeStr}"
        if logg:
            await ctx.send(
                f"Log File from {HOST_NAME} at: {currTimeStr}",
                file=discord.File(log.LOG_FILE),
            )
        else:
            await ctx.send(
                f"File {SAVE_FILE} from {HOST_NAME}",
                file=discord.File(SAVE_FILE, filename=nameStamp),
            )
        logP.debug("command upload completed")

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("leavers"),
        description=getDesc("leavers"),
    )
    async def leavers(self, ctx: commands.Context):
        supeRole = get(ctx.guild.roles, name=SUPE_ROLE)
        cached_file = load(ctx.guild.id)
        mes = discord.Embed(title="Leavers")
        memberIdList = [x.id for x in supeRole.members]
        for peep in cached_file.keys():
            if peep not in memberIdList:
                mes.add_field(name=f"{peep}", value=cached_file[peep])
        await sendMessage(mes, ctx)

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("finPatrol"),
        description=getDesc("finPatrol"),
    )
    async def finPatrol(self, ctx: commands.Context):
        patrolRole = get(ctx.guild.roles, id=int(ROLE_ID_PATROL))
        onCallRole = get(ctx.guild.roles, id=int(ROLE_ID_CALL))
        streakerRole = get(ctx.guild.roles, name=STREAKER)

        if patrolRole and onCallRole and streakerRole:
            mes = await remOnPatrol(
                patrolRole, onCallRole, streakerRole, TIME_TILL_ON_CALL
            )
            await ctx.send(mes)

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("printSave"),
        description=getDesc("printSave"),
    )
    async def printSave(self, ctx: commands.Context):
        sendMes = ""
        cache_file = load(ctx.guild.id)

        for key, val in cache_file.items():
            sendMes += f"{val}\n"
        await sendMessage(sendMes, ctx)
        await ctx.send("Printed Save File.")

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("xpAdd"),
        description=getDesc("xpAdd"),
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
        memList = await memGrab(ctx, mem)
        logP.debug(f"memList is: {memList}")
        infGrab = load(memList[0].guild.id)
        for peep in memList:
            if not infGrab:
                infGrab = {}
            if peep.id not in infGrab.keys():
                infGrab[peep.id] = {"Name": peep.name, "invXP": [0, 0, 0]}
            iniVal = infGrab[peep.id]["invXP"][-1]
            sum = iniVal + val
            if sum < 0.0:
                sum = 0.0
            infGrab[peep.id]["invXP"][-1] = sum

            await ctx.send(f"Host {peep.display_name}: {iniVal} -> {sum}")
        save(ctx.guild.id, infGrab)
        if len(memList) > 5:
            await ctx.send("Finished adding xp")

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("average"),
        description=getDesc("average"),
    )
    async def average(self, ctx: commands.Context):
        mes = discord.Embed(title="Average Enhancment Points")
        totSumPeeps = 0
        totLenPeeps = 0
        getSupe = [x for x in ctx.guild.roles if str(x.name) == SUPE_ROLE]
        if not getSupe:
            await ctx.send(f"No users of role: {SUPE_ROLE}")
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
                    f"{lenPeep} host{pluralInt(lenPeep)} for a "
                    f"total of {sumPeep} point{pluralInt(sumPeep)}"
                    f".\n Serverwide average of {avPeep}."
                ),
            )
        totLenPeeps = len(getSupe.members)
        totAvPeep = round(totSumPeeps / totLenPeeps, 2)
        mes.add_field(
            name=SUPE_ROLE,
            value=(
                f"There is a total of {totLenPeeps} "
                f"host{pluralInt(totLenPeeps)} with a sum of "
                f"{totSumPeeps} enhancement "
                f"point{pluralInt(totSumPeeps)} spent."
                f"\n Serverwide average of {totAvPeep}."
            ),
        )
        mes.set_footer(text=HOST_NAME, icon_url=self.bot.user.display_avatar)
        await sendMessage(mes, ctx)

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["poop", "pp"],
        brief=getBrief("popPeep"),
        description=getDesc("popPeep"),
    )
    async def popPeep(self, ctx: commands.Context, peep: discord.User):
        cache_file = load(ctx.guild.id)
        if peep.id not in cache_file.keys():
            ctx.send(f"{peep.display_name} is not saved in File.")
            return
        haveRemoved = cache_file.pop(peep.id)
        sendMes = f"Have removed {peep.id}: {haveRemoved}"
        logP.debug(sendMes)
        save(ctx.guild.id, cache_file)
        await ctx.send(sendMes)

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("moveRoles"),
        description=getDesc("moveRoles"),
    )
    # manager command to correct role position for roles that
    # have been created by bot
    async def moveRoles(self, ctx: commands.Context):
        managed = await manageRoles(ctx)
        await ctx.send(embed=managed)
        return

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("trimAll"),
        description=getDesc("trimAll"),
    )
    # manager command to role trim all users bot has access to
    async def trimAll(self, ctx: commands.Context, memStr: str = SUPE_ROLE):
        memList = await memGrab(ctx, memStr)
        await cut(ctx, memList)
        await ctx.send(f"Finished trimAll for {len(memList)} members.")


def restart_bot() -> None:
    os.execv(sys.executable, ["python"] + sys.argv)


# function to fetch all guild roles that are managed by bot
async def orderRole(ctx: commands.Context):
    logP.debug(masterEhnDict.values())

    supeList = [
        x
        for x in ctx.guild.roles
        if str(x) in [y["Name"] for y in masterEhnDict.values()]
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
        roleShort = [
            x
            for x in masterEhnDict.keys()
            if masterEhnDict[x]["Name"] == role.name
        ]
        logP.debug(f"roleShort = {roleShort}")

        # check to ensure role is one overseen by this bot
        if roleShort == []:
            logP.debug("Role not Supe")
            continue

        # check for intelligence roles as they are the rank position constants
        # and should not be changed by this command
        elif "Intelligence" == masterEhnDict[roleShort[0]]["Type"]:
            logP.debug("Role type intelligence")
            continue

        # fetch enhancement rank
        roleRank = masterEhnDict[roleShort[0]]["Rank"]
        logP.debug(f"Role rank is: {roleRank}")

        # check for restricted roles
        if not roleRank:
            logP.debug("Role rank zero")
            continue

        # check for rank 1 roles that do not have a lowerbound intelligence
        # role for positioning
        elif roleRank == 1:
            roleRankLower = LOWEST_ROLE

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
