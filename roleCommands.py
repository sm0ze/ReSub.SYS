# roleCommands.py

import asyncio
import random
import typing

import discord
from discord.ext import commands, tasks
from discord.utils import get

import log
from battle import NPC, battler, player
from exceptions import noFields, notADuel, notNPC, notSupeDuel
from sharedDicts import (
    leader,
    masterEhnDict,
    moveOpt,
    npcDict,
    posTask,
    powerTypes,
    restrictedList,
    rsltDict,
    taskVar,
)
from sharedFuncs import (
    count,
    countOf,
    cut,
    funcBuild,
    getBrief,
    getDesc,
    load,
    lvlEqu,
    memGrab,
    nON,
    pluralInt,
    pointsLeft,
    reqEnd,
    save,
    spent,
    toAdd,
    topEnh,
    trim,
)
from sharedVars import (
    BOTTURNWAIT,
    COMMANDSROLES,
    COMON,
    DEFDUELOPP,
    DL_ARC_DUR,
    HIDE,
    HOSTNAME,
    LEADLIMIT,
    MANAGER,
    PLAYERTURNWAIT,
    ROUNDLIMIT,
    SUPEROLE,
    TASKCD,
)

logP = log.get_logger(__name__)


ENHLIST = [(x, y) for (x, y) in powerTypes.items()]

# TODO: implement this and similiar instead of
# multiple enhancement.dict.keys() calls
# enhancement (type, rank) pairs for list command


class roleCommands(
    commands.Cog,
    name=f"{SUPEROLE} Commands",
    description=getDesc("roleCommands"),
):
    def __init__(
        self, bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot]
    ):
        self.bot = bot
        self.grabLoop.start()

    # Check if user has guild role
    async def cog_check(self, ctx: commands.Context):
        async def predicate(ctx: commands.Context):
            for role in COMMANDSROLES:
                chkRole = get(ctx.guild.roles, name=role)
                if chkRole in ctx.message.author.roles:
                    return chkRole
            raise commands.CheckFailure(
                (
                    "You do not have permission as you are missing a role in "
                    f"this list: {COMMANDSROLES}\nThe super command can be "
                    "used to gain the Supe role"
                )
            )

        # messy implementation for Supe
        return commands.check(await predicate(ctx))

    @tasks.loop(minutes=30)
    async def grabLoop(self):
        await self.bot.wait_until_ready()
        roleGrab = None
        for guild in self.bot.guilds:
            roleGrab = get(guild.roles, name=SUPEROLE)
            if roleGrab:
                await count(roleGrab.members)

    @commands.command(
        enabled=COMON,
        brief=getBrief("trim"),
        description=getDesc("trim"),
    )
    # command to trim command caller of extra roles. OBSOLETE due to cut call
    # after role add in add command
    async def trim(self, ctx: commands.Context, *, member: str = ""):
        logP.debug("funcTrim START")

        memberList = await memGrab(self, ctx, "")  # member)
        logP.debug(f"memberlist = {memberList}")

        await cut(ctx, memberList)
        logP.debug("funcTrim END")
        return

    @commands.command(
        enabled=COMON,
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
        enabled=COMON,
        aliases=["t"],
        brief=getBrief("task"),
        description=getDesc("task"),
    )
    @commands.cooldown(1, TASKCD, type=commands.BucketType.user)
    async def task(self, ctx: commands.Context):
        """
        It can be 60% minor, you only,
        25% moderate +1 random supe gets half xp,
        10% major +3 random supes get half and
        5% [imperative] everyone gets quarter xp - Geminel
        https://discord.com/channels/822410354860097577/823225800073412698/907167823284019231
        """

        taskType = random.choices(
            taskVar["taskOpt"][0],
            cum_weights=taskVar["taskWeight"],
        )
        taskShrt = posTask[taskType[0]]
        taskWorth = taskShrt["Worth"]
        logP.debug(f"Task is worth {taskWorth}")
        taskAdd = taskShrt["Add"]
        logP.debug(f"Task can have additional {taskAdd} peeps")

        if taskAdd:
            logP.debug(f"Guild has {len(ctx.message.guild.roles)} roles")
            peepToAdd = get(ctx.message.guild.roles, name=SUPEROLE)
            logP.debug(f"{peepToAdd.id}, {peepToAdd.name}")
            if taskAdd == -1:
                addPeeps = peepToAdd.members
                addPeeps.remove(ctx.message.author)
                # addNames = "every host of the Superhero Enhancement System!"
            else:
                addPeeps = random.sample(peepToAdd.members, k=taskAdd + 1)
                logP.debug(f"peeps list is: {addPeeps}")
                if ctx.message.author in addPeeps:
                    addPeeps.remove(ctx.message.author)
            xpList = [[x, taskShrt["Aid"]] for x in addPeeps[:taskAdd]]
            xpList.append([ctx.message.author, 1])
        else:
            addPeeps = ""
            xpList = [[ctx.message.author, 1]]
        logP.debug("xpList = ", xpList)
        logP.debug(f"{taskType}\nTask XP: {lvlEqu(taskWorth[0], 1)}")
        emptMes = discord.Embed(
            title=f"Alert, {nON(ctx.message.author)}!",
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

        logP.debug("selected result: ", selResult)
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
            authInf = load(ctx.message.author.guild.id)
        except Exception as e:
            logP.debug(str(e))
        if not authInf:
            authInf = {}

        for peep in reversed(xpList):
            logP.debug(f"peep is: {peep}")
            if peep[0].id in authInf.keys():
                authInf[peep[0].id]["invXP"][-1] += taskGrant * peep[1]
            else:
                authInf[peep[0].id] = {"Name": peep[0].name}
                authInf[peep[0].id]["invXP"] = [0, 0, taskGrant * peep[1]]

            if peep[0].id == ctx.message.author.id or taskAdd != -1:
                emptMes.add_field(
                    name=f"{nON(peep[0])} Earns",
                    value=(
                        f"{taskGrant * peep[1]:,} GDV XP\nTotal of "
                        f"{authInf[peep[0].id]['invXP'][-1]:,} XP"
                    ),
                )
        if taskAdd == -1:
            emptMes.add_field(
                name="Everyone Else",
                value=f"Earns {taskGrant * taskShrt['Aid']} GDV XP",
            )

        save(ctx.message.author.guild.id, authInf)
        stateL = await countOf(ctx.message.author)
        currEnhP = stateL[0]
        logP.debug(
            f"{nON(ctx.message.author)} has {currEnhP} available"
            " enhancements"
        )
        stateG = spent([ctx.message.author])
        currEnh = int(stateG[0][1])
        logP.debug(f"and enhancments of number = {currEnh}")
        logP.debug(
            f"currEnh {currEnh} < currEnhP {currEnhP}, {currEnh < currEnhP}"
        )
        if currEnh < currEnhP:
            val = (
                f"{nON(ctx.message.author)} has "
                f"{currEnhP - currEnh} unspent enhancement "
                f"point{pluralInt(currEnhP - currEnh)}."
            )

            emptMes.add_field(name="Unspent Alert", value=val)

        emptMes.set_thumbnail(url=ctx.message.author.display_avatar)

        emptMes.set_footer(
            text=HOSTNAME, icon_url=self.bot.user.display_avatar
        )
        await ctx.send(embed=emptMes)
        await ctx.message.delete(delay=1)
        return

    @commands.command(
        enabled=COMON,
        aliases=["gen"],
        brief=getBrief("generate"),
        description=getDesc("generate"),
    )
    async def generate(self, ctx: commands.Context, val: int = 5, typ=""):
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
        build = genBuild(val, typ)
        logP.debug(f"For {val} points build {build} was generated")
        mes = discord.Embed(title="Generated Build")
        if build:
            costBuild = funcBuild(build)
            if not typ:
                top = leader[highestEhn(build, False)]
            else:
                top = leader[typ]
            buildNames = [masterEhnDict[x]["Name"] for x in build]
            buildStr = ""
            for x in buildNames:
                buildStr += f"{x} \n"
            mes.add_field(
                name=f"{top} build for {costBuild[0]} points",
                value=f"{buildStr}",
            )
            await ctx.send(embed=mes)

    @commands.command(
        enabled=COMON,
        aliases=["a"],
        brief=getBrief("add"),
        description=getDesc("add"),
    )
    # add role command available to all PERMROLES users
    async def add(self, ctx: commands.Context, *, typeRank=""):

        # fetch message author and their current enhancement roles
        # as well as the build for those roles
        user = ctx.message.author
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

        pointTot = await count(user, 1)
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
                        f"{nON(user)} needs {userWantsCost} "
                        "available enhancements for "
                        f"{[useDict[x]['Name'] for x in buildList]} "
                        f"but only has {pointTot[0]}"
                    )
                )
                return
        await toAdd(ctx, user, userWantsBuild)

    @commands.command(
        enabled=COMON,
        aliases=["p"],
        brief=getBrief("points"),
        description=getDesc("points"),
    )
    # command to get author or specified user(s) enhancement total
    # and available points
    async def points(self, ctx: commands.Context, *, memberList: str = ""):
        users = await memGrab(self, ctx, memberList)
        # restrict user list to those with SUPEROLE
        supeUsers = isSuper(self, users)
        if not supeUsers:  # if no SUPEROLE users in list
            await ctx.send(f"Your list contains no {SUPEROLE}'s")
            return
        await pointsLeft(ctx, supeUsers)

    @commands.command(
        enabled=COMON,
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
        enabled=COMON,
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
            fixArg = typeRank.replace(" ", ",")
            fixArg = fixArg.replace(";", ",")
            buildList = [x.strip() for x in fixArg.split(",") if x.strip()]
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
        await ctx.send(embed=mes)

    @commands.command(
        enabled=COMON,
        aliases=["leaderboard"],
        brief=getBrief("top"),
        description=getDesc("top"),
    )
    # top 10 user leaderboard for number of used enhancements
    async def top(
        self,
        ctx: commands.Context,
        lead: typing.Optional[int] = int(LEADLIMIT),
        page: typing.Optional[int] = int(1),
        *,
        enh: str = "",
    ):

        xpKey = ["xp", "gdv"]
        if MANAGER in [str(x.name) for x in ctx.message.author.roles]:
            leade = lead
        else:
            if lead < LEADLIMIT:
                leade = lead
            else:
                leade = LEADLIMIT
        if leade < 1:
            leade = 1
        strtLead = page * leade - leade
        endLead = page * leade

        if enh.lower() in xpKey:
            serverXP = load(ctx.message.author.guild.id)
            if enh == xpKey[0]:
                resubXPList = [
                    [ctx.message.guild.get_member(x), serverXP[x]["invXP"][-1]]
                    for x in serverXP.keys()
                ]
            else:
                resubXPList = [
                    [ctx.message.guild.get_member(x), serverXP[x]["gdv"]]
                    for x in serverXP.keys()
                ]
            pointList = sorted(resubXPList, key=lambda x: x[1], reverse=True)

            blankMessage = discord.Embed(title=f"{enh.upper()} Leaderboard")

        elif enh:
            if enh not in leader.keys():
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

            blankMessage = discord.Embed(
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
            pointList = sorted(unsortedDict, key=lambda x: x[1], reverse=True)
        else:
            # list of users bot has access to
            guildList = self.bot.users
            logP.debug(f"Guild list is of length: {len(guildList)}")

            # restrict list to those with SUPEROLE
            supeList = isSuper(self, guildList)
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
                        get(y.roles, name=SUPEROLE) for y in self.bot.guilds
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

            blankMessage = discord.Embed(
                title="Host Leaderboard", description=desc
            )
        # counter and blank message to track user number and
        # return as a single message
        i = strtLead + 1
        for group in pointList[strtLead:endLead]:
            if not enh:
                blankMessage.add_field(
                    inline=True,
                    name=f"**{i}** - {nON(group[0])}",
                    value=f"\t{group[1]} enhancements",
                )
            else:
                if not enh.lower() in xpKey:
                    blankMessage.add_field(
                        inline=True,
                        name=f"**{i}** - {nON(group[0])}",
                        value=f"\tRank {group[1]} {enh}",
                    )
                else:
                    blankMessage.add_field(
                        inline=True,
                        name=f"**{i}** - {nON(group[0])}",
                        value=f"\t{group[1]:,} {enh.upper()}",
                    )
            i += 1

        blankMessage.set_footer(
            text=HOSTNAME, icon_url=self.bot.user.display_avatar
        )
        # return leaderboard to command caller
        await ctx.send(embed=blankMessage)

    @commands.command(
        enabled=COMON,
        brief=getBrief("rAdd"),
        description=getDesc("rAdd"),
    )
    async def rAdd(self, ctx: commands.Context):
        user = ctx.message.author
        userSpent = spent([user])
        userEnhancements = userSpent[0][2]
        userHas = funcBuild(userEnhancements)
        pointTot = await count(user, 1)
        if pointTot[0] < userHas[0] + 1:
            await ctx.send(
                f"{user} does not have enough points to further enhance with."
            )
            return
        randPlusBuild = genBuild(userHas[0] + 1, "", userEnhancements)
        randPlus = funcBuild(randPlusBuild)
        await toAdd(ctx, user, randPlus[2])

    @commands.command(
        enabled=COMON,
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
            for x in ctx.message.author.roles
            if x.name
            in [
                masterEhnDict[y]["Name"]
                for y in masterEhnDict.keys()
                if masterEhnDict[y]["Rank"] > 0
            ]
        ]
        logP.debug(toCut)
        await cut(ctx, [ctx.message.author], toCut)

    @commands.command(
        enabled=COMON,
        hidden=HIDE,
        aliases=["x"],
        brief=getBrief("xpGrab"),
        description=getDesc("xpGrab"),
    )
    @commands.cooldown(1, 1, commands.BucketType.default)
    async def xpGrab(self, ctx: commands.Context, *, mem: str = ""):
        typeMem = await memGrab(self, ctx, mem)
        typeMem = [typeMem[0]]
        pointList = spent(typeMem)
        i = 0
        for peep in typeMem:
            mes = discord.Embed(title=f"{nON(peep)} Stats")
            stuff = await count(peep, 1)
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
                inline=False,
                name="XP to next GDV",
                value=f"{round(nextGDVneedXP, 3):,}",
            )

            nextEnhP = int(5 * (int(stuff[1] / 5) + 1))
            nextEnhP_XP = lvlEqu(nextEnhP, 1)
            nextEnhPneedXP = nextEnhP_XP - stuff[2]

            mes.add_field(
                inline=False,
                name="XP to next Enhancement Point",
                value=f"{round(nextEnhPneedXP, 3):,}",
            )

            mes.add_field(
                inline=False,
                name=(f"Unspent Enhancement Point{pluralInt(unspent)}"),
                value=unspent,
            )

            mes.set_footer(
                text=f"{peep.name}#{peep.discriminator} - {HOSTNAME}",
                icon_url=peep.display_avatar,
            )

            await ctx.send(embed=mes)
            i += 1

    @commands.command(
        enabled=COMON,
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
            text=f"{p.p.name}#{p.p.discriminator} - {HOSTNAME}",
            icon_url=p.pic,
        )

        await ctx.send(embed=mes)

    @commands.command(
        enabled=COMON,
        aliases=["d"],
        brief=getBrief("duel"),
        description=getDesc("duel"),
    )
    async def duel(
        self,
        ctx: commands.Context,
        dontAsk: typing.Optional[
            typing.Union[typing.Literal[1], typing.Literal[2]]
        ] = None,
        opponent: typing.Union[discord.Member, str] = False,
    ):
        if not dontAsk == 2:
            if not isinstance(opponent, discord.Member):
                if not opponent:
                    opponent = get(ctx.guild.members, id=DEFDUELOPP)
                else:
                    raise notSupeDuel("Not a supe.")
            elif str(SUPEROLE) not in [x.name for x in opponent.roles]:
                raise notSupeDuel(f"{opponent} is not a {SUPEROLE}.")
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
        await startDuel(self, ctx, bat)


# restrict list from members to members with SUPEROLE
def isSuper(
    self: roleCommands, guildList: list[discord.User]
) -> list[discord.Member]:
    guilds = self.bot.guilds
    supeGuildList = []
    foundRole = []

    logP.debug(f"Guild list is: {guilds}")

    for guild in guilds:
        logP.debug(f"iter through: {guild}")
        posRole = get(guild.roles, name=SUPEROLE)
        if posRole:
            logP.debug(f"found role: {posRole}")
            foundRole.append(posRole)
    if foundRole:
        for role in foundRole:
            logP.debug(f"iter through: {role}")
            for member in role.members:
                if member in guildList:
                    logP.debug(f"appending: {member}")
                    supeGuildList.append(member)

    # return reduced user list
    return supeGuildList


async def playerDuelInput(
    self: roleCommands,
    ctx: commands.Context,
    totRounds: int,
    peep: player,
    battle: battler,
):
    if len(battle.playerList) == 2:
        if peep is battle.playerList[0]:
            notPeep = battle.playerList[1]
        else:
            notPeep = battle.playerList[0]
    else:
        raise notADuel(
            f"Expected a Duel with 2 players not {len(battle.playerList)}"
        )
    statsMes = peep.statMessage()
    statsMes += "\n\n" + battle.adpList(peep, notPeep)
    stats2Mes = notPeep.statMessage()
    stats2Mes += "\n\n" + battle.adpList(notPeep, peep)

    moveStr = ""
    reactionList = []
    moveList = []
    chosenMove = False

    for key in moveOpt.keys():
        moveCost = moveOpt[key]["cost"]
        if moveCost <= peep.sta:
            react = moveOpt[key]["reaction"]
            moveStr += f"{react}: ({moveCost}) {moveOpt[key]['name']}\n"
            moveList.append(key)
            reactionList.append(react)

    mes = discord.Embed(
        title="Game Stats",
        description=f"{totRounds}/{ROUNDLIMIT} Total Rounds",
    )
    mes.add_field(name="Your Current", value=statsMes)
    mes.add_field(name="Opponent", value=stats2Mes)
    mes.set_footer(text=HOSTNAME, icon_url=self.bot.user.display_avatar)
    if peep.missTurn:
        moveStr = "You are exhausted."
    mes.add_field(
        inline=False,
        name=f"Available Moves ({peep.sta} Stamina)",
        value=moveStr,
    )

    msg = await peep.p.send(embed=mes)
    if not peep.missTurn:
        for reac in reactionList:
            await msg.add_reaction(reac)

    def check(reaction, user):
        return user.id == peep.p.id and str(reaction.emoji) in reactionList

    if notPeep.play:
        timeOut = PLAYERTURNWAIT
    else:
        timeOut = BOTTURNWAIT

    active = True
    if not reactionList or peep.missTurn:
        active = False

    while active:
        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", timeout=timeOut, check=check
            )
            logP.debug(f"reaction: {reaction}, user: {user}")
            if str(reaction.emoji) == str(moveOpt["quit"]["reaction"]):
                peep.play = False
                active = False
                break
            for move in moveList:
                logP.debug(
                    [
                        str(moveOpt[move]["reaction"]),
                        "==",
                        str(reaction.emoji),
                        str(reaction.emoji) == str(moveOpt[move]["reaction"]),
                    ]
                )
                if str(reaction.emoji) == str(moveOpt[move]["reaction"]):
                    logP.debug(f"{reaction.emoji} found")
                    chosenMove = True
                    desperate = moveOpt[move]["desperate"]
                    typeMove = moveOpt[move]["type"]
                    moveString = moveOpt[move]["moveStr"]
                    # await msg.remove_reaction(reaction, user)
                    active = False
                    break

        except asyncio.TimeoutError:
            active = False
    if chosenMove:
        if "Focus" == moveString:
            peep.focus()
            [desperate, typeMove, moveString], notPeep = await playerDuelInput(
                self, ctx, totRounds, peep, battle
            )
    else:
        desperate, typeMove, moveString = battle.moveSelf(peep, notPeep)
    return [desperate, typeMove, moveString], notPeep


def genBuild(val: int = 0, typ: str = "", iniBuild: list = []):
    build = []
    buildFinal = []
    pickList = [x for x in leader.keys() if leader[x] not in restrictedList]

    if not typ:
        typ = random.choice(pickList)
        pickList.remove(typ)
    elif typ not in leader.keys():
        if typ[:3] in leader.keys():
            typ = typ[:3]
        else:
            typ = random.choice(pickList)
            pickList.remove(typ)

    logP.debug(f"Building a build of {val} for {typ}")

    checkInt = 1
    building = True
    if not iniBuild:
        searchBuild = [typ + str(checkInt)]
    else:
        searchBuild = iniBuild.copy()
    nextLargest = 0
    secondLoop = 0
    prevBuild = []
    maxTyp = []

    testMax = True
    maxSearch = [typ + str(10)]
    while testMax:
        maxBuild = funcBuild(maxSearch)
        if val > maxBuild[0]:
            logP.debug(f"with {val} points {typ} can be maxed")
            maxTyp.append(typ + str(10))
            build = maxBuild[2]
            typ = random.choice(pickList)
            pickList.remove(typ)
            maxSearch.append(typ + str(10))
            logP.debug(f"new max list is {maxSearch}")
        else:
            testMax = False
    if maxTyp:
        searchBuild = maxTyp.copy()
        searchBuild.append(typ + str(checkInt))

    while building:
        want = funcBuild(searchBuild)
        trimmed = trim(want[1])

        searchBuild = []

        for group in trimmed:
            rank = group[0]
            name = group[1]
            shrt = [x for x in leader.keys() if leader[x] == name]
            if shrt:
                shrt = shrt[0]
            searchBuild.append(str(shrt) + str(rank))

        logP.debug(f"Testing {want[0]} build: {searchBuild}, {want[2]}")
        if want[0] < val:
            checkInt += 1
            if checkInt > 10:
                checkInt = 10
            prevBuild = searchBuild.copy()
            searchBuild.append(typ + str(checkInt))
        elif want[0] == val:
            building = False
            build = want[2]
        else:
            nextLargest += 1
            if nextLargest > len(want[2]) - 1:
                nextLargest = 0
                if secondLoop < 2:
                    secondLoop += 1
                else:
                    build = funcBuild(prevBuild)
                    build = build[2]
                    building = False
            name = want[2][-nextLargest][1]
            rank = want[2][-nextLargest][0]
            shrt = [x for x in leader.keys() if leader[x] == name][0]
            searchBuild = prevBuild.copy()
            searchBuild.append(shrt + str(rank))

    for group in build:
        rank = group[0]
        name = group[1]
        shrt = [x for x in leader.keys() if leader[x] == name]
        if shrt:
            shrt = shrt[0]

        buildFinal.append(str(shrt) + str(rank))
    return buildFinal


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


async def startDuel(
    self: roleCommands,
    ctx: commands.Context,
    bat: battler,
):
    titleString = ""
    for peep in bat.playerList:
        titleString += f"{peep.n}: {bat.isPlay(peep)} Vs. "
    titleString = titleString[:-5]

    mes = discord.Embed(title=titleString)

    for peep in bat.playerList:
        stats = peep.statMessage()
        adpStats = bat.adpList(peep)

        mes.add_field(
            name=f"{peep.n}",
            value=f"{stats}\n\n{adpStats}",
        )

    mes.set_footer(text=HOSTNAME, icon_url=self.bot.user.display_avatar)

    sentMes = await ctx.send(
        embed=mes,
    )

    thrd = await ctx.channel.create_thread(
        name=mes.title,
        message=sentMes,
        auto_archive_duration=DL_ARC_DUR,
        reason=mes.title,
    )
    for peep in bat.playerList:
        if peep.play:
            await thrd.add_user(peep.p)

    winner = None
    mes.add_field(
        inline=False,
        name="TBD Move",
        value="Does Nothing.",
    )
    totRounds = int(0)
    while not winner:
        totRounds += 1
        Who2Move = bat.nextRound()
        iniMove = ""

        move = None
        defPeep = None

        if Who2Move.defending:
            iniMove = Who2Move.defend()
        if Who2Move.play:
            move, defPeep = await playerDuelInput(
                self, ctx, totRounds, Who2Move, bat
            )
        else:

            if len(bat.playerList) == 2:
                if Who2Move is bat.playerList[0]:
                    defPeep = bat.playerList[1]
                else:
                    defPeep = bat.playerList[0]
            else:
                raise notADuel(
                    f"Expected a Duel with 2 players not {len(bat.playerList)}"
                )
            move = bat.moveSelf(Who2Move, defPeep)

        moveStr, winner = bat.move(Who2Move, defPeep, move)

        for i, peep in enumerate(bat.playerList):
            stats = peep.statMessage()
            adpStats = bat.adpList(peep)

            mes.set_field_at(
                i,
                name=f"{peep.n}",
                value=f"{stats}\n\n{adpStats}",
            )

        numFields = len(mes.fields)
        if not numFields:
            raise noFields()

        moveTxt = iniMove + moveStr
        mes.set_field_at(
            numFields - 1,
            inline=False,
            name=f"{Who2Move.n} Move #{Who2Move.t} ",
            value=f"{moveTxt}",
        )

        mes.description = f"{totRounds}/{ROUNDLIMIT} Total Rounds"
        await bat.echoMes(mes, thrd)
        if not winner and totRounds >= ROUNDLIMIT:
            winner = "exhaustion"
        elif winner:
            if not winner == "Noone":
                totRounds = winner.t

    mes.clear_fields()
    mes.add_field(
        name=(
            f"Winner is {winner.n if isinstance(winner, player) else winner}"
            f" after {totRounds} move{pluralInt(totRounds)}."
        ),
        value="Prize to be implemented.",
    )
    if not winner == "exhaustion":
        mes.set_thumbnail(url=winner.pic)
    await bat.echoMes(mes, thrd)
    await bat.echoMes(f"<#{ctx.channel.id}>", thrd, False)
    await thrd.edit(archived=1)
    await ctx.send(embed=mes)


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
            x for x in leader.keys() if leader[x] not in restrictedList
        ]
        topRankStr = random.choice(pickList)
    return topRankStr


# function to setup cog
def setup(bot: commands.Bot):
    bot.add_cog(roleCommands(bot))
