# options.py

import os
import random

import discord
import enhancements
from BossSystemExecutable import nON, servList
from discord.ext import commands
from discord.ext.commands import MemberConverter
from discord.utils import get
from dotenv import load_dotenv
from mee6_py_api import API

DEBUG = 0
TEST = 0


def debug(*args):
    if DEBUG:
        print(*args)


# function to get the guild id from user if not found in the .env
# keeping the guild token hard coded atm as messy security
def askToken():
    tempToken = input("Enter your discord bot GUILD id: ")
    with open(".env", "a+") as f:
        f.write("DISCORD_GUILD={}\n".format(tempToken))
    return tempToken


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
if not GUILD:
    GUILD = askToken()


SUPEROLE = "Supe"
PERMROLES = ['Supe']  # guild role(s) for using these bot commands
MANAGER = 'System'  # manager role name for guild
LOWESTROLE = 2  # bot sorts roles by rank from position of int10 to LOWESTROLE
HIDE = False

# TODO: implement this and similiar instead of multiple enhancement.dict.keys() calls
# enhancement (type, rank) pairs for list command
ENHLIST = [(x, y) for (x, y) in enhancements.powerTypes.items()]


class Options(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        return

    # Check if user has guild role
    async def cog_check(self, ctx):

        debug("Role check start")

        async def predicate(ctx):
            for role in PERMROLES:
                debug("Role check {} in {}".format(role, PERMROLES))
                chkRole = get(ctx.guild.roles, name=role)
                debug("chkRole = {}".format(chkRole))
                if chkRole in ctx.author.roles:
                    return chkRole
            raise commands.CheckFailure(
                "You do not have permission as you are missing a role in this list: {}\nThe super command can be used to gain the Supe role".format(PERMROLES))  # messy implementation for Supe
        return commands.check(await predicate(ctx))

    @commands.command(brief=enhancements.commandInfo['trim']['brief'], description=enhancements.commandInfo['trim']['description'])
    # command to trim command caller of extra roles. OBSOLETE due to cut call after role add in add command
    async def trim(self, ctx, *, member=''):
        debug("funcTrim START")

        memberList = await memGrab(self, ctx, '')  # member)
        debug("\tmemberlist = {}".format(memberList))

        await cut(ctx, memberList)
        debug("funcTrim END")
        return

    @commands.command(hidden=HIDE, brief=enhancements.commandInfo['trimAll']['brief'], description=enhancements.commandInfo['trimAll']['description'])
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

    @commands.command(hidden=HIDE, brief=enhancements.commandInfo['roleInf']['brief'], description=enhancements.commandInfo['roleInf']['description'])
    @commands.has_any_role(MANAGER)
    # manager command to check if guild has role and messages some information of the role
    async def roleInf(self, ctx, *, roleStr: str):
        supeGuildRoles = await orderRole(self, ctx)
        roleStrId = [x for x in supeGuildRoles if roleStr == x.name]
        debug("Role string ID is: {}".format(roleStrId[0].id))
        if roleStrId:
            roleStrId = roleStrId[0]
            await ctx.send("{.name} has: \nposition - {.position}\ncolour - {.colour}".format(roleStrId, roleStrId, roleStrId))
        return

    @commands.command(aliases=['a'], brief=enhancements.commandInfo['add']['brief'], description=enhancements.commandInfo['add']['description'])
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
            await ctx.send("Cannot add enhancements without an enhancement to add")
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
        pointTot = await count(user)
        debug("{} with point total {} has {} {} and wants {} {}".format(
            user, pointTot, userHas[0], userHasBuild, userWantsCost, userWantsBuild))

        # check to ensure user has enough enhancement points to get requested additions
        if pointTot < userWants[0]:
            await ctx.send("{} needs {} available enhancements for {} but only has {}".format(nON(user), userWantsCost, [enhancements.power[x]['Name'] for x in buildList], pointTot))
            return

        # the guild role names grabbed from shorthand to add to user
        addList = [enhancements.power[x[1][:3].lower() + str(x[0])]['Name']
                   for x in userWantsBuild]
        debug("Add list = {}".format(addList))

        # restricted roles the user does not have that the build requires
        cantAdd = [x for x in enhancements.restrictedList if x in addList]
        cantAdd = [x for x in cantAdd if x not in [y.name for y in user.roles]]
        debug("Cant add = {}".format(cantAdd))

        # check to ensure user has restricted roles already if required for build
        if cantAdd:
            await ctx.send("Cannot add enhancements as {} does not have {}".format(nON(user), cantAdd))
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
                colour = enhancements.rankColour[int(roleRank)]
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

    @commands.command(hidden=HIDE, brief=enhancements.commandInfo['moveRoles']['brief'], description=enhancements.commandInfo['moveRoles']['description'])
    @commands.has_any_role(MANAGER)
    # manager command to correct role position for roles that have been created by bot
    async def moveRoles(self, ctx):
        await ctx.send(await manageRoles(ctx))
        return

    @commands.command(aliases=['p'], brief=enhancements.commandInfo['points']['brief'], description=enhancements.commandInfo['points']['description'])
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
            pointTot = await count(group[0])
            await ctx.send("{} has {} enhancements active out of {} enhancements available.".format(nON(group[0]), group[1], pointTot))
        return

    @commands.command(aliases=['l'], brief=enhancements.commandInfo['list']['brief'], description=enhancements.commandInfo['list']['description'])
    # help level command to list the available enhancements and the shorthand to use them in commands
    async def list(self, ctx):
        await ctx.send("Enhancement list is:")

        # dynamic message to reduce bot messages sent
        mes = ""

        # add each enhancement and the total ranks available to the message to return
        for group in ENHLIST:

            # check for mental clarity and mental celerity exception
            if group[0][0:3].lower() == "men":
                shorthand = group[0][7:10]
            else:
                shorthand = group[0][0:3]

            addMes = "{} ({}) of {} rank(s)\n".format(
                group[0], shorthand.lower(), group[1])
            debug(addMes)

            mes += addMes

        # return enhancement list to command caller
        debug("funcList - " + str(mes))
        await ctx.send("{}Starred enhancements require advanced roles".format(mes))
        return

    @commands.command(aliases=['b'], brief=enhancements.commandInfo['build']['brief'], description=enhancements.commandInfo['build']['description'])
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
        await ctx.send("This build requires {} enhancement(s) for:\n\n {} \n\n{}".format(buildTot[0], buildTot[1], enhancements.reqEnd([buildTot[0], buildTot[2]])))
        return

    @commands.command(aliases=['leaderboard', 't'], brief=enhancements.commandInfo['topten']['brief'], description=enhancements.commandInfo['topten']['description'])
    # top 10 user leaderboard for number of used enhancements
    async def topten(self, ctx):

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

        # counter and blank message to track user number and return as a single message
        i = 1
        blankMessage = ""
        for group in pointList[:10]:
            blankMessage += "**{}** - {} \n\t {} enhancements\n".format(
                i, nON(group[0]), group[1])

            # OBSOLETE message spam
            # await ctx.send("{} is number {} with {} enhancements".format(group[0], i, group[1]))
            i += 1

        # return leaderboard to command caller
        await ctx.send(blankMessage)

    @commands.command(aliases=['c', 'clear'], brief=enhancements.commandInfo['clean']['brief'], description=enhancements.commandInfo['clean']['description'])
    # remove unrestricted enhancements from command caller
    async def clean(self, ctx):
        # rank 0 enhancements are either restricted or the SUPEROLE, which should not be removed with this command
        toCut = [x.name for x in ctx.message.author.roles if x.name in [enhancements.power[y]['Name']
                                                                        for y in enhancements.power.keys() if enhancements.power[y]['Rank'] > 0]]
        debug(toCut)
        await cut(ctx, [ctx.message.author], toCut)
        return

    @commands.command(hidden=HIDE, brief=enhancements.commandInfo['xpgrab']['brief'], description=enhancements.commandInfo['xpgrab']['description'])
    @commands.has_any_role(MANAGER)
    async def xpgrab(self, ctx):
        xp = await API(GUILD).levels.get_user_xp(ctx.message.author.id)
        await ctx.send("{} xp is currently {}".format(nON(ctx.message.author), xp))
        return


# function to move roles to correct rank positions
async def manageRoles(ctx):
    debug("ManageRoles Start")

    # spam message negation
    movedRoles = 'Roles moved:\n'

    # iterate through all guild roles
    for role in ctx.message.guild.roles:
        debug("Looking at role: {}".format(role.name))

        # grab shorthand for enhancement
        roleShort = [x for x in enhancements.power.keys(
        ) if enhancements.power[x]['Name'] == role.name]
        debug("roleShort = {}".format(roleShort))

        # check to ensure role is one overseen by this bot
        if roleShort == []:
            debug("Role not Supe")
            continue

        # check for intelligence roles as they are the rank position constants and should not be changed by this command
        elif 'Intelligence' == enhancements.power[roleShort[0]]['Type']:
            debug("Role type intelligence")
            continue

        # fetch enhancement rank
        roleRank = enhancements.power[roleShort[0]]['Rank']
        debug("Role rank is: {}".format(roleRank))

        # check for restricted roles
        if not roleRank:
            debug("Role rank zero")
            continue

        # check for rank 1 roles that do not have a lowerbound intelligence role for positioning
        elif roleRank == 1:
            roleRankLower = LOWESTROLE

        else:
            roleRankLower = [x.position for x in ctx.message.guild.roles if x.name ==
                             'Rank {} Intelligence (only for Systems)'.format(roleRank - 1)][0]

        # fetch upperbound intelligence rank position
        roleRankUpper = [x.position for x in ctx.message.guild.roles if x.name ==
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
        debug("Role moved from {.position} to {}".format(
            role, roleRankUpper - 1))
        movedRoles += "Moving role {} from position {} to position {}\n".format(
            role.name, role.position, roleRankUpper - 1)
        await role.edit(position=roleRankUpper - 1, color=enhancements.rankColour[roleRank])

    # return moved roles as single message to function call
    return movedRoles


# function to get specified user's enhancement points
async def count(peep):

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
        if role.name in enhancements.patList:
            pointTot += 1
        debug(pointTot)
    # return total user points to function call
    return pointTot


# restrict list from members to members with SUPEROLE
def isSuper(self, guildList):
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
    return supeList


# from shorthand enhancement list return cost of build, role names and prerequisite roles
def funcBuild(buildList):
    reqList = []
    nameList = []
    debug("Build command buildList = {}".format(buildList))

    # iterate through shorthand enhancements
    for item in buildList:
        debug("Build command item = {}".format(item))

        # fetch enhancement prereqs and cost
        temCost = enhancements.cost(item)
        debug("Build command prereq cost = {}".format(temCost))

        # add this enhancement's prereqs to list
        reqList.append(temCost[2])

        # fetch full name for enhancement from shorthand
        tempName = enhancements.power[item]['Name']

        # add enhancement full name to lists
        reqList.append(tempName)
        nameList.append(tempName)
    debug("Build command reqList is: {}".format(reqList))

    # restrict nested prereq list to a set of prereqs
    temp = enhancements.eleCountUniStr(reqList)
    debug("temp = {}".format(temp))

    # fetch highest ranked prereqs of each type in list
    reqList = enhancements.trim([x for x in temp[1]])
    debug("reqList = {}".format(reqList))

    # sum cost of build from prereqs
    costTot = 0
    for group in reqList:
        debug(group)
        costTot += group[0]
    debug(costTot, nameList, reqList)

    # return cost of build, role names and prerequisite roles
    return costTot, nameList, reqList


# function to grab number of enhancement points spent by each user in given list
def spent(memList):
    retList = []
    debug("memList is: {}".format(memList))

    # iterate thorugh given list of users
    for peep in memList:
        supeRoles = []
        debug("current user is: {}".format(peep))
        debug("current user role list: {}".format(peep.roles))

        # messy implementation to grab shorthand for all unrestricted bot managed roles in user role list
        for roles in peep.roles:
            if roles.name in [enhancements.power[x]['Name'] for x in enhancements.power.keys() if enhancements.power[x]['Rank'] > 0]:
                supeRoles.append([x for x in enhancements.power.keys(
                ) if enhancements.power[x]['Name'] == roles.name][0])
        debug("Supe roles: {}".format(supeRoles))

        # fetch point cost (including prereqs) of enhancements
        if supeRoles:
            pointCount = funcBuild(supeRoles)[0]
        else:
            pointCount = funcBuild([])[0]

        # add (user, total build cost, enhancmeent role names) to list to return
        retList.append([peep, pointCount, supeRoles])

    debug("retlist is: {}".format(retList))
    return retList


# function to fetch all users requested by command caller
async def memGrab(self, ctx, memList=""):
    debug("\tfuncGrabList START")
    debug("\t\tmemList: {}\n\t\t and mentions: {}".format(
        memList, ctx.message.mentions))

    # first check for users mentioned in message
    if ctx.message.mentions:
        grabList = ctx.message.mentions
        debug("\t\t\tMessage mentions: {}".format(grabList))

    # else check for users named by command caller
    elif memList:
        grabList = memList.split(", ")
        debug("\t\t\tsplit grablist: {}".format(grabList))
        for i in range(0, len(grabList)):
            debug("\t\t\t\tposition {} grablist: {}".format(
                i, grabList[i]))
            grabList[i] = await MemberConverter().convert(ctx, grabList[i])

    # else use the command caller themself
    else:
        grabList = [ctx.message.author]
        debug("\t\t\tAuthor is: {}".format(grabList))
    debug("\t\t\tfixed grablist: {}".format(grabList))
    debug("\tfuncGrabList END")

    # return: mentioned users || named users || message author
    return grabList


# get roles of a lower rank on member to remove later
def toCut(member):
    debug("\tfuncCut START")

    # fetch unrestricted managed roles member has
    supeRoles = spent([member])
    debug("\t\tsupeRoles = {}".format(supeRoles[0][2]))

    # fetch build of member
    supeBuild = funcBuild(supeRoles[0][2])
    debug("\t\tsupeBuild = {}".format(supeBuild[1]))

    # fetch trimmed build of user
    supeTrim = [enhancements.power[x[1][:3].lower() + str(x[0])]['Name']
                for x in enhancements.trim(supeBuild[1])]
    debug("\t\tsupeTrim = {}".format(supeTrim))

    # fetch extra roles user has that are to be removed
    toCut = [x for x in supeBuild[1] if x not in supeTrim]
    debug("\tto CUT = {}".format(toCut))
    debug("\tfuncCut END")

    # return the roles to be removed
    return toCut


# function to remove extra or specified roles from list of users
async def cut(ctx, memberList, cutList=[]):
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
                    nON(peep), supeRoleId, random.choice(enhancements.remList))

        # notify current user has been finished with to discord
        sendMes += "{} has been cut down to size!".format(nON(peep))
        await ctx.send(sendMes)
    return


# function to fetch all guild roles that are managed by bot
async def orderRole(self, ctx):
    debug(enhancements.power.values())

    supeList = [x for x in ctx.message.author.guild.roles if str(
        x) in [y['Name'] for y in enhancements.power.values()]]

    debug(supeList)
    return supeList


# function to setup cog
def setup(bot):
    bot.add_cog(Options(bot))
