import asyncio
import datetime
import os
import sys
import time
import typing

import discord
from discord.ext import commands
from discord.utils import get

import bin.log as log
from bin.battle import testBattle
from bin.shared_consts import (
    COMMANDS_ON,
    DL_ARC_DUR,
    HOST_NAME,
    MANAGER_ROLES,
    ROLE_ID_CALL,
    ROLE_ID_PATROL,
    SAVE_FILE,
    SORT_ORDER,
    STREAKER,
    SUPE_ROLE,
    TIME_TILL_ON_CALL,
)
from bin.shared_dicts import leader, masterEhnDict
from bin.shared_funcs import (
    cut,
    dupeMes,
    getBrief,
    getDesc,
    getGuildSupeRoles,
    getLoc,
    isSuper,
    load,
    memGrab,
    pluralInt,
    pointsLeft,
    rAddFunc,
    remOnPatrol,
    save,
    sendMessage,
    splitString,
    sublist,
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
        brief=getBrief("resetAgg"),
        description=getDesc("resetAgg"),
    )
    async def resetAgg(self, ctx: commands.Context, *, memberList: str = ""):
        members = await memGrab(ctx, memberList)
        cache_file = load(ctx.guild.id)
        for member in members:
            if member.id in cache_file:
                cache_file[member.id].pop("agg", None)
        save(ctx.guild.id, cache_file)
        await ctx.send(f"Reset Aggression for {len(members)}")

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["td"],
        brief=getBrief("testDuel"),
        description=getDesc("testDuel"),
    )
    async def testDuel(
        self,
        ctx: commands.Context,
        peepBuild: typing.Union[int, str],
        notPeepBuild: typing.Union[int, str],
        generations: int = 1,
        repeats: int = 1,
        defCost: int = 20,
        outType: int = 1,
    ):
        await ctx.send(
            f"Starting simulation of {generations * repeats} "
            f"battles of {generations} generations * {repeats} repeats."
        )
        asyncio.create_task(
            testBattle(
                self.bot,
                ctx,
                peepBuild,
                notPeepBuild,
                generations,
                repeats,
                defCost,
                outType,
            )
        )

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
                file=discord.File(
                    getLoc(SAVE_FILE, "data"), filename=nameStamp
                ),
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
        embList = []
        cache_file = load(ctx.guild.id)
        cmdChnl = ctx.channel

        expectedFields = [
            "Name",
            "currPatrol",
            "topStatistics",
            "builds",
            "tut",
            "buildSort",
        ]

        # create thread from channel
        mesID = ctx.message.id
        cmdThrd: discord.Thread = await cmdChnl.create_thread(
            name=f"PrintSave #{mesID}",
            message=ctx.message,
            auto_archive_duration=int(DL_ARC_DUR),
            reason=f"PrintSave #{mesID}",
        )

        # for each user in cache file create a discord.Embed
        for userID in cache_file.keys():
            user = self.bot.get_user(int(userID))
            if user:
                titleStr = f"{user.name}#{user.discriminator}"
            elif expectedFields[0] in cache_file[userID]:
                titleStr = f"{cache_file[userID][expectedFields[0]]}:{userID}"
            else:
                titleStr = f"{userID}"

            emb = discord.Embed(title=titleStr)

            # find the keys that are not in expectedFields
            for key in cache_file[userID].keys():
                if key not in expectedFields:
                    emb.add_field(name=key, value=cache_file[userID][key])
                else:
                    if key == expectedFields[1]:
                        embStr = ""
                        currPatrolStats: dict[str] = cache_file[userID][key]
                        lastTask: float = currPatrolStats.get(
                            "lastTaskTime", None
                        )
                        patrolStart: float = currPatrolStats.get(
                            "patrolStart", None
                        )
                        patrolTasks: int = currPatrolStats.get(
                            "patrolTasks", None
                        )

                        if lastTask:
                            lastTaskTimeSinceInt = int(time.time() - lastTask)
                            lastTaskTimeSince = datetime.timedelta(
                                seconds=lastTaskTimeSinceInt
                            )
                            if lastTaskTimeSinceInt > TIME_TILL_ON_CALL:
                                # if patrol is finished skip this key
                                continue
                            embStr += f"Last Task: {lastTaskTimeSince}\n"

                        if patrolStart:
                            patrolStartTimeSince = datetime.timedelta(
                                seconds=int(time.time() - patrolStart)
                            )
                            embStr += f"Patrol Time: {patrolStartTimeSince}\n"

                        if patrolTasks:
                            embStr += f"Patrol Tasks: {patrolTasks}\n"
                        if not embStr:
                            embStr = "No Patrol Data"
                        emb.add_field(
                            name="Current Patrol Stats", value=embStr
                        )
                    elif key == expectedFields[2]:
                        embStr = ""
                        topStats: dict[str] = cache_file[userID][key]
                        totalTasks: int = topStats.get("totalTasks", None)
                        firstTask: float = topStats.get("firstTaskTime", None)
                        totalPatrols: int = topStats.get("totalPatrols", None)
                        longestPatrol: float = topStats.get(
                            "longestPatrol", None
                        )
                        mostActivePatrol: int = topStats.get(
                            "mostActivePatrol", None
                        )
                        if totalTasks:
                            embStr += f"Total Tasks: {totalTasks}\n"

                        if firstTask:
                            firstTaskTimeSince = datetime.timedelta(
                                seconds=int(time.time() - firstTask)
                            )
                            embStr += f"First Task: {firstTaskTimeSince}\n"

                        if totalPatrols:
                            embStr += f"Total Patrols: {totalPatrols}\n"

                        if longestPatrol:
                            longestPatrolTimeSince = datetime.timedelta(
                                seconds=int(longestPatrol)
                            )
                            embStr += (
                                f"Longest Patrol: {longestPatrolTimeSince}\n"
                            )

                        if mostActivePatrol:
                            embStr += (
                                f"Most Active Patrol: {mostActivePatrol}\n"
                            )
                        if not embStr:
                            embStr = "No Top Stats"
                        emb.add_field(name="Top Statistics", value=embStr)
                    elif key == expectedFields[3]:
                        embStr = ""
                        builds: dict[str, list] = cache_file[userID][key]
                        for build in builds.keys():
                            embStr += f"{build}: {builds[build]}\n"
                        if not embStr:
                            embStr = "No Builds"
                        emb.add_field(name="Saved Loadouts", value=embStr)
                    elif key == expectedFields[4]:
                        stepsLeft = (
                            cache_file[userID][key]
                            if cache_file[userID][key]
                            else "No Steps Left"
                        )
                        emb.add_field(
                            name="Tutorial Steps Left",
                            value=stepsLeft,
                        )
                    else:
                        pass
            embList.append(emb)

        await sendMessage(embList, cmdThrd)
        await cmdThrd.send("Printed Save File.")
        await ctx.send("Printed Save File.")
        # archive thread
        await cmdThrd.edit(archived=1)

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
            infGrab[peep.id].setdefault("invXP", [0, 0, 0])
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
        brief=getBrief("moveRoles"),
        description=getDesc("moveRoles"),
    )
    # manager command to correct role position for roles that
    # have been created by bot
    async def moveRoles(self, ctx: commands.Context):
        managed = await manageRoles(ctx)
        asyncio.create_task(sendMessage(managed, ctx))

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
    movedRoles: list[discord.Embed] = []

    iniFieldString = str("Initial Roles **(Position)** Final Roles\n")

    toManage, lowestRank, highestRank = getGuildSupeRoles(ctx)

    # sort toManage by rank and then by given sort order
    iniList = toManage.copy()
    toManage.sort(
        key=lambda x: (-int(x[1]["Rank"]), SORT_ORDER.index(x[1]["Type"])),
        reverse=True,
    )

    taskList = []

    for role, roleShort in toManage.copy():
        if not len(role.members):
            toManage.remove((role, roleShort))
            highestRank -= 1
            task = asyncio.create_task(role.delete(reason="No Members"))
            taskList.append(task)

    finList = toManage.copy()

    if sublist(iniList, finList):
        movedRoles.append(
            discord.Embed(title="Move Roles", description="No roles to move")
        )
        await asyncio.gather(*taskList)
        return movedRoles
    else:
        iniStringList = (
            "\n".join((f'{x[1]["Name"]}' for x in iniList))
        ).splitlines()
        finStringList = (
            "\n".join((f'{x[1]["Name"]}' for x in finList))
        ).splitlines()
        fieldStr = iniFieldString
        largestList = max(len(iniStringList), len(finStringList))
        for i in range(largestList):
            if i < len(iniStringList):
                iniString = iniStringList[i]
            else:
                iniString = ""
            if i < len(finStringList):
                finString = finStringList[i]
            else:
                finString = ""
            if iniString == finString:
                continue
            fieldStr += f"{iniString} **({i+lowestRank})** {finString}\n"
        fieldList = splitString(fieldStr, 4096)
        if fieldStr != iniFieldString:
            for i, field in enumerate(fieldList):
                movedRoles.append(
                    discord.Embed(
                        title=f"Move Roles ({1+i} of {len(fieldList)})",
                        description=field,
                    )
                )

    await asyncio.gather(*taskList)
    msgStr = f"Editing positions from {lowestRank} to {highestRank}\n"
    msg = await ctx.send(msgStr)
    # move roles to correct rank positions
    for i, (role, roleShort) in enumerate(toManage):
        rolePos = lowestRank + i
        logP.debug(f"Moving role {role.name} to position {rolePos}")
        if role.position != rolePos:
            await msg.edit(
                content=(
                    msgStr
                    + f"\nMoving ***{role.name}*** to position ***{rolePos}***"
                )
            )

            await role.edit(position=(rolePos))
    await msg.delete()

    # return moved roles as single message to function call
    if not movedRoles:
        movedRoles.append(
            discord.Embed(
                title="Move Roles",
                description="Order unchanged, positions updated.",
            )
        )
    return movedRoles


# function to setup cog
def setup(bot: commands.Bot):
    bot.add_cog(managerCommands(bot))
