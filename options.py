# options.py

import asyncio
import math
import os
import random
import typing

import discord
import tatsu
from discord.ext import commands, tasks
from discord.ext.commands import MemberConverter
from discord.utils import get
from mee6_py_api import API
from sqlitedict import SqliteDict

import enhancements as enm
import log
from battle import battler, player
from exceptions import notSupeDuel
from power import (
    cmdInf,
    leader,
    moveOpt,
    posTask,
    power,
    powerTypes,
    rankColour,
    remList,
    restrictedList,
    rsltDict,
    taskVar,
)
from sharedVars import (
    ERRORTHREAD,
    HOSTNAME,
    SAVEFILE,
    TATSU,
    setGemDiff,
)

logP = log.get_logger(__name__)

COMON = True

SUPEROLE = "Supe"
PERMROLES = ["Supe"]  # guild role(s) for using these bot commands
MANAGER = "System"  # manager role name for guild
LOWESTROLE = 2  # bot sorts roles by rank from position of int10 to LOWESTROLE
HIDE = False
LEADLIMIT = 12
NEWCALC = 1
DL_ARC_DUR = 60


DEFDUELOPP = 159985870458322944
ROUNDLIMIT = 50
PLAYERTURNWAIT = 30
BOTTURNWAIT = 60

global GEMDIFF
GEMDIFF = os.getenv("GEMDIFF")
if not GEMDIFF:
    GEMDIFF = 0.5
taskCD = 60 * 30
# taskCD = 0

# TODO: implement this and similiar instead of
# multiple enhancement.dict.keys() calls
# enhancement (type, rank) pairs for list command
ENHLIST = [(x, y) for (x, y) in powerTypes.items()]


class Options(commands.Cog):
    def __init__(
        self, bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot]
    ):
        self.bot = bot
        self.grabLoop.start()
        self._connection = bot._connection

    # Check if user has guild role
    async def cog_check(self, ctx: commands.Context):

        logP.debug("Role check start")

        async def predicate(ctx: commands.Context):
            for role in PERMROLES:
                logP.debug("Role check {} in {}".format(role, PERMROLES))
                chkRole = get(ctx.guild.roles, name=role)
                logP.debug("chkRole: {}".format(chkRole))
                if chkRole in ctx.message.author.roles:
                    return chkRole
            raise commands.CheckFailure(
                (
                    "You do not have permission as you are missing a role in "
                    "this list: {}\nThe super command can be used to gain"
                    " the Supe role"
                ).format(PERMROLES)
            )

        # messy implementation for Supe
        return commands.check(await predicate(ctx))

    @commands.Cog.listener()
    async def on_ready(self):
        global ERTHRD
        ERTHRD = await enm.getSendLoc(ERRORTHREAD, self.bot, "thread")

    @tasks.loop(minutes=30)
    async def grabLoop(self):
        await self.bot.wait_until_ready()
        roleGrab = None
        for guild in self.bot.guilds:
            roleGrab = get(guild.roles, name=SUPEROLE)
            if roleGrab:
                for peep in roleGrab.members:
                    await count(peep)

    @commands.command(
        enabled=COMON,
        brief=cmdInf["trim"]["brief"],
        description=cmdInf["trim"]["description"],
    )
    # command to trim command caller of extra roles. OBSOLETE due to cut call
    # after role add in add command
    async def trim(self, ctx: commands.Context, *, member: str = ""):
        logP.debug("funcTrim START")

        memberList = await memGrab(self, ctx, "")  # member)
        logP.debug("memberlist = {}".format(memberList))

        await cut(ctx, memberList)
        logP.debug("funcTrim END")
        return

    """@commands.command(
        hidden=HIDE,
        brief=cmdInf["trimAll"]["brief"],
        description=cmdInf["trimAll"]["description"],
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

    @commands.command(
        enabled=COMON,
        hidden=HIDE,
        brief=cmdInf["roleInf"]["brief"],
        description=cmdInf["roleInf"]["description"],
    )
    @commands.has_any_role(MANAGER)
    # manager command to check if guild has role and messages
    # some information of the role
    async def roleInf(self, ctx: commands.Context, *, roleStr: str = SUPEROLE):
        supeGuildRoles = await orderRole(self, ctx)
        roleStrId = [x for x in supeGuildRoles if roleStr == x.name]
        logP.debug("Role string ID is: {}".format(roleStrId[0].id))
        if roleStrId:
            roleStrId = roleStrId[0]
            await ctx.send(
                (
                    "{.name} has: \nposition - {.position}"
                    "\ncolour - {.colour}"
                ).format(roleStrId, roleStrId, roleStrId)
            )
        return

    @commands.command(
        enabled=COMON,
        brief=cmdInf["convert"]["brief"],
        description=cmdInf["convert"]["description"],
    )
    async def convert(
        self, ctx: commands.Context, inVar: float = 0, gdv: int = 0
    ):
        feedback = lvlEqu(inVar, gdv)
        if gdv:
            await ctx.send(
                "{} GDV is equivalent to {:,} XP".format(inVar, feedback)
            )
        else:
            await ctx.send(
                "{:,} XP is equivalent to {} GDV".format(inVar, feedback)
            )

    @commands.command(
        enabled=COMON,
        aliases=["t"],
        brief=cmdInf["task"]["brief"],
        description=cmdInf["task"]["description"],
    )
    @commands.cooldown(1, taskCD, type=commands.BucketType.user)
    async def task(self, ctx: commands.Context):
        """
        It can be 60% minor, you only,
        25% moderate +1 random supe gets half xp,
        10% major +3 random supes get half and
        5% [imperative] everyone gets quarter xp - Geminel
        https://discord.com/channels/822410354860097577/823225800073412698/907167823284019231
        """

        taskType = random.choices(
            taskVar["taskOpt"][0], cum_weights=taskVar["taskWeight"]
        )
        taskShrt = posTask[taskType[0]]
        taskWorth = taskShrt["Worth"]
        logP.debug("Task is worth {}".format(taskWorth))
        taskAdd = taskShrt["Add"]
        logP.debug("Task can have additional {} peeps".format(taskAdd))

        if taskAdd:
            logP.debug(
                "Guild has {} roles".format(len(ctx.message.guild.roles))
            )
            peepToAdd = get(ctx.message.guild.roles, name=SUPEROLE)
            logP.debug("{}, {}".format(peepToAdd.id, peepToAdd.name))
            if taskAdd == -1:
                addPeeps = peepToAdd.members
                addPeeps.remove(ctx.message.author)
                # addNames = "every host of the Superhero Enhancement System!"
            else:
                addPeeps = random.sample(peepToAdd.members, k=taskAdd + 1)
                logP.debug("peeps list is: {}".format(addPeeps))
                if ctx.message.author in addPeeps:
                    addPeeps.remove(ctx.message.author)
            xpList = [[x, taskShrt["Aid"]] for x in addPeeps[:taskAdd]]
            xpList.append([ctx.message.author, 1])
        else:
            addPeeps = ""
            xpList = [[ctx.message.author, 1]]
        logP.debug("xpList = ", xpList)
        logP.debug(
            "{}\nTask XP: {}\n10 XP in GDV: {}".format(
                taskType, lvlEqu(taskWorth[0], 1), lvlEqu(10)
            )
        )
        emptMes = discord.Embed(
            title="Alert, {}!".format(enm.nON(ctx.message.author)),
            description=("A new {} GDV task " "has been assigned.").format(
                taskType[0]
            ),
        )

        logP.debug(
            "Possible Adjectives: {}".format(len(taskShrt["Adjective"]))
        )
        selAdj = random.choice(taskShrt["Adjective"])
        logP.debug("Selected Adjective: {}".format(selAdj))

        logP.debug("Possible People: {}".format(len(taskShrt["People"])))
        selPeep = random.choice(taskShrt["People"])
        logP.debug("Selected People: {}".format(selPeep))

        logP.debug("Possible Action: {}".format(len(taskShrt["Action"])))
        selAct = random.choice(taskShrt["Action"])
        logP.debug("Selected Action: {}".format(selAct))

        logP.debug("Possible Location: {}".format(len(taskShrt["Location"])))
        selPlace = random.choice(taskShrt["Location"])
        logP.debug("Selected Location: {}".format(selPlace))

        taskGrant = random.randrange(taskWorth[0], taskWorth[1] + 1)
        logP.debug("task Grant: {}".format(taskGrant))
        taskDiff = taskWorth[1] - taskWorth[0]
        logP.debug("task diff: {}".format(taskDiff))

        selResult = round(
            ((taskGrant - taskWorth[0]) / (2 * taskDiff)) + 0.5, 3
        )

        logP.debug("selected result: ", selResult)
        logP.debug(
            "{}{}, {}".format(
                "int(selResult * 100): ",
                int(selResult * 100),
                [[x, rsltDict[x]] for x in rsltDict.keys()],
            )
        )

        selRsltWrd = [
            x
            for x in rsltDict.keys()
            if int(selResult * 100)
            in range(int(100 * rsltDict[x][0]), int(100 * rsltDict[x][1]))
        ]
        logP.debug("selected resulting word: {}".format(selRsltWrd))
        if selRsltWrd:
            selRsltWrd = selRsltWrd[0]

        elif taskWorth[1] == taskGrant:
            selRsltWrd = "flawless"
        logP.debug(
            "taskWorth[1] == taskGrant: {}, {}".format(taskWorth[1], taskGrant)
        )

        # if addPeeps:
        #     emptMes += ("Due to the task difficulty, assistance has been "
        #                 "provided by {}").format(addNames)

        emptMes.add_field(
            inline=False,
            name="{} Task".format(taskType[0]),
            value="Please prevent the {} {} from {} {}.".format(
                selAdj, selPeep, selAct, selPlace
            ),
        )

        emptMes.add_field(
            inline=False,
            name="Success!",
            value=(
                "Congratulations on completing your {} GDV task. You accomp"
                "lished {} results in your endeavors."
            ).format(taskType[0], selRsltWrd),
        )

        try:
            authInf = load(ctx.message.author.guild.id)
        except Exception as e:
            logP.debug(str(e))
        if not authInf:
            authInf = {}

        for peep in reversed(xpList):
            logP.debug("peep is: {}".format(peep))
            if peep[0].id in authInf.keys():
                authInf[peep[0].id]["invXP"][-1] += taskGrant * peep[1]
            else:
                authInf[peep[0].id] = {"Name": peep[0].name}
                authInf[peep[0].id]["invXP"] = [0, 0, taskGrant * peep[1]]

            if peep[0].id == ctx.message.author.id or taskAdd != -1:
                emptMes.add_field(
                    name="{} Earns".format(enm.nON(peep[0])),
                    value="{:,} GDV XP\nTotal of {:,} XP".format(
                        taskGrant * peep[1], authInf[peep[0].id]["invXP"][-1]
                    ),
                )
        if taskAdd == -1:
            emptMes.add_field(
                name="Everyone Else",
                value="Earns {} GDV XP".format(taskGrant * taskShrt["Aid"]),
            )

        save(ctx.message.author.guild.id, authInf)
        stateL = await countOf(ctx.message.author)
        currEnhP = stateL[0]
        logP.debug(
            "{} has {} available enhancements".format(
                enm.nON(ctx.message.author), currEnhP
            )
        )
        stateG = enm.spent([ctx.message.author])
        currEnh = int(stateG[0][1])
        logP.debug("and enhancments of number = ", currEnh)
        logP.debug(
            "currEnh {} < currEnhP {}, {}".format(
                currEnh, currEnhP, currEnh < currEnhP
            )
        )
        if currEnh < currEnhP:
            val = "{} has {} unspent enhancement point{}.".format(
                enm.nON(ctx.message.author),
                currEnhP - currEnh,
                pluralInt(currEnhP - currEnh),
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
        aliases=["a"],
        brief=cmdInf["add"]["brief"],
        description=cmdInf["add"]["description"],
    )
    # add role command available to all PERMROLES users
    async def add(self, ctx: commands.Context, *, typeRank=""):

        # fetch message author and their current enhancement roles
        # as well as the build for those roles
        user = ctx.message.author
        userSpent = enm.spent([user])
        userEnhancements = userSpent[0][2]
        userHas = enm.funcBuild(userEnhancements)
        userHasBuild = userHas[2]

        # if author did not provide an enhancement to add, return
        if not typeRank:
            await ctx.send(
                "Cannot add enhancements without an enhancement to add"
            )
            return
        # otherwise split the arglist into a readable shorthand enhancment list
        else:
            fixArg = typeRank.replace(" ", ",")
            fixArg = fixArg.replace(";", ",")
            buildList = [x.strip() for x in fixArg.split(",") if x.strip()]
            logP.debug(buildList)

        # add requested enhancements to current user build
        # then grab the information for this new user build
        [userEnhancements.append(x) for x in buildList]
        userWants = enm.funcBuild(userEnhancements)
        userWantsCost = userWants[0]
        userWantsBuild = userWants[2]
        pointTot = await count(user, 1, 1)
        logP.debug(
            "{} with point total {} has {} {} and wants {} {}".format(
                user,
                pointTot[0],
                userHas[0],
                userHasBuild,
                userWantsCost,
                userWantsBuild,
            )
        )

        # check to ensure user has enough enhancement points to
        # get requested additions
        if pointTot[0] < userWants[0]:
            await ctx.send(
                (
                    "{} needs {} available enhancements for {} but only has {}"
                ).format(
                    enm.nON(user),
                    userWantsCost,
                    [power[x]["Name"] for x in buildList],
                    pointTot[0],
                )
            )
            return

        # the guild role names grabbed from shorthand to add to user
        addList = [
            power[enm.toType(x[1]) + str(x[0])]["Name"] for x in userWantsBuild
        ]
        logP.debug("Add list = {}".format(addList))

        # restricted roles the user does not have that the build requires
        cantAdd = [x for x in restrictedList if x in addList]
        cantAdd = [x for x in cantAdd if x not in [y.name for y in user.roles]]
        logP.debug("Cant add = {}".format(cantAdd))

        # check to ensure user has restricted roles already,
        # if required for build
        if cantAdd:
            await ctx.send(
                ("Cannot add enhancements as {} does not have {}").format(
                    enm.nON(user), cantAdd
                )
            )
            return

        # guild role list with name and id attributes
        guildRoles = await user.guild.fetch_roles()

        # iterate through roles to add to user
        sendMes = ""
        for role in addList:
            logP.debug("Trying to add role: {}".format(role))

            # check for if user has enhancement role already
            roleId = get(guildRoles, name=role)
            if roleId in user.roles:
                logP.debug(
                    "{} already has the role {}".format(enm.nON(user), roleId)
                )
                # sendMes += ("{} already has the role {}\n"
                #               ).format(nON(user), roleId))
                continue

            # role names to add will have format "Rank *Rank* *Type*"
            roleRank = role.split()[1]
            logP.debug("{}, {}".format(roleId, roleRank))

            # check for role already in guild role list, create it if required
            if not roleId:
                colour = rankColour[int(roleRank)]
                logP.debug(
                    "colour for rank {} is: {}".format(roleRank, colour)
                )
                roleId = await user.guild.create_role(name=role, color=colour)

            # add requested role to user
            await user.add_roles(roleId)
            sendMes += "{} now has {}!\n".format(enm.nON(user), roleId)

        # trim the user of excess roles
        # debug("TO CUT")
        # await cut(ctx, [user])
        if not sendMes:
            await ctx.send(
                (
                    "You cannot add enhancements of an equal or lower "
                    "rank than you already have of that type"
                )
            )
        else:
            await ctx.send(sendMes)
        return

    @commands.command(hidden=True)
    @commands.has_any_role(MANAGER)
    # TODO implementation for manager specific help command
    async def hhelp(self, ctx: commands.Context):
        commands.DefaultHelpCommand(no_category="Basic Options", hidden=True)
        return

    @commands.command(
        enabled=COMON,
        hidden=HIDE,
        brief=cmdInf["moveRoles"]["brief"],
        description=cmdInf["moveRoles"]["description"],
    )
    @commands.has_any_role(MANAGER)
    # manager command to correct role position for roles that
    # have been created by bot
    async def moveRoles(self, ctx: commands.Context):
        managed = await manageRoles(ctx)
        await ctx.send(embed=managed)
        return

    @commands.command(
        enabled=COMON,
        aliases=["p"],
        brief=cmdInf["points"]["brief"],
        description=cmdInf["points"]["description"],
    )
    # command to get author or specified user(s) enhancement total
    # and available points
    async def points(self, ctx: commands.Context, *, member: str = ""):
        users = await memGrab(self, ctx, member)
        # restrict user list to those with SUPEROLE
        supeUsers = isSuper(self, users)
        if not supeUsers:  # if no SUPEROLE users in list
            await ctx.send("Your list contains no {}'s".format(SUPEROLE))
            return

        # fetch points of each SUPEROLE user
        pointList = enm.spent(supeUsers)

        # return result
        for group in pointList:
            logP.debug("group in level is: {}".format(group))
            pointTot = await countOf(group[0])
            await ctx.send(
                (
                    "{} has {} enhancement{} active out of {} enhancement{} "
                    "available."
                ).format(
                    enm.nON(group[0]),
                    group[1],
                    pluralInt(group[1]),
                    pointTot[0],
                    pluralInt(pointTot[0]),
                )
            )

    @commands.command(
        enabled=COMON,
        aliases=["l"],
        brief=cmdInf["list"]["brief"],
        description=cmdInf["list"]["description"],
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
                value="{} of {} rank{}".format(
                    shorthand.lower(), group[1], pluralInt(group[1])
                ),
            )

        # return enhancement list to command caller
        logP.debug(mes.to_dict())
        mes.set_footer(text="Starred enhancements require advanced roles")
        await ctx.send(embed=mes)

    @commands.command(
        enabled=COMON,
        aliases=["b"],
        brief=cmdInf["build"]["brief"],
        description=cmdInf["build"]["description"],
    )
    # build command to theory craft and check the prereqs for differnet
    # enhancement ranks can be used in conjunction with points command to
    # determine if user can implement a build
    async def build(
        self,
        ctx: commands.Context,
        mem: typing.Optional[discord.Member],
        *,
        typeRank: str = "",
    ):
        logP.debug("Build command start")
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
            buildList = enm.spent([mem])[0][2]
        logP.debug("buildList = {}".format(buildList))

        # fetch cost and requisite list for build
        buildTot = enm.funcBuild(buildList)

        # return build to command caller
        mes = discord.Embed(
            title="Enhancement Build",
            description="This build requires {} enhancement point{}.".format(
                buildTot[0], pluralInt(buildTot[0])
            ),
        )
        mes.add_field(
            inline=False, name="Build Enhancements", value=buildTot[1]
        )
        mes.add_field(
            inline=False,
            name="Required Enhancements",
            value=enm.reqEnd([buildTot[0], buildTot[2]]),
        )
        await ctx.send(embed=mes)

    @commands.command(
        enabled=COMON,
    )
    @commands.has_any_role(MANAGER)
    async def average(self, ctx: commands.Context):
        mes = discord.Embed(title="Average Enhancment Points")
        totSumPeeps = 0
        totLenPeeps = 0
        getSupe = [x for x in ctx.guild.roles if str(x.name) == SUPEROLE]
        if not getSupe:
            await ctx.send("No users of role: {}".format(SUPEROLE))
        else:
            getSupe = getSupe[0]
        for val in leader.values():
            peepDict = topEnh(ctx, val)

            sumPeep = sum(peepDict.values())
            lenPeep = len(peepDict.keys())
            avPeep = round(sumPeep / len(getSupe.members), 4)

            totSumPeeps += sumPeep

            mes.add_field(
                name="{}".format(val),
                value=(
                    "{} host{} for a total of {} point{}.\n "
                    "Serverwide average of {}."
                ).format(
                    lenPeep,
                    pluralInt(lenPeep),
                    sumPeep,
                    pluralInt(sumPeep),
                    avPeep,
                ),
            )
        totLenPeeps = len(getSupe.members)
        totAvPeep = round(totSumPeeps / totLenPeeps, 2)
        mes.add_field(
            name=SUPEROLE,
            value=(
                "There is a total of {} host{} with a sum of {} "
                "enhancement point{} spent.\n Serverwide average of {}."
            ).format(
                totLenPeeps,
                pluralInt(totLenPeeps),
                totSumPeeps,
                pluralInt(totSumPeeps),
                totAvPeep,
            ),
        )
        mes.set_footer(text=HOSTNAME, icon_url=self.bot.user.display_avatar)
        await ctx.send(embed=mes)

    @commands.command(
        enabled=COMON,
        aliases=["leaderboard"],
        brief=cmdInf["top"]["brief"],
        description=cmdInf["top"]["description"],
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

            blankMessage = discord.Embed(
                title="{} Leaderboard".format(enh.upper())
            )

        elif enh:
            if enh not in leader.keys():
                if enh not in leader.values():
                    await ctx.send(
                        ("No enhancement could be found for type: {}").format(
                            enh
                        )
                    )
                    return
            else:
                enh = leader[enh]
            peepDict = topEnh(ctx, enh)

            sumPeep = sum(peepDict.values())
            lenPeep = len(peepDict.keys())
            avPeep = round(sumPeep / lenPeep, 2)

            blankMessage = discord.Embed(
                title="{} Enhancement Leaderboard".format(enh),
                description=(
                    "{} is being used by {} host{} for a total of {} "
                    "enhancement point{} spent.\nFor an average of "
                    "{}."
                ).format(
                    enh,
                    lenPeep,
                    pluralInt(lenPeep),
                    sumPeep,
                    pluralInt(sumPeep),
                    avPeep,
                ),
            )

            unsortedDict = [(x, y) for x, y in peepDict.items()]
            pointList = sorted(unsortedDict, key=lambda x: x[1], reverse=True)
        else:
            # list of users bot has access to
            guildList = self.bot.users
            logP.debug("Guild list is of length: {}".format(len(guildList)))

            # restrict list to those with SUPEROLE
            supeList = isSuper(self, guildList)
            logP.debug("Supe list is of length: {}".format(len(supeList)))

            # fetch points of each SUPEROLE user
            pointList = enm.spent(supeList)

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
                "There is a total of {} host{} with a sum of {} "
                "enhancement point{} spent."
            ).format(
                totHosts, pluralInt(totHosts), totPoints, pluralInt(totPoints)
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
                    name="**{}** - {}".format(i, enm.nON(group[0])),
                    value="\t{} enhancements".format(group[1]),
                )
            else:
                if not enh.lower() in xpKey:
                    blankMessage.add_field(
                        inline=True,
                        name="**{}** - {}".format(i, enm.nON(group[0])),
                        value="\tRank {} {}".format(group[1], enh),
                    )
                else:
                    blankMessage.add_field(
                        inline=True,
                        name="**{}** - {}".format(i, enm.nON(group[0])),
                        value="\t{:,} {}".format(group[1], enh.upper()),
                    )
            i += 1

        blankMessage.set_footer(
            text=HOSTNAME, icon_url=self.bot.user.display_avatar
        )
        # return leaderboard to command caller
        await ctx.send(embed=blankMessage)

    @commands.command(
        enabled=COMON,
        aliases=["c", "clear"],
        brief=cmdInf["clean"]["brief"],
        description=cmdInf["clean"]["description"],
    )
    # remove unrestricted enhancements from command caller
    async def clean(self, ctx: commands.Context):
        # rank 0 enhancements are either restricted or the SUPEROLE,
        # which should not be removed with this command
        toCut = [
            x.name
            for x in ctx.message.author.roles
            if x.name
            in [power[y]["Name"] for y in power.keys() if power[y]["Rank"] > 0]
        ]
        logP.debug(toCut)
        await cut(ctx, [ctx.message.author], toCut)

    @commands.command(enabled=COMON, hidden=HIDE)
    @commands.has_any_role(MANAGER)
    async def xpAdd(
        self,
        ctx: commands.Context,
        val: typing.Union[float, int] = 0.0,
        *,
        mem: str = "",
    ):
        val = round(val, 2)
        logP.debug("val to add is: {}".format(val))
        memList = await memGrab(self, ctx, mem)
        logP.debug("memList is: {}".format(memList))
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
        await ctx.send("Host {}: {} -> {}".format(enm.nON(peep), iniVal, sum))

    @commands.command(
        enabled=COMON,
        hidden=HIDE,
        aliases=["x"],
        brief=cmdInf["xpGrab"]["brief"],
        description=cmdInf["xpGrab"]["description"],
    )
    # @commands.has_any_role(MANAGER)
    @commands.cooldown(1, 1, commands.BucketType.default)
    async def xpGrab(self, ctx: commands.Context, *, mem: str = ""):
        typeMem = await memGrab(self, ctx, mem)
        typeMem = [typeMem[0]]
        pointList = enm.spent(typeMem)
        # tatForce = 0
        i = 0
        # for role in ctx.author.roles:
        #     if role.name == MANAGER:
        #         tatForce = 1
        for peep in typeMem:
            mes = discord.Embed(title="{} Stats".format(enm.nON(peep)))
            stuff = await count(peep, 1, 1)
            group = pointList[i]
            unspent = stuff[0] - group[1]

            mes.set_thumbnail(url=peep.display_avatar)

            mes.add_field(name="MEE6 xp", value="{:,}".format(stuff[3][0]))
            mes.add_field(name="TATSU xp", value="{:,}".format(stuff[3][1]))
            mes.add_field(name="GDV xp", value="{:,}".format(stuff[3][-1]))
            mes.add_field(name="Total xp", value="{:,}".format(stuff[2]))
            mes.add_field(name="GDV", value="{}".format(round(stuff[1], 2)))
            mes.add_field(
                name="Enhancement Point{}".format(pluralInt(stuff[0])),
                value="{}".format(stuff[0]),
            )

            nextGDV = int(stuff[1]) + 1
            nextGDV_XP = lvlEqu(nextGDV, 1)
            nextGDVneedXP = nextGDV_XP - stuff[2]

            mes.add_field(
                inline=False,
                name="XP to next GDV",
                value="{:,}".format(round(nextGDVneedXP, 3)),
            )

            nextEnhP = int(5 * (int(stuff[1] / 5) + 1))
            nextEnhP_XP = lvlEqu(nextEnhP, 1)
            nextEnhPneedXP = nextEnhP_XP - stuff[2]

            mes.add_field(
                inline=False,
                name="XP to next Enhancement Point",
                value="{:,}".format(round(nextEnhPneedXP, 3)),
            )

            mes.add_field(
                inline=False,
                name="Unspent Enhancement Point{}".format(pluralInt(unspent)),
                value=unspent,
            )

            mes.set_footer(
                text="{}#{} - {}".format(
                    peep.name, peep.discriminator, HOSTNAME
                ),
                icon_url=peep.avatar,
            )

            await ctx.send(embed=mes)
            i += 1

    @commands.command(
        enabled=COMON,
        brief="-A command for Geminel to change thier xp total handicap.",
        description=(
            "-A command for Geminel to change thier xp total handicap."
        ),
    )
    async def diffGem(
        self, ctx: commands.Context, var: float = float(GEMDIFF)
    ):
        if int(ctx.message.author.id) not in [
            213090220147605506,
            277041901776142337,
        ]:
            mes = discord.Embed(title="You have no power here.")
            mes.set_image(
                url=(
                    "https://www.greatmanagers.com.au/wp-content/"
                    "uploads/2018/03/talktohand_trans.png"
                )
            )
            await ctx.send(embed=mes)
            return
        global GEMDIFF
        if var < 0.0:
            var = 0.0
        if var > 1.0:
            var = 1.0
        GEMDIFF = var
        setGemDiff(var)

        await ctx.send(
            "Gem diff is now {} times total XP or {}%".format(
                GEMDIFF, 100 * GEMDIFF
            )
        )

    @commands.command(enabled=COMON, aliases=["s"])
    async def stats(self, ctx: commands.Context, peep: discord.Member = False):
        if not peep:
            peep = ctx.author
        p = player(peep, self.bot)
        mes = discord.Embed(
            title="{} Stats".format(p.n),
            description=p.statMessage(),
        )
        mes.set_thumbnail(url=p.p.display_avatar)
        mes.set_footer(
            text="{}#{} - {}".format(p.p.name, p.p.discriminator, HOSTNAME),
            icon_url=p.p.avatar,
        )

        await ctx.send(embed=mes)

    @commands.command(enabled=COMON, aliases=["d"])
    async def duel(
        self,
        ctx: commands.Context,
        dontAsk: typing.Optional[typing.Literal[1]],
        opponent: discord.Member = False,
    ):
        if not opponent:
            opponent = get(ctx.guild.members, id=DEFDUELOPP)
        elif str(SUPEROLE) not in [x.name for x in opponent.roles]:
            raise notSupeDuel("Not a supe.")
        bat = battler(self.bot, ctx.author, opponent)
        await bat.findPlayers(dontAsk)
        mes = discord.Embed(
            title="{}: {} Vs. {}: {}".format(
                bat.n1, bat.isPlay(bat.p1), bat.n2, bat.isPlay(bat.p2)
            ),
        )

        p1Stats = bat.p1.statMessage()
        p2Stats = bat.p2.statMessage()

        p1Adp = bat.adpStatMessage(bat.p1, bat.p2)
        p2Adp = bat.adpStatMessage(bat.p2, bat.p1)

        mes.add_field(
            name="{}".format(bat.n1),
            value="{}{}".format(p1Stats, p1Adp),
        )
        mes.add_field(
            name="{}".format(bat.n2),
            value="{}{}".format(p2Stats, p2Adp),
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
        if bat.p1.play:
            await thrd.add_user(ctx.author)
        if bat.p2.play:
            await thrd.add_user(opponent)

        winner = None
        mes.add_field(
            inline=False,
            name="{} Move".format(bat.n1),
            value="Does Nothing.",
        )
        mes.add_field(
            inline=False,
            name="{} Move".format(bat.n2),
            value="Does Nothing.",
        )
        totRounds = int(0)
        while not winner:
            totRounds += 1
            Who2Move = bat.nextRound()
            for peep in range(2):
                move = None
                play = Who2Move[peep]
                if play == bat.p1:
                    notPlay = bat.p2
                else:
                    notPlay = bat.p1

                if isinstance(play, player):
                    if play.play:
                        move = await playerDuelInput(
                            self, ctx, totRounds, play, notPlay, bat
                        )
                    else:
                        move = bat.moveSelf(play, notPlay)
                # peep will be either 0 or 1
                if peep:
                    p2Move = move
                else:
                    p1Move = move

            moves = bat.move(Who2Move, p1Move, p2Move)
            p1Stats = bat.p1.statMessage()
            p2Stats = bat.p2.statMessage()

            p1Adp = bat.adpStatMessage(bat.p1, bat.p2)
            p2Adp = bat.adpStatMessage(bat.p2, bat.p1)

            mes.set_field_at(
                0,
                name="{}".format(bat.n1),
                value="{}{}".format(p1Stats, p1Adp),
            )
            mes.set_field_at(
                1,
                name="{}".format(bat.n2),
                value="{}{}".format(p2Stats, p2Adp),
            )
            mes.set_field_at(
                2,
                inline=False,
                name="{} Move #{} ".format(bat.n1, bat.p1.t),
                value="{}".format(moves[0]),
            )
            mes.set_field_at(
                3,
                inline=False,
                name="{} Move #{} ".format(bat.n2, bat.p2.t),
                value="{}".format(moves[1]),
            )
            winner = moves[2]
            mes.description = "{}/{} Total Rounds".format(
                totRounds, ROUNDLIMIT
            )
            await bat.echoMes(mes, thrd)
            if not winner and totRounds > ROUNDLIMIT:
                winner = "exhaustion"
                totRounds = "too many"
            elif winner:
                totRounds = bat.p1.t if winner == bat.p1.n else bat.p2.t

        mes.clear_fields()
        mes.add_field(
            name="Winner is {} after {} moves.".format(winner, totRounds),
            value="Prize to be implemented.",
        )
        if not winner == "exhaustion":
            mes.set_thumbnail(
                url=(
                    bat.p1.p.display_avatar
                    if winner == bat.n1
                    else bat.p2.p.display_avatar
                )
            )
        await bat.echoMes(mes, thrd)
        await bat.echoMes("<#{}>".format(ctx.channel.id), thrd, False)
        await thrd.edit(archived=1)
        await ctx.send(embed=mes)

    @commands.command(enabled=COMON)
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


# function to move roles to correct rank positions
async def manageRoles(ctx: commands.Context):
    logP.debug("ManageRoles Start")

    # spam message negation
    movedRoles = discord.Embed(title="Moving Roles")
    toMove = {}

    # iterate through all guild roles
    for role in ctx.message.guild.roles:
        logP.debug("Looking at role: {}".format(role.name))

        # grab shorthand for enhancement
        roleShort = [x for x in power.keys() if power[x]["Name"] == role.name]
        logP.debug("roleShort = {}".format(roleShort))

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
        logP.debug("Role rank is: {}".format(roleRank))

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
                == "Rank {} Intelligence (only for Systems)".format(
                    roleRank - 1
                )
            ][0]

        # fetch upperbound intelligence rank position
        roleRankUpper = [
            x.position
            for x in ctx.message.guild.roles
            if x.name
            == "Rank {} Intelligence (only for Systems)".format(roleRank)
        ][0]

        # roleDiff = roleRankUpper - roleRankLower

        # check for if role is already in postion
        if role.position < roleRankUpper:
            if role.position >= roleRankLower:
                logP.debug(
                    "Role within bounds {} - {}".format(
                        roleRankUpper, roleRankLower
                    )
                )
                continue

        # move role to current upperbound intelligence position,
        # forcing intelligence position to increase
        # ASSUMES current role position is lower than intelligence position
        # TODO remove assumption
        logP.debug(
            "Role to be moved from {.position} to {}".format(
                role, roleRankUpper - 1
            )
        )

        movedRoles.add_field(
            name=role.name,
            value="{} -> {}".format(role.position, roleRankUpper),
        )

        toMove[role] = roleRankUpper
    await ctx.message.guild.edit_role_positions(positions=toMove)

    # return moved roles as single message to function call
    if not movedRoles.fields:
        movedRoles.description = "No roles moved"
    logP.debug("ManageRoles End")
    return movedRoles


# function to get specified user's enhancement points


async def count(
    peep: discord.Member, typ: int = NEWCALC, tatFrc: int = 0
) -> tuple[int, float, float, list[int, int, float]]:
    logP.debug("Start count")
    global GEMDIFF
    tat = tatsu.wrapper
    """if not typ:
        # fetch MEE6 level
        level = await API(peep.guild.id).levels.get_user_level(peep.id)
        debug(level)

        # Enhancement points are equivalent to MEE6 level / 5
        if level:
            pointTot = int(level / 5)
        else:
            pointTot = 0
        debug(pointTot)
        debug(peep.roles)

        # + an enhancement point for other roles the user might have
        for role in peep.roles:
            debug(role)
            if role.name in enm.patList:
                pointTot += 1
            debug(pointTot)
        # return total user points to function call
        debug("End count")
        return [pointTot]
    else:"""
    if tatFrc:
        MEE6xp = await API(peep.guild.id).levels.get_user_xp(peep.id)
        TATSUmem = await tat.ApiWrapper(key=TATSU).get_profile(peep.id)
    else:
        TATSUmem = None
        MEE6xp = int(0)

    try:
        pickle_file = load(peep.guild.id)
        logP.debug("Pickle file loaded successfully")
    except Exception as e:
        print(e)
        pickle_file = {}

    if pickle_file and peep.id in pickle_file.keys():
        ReSubXP = float(pickle_file[peep.id]["invXP"][-1])
    else:
        ReSubXP = float(0)
    logP.debug("ReSubXP: {}".format(ReSubXP))

    if hasattr(TATSUmem, "xp"):
        TATSUxp = int(TATSUmem.xp)
        if not TATSUxp:
            TATSUxp = int(0)
    else:
        TATSUxp = int(0)
    logP.debug("TATSUxp: {}".format(TATSUxp))

    if not MEE6xp:
        MEE6xp = int(0)
        if peep.id in pickle_file.keys():
            if pickle_file[peep.id]["invXP"][0]:
                MEE6xp = int(pickle_file[peep.id]["invXP"][0])
    logP.debug("MEE6xp: {}".format(MEE6xp))

    if not TATSUxp:
        TATSUxp = int(0)
        if peep.id in pickle_file.keys():
            if pickle_file[peep.id]["invXP"][0]:
                TATSUxp = int(pickle_file[peep.id]["invXP"][1])

    if MEE6xp or TATSUxp or ReSubXP:
        totXP = ReSubXP + MEE6xp + (TATSUxp / 2)
    else:
        totXP = float(0)
    if enm.nON(peep) == "Geminel":
        totXP = round(totXP * float(GEMDIFF), 3)

    logP.debug("totXP: {}".format(totXP))

    gdv = lvlEqu(totXP)
    logP.debug("gdv: {}".format(gdv))

    enhP = math.floor(gdv / 5) + 1
    logP.debug("enhP: {}".format(enhP))
    pickle_file[peep.id] = {
        "Name": peep.name,
        "enhP": enhP,
        "gdv": gdv,
        "totXP": totXP,
        "invXP": [MEE6xp, TATSUxp, ReSubXP],
    }
    save(peep.guild.id, pickle_file)

    logP.debug("End count")

    return enhP, gdv, totXP, [MEE6xp, TATSUxp, ReSubXP]


async def countOf(
    peep: discord.Member,
) -> tuple[int, float, float, list[int, int, float]]:
    logP.debug("Start countOf")
    try:
        valDict = load(peep.guild.id)
        logP.debug("valDict loaded")
        shrt = valDict[peep.id]
        logP.debug("shrt: {}".format(shrt))
        logP.debug("End countOf - succ load")

        invXP = [
            int(shrt["invXP"][0]),
            int(shrt["invXP"][1]),
            float(shrt["invXP"][-1]),
        ]

        return (
            int(shrt["enhP"]),
            float(shrt["gdv"]),
            float(shrt["totXP"]),
            invXP,
        )
    except Exception as e:
        logP.warning(e)
        logP.debug("End countOf - fail load")
        return await count(peep)


# restrict list from members to members with SUPEROLE
def isSuper(
    self: Options, guildList: list[discord.User]
) -> list[discord.Member]:
    logP.debug("Start isSuper")
    guilds = self.bot.guilds
    supeGuildList = []
    foundRole = []

    logP.debug("Guild list is: {}".format(guilds))

    for guild in guilds:
        logP.debug("iter through: {}".format(guild))
        posRole = get(guild.roles, name=SUPEROLE)
        if posRole:
            logP.debug(["found role:", posRole])
            foundRole.append(posRole)
    if foundRole:
        for role in foundRole:
            logP.debug(["iter through:", role])
            for member in role.members:
                if member in guildList:
                    logP.debug(["appending:", member])
                    supeGuildList.append(member)

    # return reduced user list
    logP.debug("End isSuper")
    return supeGuildList


# function to fetch all users requested by command caller
async def memGrab(
    self, ctx: commands.Context, memList: str = ""
) -> list[typing.Union[discord.User, discord.Member]]:
    logP.debug("Start memGrab")
    logP.debug(
        "memList: {}\nand mentions: {}".format(memList, ctx.message.mentions)
    )
    grabList = []
    # first check for users mentioned in message
    if ctx.message.mentions:
        grabList = ctx.message.mentions
        logP.debug("Message mentions: {}".format(grabList))

    # else check for users named by command caller
    elif memList:
        strMemList = memList.split(", ")
        logP.debug("split grablist: {}".format(strMemList))
        for posMem in strMemList:
            logP.debug(["trying to find: ", posMem])
            grabMem = await MemberConverter().convert(ctx, posMem)
            if grabMem:
                grabList.append(grabMem)

    # else use the command caller themself
    else:
        grabList.append(ctx.message.author)
        logP.debug("Author is: {}".format(grabList))
    logP.debug("fixed grablist: {}".format(grabList))
    logP.debug("End memGrab")

    # return: mentioned users || named users || message author
    return grabList


# get roles of a lower rank on member to remove later
def toCut(member: discord.Member) -> list[str]:
    logP.debug("Start toCut")

    # fetch unrestricted managed roles member has
    supeRoles = enm.spent([member])
    logP.debug("supeRoles = {}".format(supeRoles[0][2]))

    # fetch build of member
    supeBuild = enm.funcBuild(supeRoles[0][2])
    logP.debug("supeBuild = {}".format(supeBuild[1]))

    # fetch trimmed build of user
    supeTrim = [
        power[enm.toType(x[1]) + str(x[0])]["Name"]
        for x in enm.trim(supeBuild[1])
    ]
    logP.debug("supeTrim = {}".format(supeTrim))

    # fetch extra roles user has that are to be removed
    toCut = [x for x in supeBuild[1] if x not in supeTrim]
    logP.debug("to CUT = {}".format(toCut))

    # return the roles to be removed
    logP.debug("End toCut")
    return toCut


# function to remove extra or specified roles from list of users
async def cut(
    ctx: commands.Context,
    memberList: list[discord.Member],
    cutList: list[str] = [],
):
    logP.debug("Start cut")
    # iterate through given user list
    # assumed list has already been reduced to users with SUPEROLE
    mes = discord.Embed(title="Cutting roles")

    for peep in memberList:

        # if no list of roles to remove was given get user's extra roles
        if not cutList:
            cutting = toCut(peep)
        else:
            cutting = cutList

        # for each role to be cut, remove it and send message to discord
        sendMes = ""
        for role in cutting:
            logP.debug(
                "\t\t role to cut: {}, from peep: {}".format(role, peep)
            )
            supeRoleId = get(peep.roles, name=role)
            logP.debug("\t\t role to cut id = {}".format(supeRoleId))
            if supeRoleId in peep.roles:
                await peep.remove_roles(supeRoleId)
                sendMes += "Removed {}, {}\n".format(
                    supeRoleId, random.choice(remList)
                )

        # notify current user has been finished with to discord
        sendMes += "{} has been cut down to size!".format(enm.nON(peep))
        mes.add_field(name="{}".format(enm.nON(peep)), value=sendMes)
    await ctx.send(embed=mes)
    logP.debug("End cut")
    return


# function to fetch all guild roles that are managed by bot
async def orderRole(self, ctx: commands.Context):
    logP.debug("Start orderRole")
    logP.debug(power.values())

    supeList = [
        x
        for x in ctx.message.author.guild.roles
        if str(x) in [y["Name"] for y in power.values()]
    ]

    logP.debug(supeList)
    logP.debug("End orderRole")
    return supeList


def lvlEqu(givVar: float = 0, inv=0) -> float:
    logP.debug("Start lvlEqu")
    if inv:
        calVar = (20 * math.pow(givVar, 2)) / 1.25
        logP.debug("{} GDV is equivalent to {:,} XP".format(givVar, calVar))
    else:
        calVar = math.sqrt((1.25 * givVar) / 20)
        logP.debug("{:,} XP is equivalent to {} GDV".format(givVar, calVar))
    logP.debug("End lvlEqu")
    return round(calVar, 2)


def aOrAn(inp: str):
    logP.debug("Start aOrAn")
    logP.debug(["input is: ", inp])
    ret = "A"
    if inp[0].lower() in "aeiou":
        ret = "An"
    logP.debug(["ret: ", ret])
    logP.debug("End aOrAn")
    return ret


def pluralInt(val: int):
    rtnStr = ""
    if not val == 1:
        rtnStr = "s"
    return rtnStr


def topEnh(ctx: commands.Context, enh: str) -> dict:

    enhNameList = {
        power[x]["Name"]: 0 for x in power.keys() if enh == power[x]["Type"]
    }
    peepDict = {}
    for peep in ctx.message.author.guild.members:
        if SUPEROLE not in [x.name for x in peep.roles]:
            continue
        for role in peep.roles:
            if role.name in enhNameList.keys():
                enhNameList[role.name] += 1
                if peep not in peepDict.keys():
                    peepDict[peep] = [
                        power[x]["Rank"]
                        for x in power.keys()
                        if power[x]["Name"] == role.name
                    ][0]
                else:
                    rank = [
                        power[x]["Rank"]
                        for x in power.keys()
                        if power[x]["Name"] == role.name
                    ][0]
                    if rank > peepDict[peep]:
                        peepDict[peep] = rank
    return peepDict


async def fetchEmoji(ctx: commands.Context, emojiStr):
    foundEmoji = None
    convertEmoji = await commands.EmojiConverter().convert(
        ctx=ctx, argument=emojiStr
    )
    if convertEmoji:
        foundEmoji = convertEmoji
    return foundEmoji


async def playerDuelInput(
    self: Options,
    ctx: commands.Context,
    totRounds: int,
    peep: player,
    notPeep: player,
    battle: battler,
):
    statsMes = peep.statMessage()
    statsMes += battle.adpStatMessage(peep, notPeep)
    stats2Mes = notPeep.statMessage()
    stats2Mes += battle.adpStatMessage(notPeep, peep)

    moveStr = ""
    reactionList = []
    moveList = []
    chosenMove = False

    for key in moveOpt.keys():
        moveCost = moveOpt[key]["cost"]
        if moveCost <= peep.sta:
            react = moveOpt[key]["reaction"]
            moveStr += "{}: ({}) {}\n".format(
                react, moveCost, moveOpt[key]["name"]
            )
            moveList.append(key)
            reactionList.append(react)

    mes = discord.Embed(
        title="Game Stats",
        description="{}/{} Total Rounds".format(totRounds, ROUNDLIMIT),
    )
    mes.add_field(name="Your Current", value=statsMes)
    mes.add_field(name="Opponent", value=stats2Mes)
    mes.set_footer(text=HOSTNAME, icon_url=self.bot.user.display_avatar)
    if peep.missTurn:
        moveStr = "You are exhausted."
    mes.add_field(
        inline=False,
        name="Available Moves ({} Stamina)".format(peep.sta),
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
            logP.debug(["reaction", reaction, "user", user])
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
                    logP.debug([str(reaction.emoji), "found"])
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
            desperate, typeMove, moveString = await playerDuelInput(
                self, ctx, totRounds, peep, notPeep, battle
            )
    else:
        desperate, typeMove, moveString = battle.moveSelf(peep, notPeep)
    return desperate, typeMove, moveString


def save(key: int, value: dict, cache_file=SAVEFILE):
    logP.debug("Start save")
    try:
        with SqliteDict(cache_file) as mydict:
            mydict[key] = value  # Using dict[key] to store
            mydict.commit()  # Need to commit() to actually flush the data
        logP.debug("saved {} of length: {}".format(key, len(value)))
    except Exception as ex:
        logP.warning(["Error during storing data (Possibly unsupported):", ex])
    logP.debug("End save")


def load(key: int, cache_file=SAVEFILE) -> dict:
    logP.debug("Start load")
    try:
        with SqliteDict(cache_file) as mydict:
            # No need to use commit(), since we are only loading data!
            value = mydict[key]
        logP.debug("Loaded with key {} length: {}".format(key, len(value)))
        return value
    except Exception as ex:
        logP.warning(["Error during loading data:", ex])
    logP.debug("End load")


# function to setup cog
def setup(bot: commands.Bot):
    bot.add_cog(Options(bot))
