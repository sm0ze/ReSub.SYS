# options.py

import math
import os
import random

import discord
import enhancements as enm
import tatsu
from BossSystemExecutable import askToken, nON, servList
from discord.ext import commands, tasks
from discord.ext.commands import MemberConverter
from discord.utils import get
from dotenv import load_dotenv
from mee6_py_api import API
from sqlitedict import SqliteDict

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
# GUILD is the guild id the bot and MEE6 bot are on,
# it's possible to grab this after bot logs into guild instead of hard coding it
load_dotenv()
GUILD = os.getenv('DISCORD_GUILD')
TATSU = os.getenv('TATSU_TOKEN')
SAVEFILE = os.getenv('SAVEFILE')
STARTCHANNEL = os.getenv('STARTCHANNEL')

if not GUILD:
    GUILD = askToken('DISCORD_GUILD')
if not TATSU:
    TATSU = askToken('TATSU_TOKEN')
if not SAVEFILE:
    SAVEFILE = askToken('SAVEFILE')
if not STARTCHANNEL:
    STARTCHANNEL = askToken('STARTCHANNEL')


SUPEROLE = "Supe"
PERMROLES = ['Supe']  # guild role(s) for using these bot commands
MANAGER = 'System'  # manager role name for guild
LOWESTROLE = 2  # bot sorts roles by rank from position of int10 to LOWESTROLE
HIDE = False
LEADLIMIT = 10
NEWCALC = 1
GEMDIFF = 0.5
taskCD = 60 * 30

# TODO: implement this and similiar instead of multiple enhancement.dict.keys() calls
# enhancement (type, rank) pairs for list command
ENHLIST = [(x, y) for (x, y) in enm.powerTypes.items()]


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
                "You do not have permission as you are missing a role in this list: {}\nThe super command can be used to gain the Supe role".format(PERMROLES))  # messy implementation for Supe
        return commands.check(await predicate(ctx))

    @tasks.loop(minutes=30)
    async def grabLoop(self):
        await self.bot.wait_until_ready()
        debug("Start channel id is", STARTCHANNEL)
        StrtChannel = self.bot.get_channel(int(STARTCHANNEL))
        debug("Start channel is", StrtChannel)
        if DEBUG and StrtChannel:
            await StrtChannel.send('Bot has started xp update')
        roleGrab = None
        for guild in self.bot.guilds:
            roleGrab = get(guild.roles, name=SUPEROLE)
            debug("role grabbed = ", roleGrab)
            if roleGrab:
                for peep in roleGrab.members:
                    await count(peep)
        if DEBUG and StrtChannel:
            await StrtChannel.send('Bot has finished xp update')

    @commands.command(
        brief=enm.cmdInf['trim']['brief'],
        description=enm.cmdInf['trim']['description'])
    # command to trim command caller of extra roles. OBSOLETE due to cut call after role add in add command
    async def trim(self, ctx, *, member=''):
        debug("funcTrim START")

        memberList = await memGrab(self, ctx, '')  # member)
        debug("\tmemberlist = {}".format(memberList))

        await cut(ctx, memberList)
        debug("funcTrim END")
        return

    @commands.command(
        hidden=HIDE,
        brief=enm.cmdInf['trimAll']['brief'],
        description=enm.cmdInf['trimAll']['description'])
    @commands.has_any_role(MANAGER)
    # manager command to role trim all users bot has access to
    async def trimAll(self, ctx):
        debug("funcTrimAll START")

        memberList = isSuper(self, servList(self.bot))
        debug("\tmemberlist to cut = {}".format(
            [x.name for x in memberList]))

        await cut(ctx, memberList)
        debug("funcTrimAll END")
        return

    @commands.command(
        hidden=HIDE,
        brief=enm.cmdInf['roleInf']['brief'],
        description=enm.cmdInf['roleInf']['description'])
    @commands.has_any_role(MANAGER)
    # manager command to check if guild has role and messages some information of the role
    async def roleInf(self, ctx, *, roleStr: str):
        supeGuildRoles = await orderRole(self, ctx)
        roleStrId = [x for x in supeGuildRoles if roleStr == x.name]
        debug("Role string ID is: {}".format(roleStrId[0].id))
        if roleStrId:
            roleStrId = roleStrId[0]
            await ctx.send(
                "{.name} has: \nposition - {.position}\ncolour - {.colour}".format(roleStrId, roleStrId, roleStrId))
        return

    @commands.command(
        brief=enm.cmdInf['convert']['brief'],
        description=enm.cmdInf['convert']['description'])
    async def convert(self, ctx, inVar: float = 0, gdv=0):
        feedback = lvlEqu(inVar, gdv)
        if gdv:
            await ctx.send(
                "{} GDV is equivalent to {:,} XP".format(inVar, feedback))
        else:
            await ctx.send(
                "{:,} XP is equivalent to {} GDV".format(inVar, feedback))

    @commands.command(
        aliases=['t'],
        brief=enm.cmdInf['task']['brief'],
        description=enm.cmdInf['task']['description'])
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
            enm.taskVar['taskOpt'][0], cum_weights=enm.taskVar['taskWeight'])
        taskShrt = enm.posTask[taskType[0]]
        taskWorth = taskShrt['Worth']
        debug("Task is worth {}".format(taskWorth))
        taskAdd = taskShrt['Add']
        debug("Task can have additional {} peeps".format(taskAdd))

        if taskAdd:
            debug(ctx.message.guild.roles)
            peepToAdd = get(ctx.message.guild.roles, name=SUPEROLE)
            debug(peepToAdd.id, peepToAdd.name)
            if taskAdd == -1:
                addPeeps = peepToAdd.members
                addPeeps.remove(ctx.message.author)
                addNames = "every host of the Superhero Enhancement System!"
            else:
                addPeeps = random.sample(peepToAdd.members, k=taskAdd + 1)
                debug("peeps list is: {}".format(addPeeps))
                if ctx.message.author in addPeeps:
                    addPeeps.remove(ctx.message.author)
                addNames = [nON(x) for x in addPeeps[:taskAdd]]
            xpList = [[x, taskShrt['Aid']] for x in addPeeps[:taskAdd]]
            xpList.append([ctx.message.author, 1])
        else:
            addPeeps = ''
            xpList = [[ctx.message.author, 1]]
        debug("xpList = ", xpList)
        debug("{}\nTask XP: {}\n10 XP in GDV: {}".format(
            taskType, lvlEqu(taskWorth[0], 1), lvlEqu(10)))
        emptMes = "Alert, {}; a new {} GDV task has been assigned.".format(
            nON(ctx.message.author), taskType[0])

        debug("Possible Adjective: {}".format(taskShrt['Adjective']))
        selAdj = random.choice(taskShrt['Adjective'])
        debug("Selected Adjective: {}".format(selAdj))

        debug("Possible People: {}".format(taskShrt['People']))
        selPeep = random.choice(taskShrt['People'])
        debug("Selected People: {}".format(selPeep))

        debug("Possible Action: {}".format(taskShrt['Action']))
        selAct = random.choice(taskShrt['Action'])
        debug("Selected Action: {}".format(selAct))

        debug("Possible Location: {}".format(taskShrt['Location']))
        selPlace = random.choice(taskShrt['Location'])
        debug("Selected Location: {}".format(selPlace))

        taskGrant = random.randrange(taskWorth[0], taskWorth[1] + 1)
        debug("task Grant = ", taskGrant)
        taskDiff = taskWorth[1] - taskWorth[0]
        debug("task diff = ", taskDiff)

        selResult = round(
            ((taskGrant - taskWorth[0]) / (2 * taskDiff)) + 0.5, 2)
        debug("selected result = ", selResult)

        selRsltWrd = [x for x in enm.rsltDict.keys()
                      if int(selResult * 100) in
                      range(
                      int(100 * enm.rsltDict[x][0]),
                      int(100 * enm.rsltDict[x][1]))]
        debug("selected resulting word = ", selRsltWrd)
        if selRsltWrd:
            selRsltWrd = selRsltWrd[0]
        elif taskWorth[1] == taskGrant:
            selRsltWrd = "flawless"

        """if addPeeps:
            emptMes += " Due to the task difficulty, assistance has been provided by {}".format(
                addNames)"""

        emptMes += " Please prevent the {} {} from {} {}.".format(
            selAdj,
            selPeep,
            selAct,
            selPlace)

        emptMes += "\n\nCongratulations on completing your {} GDV task. You accomplished {} results in your endeavors, resulting in;\n".format(
            taskType[0],
            selRsltWrd)

        try:
            authInf = load(ctx.message.author.guild.id)
        except Exception as e:
            debug(e)
        if not authInf:
            authInf = {}

        for peep in reversed(xpList):
            debug("peep is: ", peep)
            if peep[0].id in authInf.keys():
                authInf[peep[0].id]['invXP'][-1] += taskGrant * peep[1]
            else:
                authInf[peep[0].id] = {'Name': peep[0].name}
                authInf[peep[0].id]['invXP'] = [0, 0, taskGrant * peep[1]]
            if taskAdd != -1:
                emptMes += "\n{} earning {:,} GDV XP for a total of {:,} XP".format(
                    nON(peep[0]),
                    taskGrant * peep[1],
                    authInf[peep[0].id]['invXP'][-1])
        if taskAdd == -1:
            emptMes += "\n{} earning {:,} GDV XP for a total of {:,} XP\nEveryone else earning {:,} GDV XP.".format(
                nON(ctx.message.author),
                taskGrant,
                authInf[ctx.message.author.id]['invXP'][-1],
                taskGrant * taskShrt['Aid'])

        save(ctx.message.author.guild.id, authInf)
        stateL = await countOf(ctx.message.author)
        currEnhP = stateL[0]
        debug("{} has {} available enhancements".format(
            nON(ctx.message.author), currEnhP))
        stateG = spent([ctx.message.author])
        currEnh = int(stateG[0][1])
        debug("and enhancments of number = ", currEnh)
        debug("currEnh {} < currEnhP {}".format(
            currEnh, currEnhP), currEnh < currEnhP)
        if currEnh < currEnhP:
            emptMes += "\nAlert, {} has {} unspent enhancement point{}.".format(
                nON(ctx.message.author),
                currEnhP - currEnh,
                pluralInt(currEnhP - currEnh))

        await ctx.send(emptMes)

        return

    @task.error
    async def task_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CommandOnCooldown):
            cdTime = round(error.retry_after, 2)
            mes = "You have no available tasks at this time. Please search again in {} minutes or {} seconds.".format(
                round(cdTime / 60, 2),
                cdTime)
        else:
            mes = str(error)
        await ctx.send(
            embed=discord.Embed(
                title="No Tasks",
                description=mes),
            delete_after=5)
        await ctx.message.delete(delay=5)

    @commands.command(
        aliases=['a'],
        brief=enm.cmdInf['add']['brief'],
        description=enm.cmdInf['add']['description'])
    # add role command available to all PERMROLES users
    async def add(self, ctx, *, typeRank=''):

        # fetch message author and their current enhancement roles
        # as well as the build for those roles
        user = ctx.message.author
        userSpent = spent([user])
        userEnhancements = userSpent[0][2]
        userHas = funcBuild(userEnhancements)
        userHasBuild = userHas[2]

        if not typeRank:  # if author did not provide an enhancement to add, return
            await ctx.send(
                "Cannot add enhancements without an enhancement to add")
            return
        else:  # otherwise split the arglist into a readable shorthand enhancment list
            fixArg = typeRank.replace(' ', ',')
            fixArg = fixArg.replace(';', ',')
            buildList = [x.strip() for x in fixArg.split(',') if x.strip()]
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
                userWantsBuild))

        # check to ensure user has enough enhancement points to get requested additions
        if pointTot[0] < userWants[0]:
            await ctx.send(
                "{} needs {} available enhancements for {} but only has {}".format(
                    nON(user),
                    userWantsCost,
                    [enm.power[x]['Name'] for x in buildList],
                    pointTot[0]))
            return

        # the guild role names grabbed from shorthand to add to user
        addList = [enm.power[enm.toType(x[1]) + str(x[0])]['Name']
                   for x in userWantsBuild]
        debug("Add list = {}".format(addList))

        # restricted roles the user does not have that the build requires
        cantAdd = [x for x in enm.restrictedList if x in addList]
        cantAdd = [x for x in cantAdd if x not in [y.name for y in user.roles]]
        debug("Cant add = {}".format(cantAdd))

        # check to ensure user has restricted roles already if required for build
        if cantAdd:
            await ctx.send(
                "Cannot add enhancements as {} does not have {}".format(nON(user), cantAdd))
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
                # sendMes += "{} already has the role {}\n".format(nON(user), roleId))
                continue

            # role names to add will have format "Rank *Rank* *Type*"
            roleRank = role.split()[1]
            debug(roleId, roleRank)

            # check for role already in guild role list, create it if required
            if not roleId:
                colour = enm.rankColour[int(roleRank)]
                debug("colour for rank {} is: {}".format(roleRank, colour))
                roleId = await user.guild.create_role(name=role, color=colour)

            # add requested role to user
            await user.add_roles(roleId)
            sendMes += "{} now has {}!\n".format(nON(user), roleId)

        # trim the user of excess roles
        # debug("TO CUT")
        # await cut(ctx, [user])
        if not sendMes:
            await ctx.send("You cannot add enhancements of an equal or lower rank than you already have of that type")
        else:
            await ctx.send(sendMes)
        return

    @commands.command(hidden=True)
    @commands.has_any_role(MANAGER)
    # TODO implementation for manager specific help command
    async def hhelp(self, ctx):
        commands.DefaultHelpCommand(
            no_category='Basic Options', hidden=True)
        return

    @commands.command(
        hidden=HIDE,
        brief=enm.cmdInf['moveRoles']['brief'],
        description=enm.cmdInf['moveRoles']['description'])
    @commands.has_any_role(MANAGER)
    # manager command to correct role position for roles that have been created by bot
    async def moveRoles(self, ctx):
        managed = await manageRoles(ctx)
        if managed:
            await ctx.send(managed)
        else:
            await ctx.send("No roles moved")
        return

    @commands.command(
        aliases=['p'],
        brief=enm.cmdInf['points']['brief'],
        description=enm.cmdInf['points']['description'])
    # command to get author or specified user(s) enhancement total and available points
    async def points(self, ctx, *, member=''):
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
                "{} has {} enhancements active out of {} enhancements available.".format(
                    nON(group[0]),
                    group[1],
                    pointTot[0]))
        return

    @commands.command(
        aliases=['l'],
        brief=enm.cmdInf['list']['brief'],
        description=enm.cmdInf['list']['description'])
    # help level command to list the available enhancements and the shorthand to use them in commands
    async def list(self, ctx):
        # dynamic message to reduce bot messages sent
        mes = discord.Embed(
            title="Enhancements List",
            description="Use the 3 letter shorthand along with the rank you are querying for commands.\nEx: str1 for the first rank of strength.")

        # add each enhancement and the total ranks available to the message to return
        for group in ENHLIST:

            # check for mental clarity and mental celerity exception
            if group[0][0:3].lower() == "men":
                shorthand = group[0][7:10]
            else:
                shorthand = group[0][0:3]

            mes.add_field(
                name=group[0],
                value="{} of {} rank(s)".format(shorthand.lower(), group[1]))

        # return enhancement list to command caller
        debug("funcList - ", mes)
        mes.set_footer(text="Starred enhancements require advanced roles")
        await ctx.send(embed=mes)
        return

    @commands.command(
        aliases=['b'],
        brief=enm.cmdInf['build']['brief'],
        description=enm.cmdInf['build']['description'])
    # build command to theory craft and check the prereqs for differnet enhancement ranks
    # can be used in conjunction with points command to determine if user can implement a build
    async def build(self, ctx, *, typeRank=''):
        debug("Build command start")
        debug(typeRank)

        # check for args, else use user's current build
        # split args into iterable shorthand list
        if typeRank:
            fixArg = typeRank.replace(' ', ',')
            fixArg = fixArg.replace(';', ',')
            buildList = [x.strip() for x in fixArg.split(',') if x.strip()]
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
                buildTot[0],
                pluralInt(buildTot[0])))
        mes.add_field(
            inline=False,
            name="Build Enhancements",
            value=buildTot[1])
        mes.add_field(
            inline=False,
            name="Required Enhancements",
            value=enm.reqEnd([buildTot[0], buildTot[2]]))
        await ctx.send(embed=mes)

    @commands.command(
        aliases=['leaderboard'],
        brief=enm.cmdInf['top']['brief'],
        description=enm.cmdInf['top']['description'])
    # top 10 user leaderboard for number of used enhancements
    async def top(self, ctx, *, enh=""):
        xpKey = ["gdv xp", "gdv"]
        if enh.lower() in xpKey:
            serverXP = load(ctx.message.author.guild.id)
            resubXPList = [
                [ctx.message.guild.get_member(x), serverXP[x]['invXP'][-1]]
                for x in serverXP.keys()]
            pointList = sorted(resubXPList, key=lambda x: x[1], reverse=True)

            blankMessage = discord.Embed(title="GDV XP Leaderboard")

        elif enh:
            if enh not in enm.leader.keys():
                if enh not in enm.leader.values():
                    await ctx.send(
                        "No enhancement could be found for type: {}".format(enh))
                    return
            else:
                enh = enm.leader[enh]
            enhNameList = {enm.power[x]['Name']: 0 for x in enm.power.keys(
            ) if enh == enm.power[x]['Type']}
            peepDict = {}
            for peep in ctx.message.author.guild.members:
                if SUPEROLE not in [x.name for x in peep.roles]:
                    continue
                for role in peep.roles:
                    if role.name in enhNameList.keys():
                        enhNameList[role.name] += 1
                        if peep not in peepDict.keys():
                            peepDict[peep] = [enm.power[x]['Rank']
                                              for x in enm.power.keys()
                                              if enm.power[x]['Name'] ==
                                              role.name][0]
                        else:
                            rank = [enm.power[x]['Rank']
                                    for x in enm.power.keys()
                                    if enm.power[x]['Name'] ==
                                    role.name][0]
                            if rank > peepDict[peep]:
                                peepDict[peep] = rank

            blankMessage = discord.Embed(
                title="{} Enhancement Leaderboard",
                description="{} is being used by {} hosts for a total of {} enhancement points spent.\n".format(
                    enh,
                    len(peepDict.keys()),
                    sum(peepDict.values())))

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

            # sort list of users with enhancements by number of enhancements, descending
            pointList = sorted(pointList, key=lambda x: x[1], reverse=True)
            debug(pointList)
            desc = "There are {} hosts with a total of {} enhancement points spent.".format(
                sum([len(x.members)
                     for x in [get(y.roles, name=SUPEROLE)
                               for y in self.bot.guilds]]),
                sum([x[1] for x in pointList]))

            blankMessage = discord.Embed(
                title="Host Leaderboard",
                description=desc)
        # counter and blank message to track user number and return as a single message
        i = 1
        for group in pointList[:LEADLIMIT]:
            if not enh:
                blankMessage.add_field(
                    inline=False,
                    name="**{}** - {}".format(i, nON(group[0])),
                    value="\t{} enhancements".format(group[1]))
            else:
                if not enh.lower() in xpKey:
                    blankMessage.add_field(
                        inline=False,
                        name="**{}** - {}".format(i, nON(group[0])),
                        value="\tRank {} {}".format(group[1], enh))
                else:
                    blankMessage.add_field(
                        inline=False,
                        name="**{}** - {}".format(i, nON(group[0])),
                        value="\t{:,} GDV XP".format(group[1]))
            i += 1

        # return leaderboard to command caller
        await ctx.send(embed=blankMessage)

    @ commands.command(
        aliases=['c', 'clear'],
        brief=enm.cmdInf['clean']['brief'],
        description=enm.cmdInf['clean']['description'])
    # remove unrestricted enhancements from command caller
    async def clean(self, ctx):
        # rank 0 enhancements are either restricted or the SUPEROLE, which should not be removed with this command
        toCut = [x.name
                 for x in ctx.message.author.roles
                 if x.name in [enm.power[y]['Name']
                               for y in enm.power.keys()
                               if enm.power[y]['Rank'] > 0]]
        debug(toCut)
        await cut(ctx, [ctx.message.author], toCut)
        return

    @ commands.command(hidden=HIDE)
    @ commands.has_any_role(MANAGER)
    async def xpAdd(self, ctx, val: float, *, mem=''):
        val = round(val, 2)
        debug("val is", val)
        memList = await memGrab(self, ctx, mem)
        debug("memList is", memList)
        peep = memList[0]

        infGrab = load(peep.guild.id)
        if not infGrab:
            infGrab = {}
        if peep.id not in infGrab.keys():
            infGrab[peep.id] = {'Name': peep.name, 'invXP': [0, 0, 0]}
        iniVal = infGrab[peep.id]['invXP'][-1]
        sum = iniVal + val
        if sum < 0.0:
            sum = 0.0
        infGrab[peep.id]['invXP'][-1] = sum
        save(ctx.message.author.guild.id, infGrab)
        await ctx.send("Host {}: {} -> {}".format(nON(peep), iniVal, sum))

    @ commands.command(
        hidden=HIDE,
        brief=enm.cmdInf['xpGrab']['brief'],
        description=enm.cmdInf['xpGrab']['description'])
    # @commands.has_any_role(MANAGER)
    @ commands.cooldown(1, 1, commands.BucketType.default)
    async def xpGrab(self, ctx, *, mem=''):
        typeMem = await memGrab(self, ctx, mem)
        typeMem = [typeMem[0]]
        tatForce = 0
        for role in ctx.author.roles:
            if role.name == MANAGER:
                tatForce = 1
        for peep in typeMem:
            mes = ''
            stuff = await count(peep, 1, 1)
            mes += "{}'s MEE6 xp is currently {:,}\n".format(
                nON(peep), stuff[3][0])
            mes += "{}'s TATSU xp is currently {:,}\n".format(
                nON(peep), stuff[3][1])
            mes += "{}'s ReSub xp is currently {:,}\n".format(
                nON(peep), stuff[3][-1])
            mes += "{}'s Total xp is currently {:,}\n".format(
                nON(peep), stuff[2])
            mes += "{}'s resub GDV is currently {}\n".format(
                nON(peep), round(stuff[1], 2))
            mes += "{}'s enhancement points are currently {}\n".format(
                nON(peep), stuff[0])

            nextGDV = int(stuff[1]) + 1
            nextGDV_XP = lvlEqu(nextGDV, 1)
            nextGDVneedXP = nextGDV_XP - stuff[2]

            mes += "{}'s required XP to next GDV is {:,}\n".format(
                nON(peep), nextGDVneedXP)

            nextEnhP = int(5 * (int(stuff[1] / 5) + 1))
            nextEnhP_XP = lvlEqu(nextEnhP, 1)
            nextEnhPneedXP = nextEnhP_XP - stuff[2]

            mes += "{}'s required XP to next enhancement point is {:,}".format(
                nON(peep), nextEnhPneedXP)
            await ctx.send(mes)
        return


# function to move roles to correct rank positions
async def manageRoles(ctx):
    debug("ManageRoles Start")

    # spam message negation
    movedRoles = 'Roles moved:\n'
    toMove = {}

    # iterate through all guild roles
    for role in ctx.message.guild.roles:
        debug("Looking at role: {}".format(role.name))

        # grab shorthand for enhancement
        roleShort = [x for x in enm.power.keys(
        ) if enm.power[x]['Name'] == role.name]
        debug("roleShort = {}".format(roleShort))

        # check to ensure role is one overseen by this bot
        if roleShort == []:
            debug("Role not Supe")
            continue

        # check for intelligence roles as they are the rank position constants and should not be changed by this command
        elif 'Intelligence' == enm.power[roleShort[0]]['Type']:
            debug("Role type intelligence")
            continue

        # fetch enhancement rank
        roleRank = enm.power[roleShort[0]]['Rank']
        debug("Role rank is: {}".format(roleRank))

        # check for restricted roles
        if not roleRank:
            debug("Role rank zero")
            continue

        # check for rank 1 roles that do not have a lowerbound intelligence role for positioning
        elif roleRank == 1:
            roleRankLower = LOWESTROLE

        else:
            roleRankLower = [x.position
                             for x in ctx.message.guild.roles
                             if x.name ==
                             'Rank {} Intelligence (only for Systems)'.format(roleRank - 1)][0]

        # fetch upperbound intelligence rank position
        roleRankUpper = [x.position
                         for x in ctx.message.guild.roles
                         if x.name ==
                         'Rank {} Intelligence (only for Systems)'.format(roleRank)][0]

        roleDiff = roleRankUpper - roleRankLower

        # check for if role is already in postion
        if role.position < roleRankUpper:
            if role.position >= roleRankLower:
                debug("Role within bounds {} - {}".format(roleRankUpper, roleRankLower))
                continue

        # move role to current upperbound intelligence position, forcing intelligence position to increase
        # ASSUMES current role position is lower than intelligence position
        # TODO remove assumption
        debug("Role to be moved from {.position} to {}".format(
            role, roleRankUpper - 1))
        movedRoles += "Moving role {} from position {} to position {}\n".format(
            role.name, role.position, roleRankUpper)
        toMove[role] = roleRankUpper
    await ctx.message.guild.edit_role_positions(positions=toMove)

    # return moved roles as single message to function call
    if movedRoles != 'Roles moved:\n':
        return movedRoles
    return ""

# function to get specified user's enhancement points


async def count(peep, typ=NEWCALC, tatFrc=0):
    debug("Start count")
    if not typ:
        # fetch MEE6 level
        level = await API(GUILD).levels.get_user_level(peep.id)
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
    else:
        if tatFrc:
            MEE6xp = await API(GUILD).levels.get_user_xp(peep.id)
            TATSUmem = await tatsu.wrapper.ApiWrapper(key=TATSU).get_profile(peep.id)
        else:
            TATSUmem = None
            MEE6xp = 0
        try:
            pickle_file = load(peep.guild.id)
            debug(pickle_file)
            ReSubXP = pickle_file[peep.id]['invXP'][-1]
        except:
            ReSubXP = 0
        debug("ReSubXP = ", ReSubXP)

        try:
            TATSUxp = TATSUmem.xp
        except:
            TATSUxp = 0
        debug("TATSUxp = ", TATSUxp)

        try:
            if not MEE6xp:
                if pickle_file[peep.id]['invXP'][0]:
                    MEE6xp = pickle_file[peep.id]['invXP'][0]
        except:
            MEE6xp = 0
        debug("MEE6xp = ", MEE6xp)

        try:
            if not TATSUxp:
                if pickle_file[peep.id]['invXP'][0]:
                    TATSUxp = pickle_file[peep.id]['invXP'][1]
        except:
            TATSUxp = 0
        if MEE6xp or TATSUxp or ReSubXP:
            totXP = ReSubXP + MEE6xp + (TATSUxp / 2)
        else:
            totXP = 0
        if nON(peep) == 'Geminel':
            totXP = totXP * GEMDIFF
        debug("totXP = ", totXP)

        gdv = lvlEqu(totXP)
        debug("gdv = ", gdv)

        enhP = math.floor(gdv / 5) + 1
        debug("enhP = ", enhP)
        if pickle_file:
            pickle_file[peep.id] = {'Name': peep.name,
                                    'enhP': enhP, 'gdv': gdv, 'totXP': totXP, 'invXP': [MEE6xp, TATSUxp, ReSubXP]}
            save(peep.guild.id, pickle_file)
        else:
            save(peep.guild.id, {peep.id: {'Name': peep.name,
                                 'enhP': enhP, 'gdv': gdv, 'totXP': totXP, 'invXP': [MEE6xp, TATSUxp, ReSubXP]}})
        debug("End count")
        return enhP, gdv, totXP, [MEE6xp, TATSUxp, ReSubXP]


async def countOf(peep):
    debug("Start countOf")
    try:
        valDict = load(peep.guild.id)
        debug('valDict = ', valDict)
        shrt = valDict[peep.id]
        debug('shrt = ', shrt)
        debug("End countOf - succ load")
        return shrt['enhP'], shrt['gdv'], shrt['totXP'], shrt['invXP']
    except:
        debug("End countOf - fail load")
        return await count(peep)


# restrict list from members to members with SUPEROLE
def isSuper(self, guildList):
    debug("Start isSuper")
    guilds = self.bot.guilds
    supeGuildList = []
    [supeGuildList.append(z) for z in [x.members for x in [
        get(y.roles, name=SUPEROLE) for y in guilds]]]
    debug("[get(y.roles, name=SUPEROLE) for y in guilds] = {}".format(
        [get(y.roles, name=SUPEROLE) for y in guilds]))
    debug("[x.members for x in [get(y.roles, name=SUPEROLE) for y in guilds]] = {}".format(
        [x.members for x in [get(y.roles, name=SUPEROLE) for y in guilds]]))
    debug("[supeGuildList.append(z) for z in [x.members for x in [get(y.roles, name=SUPEROLE) for y in guilds]]] = {}".format(supeGuildList))
    supeList = [x for x in supeGuildList[0] if x in guildList]
    debug(supeList)

    # return reduced user list
    debug("End isSuper")
    return supeList


# from shorthand enhancement list return cost of build, role names and prerequisite roles
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
        tempName = enm.power[item]['Name']

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


# function to grab number of enhancement points spent by each user in given list
def spent(memList):
    debug("Start spent")
    retList = []
    debug("memList is: {}".format(memList))

    # iterate thorugh given list of users
    for peep in memList:
        supeRoles = []
        debug("current user is: {}".format(peep))
        debug("current user role list: {}".format(peep.roles))

        # messy implementation to grab shorthand for all unrestricted bot managed roles in user role list
        for roles in peep.roles:
            if roles.name in [enm.power[x]['Name'] for x in enm.power.keys() if enm.power[x]['Rank'] > 0]:
                supeRoles.append([x for x in enm.power.keys(
                ) if enm.power[x]['Name'] == roles.name][0])
        debug("Supe roles: {}".format(supeRoles))

        # fetch point cost (including prereqs) of enhancements
        if supeRoles:
            pointCount = funcBuild(supeRoles)[0]
        else:
            pointCount = funcBuild([])[0]

        # add (user, total build cost, enhancmeent role names) to list to return
        retList.append([peep, pointCount, supeRoles])

    debug("retlist is: {}".format(retList))
    debug("End spent")
    return retList


# function to fetch all users requested by command caller
async def memGrab(self, ctx, memList=""):
    debug("Start memGrab")
    debug("memList: {}\nand mentions: {}".format(
        memList, ctx.message.mentions))

    # first check for users mentioned in message
    if ctx.message.mentions:
        grabList = ctx.message.mentions
        debug("Message mentions: {}".format(grabList))

    # else check for users named by command caller
    elif memList:
        grabList = memList.split(", ")
        debug("split grablist: {}".format(grabList))
        for i in range(0, len(grabList)):
            debug("position {} grablist: {}".format(
                i, grabList[i]))
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
    supeTrim = [enm.power[enm.toType(x[1]) + str(x[0])]['Name']
                for x in enm.trim(supeBuild[1])]
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
            debug("\t\t role to cut = {}\n\t\t from peep {}".format(role, peep))
            supeRoleId = get(peep.roles, name=role)
            debug("\t\t role to cut id = {}".format(supeRoleId))
            if supeRoleId in peep.roles:
                await peep.remove_roles(supeRoleId)
                sendMes += "{} no longer has {} \n{}\n".format(
                    nON(peep), supeRoleId, random.choice(enm.remList))

        # notify current user has been finished with to discord
        sendMes += "{} has been cut down to size!".format(nON(peep))
        await ctx.send(sendMes)
    debug("End cut")
    return


# function to fetch all guild roles that are managed by bot
async def orderRole(self, ctx):
    debug("Start orderRole")
    debug(enm.power.values())

    supeList = [x for x in ctx.message.author.guild.roles if str(
        x) in [y['Name'] for y in enm.power.values()]]

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
    ret = 'A'
    if inp.lower() in "aeiou":
        ret = 'An'
    debug("ret = ", ret)
    debug("End aOrAn")
    return ret


def pluralInt(val: int):
    rtnStr = ""
    if not val == 1:
        rtnStr = "s"
    return rtnStr


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
def setup(bot):
    bot.add_cog(Options(bot))
