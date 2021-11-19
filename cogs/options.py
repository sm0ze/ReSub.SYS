# options.py

import math
import os
import random
import typing

import discord
import tatsu
from BossSystemExecutable import askToken, nON, servList
from discord.ext import commands, tasks
from discord.ext.commands import MemberConverter
from discord.utils import get
from dotenv import load_dotenv
from mee6_py_api import API
from sqlitedict import SqliteDict
import SysInf.enhancements as enm
from SysInf.power import (
    cmdInf,
    leader,
    posTask,
    power,
    powerTypes,
    rankColour,
    remList,
    restrictedList,
    rsltDict,
    taskVar,
)

DEBUG = 0
TEST = 0


def debug(*args):
    if DEBUG:
        print(*args)


debug("{} DEBUG TRUE".format(os.path.basename(__file__)))


if TEST:
    print("{} TEST TRUE".format(os.path.basename(__file__)))
# if TEST: print("".format())

# .env variables that are not shared with github and other users.
# Use your own if testing this with your own bot
load_dotenv()
TATSU = os.getenv("TATSU_TOKEN")
SAVEFILE = os.getenv("SAVEFILE")
STARTCHANNEL = os.getenv("STARTCHANNEL")

if not TATSU:
    TATSU = askToken("TATSU_TOKEN")
if not SAVEFILE:
    SAVEFILE = askToken("SAVEFILE")
if not STARTCHANNEL:
    STARTCHANNEL = askToken("STARTCHANNEL")


SUPEROLE = "Supe"
PERMROLES = ["Supe"]  # guild role(s) for using these bot commands
MANAGER = "System"  # manager role name for guild
LOWESTROLE = 2  # bot sorts roles by rank from position of int10 to LOWESTROLE
HIDE = False
LEADLIMIT = 12
NEWCALC = 1
GEMDIFF = 0.5
taskCD = 60 * 30

if DEBUG:
    taskCD = 0

# TODO: implement this and similiar instead of
# multiple enhancement.dict.keys() calls
# enhancement (type, rank) pairs for list command
ENHLIST = [(x, y) for (x, y) in powerTypes.items()]


class Options(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.grabLoop.start()
        self._connection = bot._connection

    # Check if user has guild role
    async def cog_check(self, ctx):

        debug("Role check start")

        async def predicate(ctx):
            for role in PERMROLES:
                debug("Role check {} in {}".format(role, PERMROLES))
                chkRole = get(ctx.guild.roles, name=role)
                debug("chkRole = {}".format(chkRole))
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

    @tasks.loop(minutes=30)
    async def grabLoop(self):
        await self.bot.wait_until_ready()
        debug("Start channel id is", STARTCHANNEL)
        StrtChannel = self.bot.get_channel(int(STARTCHANNEL))
        debug("Start channel is", StrtChannel)
        if DEBUG and StrtChannel:
            await StrtChannel.send("Bot has started xp update")
        roleGrab = None
        for guild in self.bot.guilds:
            roleGrab = get(guild.roles, name=SUPEROLE)
            debug("role grabbed = ", roleGrab)
            if roleGrab:
                for peep in roleGrab.members:
                    await count(peep)
        if DEBUG and StrtChannel:
            await StrtChannel.send("Bot has finished xp update")

    @commands.command(
        brief=cmdInf["trim"]["brief"],
        description=cmdInf["trim"]["description"],
    )
    # command to trim command caller of extra roles. OBSOLETE due to cut call
    # after role add in add command
    async def trim(self, ctx, *, member=""):
        debug("funcTrim START")

        memberList = await memGrab(self, ctx, "")  # member)
        debug("\tmemberlist = {}".format(memberList))

        await cut(ctx, memberList)
        debug("funcTrim END")
        return

    """@commands.command(
        hidden=HIDE,
        brief=cmdInf["trimAll"]["brief"],
        description=cmdInf["trimAll"]["description"],
    )
    @commands.has_any_role(MANAGER)
    # manager command to role trim all users bot has access to
    async def trimAll(self, ctx):
        debug("funcTrimAll START")

        memberList = isSuper(self, servList(self.bot))
        debug("\tmemberlist to cut = {}".format([x.name for x in memberList]))

        await cut(ctx, memberList)
        debug("funcTrimAll END")
        return"""

    @commands.command(
        hidden=HIDE,
        brief=cmdInf["roleInf"]["brief"],
        description=cmdInf["roleInf"]["description"],
    )
    @commands.has_any_role(MANAGER)
    # manager command to check if guild has role and messages
    # some information of the role
    async def roleInf(self, ctx, *, roleStr: str):
        supeGuildRoles = await orderRole(self, ctx)
        roleStrId = [x for x in supeGuildRoles if roleStr == x.name]
        debug("Role string ID is: {}".format(roleStrId[0].id))
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
        brief=cmdInf["convert"]["brief"],
        description=cmdInf["convert"]["description"],
    )
    async def convert(self, ctx, inVar: float = 0, gdv=0):
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
        aliases=["t"],
        brief=cmdInf["task"]["brief"],
        description=cmdInf["task"]["description"],
    )
    @commands.cooldown(1, taskCD, type=commands.BucketType.user)
    async def task(self, ctx):
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
        debug("Task is worth {}".format(taskWorth))
        taskAdd = taskShrt["Add"]
        debug("Task can have additional {} peeps".format(taskAdd))

        if taskAdd:
            debug(ctx.message.guild.roles)
            peepToAdd = get(ctx.message.guild.roles, name=SUPEROLE)
            debug(peepToAdd.id, peepToAdd.name)
            if taskAdd == -1:
                addPeeps = peepToAdd.members
                addPeeps.remove(ctx.message.author)
                # addNames = "every host of the Superhero Enhancement System!"
            else:
                addPeeps = random.sample(peepToAdd.members, k=taskAdd + 1)
                debug("peeps list is: {}".format(addPeeps))
                if ctx.message.author in addPeeps:
                    addPeeps.remove(ctx.message.author)
            xpList = [[x, taskShrt["Aid"]] for x in addPeeps[:taskAdd]]
            xpList.append([ctx.message.author, 1])
        else:
            addPeeps = ""
            xpList = [[ctx.message.author, 1]]
        debug("xpList = ", xpList)
        debug(
            "{}\nTask XP: {}\n10 XP in GDV: {}".format(
                taskType, lvlEqu(taskWorth[0], 1), lvlEqu(10)
            )
        )
        emptMes = discord.Embed(
            title="Alert, {}!".format(nON(ctx.message.author)),
            description=("A new {} GDV task " "has been assigned.").format(
                taskType[0]
            ),
        )

        debug("Possible Adjective: {}".format(taskShrt["Adjective"]))
        selAdj = random.choice(taskShrt["Adjective"])
        debug("Selected Adjective: {}".format(selAdj))

        debug("Possible People: {}".format(taskShrt["People"]))
        selPeep = random.choice(taskShrt["People"])
        debug("Selected People: {}".format(selPeep))

        debug("Possible Action: {}".format(taskShrt["Action"]))
        selAct = random.choice(taskShrt["Action"])
        debug("Selected Action: {}".format(selAct))

        debug("Possible Location: {}".format(taskShrt["Location"]))
        selPlace = random.choice(taskShrt["Location"])
        debug("Selected Location: {}".format(selPlace))

        taskGrant = random.randrange(taskWorth[0], taskWorth[1] + 1)
        if DEBUG:
            # taskGrant = taskWorth[1]
            pass
        debug("task Grant = ", taskGrant)
        taskDiff = taskWorth[1] - taskWorth[0]
        debug("task diff = ", taskDiff)

        selResult = round(
            ((taskGrant - taskWorth[0]) / (2 * taskDiff)) + 0.5, 3
        )

        debug("selected result = ", selResult)
        debug(
            "int(selResult * 100):",
            int(selResult * 100),
            [[x, rsltDict[x]] for x in rsltDict.keys()],
        )

        selRsltWrd = [
            x
            for x in rsltDict.keys()
            if int(selResult * 100)
            in range(int(100 * rsltDict[x][0]), int(100 * rsltDict[x][1]))
        ]
        debug("selected resulting word = ", selRsltWrd)
        if selRsltWrd:
            selRsltWrd = selRsltWrd[0]

        elif taskWorth[1] == taskGrant:
            selRsltWrd = "flawless"
        debug("taskWorth[1] == taskGrant", taskWorth[1], taskGrant)

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
            debug(e)
        if not authInf:
            authInf = {}

        for peep in reversed(xpList):
            debug("peep is: ", peep)
            if peep[0].id in authInf.keys():
                authInf[peep[0].id]["invXP"][-1] += taskGrant * peep[1]
            else:
                authInf[peep[0].id] = {"Name": peep[0].name}
                authInf[peep[0].id]["invXP"] = [0, 0, taskGrant * peep[1]]

            if peep[0].id == ctx.message.author.id or taskAdd != -1:
                emptMes.add_field(
                    name="{} Earns".format(nON(peep[0])),
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
        debug(
            "{} has {} available enhancements".format(
                nON(ctx.message.author), currEnhP
            )
        )
        stateG = spent([ctx.message.author])
        currEnh = int(stateG[0][1])
        debug("and enhancments of number = ", currEnh)
        debug(
            "currEnh {} < currEnhP {}".format(currEnh, currEnhP),
            currEnh < currEnhP,
        )
        if currEnh < currEnhP:
            val = "{} has {} unspent enhancement point{}.".format(
                nON(ctx.message.author),
                currEnhP - currEnh,
                pluralInt(currEnhP - currEnh),
            )

            emptMes.add_field(name="Unspent Alert", value=val)

        await ctx.send(embed=emptMes)

        return

    @task.error
    async def task_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            cdTime = round(error.retry_after, 2)
            mes = (
                "You have no available tasks at this time. Please search ag"
                "ain in {} minutes or {} seconds."
            ).format(round(cdTime / 60, 2), cdTime)
        else:
            mes = str(error)
        await ctx.send(
            embed=discord.Embed(title="No Tasks", description=mes),
            delete_after=5,
        )
        await ctx.message.delete(delay=5)

    @commands.command(
        aliases=["a"],
        brief=cmdInf["add"]["brief"],
        description=cmdInf["add"]["description"],
    )
    # add role command available to all PERMROLES users
    async def add(self, ctx, *, typeRank=""):

        # fetch message author and their current enhancement roles
        # as well as the build for those roles
        user = ctx.message.author
        userSpent = spent([user])
        userEnhancements = userSpent[0][2]
        userHas = funcBuild(userEnhancements)
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
            debug(buildList)

        # add requested enhancements to current user build
        # then grab the information for this new user build
        [userEnhancements.append(x) for x in buildList]
        userWants = funcBuild(userEnhancements)
        userWantsCost = userWants[0]
        userWantsBuild = userWants[2]
        pointTot = await count(user, 1, 1)
        debug(
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
                    nON(user),
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
        debug("Add list = {}".format(addList))

        # restricted roles the user does not have that the build requires
        cantAdd = [x for x in restrictedList if x in addList]
        cantAdd = [x for x in cantAdd if x not in [y.name for y in user.roles]]
        debug("Cant add = {}".format(cantAdd))

        # check to ensure user has restricted roles already,
        # if required for build
        if cantAdd:
            await ctx.send(
                ("Cannot add enhancements as {} does not have {}").format(
                    nON(user), cantAdd
                )
            )
            return

        # guild role list with name and id attributes
        guildRoles = await user.guild.fetch_roles()

        # iterate through roles to add to user
        sendMes = ""
        for role in addList:
            debug("Trying to add role: {}".format(role))

            # check for if user has enhancement role already
            roleId = get(guildRoles, name=role)
            if roleId in user.roles:
                debug("{} already has the role {}".format(nON(user), roleId))
                # sendMes += ("{} already has the role {}\n"
                #               ).format(nON(user), roleId))
                continue

            # role names to add will have format "Rank *Rank* *Type*"
            roleRank = role.split()[1]
            debug(roleId, roleRank)

            # check for role already in guild role list, create it if required
            if not roleId:
                colour = rankColour[int(roleRank)]
                debug("colour for rank {} is: {}".format(roleRank, colour))
                roleId = await user.guild.create_role(name=role, color=colour)

            # add requested role to user
            await user.add_roles(roleId)
            sendMes += "{} now has {}!\n".format(nON(user), roleId)

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
    async def hhelp(self, ctx):
        commands.DefaultHelpCommand(no_category="Basic Options", hidden=True)
        return

    @commands.command(
        hidden=HIDE,
        brief=cmdInf["moveRoles"]["brief"],
        description=cmdInf["moveRoles"]["description"],
    )
    @commands.has_any_role(MANAGER)
    # manager command to correct role position for roles that
    # have been created by bot
    async def moveRoles(self, ctx):
        managed = await manageRoles(ctx)
        await ctx.send(embed=managed)
        return

    @commands.command(
        aliases=["p"],
        brief=cmdInf["points"]["brief"],
        description=cmdInf["points"]["description"],
    )
    # command to get author or specified user(s) enhancement total
    # and available points
    async def points(self, ctx, *, member=""):
        users = await memGrab(self, ctx, member)
        # restrict user list to those with SUPEROLE
        supeUsers = isSuper(self, users)
        if not supeUsers:  # if no SUPEROLE users in list
            [await ctx.send("{} is not a Supe".format(nON(x))) for x in users]
            return

        # fetch points of each SUPEROLE user
        pointList = spent(supeUsers)

        # return result
        for group in pointList:
            debug("group in level is: {}".format(group))
            pointTot = await countOf(group[0])
            await ctx.send(
                (
                    "{} has {} enhancement{} active out of {} enhancement{} "
                    "available."
                ).format(
                    nON(group[0]),
                    group[1],
                    pluralInt(group[1]),
                    pointTot[0],
                    pluralInt(pointTot[0]),
                )
            )
        return

    @commands.command(
        aliases=["l"],
        brief=cmdInf["list"]["brief"],
        description=cmdInf["list"]["description"],
    )
    # help level command to list the available enhancements and the
    # shorthand to use them in commands
    async def list(self, ctx):
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
        debug("funcList - ", mes)
        mes.set_footer(text="Starred enhancements require advanced roles")
        await ctx.send(embed=mes)
        return

    @commands.command(
        aliases=["b"],
        brief=cmdInf["build"]["brief"],
        description=cmdInf["build"]["description"],
    )
    # build command to theory craft and check the prereqs for differnet
    # enhancement ranks can be used in conjunction with points command to
    # determine if user can implement a build
    async def build(self, ctx, *, typeRank=""):
        debug("Build command start")
        debug(typeRank)

        # check for args, else use user's current build
        # split args into iterable shorthand list
        if typeRank:
            fixArg = typeRank.replace(" ", ",")
            fixArg = fixArg.replace(";", ",")
            buildList = [x.strip() for x in fixArg.split(",") if x.strip()]
            debug(buildList)
        else:
            buildList = spent([ctx.message.author])[0][2]
        debug("buildList = {}".format(buildList))

        # fetch cost and requisite list for build
        buildTot = funcBuild(buildList)

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

    @commands.command()
    @commands.has_any_role(MANAGER)
    async def average(self, ctx):
        mes = discord.Embed(title="Average Enhancment Points")
        debug(leader.keys())
        getSupe = [x for x in ctx.guild.roles if str(x.name) == SUPEROLE]
        if not getSupe:
            await ctx.send("No users of role: {}".format(SUPEROLE))
        else:
            getSupe = getSupe[0]
        for val in leader.values():
            debug("value", val)
            peepDict = topEnh(ctx, val)
            debug("peepDict", peepDict)

            sumPeep = sum(peepDict.values())
            lenPeep = len(peepDict.keys())
            avPeep = round(sumPeep / len(getSupe.members), 4)

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
        await ctx.send(embed=mes)

    @commands.command(
        aliases=["leaderboard"],
        brief=cmdInf["top"]["brief"],
        description=cmdInf["top"]["description"],
    )
    # top 10 user leaderboard for number of used enhancements
    async def top(
        self,
        ctx,
        lead: typing.Optional[int] = LEADLIMIT,
        page: typing.Optional[int] = 1,
        *,
        enh=""
    ):

        xpKey = ["xp", "gdv"]
        if MANAGER in [str(x.name) for x in ctx.message.author.roles]:
            leader = lead
        else:
            if lead < LEADLIMIT:
                leader = lead
            else:
                leader = LEADLIMIT
        if leader < 1:
            leader = 1
        strtLead = page * leader - leader
        endLead = page * leader

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
            debug("HERE enh", enh)
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
            guildList = servList(self.bot)
            debug("Guild list is: {}".format(guildList))

            # restrict list to those with SUPEROLE
            supeList = isSuper(self, guildList)
            debug("Supe list is: {}".format(supeList))

            # fetch points of each SUPEROLE user
            pointList = spent(supeList)
            debug(pointList)

            # sort list of users with enhancements by
            # number of enhancements; descending
            pointList = sorted(pointList, key=lambda x: x[1], reverse=True)
            debug(pointList)
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
                    name="**{}** - {}".format(i, nON(group[0])),
                    value="\t{} enhancements".format(group[1]),
                )
            else:
                if not enh.lower() in xpKey:
                    blankMessage.add_field(
                        inline=True,
                        name="**{}** - {}".format(i, nON(group[0])),
                        value="\tRank {} {}".format(group[1], enh),
                    )
                else:
                    blankMessage.add_field(
                        inline=True,
                        name="**{}** - {}".format(i, nON(group[0])),
                        value="\t{:,} {}".format(group[1], enh.upper()),
                    )
            i += 1

        # return leaderboard to command caller
        await ctx.send(embed=blankMessage)

    @commands.command(
        aliases=["c", "clear"],
        brief=cmdInf["clean"]["brief"],
        description=cmdInf["clean"]["description"],
    )
    # remove unrestricted enhancements from command caller
    async def clean(self, ctx):
        # rank 0 enhancements are either restricted or the SUPEROLE,
        # which should not be removed with this command
        toCut = [
            x.name
            for x in ctx.message.author.roles
            if x.name
            in [power[y]["Name"] for y in power.keys() if power[y]["Rank"] > 0]
        ]
        debug(toCut)
        await cut(ctx, [ctx.message.author], toCut)
        return

    @commands.command(hidden=HIDE)
    @commands.has_any_role(MANAGER)
    async def xpAdd(self, ctx, val: float, *, mem=""):
        val = round(val, 2)
        debug("val is", val)
        memList = await memGrab(self, ctx, mem)
        debug("memList is", memList)
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
        await ctx.send("Host {}: {} -> {}".format(nON(peep), iniVal, sum))

    @commands.command(
        hidden=HIDE,
        brief=cmdInf["xpGrab"]["brief"],
        description=cmdInf["xpGrab"]["description"],
    )
    # @commands.has_any_role(MANAGER)
    @commands.cooldown(1, 1, commands.BucketType.default)
    async def xpGrab(self, ctx, *, mem=""):
        typeMem = await memGrab(self, ctx, mem)
        typeMem = [typeMem[0]]
        pointList = spent(typeMem)
        # tatForce = 0
        i = 0
        # for role in ctx.author.roles:
        #     if role.name == MANAGER:
        #         tatForce = 1
        for peep in typeMem:
            mes = discord.Embed(title="{} Stats".format(nON(peep)))
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
                value="{:,}".format(nextGDVneedXP),
            )

            nextEnhP = int(5 * (int(stuff[1] / 5) + 1))
            nextEnhP_XP = lvlEqu(nextEnhP, 1)
            nextEnhPneedXP = nextEnhP_XP - stuff[2]

            mes.add_field(
                inline=False,
                name="XP to next Enhancement Point",
                value="{:,}".format(nextEnhPneedXP),
            )

            mes.add_field(
                inline=False,
                name="Unspent Enhancement Point{}".format(pluralInt(unspent)),
                value=unspent,
            )

            mes.set_footer(
                text="{}#{}".format(peep.name, peep.discriminator),
                icon_url=peep.avatar,
            )

            await ctx.send(embed=mes)
            i += 1
        return


# function to move roles to correct rank positions
async def manageRoles(ctx):
    debug("ManageRoles Start")

    # spam message negation
    movedRoles = discord.Embed(title="Moving Roles")
    toMove = {}

    # iterate through all guild roles
    for role in ctx.message.guild.roles:
        debug("Looking at role: {}".format(role.name))

        # grab shorthand for enhancement
        roleShort = [x for x in power.keys() if power[x]["Name"] == role.name]
        debug("roleShort = {}".format(roleShort))

        # check to ensure role is one overseen by this bot
        if roleShort == []:
            debug("Role not Supe")
            continue

        # check for intelligence roles as they are the rank position constants
        # and should not be changed by this command
        elif "Intelligence" == power[roleShort[0]]["Type"]:
            debug("Role type intelligence")
            continue

        # fetch enhancement rank
        roleRank = power[roleShort[0]]["Rank"]
        debug("Role rank is: {}".format(roleRank))

        # check for restricted roles
        if not roleRank:
            debug("Role rank zero")
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
                == ("Rank {} Intelligence (only for " "Systems)").format(
                    roleRank - 1
                )
            ][0]

        # fetch upperbound intelligence rank position
        roleRankUpper = [
            x.position
            for x in ctx.message.guild.roles
            if x.name
            == ("Rank {} Intelligence (only for " "Systems)").format(roleRank)
        ][0]

        # roleDiff = roleRankUpper - roleRankLower

        # check for if role is already in postion
        if role.position < roleRankUpper:
            if role.position >= roleRankLower:
                debug(
                    "Role within bounds {} - {}".format(
                        roleRankUpper, roleRankLower
                    )
                )
                continue

        # move role to current upperbound intelligence position,
        # forcing intelligence position to increase
        # ASSUMES current role position is lower than intelligence position
        # TODO remove assumption
        debug(
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
    debug("ManageRoles End")
    return movedRoles


# function to get specified user's enhancement points


async def count(peep: discord.Member, typ=NEWCALC, tatFrc=0):
    debug("Start count")
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
        MEE6xp = 0
    try:
        pickle_file = load(peep.guild.id)
        debug(pickle_file)
        ReSubXP = pickle_file[peep.id]["invXP"][-1]
    except Exception as e:
        print(e)
        ReSubXP = 0
    debug("ReSubXP = ", ReSubXP)

    try:
        TATSUxp = TATSUmem.xp
    except AttributeError:
        TATSUxp = 0
    debug("TATSUxp = ", TATSUxp)

    try:
        if not MEE6xp:
            if pickle_file[peep.id]["invXP"][0]:
                MEE6xp = pickle_file[peep.id]["invXP"][0]
    except Exception as e:
        print(e)
        MEE6xp = 0
    debug("MEE6xp = ", MEE6xp)

    try:
        if not TATSUxp:
            if pickle_file[peep.id]["invXP"][0]:
                TATSUxp = pickle_file[peep.id]["invXP"][1]
    except Exception as e:
        print(e)
        TATSUxp = 0
    if MEE6xp or TATSUxp or ReSubXP:
        totXP = ReSubXP + MEE6xp + (TATSUxp / 2)
    else:
        totXP = 0
    if nON(peep) == "Geminel":
        totXP = totXP * GEMDIFF
    debug("totXP = ", totXP)

    gdv = lvlEqu(totXP)
    debug("gdv = ", gdv)

    enhP = math.floor(gdv / 5) + 1
    debug("enhP = ", enhP)
    if pickle_file:
        pickle_file[peep.id] = {
            "Name": peep.name,
            "enhP": enhP,
            "gdv": gdv,
            "totXP": totXP,
            "invXP": [MEE6xp, TATSUxp, ReSubXP],
        }
        save(peep.guild.id, pickle_file)
    else:
        save(
            peep.guild.id,
            {
                peep.id: {
                    "Name": peep.name,
                    "enhP": enhP,
                    "gdv": gdv,
                    "totXP": totXP,
                    "invXP": [MEE6xp, TATSUxp, ReSubXP],
                }
            },
        )
    debug("End count")
    return enhP, gdv, totXP, [MEE6xp, TATSUxp, ReSubXP]


async def countOf(peep):
    debug("Start countOf")
    try:
        valDict = load(peep.guild.id)
        debug("valDict = ", valDict)
        shrt = valDict[peep.id]
        debug("shrt = ", shrt)
        debug("End countOf - succ load")
        return shrt["enhP"], shrt["gdv"], shrt["totXP"], shrt["invXP"]
    except Exception as e:
        print(e)
        debug("End countOf - fail load")
        return await count(peep)


# restrict list from members to members with SUPEROLE
def isSuper(self, guildList):
    debug("Start isSuper")
    guilds = self.bot.guilds
    supeGuildList = []
    [
        supeGuildList.append(z)
        for z in [
            x.members for x in [get(y.roles, name=SUPEROLE) for y in guilds]
        ]
    ]
    debug(
        "[get(y.roles, name=SUPEROLE) for y in guilds] = {}".format(
            [get(y.roles, name=SUPEROLE) for y in guilds]
        )
    )
    debug(
        (
            "[x.members for x in [get(y.roles, name=SUPEROLE) for y in "
            "guilds]] = {}"
        ).format(
            [x.members for x in [get(y.roles, name=SUPEROLE) for y in guilds]]
        )
    )
    debug(
        (
            "[supeGuildList.append(z) for z in [x.members for x in "
            "[get(y.roles, name=SUPEROLE) for y in guilds]]] = {}"
        ).format(supeGuildList)
    )
    supeList = [x for x in supeGuildList[0] if x in guildList]
    debug(supeList)

    # return reduced user list
    debug("End isSuper")
    return supeList


# from shorthand enhancement list return cost of build,
# role names and prerequisite roles
def funcBuild(buildList):
    debug("Start funcBuild")
    reqList = []
    nameList = []
    debug("Build command buildList = {}".format(buildList))

    # iterate through shorthand enhancements
    for item in buildList:
        debug("Build command item = {}".format(item))
        # fetch enhancement prereqs and cost
        temCost = enm.cost(item)
        debug("Build command prereq cost = {}".format(temCost))

        # add this enhancement's prereqs to list
        reqList.append(temCost[2])

        # fetch full name for enhancement from shorthand
        tempName = power[item]["Name"]

        # add enhancement full name to lists
        reqList.append(tempName)
        nameList.append(tempName)
    debug("Build command reqList is: {}".format(reqList))

    # restrict nested prereq list to a set of prereqs
    temp = enm.eleCountUniStr(reqList)
    debug("temp = {}".format(temp))

    # fetch highest ranked prereqs of each type in list
    reqList = enm.trim([x for x in temp[1]])
    debug("reqList = {}".format(reqList))

    # sum cost of build from prereqs
    costTot = 0
    for group in reqList:
        debug(group)
        costTot += group[0]
    debug(costTot, nameList, reqList)

    # return cost of build, role names and prerequisite roles
    debug("End funcBuild")
    return costTot, nameList, reqList


# function to grab number of enhancement points
# spent by each user in given list
def spent(memList):
    debug("Start spent")
    retList = []
    debug("memList is: {}".format(memList))

    # iterate thorugh given list of users
    for peep in memList:
        supeRoles = []
        debug("current user is: {}".format(peep))
        debug("current user role list: {}".format(peep.roles))

        # messy implementation to grab shorthand for all unrestricted bot
        # managed roles in user role list
        for roles in peep.roles:
            if roles.name in [
                power[x]["Name"] for x in power.keys() if power[x]["Rank"] > 0
            ]:
                supeRoles.append(
                    [
                        x
                        for x in power.keys()
                        if power[x]["Name"] == roles.name
                    ][0]
                )
        debug("Supe roles: {}".format(supeRoles))

        # fetch point cost (including prereqs) of enhancements
        if supeRoles:
            pointCount = funcBuild(supeRoles)[0]
        else:
            pointCount = funcBuild([])[0]

        # add (user, total build cost, enhancmeent role names)
        # to list to return
        retList.append([peep, pointCount, supeRoles])

    debug("retlist is: {}".format(retList))
    debug("End spent")
    return retList


# function to fetch all users requested by command caller
async def memGrab(self, ctx, memList=""):
    debug("Start memGrab")
    debug(
        "memList: {}\nand mentions: {}".format(memList, ctx.message.mentions)
    )

    # first check for users mentioned in message
    if ctx.message.mentions:
        grabList = ctx.message.mentions
        debug("Message mentions: {}".format(grabList))

    # else check for users named by command caller
    elif memList:
        grabList = memList.split(", ")
        debug("split grablist: {}".format(grabList))
        for i in range(0, len(grabList)):
            debug("position {} grablist: {}".format(i, grabList[i]))
            grabList[i] = await MemberConverter().convert(ctx, grabList[i])

    # else use the command caller themself
    else:
        grabList = [ctx.message.author]
        debug("Author is: {}".format(grabList))
    debug("fixed grablist: {}".format(grabList))
    debug("End memGrab")

    # return: mentioned users || named users || message author
    return grabList


# get roles of a lower rank on member to remove later
def toCut(member):
    debug("Start toCut")

    # fetch unrestricted managed roles member has
    supeRoles = spent([member])
    debug("supeRoles = {}".format(supeRoles[0][2]))

    # fetch build of member
    supeBuild = funcBuild(supeRoles[0][2])
    debug("supeBuild = {}".format(supeBuild[1]))

    # fetch trimmed build of user
    supeTrim = [
        power[enm.toType(x[1]) + str(x[0])]["Name"]
        for x in enm.trim(supeBuild[1])
    ]
    debug("supeTrim = {}".format(supeTrim))

    # fetch extra roles user has that are to be removed
    toCut = [x for x in supeBuild[1] if x not in supeTrim]
    debug("to CUT = {}".format(toCut))

    # return the roles to be removed
    debug("End toCut")
    return toCut


# function to remove extra or specified roles from list of users
async def cut(ctx, memberList, cutList=[]):
    debug("Start cut")
    # iterate through given user list
    # assumed list has already been reduced to users with SUPEROLE
    for peep in memberList:

        # if no list of roles to remove was given get user's extra roles
        if not cutList:
            cutting = toCut(peep)
        else:
            cutting = cutList

        # for each role to be cut, remove it and send message to discord
        sendMes = ""
        for role in cutting:
            debug(
                "\t\t role to cut = {}\n\t\t from peep {}".format(role, peep)
            )
            supeRoleId = get(peep.roles, name=role)
            debug("\t\t role to cut id = {}".format(supeRoleId))
            if supeRoleId in peep.roles:
                await peep.remove_roles(supeRoleId)
                sendMes += "{} no longer has {} \n{}\n".format(
                    nON(peep), supeRoleId, random.choice(remList)
                )

        # notify current user has been finished with to discord
        sendMes += "{} has been cut down to size!".format(nON(peep))
        await ctx.send(sendMes)
    debug("End cut")
    return


# function to fetch all guild roles that are managed by bot
async def orderRole(self, ctx):
    debug("Start orderRole")
    debug(power.values())

    supeList = [
        x
        for x in ctx.message.author.guild.roles
        if str(x) in [y["Name"] for y in power.values()]
    ]

    debug(supeList)
    debug("End orderRole")
    return supeList


def lvlEqu(givVar: float = 0, inv=0):
    debug("Start lvlEqu")
    if inv:
        calVar = (20 * math.pow(givVar, 2)) / 1.25
        debug("{} GDV is equivalent to {:,} XP".format(givVar, calVar))
    else:
        calVar = math.sqrt((1.25 * givVar) / 20)
        debug("{:,} XP is equivalent to {} GDV".format(givVar, calVar))
    debug("End lvlEqu")
    return round(calVar, 2)


def aOrAn(inp):
    debug("Start aOrAn")
    debug("input is: ", inp)
    ret = "A"
    if inp.lower() in "aeiou":
        ret = "An"
    debug("ret = ", ret)
    debug("End aOrAn")
    return ret


def pluralInt(val: int):
    rtnStr = ""
    if not val == 1:
        rtnStr = "s"
    return rtnStr


def topEnh(ctx, enh):

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


def save(key, value, cache_file=SAVEFILE):
    debug("Start save")
    try:
        with SqliteDict(cache_file) as mydict:
            mydict[key] = value  # Using dict[key] to store
            mydict.commit()  # Need to commit() to actually flush the data
        debug("saved {}: {}".format(key, value))
    except Exception as ex:
        print("Error during storing data (Possibly unsupported):", ex)
    debug("End save")


def load(key, cache_file=SAVEFILE):
    debug("Start load")
    try:
        with SqliteDict(cache_file) as mydict:
            # No need to use commit(), since we are only loading data!
            value = mydict[key]
        debug("Loaded: ", value)
        return value
    except Exception as ex:
        print("Error during loading data:", ex)
    debug("End load")


# function to setup cog
def setup(bot: commands.Bot):
    bot.add_cog(Options(bot))


if TEST:

    async def Testing():
        pass
