# roleCommands.py

import asyncio
import datetime
import random
import time
import typing

import discord
from discord.ext import commands, tasks
from discord.utils import get

import bin.log as log
import bin.shared_dyVars as shared_dyVars
from bin.battle import (
    NPC,
    NPC_from_diff,
    battler,
    player,
    playerFromBuild,
    startDuel,
)
from bin.exceptions import notNPC, notSupeDuel
from bin.shared_consts import (
    ACTIVE_SEC,
    AID_WEIGHT,
    ASK_NPC,
    ASK_SELF,
    COMMANDS_ON,
    COMMANDS_ROLES,
    DEFAULT_DUEL_OPP,
    HIDE,
    HOST_NAME,
    LEAD_LIMIT,
    ROLE_ID_CALL,
    ROLE_ID_PATROL,
    STREAKER,
    SUPE_ROLE,
    TASK_CD,
    TIME_TILL_ON_CALL,
)
from bin.shared_dicts import (
    baseDict,
    leader,
    masterEhnDict,
    npcDict,
    posTask,
    powerTypes,
    reqResList,
    restrictedList,
    rsltDict,
    taskVar,
)
from bin.shared_funcs import (
    aOrAn,
    blToStr,
    buffStrGen,
    buildFromString,
    compareBuild,
    count,
    countIdList,
    cut,
    funcBuild,
    genBuild,
    genderPick,
    getBrief,
    getDesc,
    getHelpers,
    isSuper,
    load,
    loadAllPers,
    lvlEqu,
    mee6DictGrab,
    memGrab,
    pickWeightedSupe,
    pluralInt,
    pointsLeft,
    rAddFunc,
    remOnCall,
    remOnPatrol,
    reqEnd,
    rollTask,
    save,
    sendMessage,
    spent,
    strList,
    tatsuXpGrab,
    toAdd,
    toCut,
    topEnh,
)

logP = log.get_logger(__name__)


ENHLIST = [(x, y) for (x, y) in powerTypes.items()]

# TODO: implement this and similiar instead of
# multiple enhancement.dict.keys() calls
# enhancement (type, rank) pairs for list command


class roleCommands(
    commands.Cog,
    name=f"{SUPE_ROLE} Commands",
    description=getDesc("roleCommands"),
):
    def __init__(
        self, bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot]
    ):
        self.bot = bot
        if HOST_NAME not in ["sm0ze-desktop", "smoze-laptop"]:
            self.remOnCallLoop.start()
            self.remOnPatrolLoop.start()
            self.xpLoop.start()

    # Check if user has guild role
    async def cog_check(self, ctx: commands.Context):
        async def predicate(ctx: commands.Context):
            for role in COMMANDS_ROLES:
                chkRole = get(ctx.guild.roles, name=role)
                if chkRole in ctx.author.roles:
                    return chkRole
            raise commands.CheckFailure(
                (
                    "You do not have permission as you are missing a role in "
                    f"this list: {COMMANDS_ROLES}\nThe super command can be "
                    "used to gain the Supe role"
                )
            )

        # messy implementation for Supe
        return commands.check(await predicate(ctx))

    @tasks.loop(minutes=5)
    async def xpLoop(self):
        roleGrab = None
        for guild in self.bot.guilds:
            roleGrab = get(guild.roles, name=SUPE_ROLE)
            if roleGrab:
                await mee6DictGrab(roleGrab)

            if shared_dyVars.tatsuUpdateList:
                await tatsuXpGrab(roleGrab)

    @xpLoop.before_loop
    async def before_xpLoop(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=10)
    async def remOnPatrolLoop(self):
        for guild in self.bot.guilds:
            patrolRole = get(guild.roles, id=int(ROLE_ID_PATROL))
            onCallRole = get(guild.roles, id=int(ROLE_ID_CALL))
            streakerRole = get(guild.roles, name=STREAKER)
            if patrolRole and onCallRole and streakerRole:
                await remOnPatrol(
                    patrolRole, onCallRole, streakerRole, TIME_TILL_ON_CALL
                )

    @remOnPatrolLoop.before_loop
    async def before_remOnPatrolLoop(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=60)
    async def remOnCallLoop(self):
        for guild in self.bot.guilds:
            onCallRole = get(guild.roles, id=int(ROLE_ID_CALL))

            if onCallRole:
                await remOnCall(onCallRole, ACTIVE_SEC)

    @remOnCallLoop.before_loop
    async def before_remOnCallLoop(self):
        await self.bot.wait_until_ready()

    @commands.command(enabled=COMMANDS_ON, hidden=True)
    @commands.is_owner()
    async def forceTatsu(self, ctx: commands.Context):
        roleGrab = get(ctx.guild.roles, name=SUPE_ROLE)
        mes = await tatsuXpGrab(roleGrab)
        if mes:
            await sendMessage(ctx, mes)

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["rem"],
        brief=getBrief("remove"),
        description=getDesc("remove"),
    )
    async def remove(self, ctx: commands.Context, *, typeStr: str = ""):
        user = ctx.author
        if toCut(user):
            await cut(ctx, [user])
        userSpent = spent([user])
        userEnhancements = userSpent[0][2]
        userHas = funcBuild(userEnhancements)
        userHasBuild = userHas[2]
        typList = []
        if not typeStr:
            await ctx.send("Please enter a type to remove")
        else:
            fixArg = typeStr.replace(" ", ",")
            fixArg = fixArg.replace(";", ",")
            fixedTypStr = [x.strip() for x in fixArg.split(",") if x.strip()]
            typList = [x for x in leader if x in fixedTypStr]

        logP.debug(f"{user.name} requested to remove {typList}")

        userWantsEnhancements = userEnhancements.copy()
        for typ in typList:
            if typ in [x[:3] for x in userEnhancements]:
                userWantsEnhancements.remove(
                    [x for x in userEnhancements if x[:3] == typ][0]
                )
        userWants = funcBuild(userWantsEnhancements)
        userWantsBuild = userWants[2]
        remRoles = compareBuild(userHasBuild, userWantsBuild)
        if remRoles:
            await cut(ctx, [user], remRoles)
        await toAdd(ctx, user, userWantsBuild)

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["npc"],
        brief=getBrief("npcList"),
        description=getDesc("npcList"),
    )
    async def npcList(self, ctx: commands.Context, toList: str = ""):
        newMes = discord.Embed(title="NPC List")
        peepList = []
        if toList:
            if not (
                toList in npcDict.keys()
                or toList in [npcDict[x]["name"] for x in npcDict.keys()]
            ):
                if not toList.lower() == "stats":
                    await ctx.send(f"NPC {toList} not found.")
                    return
            NPCid = ""
            if toList in npcDict.keys():
                NPCid = toList
            elif toList in [npcDict[x]["name"] for x in npcDict.keys()]:
                posName = [
                    x for x in npcDict.keys() if npcDict[x]["name"] == toList
                ]
                if posName:
                    NPCid = posName[0]
            elif toList.lower() == "stats":
                for x in npcDict.keys():
                    peepList.append(x)

            if NPCid:
                peepList.append(NPCid)
            for peep in peepList:
                foundNPC = NPC(self.bot, npcDict[peep])
                foundPlayer = player(foundNPC, self.bot)
                newMes.add_field(
                    name=f"{foundPlayer.n} ({foundPlayer.bC})",
                    value=f"{foundPlayer.statMessage()}",
                )

                if NPCid:
                    playerEhnListStr = blToStr(foundPlayer.bL)
                    newMes.add_field(
                        name="Enhancements", value=playerEhnListStr
                    )
                    newMes.set_thumbnail(url=foundNPC.picUrl)
        else:
            peepListStr = ""
            for peep in npcDict.keys():
                peepListStr += f"{peep}: {npcDict[peep]['name']}\n"
            newMes.add_field(name="ID: Name", value=peepListStr)
        await sendMessage(ctx, newMes)

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("trim"),
        description=getDesc("trim"),
    )
    # command to trim command caller of extra roles. OBSOLETE due to cut call
    # after role add in add command
    async def trim(self, ctx: commands.Context):

        memberList = await memGrab(ctx, "")

        await cut(ctx, memberList)

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["tu"],
        brief=getBrief("tatsuUpdate"),
        description=getDesc("tatsuUpdate"),
    )
    async def tatsuUpdate(self, ctx: commands.Context):
        if ctx.author not in shared_dyVars.tatsuUpdateList:
            shared_dyVars.tatsuUpdateList.append(ctx.author)
            await ctx.send("Your tatsu xp will update on next update loop.")
        else:
            await ctx.send("You are already set to update your xp soon.")

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("convert"),
        description=getDesc("convert"),
    )
    async def convert(
        self, ctx: commands.Context, inVar: float = 0, gdv: int = 0
    ):
        feedback = lvlEqu(inVar, gdv)
        if gdv:
            await ctx.send(f"{inVar} GDV is equivalent to {feedback:,} XP")
        else:
            await ctx.send(f"{inVar:,} XP is equivalent to {feedback} GDV")

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["t"],
        brief=getBrief("task"),
        description=getDesc("task"),
    )
    @commands.cooldown(1, TASK_CD, type=commands.BucketType.user)
    async def task(self, ctx: commands.Context):

        taskType = random.choices(
            taskVar["taskOpt"][0],
            cum_weights=taskVar["taskWeight"],
        )
        taskShrt = posTask[taskType[0]]
        taskWorth = taskShrt["Worth"]
        logP.debug(f"Task is worth {taskWorth}")
        taskAdd = taskShrt["Add"]
        logP.debug(f"Task can have additional {taskAdd} peeps")

        patrolRole = get(ctx.guild.roles, id=int(ROLE_ID_PATROL))
        supRole = get(ctx.guild.roles, name=SUPE_ROLE)
        onCallRole = get(ctx.guild.roles, id=int(ROLE_ID_CALL))

        aidPick = [patrolRole, onCallRole, supRole]

        xpList = getHelpers(ctx, taskShrt, taskAdd, aidPick, AID_WEIGHT)
        logP.debug("xpList = ", xpList)
        logP.debug(f"{taskType}\nTask XP: {lvlEqu(taskWorth[0], 1)}")
        emptMes = discord.Embed(
            title=f"Alert, {ctx.author.display_name}!",
            description=f"A new {taskType[0]} GDV task has been assigned.",
        )

        logP.debug(f"Possible Adjectives: {len(taskShrt['Adjective'])}")
        selAdj = random.choice(taskShrt["Adjective"])
        logP.debug(f"Selected Adjective: {selAdj}")

        logP.debug(f"Possible People: {len(taskShrt['People'])}")
        selPeep = random.choice(taskShrt["People"])
        logP.debug(f"Selected People: {selPeep}")

        logP.debug(f"Possible Action: {len(taskShrt['Action'])}")
        selAct = random.choice(taskShrt["Action"])
        logP.debug(f"Selected Action: {selAct}")

        logP.debug(f"Possible Location: {len(taskShrt['Location'])}")
        selPlace = random.choice(taskShrt["Location"])
        logP.debug(f"Selected Location: {selPlace}")

        taskGrant = random.randrange(taskWorth[0], taskWorth[1] + 1)
        logP.debug(f"task Grant: {taskGrant}")
        taskDiff = taskWorth[1] - taskWorth[0]
        logP.debug(f"task diff: {taskDiff}")

        selResult = round(
            ((taskGrant - taskWorth[0]) / (2 * taskDiff)) + 0.5, 3
        )

        logP.debug(f"selected result: {selResult}")
        varList = rsltDict.keys()
        logP.debug(
            f"int(selResult * 100): {int(selResult * 100)}, "
            f"{[[x, rsltDict[x]] for x in varList]}"
        )

        selRsltWrd = [
            x
            for x in rsltDict.keys()
            if int(selResult * 100)
            in range(
                int(100 * rsltDict[x][0]),
                int(100 * rsltDict[x][1]),
            )
        ]
        logP.debug(f"selected resulting word: {selRsltWrd}")
        if selRsltWrd:
            selRsltWrd = selRsltWrd[0]

        elif taskWorth[1] == taskGrant:
            selRsltWrd = "flawless"
        logP.debug(f"taskWorth[1] == taskGrant: {taskWorth[1]}, {taskGrant}")

        emptMes.add_field(
            inline=False,
            name=f"{taskType[0]} Task",
            value=(
                f"Please prevent the {selAdj} {selPeep} from "
                f"{selAct} {selPlace}."
            ),
        )

        emptMes.add_field(
            inline=False,
            name="Success!",
            value=(
                f"Congratulations on completing your {taskType[0]} GDV task. "
                f"You accomplished {selRsltWrd} results in your endeavors."
            ),
        )

        try:
            cached_file = load(ctx.guild.id)
        except Exception as e:
            logP.debug(str(e))
        if not cached_file:
            cached_file = {}

        for peep in reversed(xpList):
            logP.debug(f"peep is: {peep}")
            if peep[0].id in cached_file.keys():
                cached_file[peep[0].id].setdefault("invXP", [0, 0, 0])
                cached_file[peep[0].id]["invXP"][-1] += taskGrant * peep[1]
            else:
                cached_file[peep[0].id] = {"Name": peep[0].name}
                cached_file[peep[0].id]["invXP"] = [0, 0, taskGrant * peep[1]]

            if peep[0].id == ctx.author.id or taskAdd != -1:
                emptMes.add_field(
                    name=f"{peep[0].display_name} Earns",
                    value=(
                        f"{taskGrant * peep[1]:,} GDV XP\nTotal of "
                        f"{cached_file[peep[0].id]['invXP'][-1]:,} XP"
                    ),
                )
        if taskAdd == -1:
            emptMes.add_field(
                name="Everyone Else",
                value=f"Earns {taskGrant * taskShrt['Aid']} GDV XP",
            )

        if patrolRole and onCallRole:
            patrolMes = ""
            authInf = cached_file[ctx.author.id]

            currTime = time.time()

            authInf.setdefault("topStatistics", {})
            authInf.setdefault("currPatrol", {})

            authInf["topStatistics"].setdefault("totalTasks", 0)
            authInf["topStatistics"].setdefault("firstTaskTime", currTime)

            authInf["topStatistics"]["totalTasks"] += 1
            authInf["currPatrol"]["lastTaskTime"] = currTime
            if patrolRole not in ctx.author.roles:
                await ctx.author.add_roles(patrolRole)
                if onCallRole in ctx.author.roles:
                    await ctx.author.remove_roles(onCallRole)

                authInf["currPatrol"]["patrolStart"] = currTime
                authInf["currPatrol"]["patrolTasks"] = 1

                authInf["topStatistics"].setdefault("totalPatrols", 0)
                authInf["topStatistics"]["totalPatrols"] += 1

                totPatrols = authInf["topStatistics"]["totalPatrols"]

                patrolMes += (
                    f"{ctx.author.display_name} is starting their Patrol "
                    f"#{totPatrols}!\n"
                )

            else:
                authInf["currPatrol"].setdefault("patrolTasks", 0)
                authInf["currPatrol"]["patrolTasks"] += 1

                currPatrolStart = authInf["currPatrol"].setdefault(
                    "patrolStart", currTime
                )
                if not currPatrolStart:
                    currPatrolStart = currTime
                    authInf["currPatrol"]["patrolStart"] = currTime
                totPatrols = authInf["topStatistics"].setdefault(
                    "totalPatrols", 1
                )
                currPatrolTime = str(
                    datetime.timedelta(
                        seconds=int(round(currTime - currPatrolStart))
                    )
                )
                currPatrolTasks = authInf["currPatrol"]["patrolTasks"]

                patrolMes += (
                    f"{ctx.author.display_name} is continuing their Patrol "
                    f"#{totPatrols}! \nThey have completed "
                    f"{currPatrolTasks} tasks on this patrol over the last "
                    f"{currPatrolTime}"
                )
            emptMes.add_field(inline=False, name="Patrolling", value=patrolMes)

        save(ctx.author.guild.id, cached_file)
        stateL = count(ctx.author)
        currEnhP = stateL[0]
        logP.debug(
            f"{ctx.author.display_name} has {currEnhP} available"
            " enhancements"
        )
        stateG = spent([ctx.author])
        currEnh = int(stateG[0][1])
        logP.debug(f"and enhancments of number = {currEnh}")
        logP.debug(
            f"currEnh {currEnh} < currEnhP {currEnhP}, {currEnh < currEnhP}"
        )
        if currEnh < currEnhP:
            val = (
                f"{ctx.author.display_name} has "
                f"{currEnhP - currEnh} unspent enhancement "
                f"point{pluralInt(currEnhP - currEnh)}."
            )

            emptMes.add_field(name="Unspent Alert", value=val)

        emptMes.set_thumbnail(url=ctx.author.display_avatar)

        emptMes.set_footer(
            text=HOST_NAME, icon_url=self.bot.user.display_avatar
        )

        await ctx.send(embed=emptMes)
        await ctx.message.delete(delay=1)
        return

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("setAgg"),
        description=getDesc("setAgg"),
    )
    async def setAgg(self, ctx: commands.Context, agg: float = None):
        cache = load(ctx.guild.id)
        cache.setdefault(ctx.author.id, {})

        if agg is not None:
            agg = max(0.0, min(agg, 10.0))
            cache[ctx.author.id]["agg"] = agg

        save(ctx.guild.id, cache)
        await ctx.send(
            (
                f"{ctx.author.display_name}'s Aggression is set to "
                f"{cache[ctx.author.id].get('agg', baseDict['AGG'])}"
            )
        )

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["it", "intTask"],
        brief=getBrief("interactiveTask"),
        description=getDesc("interactiveTask"),
    )
    async def interactiveTask(self, ctx: commands.Context):
        autSpent = spent([ctx.author])
        loadedPers = loadAllPers(self.bot)
        opp = None
        possibleOpp = None
        if loadedPers:
            oppDict = {}
            for pers in loadedPers:
                oppDict[pers[0]] = (pers[1], pers[2])
            possibleOpp = [
                x[0]
                for x in loadedPers
                if x[0].bV
                in range(max(0, autSpent[0][1] - 3), autSpent[0][1] + 4)
            ]
            if possibleOpp:
                liveWeights = [0.4, 0.6]
                liveWeights = [1, 0]
                toLoad = random.choices([True, False], weights=liveWeights)[0]
                if toLoad:
                    opp = random.choice(possibleOpp)
                    opp.reRoll()

        if not opp:
            opp = rollTask(self.bot, ctx.author)

        isPersStr = ""
        if toLoad:
            isPersStr = (
                f"persistent (W: {oppDict[opp][0]}, L: {oppDict[opp][1]}) "
            )
        await ctx.send(
            (
                f"It is {aOrAn(opp.rank).lower()} {opp.rank} task to stop the "
                f"{isPersStr}"
                f"{opp.desc} {opp.n.lower()} {opp.task}.\n"
                f"{genderPick(opp.gender, 'their').capitalize()} enhancements "
                f"are ({opp.bV}):\n{blToStr(opp.bL)}"
            )
        )

        # buff the players based on the task rank here
        patrolRole = get(ctx.guild.roles, id=int(ROLE_ID_PATROL))
        supRole = get(ctx.guild.roles, name=SUPE_ROLE)
        onCallRole = get(ctx.guild.roles, id=int(ROLE_ID_CALL))

        aidPick = [patrolRole, onCallRole, supRole]
        taskAdd = taskVar["addP"][opp.rank]

        aidList = pickWeightedSupe(ctx, aidPick, AID_WEIGHT, taskAdd)

        bat = battler(self.bot, [ctx.author, opp])

        if aidList:

            peepBuffDict, aidNames = bat.playerList[0].grabExtra(ctx, aidList)
            notPeepBuffDict = bat.playerList[1].grabExtra(ctx, aidList, True)[
                0
            ]

            peepEmb = buffStrGen(peepBuffDict, bat.playerList[0].n, aidNames)

            notPeepEmb = buffStrGen(
                notPeepBuffDict, bat.playerList[1].n, aidNames, True
            )

            await sendMessage(ctx, [peepEmb, notPeepEmb])

        else:
            await bat.playerList[1].genBuff(ctx)
            return

        bat.playerList[0].play = True
        asyncio.create_task(startDuel(self.bot, ctx, bat, saveOpp=opp))

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["lo"],
        brief=getBrief("loadout"),
        description=getDesc("loadout"),
    )
    async def loadout(
        self, ctx: commands.Context, doWith: str = "all", buildName: str = ""
    ):
        saveStrL = ["save", "s"]
        delStrL = ["delete", "del", "d"]
        loadStrL = ["load", "l"]
        allStrL = ["all", "a"]
        clearStrL = ["clear", "c"]
        toggleStrL = ["toggle", "tog", "t"]

        cache_file = load(ctx.guild.id)

        lowDoWith = doWith.lower()

        cache_file.setdefault(ctx.author.id, {"Name": ctx.author.name})
        cache_file[ctx.author.id].setdefault("builds", {})

        builds = cache_file[ctx.author.id]["builds"]
        if not isinstance(builds, dict):
            builds = dict(builds)
        cache_file[ctx.author.id].setdefault("buildSort", False)

        if (
            lowDoWith not in (allStrL + clearStrL + toggleStrL)
            and doWith not in builds.keys()
            and not buildName
        ):
            await ctx.send("No buildname to edit.")
            return

        if lowDoWith in saveStrL:
            if not buildName:
                await ctx.send("You need a buildname to save this build.")
            builds[buildName] = spent([ctx.author])[0][2]
            await sendMessage(
                ctx,
                (f"Saved {buildName}: " f"{builds[buildName]}"),
            )

        elif lowDoWith in delStrL:
            if not builds:
                await ctx.send("No builds saved")
                return
            if buildName not in builds.keys():
                await ctx.send(f"no saved build named {buildName}")
                return
            await sendMessage(
                ctx,
                ("Removed build: " f"{builds.pop(buildName)}"),
            )

        elif lowDoWith in allStrL:
            if not builds:
                await ctx.send("No builds saved")
                return
            mes = discord.Embed(title="Saved Builds")

            iterList = builds.items()

            if cache_file[ctx.author.id]["buildSort"]:
                iterList = sorted(iterList, key=lambda x: x[0])

            for name, val in iterList:
                if isinstance(val, bool):
                    continue
                FPC = playerFromBuild(self.bot, val, name)
                valStr = FPC.statMessage() + "\n\n"
                valStr += blToStr(val)
                mes.add_field(
                    name=f"Build ({FPC.fB[0]}): {name}", value=valStr
                )
            await sendMessage(ctx, mes)

        elif lowDoWith in clearStrL:
            valLen = len(builds.keys())
            builds = {}
            await ctx.send(f"All {valLen} builds cleared.")

        elif lowDoWith in toggleStrL:
            cache_file[ctx.author.id]["buildSort"] = not cache_file[
                ctx.author.id
            ]["buildSort"]
            terminary = (
                "sorting"
                if cache_file[ctx.author.id]["buildSort"]
                else "not sorting"
            )
            await ctx.send(
                f"Your loadout list is now {terminary} alphabetically."
            )

        elif lowDoWith in loadStrL or doWith in builds.keys():
            if not builds:
                await ctx.send("No builds saved")
                return

            if doWith in builds.keys():
                buildName = doWith

            if buildName not in builds.keys():
                await ctx.send(
                    f"Build {buildName} not found in saved build list"
                )
                return
            authCount = count(ctx.author)
            buildToAdd = funcBuild(builds[buildName])
            if authCount[0] < buildToAdd[0]:
                await ctx.send(
                    (
                        f"You have {authCount[0]} points but require "
                        f"{buildToAdd[0]} for this saved build."
                    )
                )
                return

            toCut = [
                x.name
                for x in ctx.author.roles
                if x.name
                in [
                    masterEhnDict[y]["Name"]
                    for y in masterEhnDict.keys()
                    if masterEhnDict[y]["Rank"] > 0
                ]
            ]
            await cut(ctx, [ctx.author], toCut)
            await toAdd(ctx, ctx.author, buildToAdd[2])

        else:
            await ctx.send(f"{doWith} is not a recognised option.")

        cache_file[ctx.author.id]["builds"] = builds
        save(ctx.guild.id, cache_file)

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["gen"],
        brief=getBrief("generate"),
        description=getDesc("generate"),
    )
    async def generate(
        self,
        ctx: commands.Context,
        val: int = 5,
        typ: str = "",
        *,
        typeRank: str = "",
    ):
        if typeRank:
            fixArg = typeRank.replace(" ", ",")
            fixArg = fixArg.replace(";", ",")
            iniBuild = [x.strip() for x in fixArg.split(",") if x.strip()]
        else:
            iniBuild = typeRank.split()
        if typ:
            typ = typ.lower()
        if val < 0:
            await ctx.send("A positive integer is required")
            return
        if typ not in leader.keys():
            if typ in leader.values():
                typ = [x for x in leader.keys() if leader[x] == typ]
                if typ:
                    typ = typ[0]
            else:
                typ = ""
        build = genBuild(val, typ, iniBuild)

        mes = discord.Embed(title="Generated Build")
        if build:
            costBuild = funcBuild(build)
            if not typ:
                top = leader[highestEhn(build, False)]
            else:
                top = leader[typ]
            buildStr = blToStr(build)
            mes.add_field(
                name=f"{top} build for {costBuild[0]} points",
                value=f"{buildStr}",
            )
            await ctx.send(embed=mes)
            logP.debug(
                f"For {costBuild[0]} points build {build} was generated"
            )

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["a"],
        brief=getBrief("add"),
        description=getDesc("add"),
    )
    # add role command available to all PERMROLES users
    async def add(self, ctx: commands.Context, *, typeRank: str = ""):

        # fetch message author and their current enhancement roles
        # as well as the build for those roles
        user = ctx.author
        userSpent = spent([user])
        userEnhancements = userSpent[0][2]
        userHas = funcBuild(userEnhancements)
        userHasBuild = userHas[2]
        specified = (
            False
            if not typeRank
            else False
            if typeRank in leader.keys()
            else True
        )

        pointTot = count(user)
        if pointTot[0] <= userHas[0]:
            await ctx.send("User has no spare enhancement points.")
            return
        # if author did not provide an enhancement to add, return
        if not typeRank:
            buildList = [highestEhn(userEnhancements)]
            typeRank = buildList[0]
        # otherwise split the arglist into a readable shorthand enhancment list
        else:
            fixArg = typeRank.replace(" ", ",")
            fixArg = fixArg.replace(";", ",")
            buildList = [x.strip() for x in fixArg.split(",") if x.strip()]

        logP.debug(buildList)

        buildList, userEnhancements = checkAddBuild(
            buildList, userEnhancements
        )

        # add requested enhancements to current user build
        # then grab the information for this new user build
        userWants = funcBuild(userEnhancements)
        userWantsCost = userWants[0]
        userWantsBuild = userWants[2]

        logP.debug(
            f"{user} with point total {pointTot[0]} has {userHas[0]} "
            f"{userHasBuild} and wants {userWantsCost} {userWantsBuild}"
        )

        # check to ensure user has enough enhancement points to
        # get requested additions
        if pointTot[0] < userWants[0]:
            userWantsIni = genBuild(pointTot[0], typeRank, userSpent[0][2])
            userWants = funcBuild(userWantsIni)
            userWantsBuild = userWants[2]
            if specified or pointTot[0] < userWants[0]:
                useDict = masterEhnDict
                await ctx.send(
                    (
                        f"{user.display_name} needs {userWantsCost} "
                        "available enhancements for "
                        f"{[useDict[x]['Name'] for x in buildList]} "
                        f"but only has {pointTot[0]}"
                    )
                )
                return
        await toAdd(ctx, user, userWantsBuild)

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["p"],
        brief=getBrief("points"),
        description=getDesc("points"),
    )
    # command to get author or specified user(s) enhancement total
    # and available points
    async def points(self, ctx: commands.Context, *, memberList: str = ""):
        users = await memGrab(ctx, memberList)
        # restrict user list to those with SUPEROLE
        supeUsers = isSuper(self.bot, users)
        if not supeUsers:  # if no SUPEROLE users in list
            await ctx.send(f"Your list contains no {SUPE_ROLE}'s")
            return
        await pointsLeft(ctx, supeUsers)

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["l"],
        brief=getBrief("list"),
        description=getDesc("list"),
    )
    # help level command to list the available enhancements and the
    # shorthand to use them in commands
    async def list(self, ctx: commands.Context):
        # dynamic message to reduce bot messages sent
        mes = discord.Embed(
            title="Enhancements List",
            description=(
                "Use the 3 letter shorthand along with the rank you a"
                "re querying for commands.\nEx: str1 for the first ra"
                "nk of strength."
            ),
        )

        # add each enhancement and
        # the total ranks available to the message to return
        for group in ENHLIST:

            # check for mental clarity and mental celerity exception
            if group[0][0:3].lower() == "men":
                shorthand = group[0][7:10]
            else:
                shorthand = group[0][0:3]

            mes.add_field(
                name=group[0],
                value=(
                    f"{shorthand.lower()} of {group[1]} "
                    f"rank{pluralInt(group[1])}"
                ),
            )

        # return enhancement list to command caller
        logP.debug(mes.to_dict())
        mes.set_footer(text="Starred enhancements require advanced roles")
        await ctx.send(embed=mes)

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["b"],
        brief=getBrief("build"),
        description=getDesc("build"),
    )
    # build command to theory craft and check the prereqs for differnet
    # enhancement ranks can be used in conjunction with points command to
    # determine if user can implement a build
    async def build(
        self,
        ctx: commands.Context,
        mem: typing.Optional[discord.Member] = None,
        *,
        typeRank: str = "",
    ):
        logP.debug(typeRank)

        if not mem:
            mem = ctx.author

        # check for args, else use user's current build
        # split args into iterable shorthand list
        if typeRank:
            buildList = buildFromString(typeRank)
        else:
            buildList = spent([mem])[0][2]
        logP.debug(f"buildList = {buildList}")

        # fetch cost and requisite list for build
        buildTot = funcBuild(buildList)

        # return build to command caller
        mes = discord.Embed(
            title="Enhancement Build",
            description=(
                f"This build requires {buildTot[0]} enhancement "
                f"point{pluralInt(buildTot[0])}."
            ),
        )
        mes.add_field(
            inline=False, name="Build Enhancements", value=buildTot[1]
        )
        mes.add_field(
            inline=False,
            name="Required Enhancements",
            value=reqEnd([buildTot[0], buildTot[2]]),
        )
        FPC = playerFromBuild(self.bot, strList(buildTot[2]), "NA")
        mes.add_field(inline=False, name="Stats", value=FPC.statMessage())
        await ctx.send(embed=mes)

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["leaderboard"],
        brief=getBrief("top"),
        description=getDesc("top"),
    )
    # top 10 user leaderboard for number of used enhancements
    async def top(
        self,
        ctx: commands.Context,
        lead: typing.Optional[int] = int(LEAD_LIMIT),
        page: typing.Optional[int] = int(1),
        *,
        enh: str = "",
    ):
        enhL = enh.lower()

        xpKey = ["xp", "gdv"]
        patrolKey = {
            "long": "Longest Patrol",
            "active": "Most Active Patrol",
            "tasks": "Total Completed Tasks",
            "patrols": "Total Completed Patrols",
        }
        patrolLoad = {
            "long": "longestPatrol",
            "active": "mostActivePatrol",
            "tasks": "totalTasks",
            "patrols": "totalPatrols",
        }

        if lead < 1:
            lead = 1
        strtLead = page * lead - lead
        endLead = page * lead

        if enhL in xpKey:
            serverXP = load(ctx.guild.id)
            serverXP: dict[int, dict] = countIdList(ctx, serverXP.keys())
            if enhL == xpKey[0]:
                resubXPList = [
                    [ctx.guild.get_member(x), serverXP[x]["invXP"][-1]]
                    for x in serverXP.keys()
                    if ctx.guild.get_member(x)
                ]
            else:
                resubXPList = [
                    [ctx.guild.get_member(x), serverXP[x].get("gdv", 0)]
                    for x in serverXP.keys()
                    if ctx.guild.get_member(x)
                ]
            pointList = sorted(resubXPList, key=lambda x: -x[1])

            leaderMes = discord.Embed(title=f"{enh.upper()} Leaderboard")

        elif enhL in patrolKey.keys():
            peepList = load(ctx.guild.id)
            grabbedStatList = []

            for peep in peepList:
                topStats = peepList[peep].get("topStatistics", {})
                peepScore = topStats.get(patrolLoad[enhL], 0)
                if peepScore:
                    grabbedStatList.append(
                        [ctx.guild.get_member(peep), peepScore]
                    )

            pointList = sorted(grabbedStatList, key=lambda x: -x[1])

            leaderMes = discord.Embed(title=f"{patrolKey[enhL]} Leaderboard")

        elif enh:
            if enhL not in leader.keys():
                if enh not in leader.values():
                    await ctx.send(
                        (f"No enhancement could be found for type: {enh}")
                    )
                    return
            else:
                enh = leader[enh]
            peepDict = topEnh(ctx, enh)

            sumPeep = sum(peepDict.values())
            lenPeep = len(peepDict.keys())
            avPeep = round(sumPeep / lenPeep, 2)

            leaderMes = discord.Embed(
                title=f"{enh} Enhancement Leaderboard",
                description=(
                    f"{enh} is being used by {lenPeep} "
                    f"host{pluralInt(lenPeep)} for a total of "
                    f"{sumPeep} enhancement "
                    f"point{pluralInt(sumPeep)} spent.\nFor an "
                    f"average of {avPeep}."
                ),
            )

            unsortedDict = [(x, y) for x, y in peepDict.items()]
            pointList = sorted(unsortedDict, key=lambda x: -x[1])
        else:
            # list of users bot has access to
            guildList = self.bot.users
            logP.debug(f"Guild list is of length: {len(guildList)}")

            # restrict list to those with SUPEROLE
            supeList = isSuper(self.bot, guildList)
            logP.debug(f"Supe list is of length: {len(supeList)}")

            # fetch points of each SUPEROLE user
            pointList = spent(supeList)

            # sort list of users with enhancements by
            # number of enhancements; descending
            pointList = sorted(pointList, key=lambda x: x[1], reverse=True)
            totHosts = sum(
                [
                    len(x.members)
                    for x in [
                        get(y.roles, name=SUPE_ROLE) for y in self.bot.guilds
                    ]
                ]
            )
            totPoints = sum([x[1] for x in pointList])
            desc = (
                f"There is a total of {totHosts} "
                f"host{pluralInt(totHosts)} with a sum of "
                f"{totPoints} enhancement "
                f"point{pluralInt(totPoints)} spent."
            )

            leaderMes = discord.Embed(
                title="Host Leaderboard", description=desc
            )
        # counter and blank message to track user number and
        # return as a single message
        i = strtLead + 1
        for group in pointList[strtLead:endLead]:
            if not enh:
                leaderMes.add_field(
                    inline=True,
                    name=f"**{i}** - {group[0].display_name}",
                    value=f"\t{group[1]} enhancement{pluralInt(group[1])}",
                )
            else:
                if enhL in xpKey:
                    leaderMes.add_field(
                        inline=True,
                        name=f"**{i}** - {group[0].display_name}",
                        value=f"\t{group[1]:,} {enh.upper()}",
                    )
                elif enhL in patrolKey.keys():
                    if enhL == "active" or enhL == "tasks":
                        leaderMes.add_field(
                            inline=True,
                            name=f"**{i}** - {group[0].display_name}",
                            value=f"\t{group[1]} task{pluralInt(group[1])}",
                        )
                    elif enhL == "long":
                        leaderMes.add_field(
                            inline=True,
                            name=f"**{i}** - {group[0].display_name}",
                            value=f"\t{datetime.timedelta(seconds=group[1])}",
                        )
                    elif enhL == "patrols":
                        leaderMes.add_field(
                            inline=True,
                            name=f"**{i}** - {group[0].display_name}",
                            value=f"\t{group[1]} patrol{pluralInt(group[1])}",
                        )
                else:
                    leaderMes.add_field(
                        inline=True,
                        name=f"**{i}** - {group[0].display_name}",
                        value=f"\tRank {group[1]} {enh}",
                    )

            i += 1

        leaderMes.set_footer(
            text=HOST_NAME, icon_url=self.bot.user.display_avatar
        )
        # return leaderboard to command caller
        await sendMessage(ctx, leaderMes)

    @commands.command(
        enabled=COMMANDS_ON,
        brief=getBrief("rAdd"),
        description=getDesc("rAdd"),
    )
    async def rAdd(self, ctx: commands.Context, incAmount: int = 1):
        user = ctx.author
        await rAddFunc(ctx, [user], incAmount)
        await ctx.send(f"Finished rAdd-ing to {user.display_name}")

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["c", "clean"],
        brief=getBrief("clear"),
        description=getDesc("clear"),
    )
    # remove unrestricted enhancements from command caller
    async def clear(self, ctx: commands.Context):
        # rank 0 enhancements are either restricted or the SUPEROLE,
        # which should not be removed with this command
        toCut = [
            x.name
            for x in ctx.author.roles
            if x.name
            in [
                masterEhnDict[y]["Name"]
                for y in masterEhnDict.keys()
                if masterEhnDict[y]["Rank"] > 0
            ]
        ]
        logP.debug(toCut)
        await cut(ctx, [ctx.author], toCut)

    @commands.command(
        enabled=COMMANDS_ON,
        hidden=HIDE,
        aliases=["x"],
        brief=getBrief("xpGrab"),
        description=getDesc("xpGrab"),
    )
    @commands.cooldown(1, 1, commands.BucketType.default)
    async def xpGrab(self, ctx: commands.Context, *, mem: str = ""):
        typeMem = await memGrab(ctx, mem)
        pointList = spent(typeMem)
        i = 0
        savedCache = load(ctx.guild.id)
        scrollList = [x for x in typeMem if x.id in savedCache.keys()]
        if len(typeMem) != len(scrollList):
            await ctx.send(
                (
                    f"Of list of {len(typeMem)}, "
                    f"{len(scrollList)} are in saveFile."
                )
            )
        for peep in scrollList:
            mes = discord.Embed(title=f"{peep.display_name} Stats")
            stuff = count(peep)
            group = pointList[i]
            unspent = stuff[0] - group[1]

            mes.set_thumbnail(url=peep.display_avatar)

            mes.add_field(name="MEE6 xp", value=f"{stuff[3][0]:,}")
            mes.add_field(name="TATSU xp", value=f"{stuff[3][1]:,}")
            mes.add_field(name="GDV xp", value=f"{stuff[3][-1]:,}")
            mes.add_field(name="Total xp", value=f"{stuff[2]:,}")
            mes.add_field(name="GDV", value=f"{round(stuff[1], 2)}")
            mes.add_field(
                name=f"Enhancement Point{pluralInt(stuff[0])}",
                value=f"{stuff[0]}",
            )

            nextGDV = int(stuff[1]) + 1
            nextGDV_XP = lvlEqu(nextGDV, 1)
            nextGDVneedXP = nextGDV_XP - stuff[2]

            mes.add_field(
                name="Next GDV",
                value=f"{round(nextGDVneedXP, 3):,} XP",
            )

            nextEnhP = int(5 * (int(stuff[1] / 5) + 1))
            nextEnhP_XP = lvlEqu(nextEnhP, 1)
            nextEnhPneedXP = nextEnhP_XP - stuff[2]

            mes.add_field(
                name="Next EP",
                value=f"{round(nextEnhPneedXP, 3):,} XP",
            )

            mes.add_field(
                name=(f"Unspent EP{pluralInt(unspent)}"),
                value=unspent,
            )

            mes.set_footer(
                text=f"{peep.name}#{peep.discriminator} - {HOST_NAME}",
                icon_url=peep.display_avatar,
            )
            patrolRole = get(ctx.guild.roles, id=int(ROLE_ID_PATROL))
            isPatrolStr = "Not Patrolling"
            patrolStats = ""
            if patrolRole:
                if peep in patrolRole.members:
                    isPatrolStr = (
                        f"Patrol #{stuff[5].setdefault('totalPatrols',1)}"
                    )

                    currTime = time.time()

                    currPatrolStart = stuff[4].setdefault(
                        "patrolStart", currTime
                    )

                    if currPatrolStart:
                        patrolLength = currTime - currPatrolStart
                    else:
                        patrolLength = 0
                    currPatrolTime = str(
                        datetime.timedelta(seconds=int(round(patrolLength)))
                    )
                    currPatrolTasks = stuff[4].setdefault("patrolTasks", 1)

                    patrolStats += (
                        f"{peep.display_name} has completed "
                        f"{currPatrolTasks} tasks on this patrol over the "
                        f"last {currPatrolTime}"
                    )
                mes.add_field(name="Patrol", value=isPatrolStr)
                if patrolStats:
                    mes.add_field(
                        inline=False, name="Patrol Stats", value=patrolStats
                    )

            await ctx.send(embed=mes)
            i += 1

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["s"],
        brief=getBrief("stats"),
        description=getDesc("stats"),
    )
    async def stats(self, ctx: commands.Context, peep: discord.Member = False):
        if not peep:
            peep = ctx.author
        p = player(peep, self.bot)
        mes = discord.Embed(
            title=f"{p.n} Stats",
            description=p.statMessage(),
        )
        mes.set_thumbnail(url=p.p.display_avatar)
        mes.set_footer(
            text=f"{p.p.name}#{p.p.discriminator} - {HOST_NAME}",
            icon_url=p.picUrl,
        )

        await ctx.send(embed=mes)

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["gd", "genD", "genDuel"],
        brief=getBrief("generateDuel"),
        description=getDesc("generateDuel"),
    )
    async def generateDuel(self, ctx: commands.Context, diffVal: int = 0):
        FPC: NPC = NPC_from_diff(ctx, diffVal)
        mes = f"Creating a duel against {FPC.n}\n**Enhancements**\n"

        mes += blToStr(FPC.bL)

        await sendMessage(ctx, mes)

        bat = battler(self.bot, [ctx.author, FPC])
        await bat.findPlayers(0)
        await bat.playerList[1].genBuff(ctx)
        asyncio.create_task(startDuel(self.bot, ctx, bat))

    @commands.command(
        enabled=COMMANDS_ON,
        aliases=["d"],
        brief=getBrief("duel"),
        description=getDesc("duel"),
    )
    async def duel(
        self,
        ctx: commands.Context,
        dontAsk: typing.Optional[
            typing.Union[
                typing.Literal[1], typing.Literal[2], typing.Literal[3]
            ]
        ] = ASK_SELF,
        opponent: typing.Union[discord.Member, str] = False,
    ):
        if not dontAsk == ASK_NPC:
            if not isinstance(opponent, discord.Member):
                if not opponent:
                    opponent = get(ctx.guild.members, id=DEFAULT_DUEL_OPP)
                else:

                    raise notSupeDuel("Not a supe.")
            nameList = [x.name for x in opponent.roles]
            if (str(SUPE_ROLE) not in nameList) and str(
                "Bots"
            ) not in nameList:
                raise notSupeDuel(f"{opponent} is not a {SUPE_ROLE}.")
            bat = battler(self.bot, [ctx.author, opponent])

        else:
            npcPlayer = [
                npcDict[x]
                for x in npcDict.keys()
                if str(opponent) == npcDict[x]["name"] or str(opponent) == x
            ]
            if npcPlayer:
                npcPlayer = npcPlayer[0]

                logP.debug(f"Found npc: {npcPlayer}")

                npcOpp = NPC(self.bot, npcPlayer)

                bat = battler(
                    self.bot,
                    [ctx.author, npcOpp],
                )
            else:
                raise notNPC(f"{opponent} is not an NPC")
        await bat.findPlayers(dontAsk)
        asyncio.create_task(startDuel(self.bot, ctx, bat))


def checkAddBuild(listAdd: list = [], listBase: list = []):
    enhNumList = masterEhnDict.keys()
    userKeyList = {}
    listRet = []
    listBaseNew = listBase.copy()

    for item in listBaseNew:
        typ = item[:3]
        typRank = int(item[3:])
        logP.debug(f"Splitting {item} into {typ} and {typRank}")
        userKeyList[typ] = typRank

    for item in listAdd:
        if item in listBaseNew:
            continue
        elif item in enhNumList:
            listBaseNew.append(item)
            listRet.append(item)
            logP.debug(f"Adding {item} to listBase")
            continue
        elif item in leader.values():
            for shrt in leader.keys():
                if item == leader[shrt]:
                    item = shrt
        if item in leader.keys():
            if leader[item] in restrictedList:
                continue

            if item in userKeyList.keys():
                strAdd = str(item) + str(userKeyList[item] + 1)
                logP.debug(f"Adding {strAdd} to listBase")
                listBaseNew.append(strAdd)
                listRet.append(strAdd)
            else:
                strAdd = str(item) + str(1)
                logP.debug(f"Adding {strAdd} to listBase")
                listBaseNew.append(strAdd)
                listRet.append(strAdd)

    return listRet, listBaseNew


def highestEhn(userEhnList: list = [], belowTop: bool = True):
    topRank = 0
    topRankStr = ""
    multTopList = []
    for item in userEhnList:
        rank = int(item[3:])
        typ = str(item[:3])
        if rank > topRank:
            if rank == 10:
                if belowTop:
                    continue
            topRank = rank
            multTopList.clear()
            multTopList.append(typ)
            topRankStr = typ
        elif rank == topRank:
            multTopList.append(typ)

    if len(multTopList) > 1:
        topRankStr = str(random.choice(multTopList))

    if not topRankStr:
        pickList = [
            x
            for x in leader.keys()
            if leader[x] not in restrictedList and x not in reqResList
        ]
        topRankStr = random.choice(pickList)
    return topRankStr


# function to setup cog
def setup(bot: commands.Bot):
    bot.add_cog(roleCommands(bot))
