#options.py

import discord
import os
import enhancements

from discord.ext import commands
from discord.ext.commands import MemberConverter
from discord.utils import get
from dotenv import load_dotenv
from mee6_py_api import API
from BossSystemExecutable import servList, nickOrName

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CLIENT = os.getenv('DISCORD_CLIENT')
GUILD = os.getenv('DISCORD_GUILD')

mee6API = API(GUILD)
converter = discord.ext.commands.MemberConverter

permRoles = ['Supe']
enhList = [(x, y) for (x, y) in enhancements.powerTypes.items()]

DEBUG = 0
TEST = 0

if DEBUG:
    print("{} DEBUG TRUE".format(os.path.basename(__file__)))
#if DEBUG: print()
if TEST:
    print("{} TEST TRUE".format(os.path.basename(__file__)))
#if TEST: print()


class options(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        # Check if user has admin role
        if DEBUG:
            print("Role check start")

        async def predicate(ctx):
            for role in permRoles:
                if DEBUG:
                    print("Role check {} in {}".format(role, permRoles))
                chkRole = get(ctx.guild.roles, name=role)
                if DEBUG:
                    print("chkRole = {}".format(chkRole))
                if chkRole in ctx.author.roles:
                    return chkRole
            raise commands.CheckFailure(
                "You do not have permission as you are missing a role in this list: {}\nThe super command can be used to gain the Supe role".format(permRoles))
        return commands.check(await predicate(ctx))

    @commands.command(brief="-Removes duplicate enhancements of lower rank.\n")
    async def trim(self, ctx, *, member=''):
        if DEBUG:
            print("funcTrim START")
        memberList = await memGrab(self, ctx, '')  # member)
        if DEBUG:
            print("\tmemberlist = {}".format(memberList))
        await cut(ctx, memberList)
        if DEBUG:
            print("funcTrim END")
        return

    @commands.command(hidden=True)
    @commands.is_owner()
    async def trimAll(self, ctx):
        if DEBUG:
            print("funcTrimAll START")
        memberList = isSuper(servList(self.bot))
        if DEBUG:
            print("\tmemberlist to cut = {}".format(
                [x.name for x in memberList]))
        await cut(ctx, memberList)
        if DEBUG:
            print("funcTrimAll END")
        return

    @commands.command(hidden=True)
    @commands.is_owner()
    async def roles(self, ctx, *, roleStr: str):
        supeGuildRoles = await orderRole(self, ctx)
        roleStrId = [x for x in supeGuildRoles if roleStr == x.name]
        if DEBUG:
            print("Role string ID is: {}".format(roleStrId[0].id))
        if roleStrId:
            roleStrId = roleStrId[0]
            roleRank = enhancements.power[x]['Rank']
            await ctx.send("{.name} has: \nposition - {.position}\ncolour - {.colour}".format(roleStrId, roleStrId, roleStrId))
        return


    @commands.command(brief="-Allows host to add enhancement and its prerequisites to themself.\n")
    async def add(self, ctx, typeRank=''):
        user = ctx.message.author
        userSpent = spent([user])
        userEnhancements = userSpent[0][2]
        userHas = funcBuild(userEnhancements)
        userHasBuild = userHas[2]
        if not typeRank:
            await ctx.send("Cannot add enhancements without an enhancement to add")
            return
        userEnhancements.append(typeRank)
        userWants = funcBuild(userEnhancements)
        userWantsCost = userWants[0]
        userWantsBuild = userWants[2]
        pointTot = await count(user)
        if DEBUG: print("{} with point total {} has {} {} and wants {} {}".format(user, pointTot, userHas[0], userHasBuild, userWantsCost, userWantsBuild))
        if pointTot < userWants[0]:
            await ctx.send("{} needs {} available enhancements for {} but only has {}".format(nickOrName(user), userWantsCost, enhancements.power[typeRank]['Name'], pointTot))
            return
        addList = [enhancements.power[x[1][:3].lower()+str(x[0])]['Name'] for x in userWantsBuild]
        if DEBUG: print("Add list = {}".format(addList))
        cantAdd = [x for x in enhancements.restrictedList if x in addList]
        cantAdd = [x for x in cantAdd if x not in [y.name for y in user.roles]]
        if DEBUG: print("Cant add = {}".format(cantAdd))
        if cantAdd:
            await ctx.send("Cannot add enhancements as {} does not have {}".format(nickOrName(user), cantAdd))
            return
        guildRoles = await user.guild.fetch_roles()
        for role in addList:
            if DEBUG: print("Trying to add role: {}".format(role))
            roleId = get(guildRoles, name=role)
            if roleId in user.roles:
                await ctx.send("{} already has the role {}".format(nickOrName(user), roleId))
                continue
            roleRank = role.split()[1]
            if DEBUG: print(roleId, roleRank)
            if not roleId:
                colour = enhancements.rankColour[int(roleRank)]
                if DEBUG: print("colour for rank {} is: {}".format(roleRank, colour))
                roleId = await user.guild.create_role(name=role, color=colour)
            await user.add_roles(roleId)
            await ctx.send("{} now has {}!".format(nickOrName(user), roleId))
        if DEBUG: print("TO CUT")
        await cut(ctx, [user])



    @commands.command(brief="-Shows target host's available and spent enhancement points.\n")
    async def points(self, ctx, *, member=''):
        users = await memGrab(self, ctx, member)
        supeUsers = isSuper(users)
        if not supeUsers:
            [await ctx.send("{} is not a Supe".format(nickOrName(x))) for x in users]
            return
        pointList = spent(supeUsers)

        for group in pointList:
            if DEBUG:
                print("group in level is: {}".format(group))
            pointTot = await count(group[0])
            await ctx.send("{} has {} enhancements active out of {} enhancements available.".format(nickOrName(group[0]), group[1], pointTot))
        return

    @commands.command(brief="-Lists all available enhancements.\n")
    async def list(self, ctx):
        await ctx.send("Enhancement list is:")
        mes = ""
        for group in enhList:
            if group[0][0:3].lower() == "men":
                shorthand = group[0][7:10]
            else:
                shorthand = group[0][0:3]
            addMes = "{} ({}) of {} rank(s)\n".format(
                group[0], shorthand.lower(), group[1])
            if DEBUG:
                print(addMes)
            mes += addMes
            #if DEBUG: print("funcList - " + "message is at {}".format(mes))
        if DEBUG:
            print("funcList - " + str(mes))
        await ctx.send("{}Starred enhancements require assignment".format(mes))
        return

    @commands.command(brief="-Total points required and their prerequisite enhancements.\n", description="Use the shorthand enhancement codes separated by commas to find a builds total enhancement cost and prerequisites. \nExample: For a build with Rank 4 Regeneration and Rank 4 Mental Celerity the shorthand would be 'reg4, cel4'")
    async def build(self, ctx, *, typeRank=''):
        if DEBUG:
            print("Build command start")
        if DEBUG:
            print(typeRank)
        if typeRank:
            buildList = typeRank.split(', ')
        else:
            buildList = spent([ctx.message.author])[0][2]
        if DEBUG:
            print("buildList = {}".format(buildList))
        buildTot = funcBuild(buildList)
        await ctx.send("This build requires {} enhancement(s) for:\n\n {} \n\n{}".format(buildTot[0], buildTot[1], enhancements.reqEnd([buildTot[0], buildTot[2]])))
        return

    @commands.command(brief="-Shows the top ten Supes by their enhancements.\n")
    async def topten(self, ctx):
        guildList = servList(self.bot)
        if DEBUG:
            print("Guild list is: {}".format(guildList))
        supeList = isSuper(guildList)
        if DEBUG:
            print("Supe list is: {}".format(supeList))
        pointList = spent(supeList)
        if DEBUG:
            print(pointList)
        pointList = sorted(pointList, key=lambda x: x[1], reverse=True)
        if DEBUG:
            print(pointList)
        i = 1
        blankMessage = ""
        for group in pointList[:10]:
            blankMessage += "**{}** - {} \n\t {} enhancements\n".format(
                i, nickOrName(group[0]), group[1])
            # await ctx.send("{} is number {} with {} enhancements".format(group[0], i, group[1]))
            i += 1
        await ctx.send(blankMessage)

    @commands.command(brief="-Removes all enhancements from host.\n")
    async def clean(self, ctx):
        toCut = [x.name for x in ctx.message.author.roles if x.name in [enhancements.power[y]['Name'] for y in enhancements.power.keys() if enhancements.power[y]['Rank'] > 0]]
        if DEBUG:
            print(toCut)
        await cut(ctx, [ctx.message.author], toCut)
        return


async def count(peep):
    level = await mee6API.levels.get_user_level(peep.id)
    if level:
        pointTot = int(level / 5)
    else:
        level = 0
    if DEBUG:
        print(peep.roles)
    for role in peep.roles:
        if DEBUG:
            print(role)
        if str(role) in enhancements.patList:
            pointTot += 1
    return pointTot


def isSuper(guildList):
    supeList = []
    for pers in guildList:
        if DEBUG:
            print("Pers is {}".format(pers))
        for role in pers.roles:
            if DEBUG:
                print("role is {}".format(role))
            if str(role) == permRoles[0]:
                supeList.append(pers)
                if DEBUG:
                    print("{} added to {} list".format(pers, role))
    return supeList


def funcBuild(buildList):
    reqList = []
    nameList = []
    if DEBUG:
        print("Build command buildList = {}".format(buildList))
    for item in buildList:
        if DEBUG:
            print("Build command item = {}".format(item))
        temCost = enhancements.cost(item)
        if DEBUG:
            print("Build command prereq cost = {}".format(temCost))
        reqList.append(temCost[2])
        tempName = enhancements.power[item]['Name']
        reqList.append(tempName)
        nameList.append(tempName)
    if DEBUG:
        print("Build command reqList is: {}".format(reqList))
    temp = enhancements.eleCountUniStr(reqList)
    if DEBUG: print("temp = {}".format(temp))
    reqList = enhancements.trim([x for x in temp[1]])
    if DEBUG: print("reqList = {}".format(reqList))
    costTot = 0
    for group in reqList:
        if DEBUG: print(group)
        costTot += group[0]
    if DEBUG: print(costTot, nameList, reqList)
    return costTot, nameList, reqList


def spent(memList):
    retList = []
    if DEBUG:
        print("memList is: {}".format(memList))
    for peep in memList:
        supeRoles = []
        if DEBUG:
            print("current user is: {}".format(peep))
        if DEBUG:
            print("current user role list: {}".format(peep.roles))

        for roles in peep.roles:
            if str(roles) in [enhancements.power[x]['Name'] for x in enhancements.power.keys() if enhancements.power[x]['Rank'] > 0]:
                supeRoles.append([x for x in enhancements.power.keys(
                ) if enhancements.power[x]['Name'] == str(roles)][0])
        if DEBUG:
            print("Supe roles: {}".format(supeRoles))
        pointCount = funcBuild(supeRoles)[0]
        """
        for posEnh in peep.roles:
            posEnh = str(posEnh)
            if DEBUG: print("current role is: {}".format(posEnh))
            if DEBUG: print([enhancements.power[x]['Name'] for x in enhancements.power.keys()])
            if DEBUG: print(posEnh in [enhancements.power[x]['Name'] for x in enhancements.power.keys()])
            if posEnh in [enhancements.power[x]['Name'] for x in enhancements.power.keys()]:
                pointCount += 1
        """
        retList.append([peep, pointCount, supeRoles])
    if DEBUG:
        print("retlist is: {}".format(retList))
    return retList


async def memGrab(self, ctx, memList=""):
    if DEBUG:
        print("\tfuncGrabList START")
    if DEBUG:
        print("\t\tmemList: {}\n\t\t and mentions: {}".format(
            memList, ctx.message.mentions))
    if ctx.message.mentions:
        grabList = ctx.message.mentions
        if DEBUG:
            print("\t\t\tMessage mentions: {}".format(grabList))
    elif memList:
        grabList = memList.split(", ")
        if DEBUG:
            print("\t\t\tsplit grablist: {}".format(grabList))
        for i in range(0, len(grabList)):
            if DEBUG:
                print("\t\t\t\tposition {} grablist: {}".format(
                    i, grabList[i]))
            grabList[i] = await MemberConverter().convert(ctx, grabList[i])
    else:
        grabList = [ctx.message.author]
        if DEBUG:
            print("\t\t\tAuthor is: {}".format(grabList))
    if DEBUG:
        print("\t\t\tfixed grablist: {}".format(grabList))
    if DEBUG:
        print("\tfuncGrabList END")
    return grabList


def toCut(member):
    if DEBUG:
        print("\tfuncCut START")
    supeRoles = spent([member])
    if DEBUG:
        print("\t\tsupeRoles = {}".format(supeRoles[0][2]))
    supeBuild = funcBuild(supeRoles[0][2])
    if DEBUG:
        print("\t\tsupeBuild = {}".format(supeBuild[1]))
    supeTrim = [enhancements.power[x[1][:3].lower()+str(x[0])]['Name'] for x in enhancements.trim(supeBuild[1])]
    if DEBUG:
        print("\t\tsupeTrim = {}".format(supeTrim))
    toCut = [x for x in supeBuild[1] if x not in supeTrim]
    if DEBUG:
        print("\tto CUT = {}".format(toCut))
    if DEBUG:
        print("\tfuncCut END")
    return toCut


async def cut(ctx, memberList, cutList=[]):
    for peep in memberList:
        if not cutList:
            cutting = toCut(peep)
        else:
            cutting = cutList
        for role in cutting:
            if DEBUG:
                print("\t\t role to cut = {}\n\t\t from peep {}".format(role, peep))
            supeRoleId = get(peep.roles, name=role)
            if DEBUG:
                print("\t\t role to cut id = {}".format(supeRoleId))
            if supeRoleId in peep.roles:
                await peep.remove_roles(supeRoleId)
                await ctx.send("{} no longer has {} \n( ╥﹏╥) ノシ".format(nickOrName(peep), supeRoleId))
        await ctx.send("{} has been cut down to size!".format(nickOrName(peep)))


async def orderRole(self, ctx):
    if DEBUG:
        print(enhancements.power.values())
    supeList = [x for x in ctx.message.author.guild.roles if str(
        x) in [y['Name'] for y in enhancements.power.values()]]
    if DEBUG:
        print(supeList)
    return supeList



def setup(bot):
    bot.add_cog(options(bot))
