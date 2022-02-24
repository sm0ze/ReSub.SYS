# sharedFuncs.py

import asyncio
import copy
import datetime
import json
import math
import os
import random
import re
import time
import typing

import bin.log as log
import bin.shared.dyVars as shared_dyVars
import discord
import tatsu
from bin.shared.consts import (
    AID_WEIGHT,
    GEM_DIFF,
    HOST_NAME,
    ROLE_ID_CALL,
    ROLE_ID_PATROL,
    SAVE_FILE,
    SORT_ORDER,
    START_CHANNEL,
    SUPE_ROLE,
    TATSU,
)
from bin.shared.dicts import (
    activeDic,
    baseDict,
    cmdInf,
    genDictAll,
    leader,
    masterEhnDict,
    powerTypes,
    rankColour,
    remList,
    reqResList,
    restrictedList,
    taskVar,
)
from discord.abc import Messageable
from discord.ext import commands
from discord.ext.commands.converter import MemberConverter, RoleConverter
from discord.utils import get
from mee6_py_api import API
from sqlitedict import SqliteDict

logP = log.get_logger(__name__)

STRCHNL = None

SLEEP = False


# count number of unique strings in nested list
# and return count and unnested set
# TODO rewrite messy implementation ?and? every call of this function
def eleCountUniStr(varList, reqursion: bool = False):
    uniList = []
    # if not reqursion:
    # logP.debug(f"List of {len(varList)} elements to make unique")
    for ele in varList:
        if isinstance(ele, list):
            if ele:
                rec = eleCountUniStr(ele, True)
                for uni in rec[1]:
                    if uni not in uniList:
                        uniList.append(uni)
        else:
            if ele and ele not in uniList:
                uniList.append(ele)
    # if not reqursion:
    # logP.debug(f"List of {len(uniList)} elements to return")
    return len(uniList), uniList


# calculate number of prerequisites +1 to get cost of enhancement
def cost(inName: str, inDict: dict = masterEhnDict):
    required = []

    # logP.debug(f"{inName} has requisites: {inDict[inName]['Prereq']}")

    # for each prereq given enhancement has
    for req in inDict[inName]["Prereq"]:
        # check for restricted enhancement, as those are not counted
        if req not in required:
            # logP.debug(
            #    str(req) + " requisite has name: " + str(inDict[req]["Name"])
            # )

            # save prereq full name for later
            required.append(inDict[req]["Name"])

            # check for prereq' prereqs
            subReq = cost(req, inDict)[2]

            # save prereq' prereqs
            if subReq:
                required.append(subReq)

    # trim list of prereqs to remove duplicates
    ans = eleCountUniStr(required)
    # logP.debug(f"ans before restricted list length: {len(ans)}")

    # total cost of given enhancement
    ansTot = ans[0]
    # enhancement cost = ansTot+1
    # unique prereq string = ans[1]
    return ansTot + 1, ans[1], required


# function to remove lower ranked enhancements from the list
def trim(pList, inDict=masterEhnDict):
    logP.debug("Start of trim function")
    tierDict = {}
    trimList = []
    if pList:
        logP.debug(f"list of length {len(pList)} to trim")

    # iterate thorugh list of given enhancements
    for pow in pList:
        # fetch enhancement attrs
        powRank = [
            inDict[x]["Rank"]
            for x in inDict.keys()
            if inDict[x]["Name"] == pow
        ][0]
        powType = [
            inDict[x]["Type"]
            for x in inDict.keys()
            if inDict[x]["Name"] == pow
        ][0]
        # logP.debug(f"Enhancement: {pow}, Type: {powType}, Rank: {powRank}")

        # if enhancement not already counted, add it to dictionary
        if powType not in tierDict.keys():
            tierDict[powType] = powRank
            # logP.debug(f"{powType} of rank {powRank} added to dict")

        # else if enhancment greater in rank than already counted enhancement
        # edit dictionary
        elif powRank > tierDict[powType]:
            # logP.debug(
            #   f"{powType} of rank {tierDict[powType]} increased to {powRank}"
            # )
            tierDict[powType] = powRank

    # add key value pairs in dictionary to a list of lists
    for key, val in tierDict.items():
        trimList.append([val, key])

    # return sorted trimmed list of highest ranked enhancements, descending
    trimList = sorted(trimList, key=lambda x: (-int(x[0]), str(x[1])))
    # logP.debug(f"dict tierDict: {tierDict}")
    logP.debug(f"trimList: {trimList}")
    return trimList


# function to turn given list of [rank, enhancment]
# into str for discord message
def reqEnd(endList):
    logP.debug(f"{endList}")

    # check for no prereqs
    if len(endList[1]) == 0:
        reqStr = "Build has no prerequisites."

    # otherwise add prereqs to message
    else:
        logP.debug(f"{endList[1]}")
        reqStr = ""
        for req in endList[1]:
            reqName = masterEhnDict[toType(req[1]) + str(req[0])]["Name"]
            reqStr += f"{reqName}\n"

    # return message
    return reqStr


def toType(role: str):
    thing = [x for x in leader.keys() if role == leader[x]]
    logP.debug(f"Convert: {role}, to: {thing}")
    return thing[0] if thing else False


# from shorthand enhancement list return cost of build,
# role names and prerequisite roles
def funcBuild(
    buildList: list[str],
) -> tuple[int, list[str], list]:
    reqList = []
    nameList = []
    logP.debug(f"Build command buildList has length: {len(buildList)}")

    # iterate through shorthand enhancements
    for item in buildList:
        # logP.debug(f"Build command item: {item}")
        # fetch enhancement prereqs and cost
        temCost = cost(item)
        # logP.debug(f"Build command prereq cost length: {len(temCost)}")

        # add this enhancement's prereqs to list
        reqList.append(temCost[2])

        # fetch full name for enhancement from shorthand
        tempName = masterEhnDict[item]["Name"]

        # add enhancement full name to lists
        reqList.append(tempName)
        nameList.append(tempName)
    logP.debug(f"Build command reqList is of length: {len(reqList)}")

    # restrict nested prereq list to a set of prereqs
    temp = eleCountUniStr(reqList)

    # fetch highest ranked prereqs of each type in list
    reqList = trim([x for x in temp[1]])
    logP.debug(f"reqList len = {len(reqList)}")

    # sum cost of build from prereqs
    costTot = 0
    for group in reqList:
        costTot += group[0]

    logP.debug(f"Total cost of build is: {costTot}")
    # return cost of build, role names and prerequisite roles
    return costTot, nameList[::-1], reqList


# function to grab number of enhancement points
# spent by each user in given list
def spent(
    memList: list[discord.Member],
) -> list[tuple[discord.Member, int, list[str]]]:
    retList = []
    logP.debug(f"memList is: {memList}")

    # iterate thorugh given list of users
    for peep in memList:
        supeRoles = []
        logP.debug(f"current user is: {peep}")
        logP.debug(f"current user role list length: {len(peep.roles)}")

        # messy implementation to grab shorthand for all unrestricted bot
        # managed roles in user role list
        for roles in peep.roles:
            if roles.name in [
                masterEhnDict[x]["Name"]
                for x in masterEhnDict.keys()
                if masterEhnDict[x]["Rank"] > 0
            ]:
                supeRoles.append(
                    [
                        x
                        for x in masterEhnDict.keys()
                        if masterEhnDict[x]["Name"] == roles.name
                    ][0]
                )
        logP.debug(f"Supe roles: {supeRoles}")

        # fetch point cost (including prereqs) of enhancements
        if supeRoles:
            pointCount = funcBuild(supeRoles)[0]
        else:
            pointCount = funcBuild([])[0]

        # add (user, total build cost, enhancmeent role names)
        # to list to return
        retList.append(
            (
                peep,
                pointCount,
                sorted(supeRoles, key=lambda x: (-int(x[3:]), x[:3])),
            )
        )

    logP.debug(f"retlist is: {retList}")
    return retList


async def dupeError(
    mes: discord.Embed,
    ctx: commands.Context,
    channel: typing.Union[discord.TextChannel, discord.Thread],
):
    author = ctx.author.display_name
    autID = ctx.author.id
    currTime = time.localtime()
    currTimeStr = (
        f"{currTime.tm_year:04d}.{currTime.tm_mon:02d}."
        f"{currTime.tm_mday:02d}_{currTime.tm_hour:02d}."
        f"{currTime.tm_min:02d}.{currTime.tm_sec:02d}"
    )

    errMes = (
        f"At {currTimeStr}, {author} ({autID}) "
        f"produced this error on {HOST_NAME}: "
    )
    logP.warning(errMes + str(mes.to_dict()["description"]))

    if isinstance(channel, discord.Thread):
        if channel.archived:
            await channel.edit(archived=0)

    await channel.send(errMes)
    if isinstance(mes, discord.Embed):
        await channel.send(embed=mes)
    if isinstance(mes, str):
        await channel.send(mes)

    if isinstance(channel, discord.Thread):
        await channel.edit(archived=1)


async def getSendLoc(id, bot: commands.Bot, attr: str = "channel"):
    otherOpt = []
    iterList = [x for y in bot.guilds for x in getattr(y, f"{attr}s")]
    sendLoc = [x for x in iterList if int(x.id) == int(id)]

    if attr == "thread":
        otherOpt = [
            x.archived_threads()
            for y in bot.guilds
            for x in y.text_channels
            if int(x.id) == int(START_CHANNEL)
        ]

    if otherOpt and not sendLoc:
        sendLoc = []
        for x in otherOpt:
            async for y in x:
                if int(y.id) == int(id):
                    sendLoc.append(y)

    logP.debug(
        (
            f"searching for {id} in list of {len(iterList)} length or other"
            f" list of length {len(otherOpt)} = {sendLoc}"
        )
    )

    if isinstance(sendLoc, list):
        if sendLoc:
            sendLoc = sendLoc[0]
    return sendLoc


async def dupeMes(bot, channel=None, mes: str = None):
    global STRCHNL
    if not STRCHNL:
        STRCHNL = await getSendLoc(START_CHANNEL, bot, "channel")
    if isinstance(channel, commands.Context):
        channel = channel.channel

    if mes:
        print(mes)
        if STRCHNL:
            await STRCHNL.send(mes)
            if channel:
                if not STRCHNL == channel:
                    await channel.send(mes)


async def memGrab(
    ctx: commands.Context, memList: str = ""
) -> list[typing.Union[discord.User, discord.Member]]:
    logP.debug(f"memList: {memList}\nand mentions: {ctx.message.mentions}")
    grabList = []
    # first check for users mentioned in message
    if ctx.message.mentions:
        grabList = ctx.message.mentions
        logP.debug(f"Message mentions: {grabList}")

    # else check for users named by command caller
    elif memList:
        strMemList = memList.split(", ")
        logP.debug(f"split grablist: {strMemList}")
        for posMem in strMemList:
            logP.debug(f"trying to find: {posMem}")
            grabMem = None
            try:
                grabMem = await MemberConverter().convert(ctx, posMem)
                logP.debug(f"adding: {grabMem}")
                grabList.append(grabMem)
            except commands.BadArgument:
                pass
            if not grabMem:
                try:
                    grabMem = await RoleConverter().convert(ctx, posMem)
                    logP.debug(f"found: {grabMem}")
                    await ctx.send(
                        (
                            f"Pulling {len(grabMem.members)} members "
                            f"from the role {grabMem}"
                        )
                    )
                    for peep in grabMem.members:
                        grabList.append(peep)
                    logP.debug(f"adding: {grabMem}")

                except commands.BadArgument:
                    pass

    # else use the command caller themself
    else:
        grabList.append(ctx.author)
        logP.debug(f"Author is: {grabList}")
    logP.debug(f"fixed grablist: {grabList}")

    # return: mentioned users || named users || message author
    return grabList


def getLoc(fileName: str, dirName: str):
    # get the root directory of the project
    # if there is not a directory of dirName, create it
    # return the full path of the file
    rootDir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    if not os.path.exists(os.path.join(rootDir, dirName)):
        os.mkdir(os.path.join(rootDir, dirName))
    return os.path.join(rootDir, dirName, fileName)


def save(key: int, value: dict, cache_file=getLoc(SAVE_FILE, "data")):
    try:
        with SqliteDict(cache_file) as mydict:
            mydict[key] = value  # Using dict[key] to store
            mydict.commit()  # Need to commit() to actually flush the data
        logP.debug(f"saved {key} of length: {len(value)}")
    except Exception as ex:
        logP.warning(["Error during storing data (Possibly unsupported):", ex])


def load(
    key: int, cache_file=getLoc(SAVE_FILE, "data")
) -> dict[int, dict[str]]:
    try:
        value = {}
        with SqliteDict(cache_file) as mydict:
            # No need to use commit(), since we are only loading data!
            value = mydict[key]
        logP.debug(f"Loaded with key {key} length: {len(value)}")
        return value
    except Exception as ex:
        logP.warning(["Error during loading data:", ex])
        return {}


def lvlEqu(givVar: float = 0, inv=0) -> float:
    if inv:
        # calVar = (20 * math.pow(givVar, 2)) / 1.25
        calVar = ((500 * math.pow(givVar, 2)) / 51) + ((35000 * givVar) / 51)
        logP.debug(f"{givVar:0.2g} GDV is equivalent to {calVar:,} XP")
    else:
        # calVar = math.sqrt((1.25 * givVar) / 20)
        calVar = -35 + (
            math.sqrt((51 * givVar) + 612500) / (10 * math.sqrt(5))
        )
        logP.debug(f"{givVar:,} XP is equivalent to {calVar:0.2g} GDV")
    return round(calVar, 2)


def aOrAn(inp: str):
    logP.debug(f"input is: {inp}")
    ret = "A"
    if inp[0].lower() in "aeiou":
        ret = "An"
    logP.debug(f"ret: {ret}")
    return ret


def pluralInt(val: int):
    rtnStr = ""
    if not val == 1:
        rtnStr = "s"
    return rtnStr


def topEnh(ctx: commands.Context, enh: str) -> dict:

    enhNameList = {
        masterEhnDict[x]["Name"]: 0
        for x in masterEhnDict.keys()
        if enh == masterEhnDict[x]["Type"]
    }
    peepDict = {}
    for peep in ctx.guild.members:
        if SUPE_ROLE not in [x.name for x in peep.roles]:
            continue
        for role in peep.roles:
            if role.name in enhNameList.keys():
                enhNameList[role.name] += 1
                if peep not in peepDict.keys():
                    peepDict[peep] = [
                        masterEhnDict[x]["Rank"]
                        for x in masterEhnDict.keys()
                        if masterEhnDict[x]["Name"] == role.name
                    ][0]
                else:
                    rank = [
                        masterEhnDict[x]["Rank"]
                        for x in masterEhnDict.keys()
                        if masterEhnDict[x]["Name"] == role.name
                    ][0]
                    if rank > peepDict[peep]:
                        peepDict[peep] = rank
    return peepDict


def asleep(var=None):
    global SLEEP
    if var:
        SLEEP = not SLEEP
    return SLEEP


# get roles of a lower rank on member to remove later
def toCut(member: discord.Member) -> list[str]:

    # fetch unrestricted managed roles member has
    supeRoles = spent([member])
    logP.debug(f"supeRoles = {supeRoles[0][2]}")

    # fetch build of member
    supeBuild = funcBuild(supeRoles[0][2])
    logP.debug(f"supeBuild = {supeBuild[1]}")

    # fetch trimmed build of user
    supeTrim = [
        masterEhnDict[toType(x[1]) + str(x[0])]["Name"]
        for x in trim(supeBuild[1])
    ]
    logP.debug(f"supeTrim = {supeTrim}")

    # fetch extra roles user has that are to be removed
    toCut = [x for x in supeBuild[1] if x not in supeTrim]
    logP.debug(f"to CUT = {toCut}")

    # return the roles to be removed
    return toCut


# function to remove extra or specified roles from list of users
async def cut(
    ctx: commands.Context,
    memberList: list[discord.Member],
    cutList: list[str] = [],
):
    # iterate through given user list
    # assumed list has already been reduced to users with SUPEROLE
    mes = discord.Embed(title="Cutting Roles")

    for peep in memberList:

        # if no list of roles to remove was given get user's extra roles
        if not cutList:
            cutting = toCut(peep)
        else:
            cutting = cutList

        # for each role to be cut, remove it and send message to discord
        sendMes = ""
        idRemList = []
        for role in cutting:
            logP.debug(f"role to cut: {role}, from peep: {peep}")
            supeRoleId = get(peep.roles, name=role)
            logP.debug(f"role to cut id = {supeRoleId}")
            if supeRoleId in peep.roles:
                idRemList.append(supeRoleId)
                sendMes += f"Removed {supeRoleId}, {random.choice(remList)}\n"
        await peep.remove_roles(*idRemList)

        # notify current user has been finished with to discord
        sendMes += f"{peep.display_name} has been cut down to size!"
        mes.add_field(name=f"{peep.display_name}", value=sendMes)
    await sendMessage(ctx, mes)


async def toAdd(ctx: commands.Context, user: discord.Member, givenBuild: list):
    # the guild role names grabbed from shorthand to add to user
    addList: list[str] = [
        masterEhnDict[toType(x[1]) + str(x[0])]["Name"] for x in givenBuild
    ]
    logP.debug(f"Add list = {addList}")

    # restricted roles the user does not have that the build requires
    cantAdd = [x for x in restrictedList if x in addList]
    cantAdd = [x for x in cantAdd if x not in [y.name for y in user.roles]]
    logP.debug(f"Cant add = {cantAdd}")

    # check to ensure user has restricted roles already,
    # if required for build
    if cantAdd:
        await ctx.send(
            (
                f"Cannot add enhancements as {user.display_name} "
                f"does not have {cantAdd}"
            )
        )
        return

    # guild role list with name and id attributes
    guildRoles = await user.guild.fetch_roles()

    # iterate through roles to add to user
    sendMes = discord.Embed(title="Adding Roles")
    rolesToAddStr = ""
    rolesToAdd = []
    toMove = {}
    for role in addList:
        logP.debug(f"Trying to add role: {role}")

        # check for if user has enhancement role already
        roleId = get(guildRoles, name=role)
        if roleId in user.roles:
            logP.debug(f"{user.display_name} already has the role {roleId}")
            continue

        # role names to add will have format "Rank *Rank* *Type*"
        roleRank = role.split()[1]
        logP.debug(f"{roleId}, {roleRank}")

        # check for role already in guild role list, create it if required
        if not roleId:
            colour = rankColour[int(roleRank)]
            logP.debug(f"colour for rank {roleRank} is: {colour}")
            roleId = await user.guild.create_role(name=role, color=colour)
            roleToPos = calcRolePos(ctx, roleId)
            toMove[roleId] = roleToPos

        # add requested role to user
        rolesToAdd.append(roleId)
        rolesToAddStr += f"Added {roleId}!\n"

    if len(toMove):
        await ctx.guild.edit_role_positions(toMove)
    # trim the user of excess roles
    # debug("TO CUT")
    # await cut(ctx, [user])
    if rolesToAddStr:
        sendMes.add_field(name=f"{user.display_name}", value=rolesToAddStr)
        await user.add_roles(*rolesToAdd)
    await sendMessage(ctx, sendMes)


async def pointsLeft(
    ctx: commands.Context,
    supeUsers: list[discord.Member],
    hideFull: bool = False,
):
    # fetch points of each SUPEROLE user
    pointList = spent(supeUsers)
    skipped = 0
    # return result
    for group in pointList:
        logP.debug(f"group in level is: {group}")
        pointTot = count(group[0])

        if hideFull:
            if group[1] == pointTot[0]:
                skipped += 1
                continue
        await ctx.send(
            (
                f"{group[0].display_name} has {pointTot[0]- group[1]} "
                "spare enhancement points."
            )
        )
    if skipped:
        await ctx.send(
            f"{len(supeUsers)} members scanned. {skipped} members skipped."
        )
    if len(supeUsers) > 10:
        await ctx.send("Point scanning finished.")


async def mee6DictGrab(roleTo: discord.Role):
    numToGrab = len(roleTo.guild.members)
    pages = math.floor(numToGrab / 100) + 1

    leaderboard = await API(roleTo.guild.id).levels.get_all_leaderboard_pages(
        pages, roleTo.guild.id
    )

    memberList = []

    for page in leaderboard:
        memberList += page["players"]

    logP.debug(f"mee6 peep list of length: {len(memberList)}")

    savedCache = load(roleTo.guild.id)

    for peep in [x for x in memberList if int(x["id"]) in savedCache.keys()]:
        peepID = int(peep["id"])
        savedCache[peepID].setdefault("invXP", [0, 0, 0])
        origXP = savedCache[peepID]["invXP"][0]
        savedCache[peepID]["invXP"][0] = peep["xp"]
        logP.debug(
            (
                "Updating Mee6XP for "
                f"{peep['username']}: {origXP} -> {peep['xp']}"
            )
        )

    save(roleTo.guild.id, savedCache)


async def tatsuXpGrab(roleTo: discord.Role):
    tat = tatsu.wrapper
    mes = ""
    savedCache = load(roleTo.guild.id)
    peepList: list[discord.Member] = shared_dyVars.tatsuUpdateList.copy()
    for peep in peepList:
        TATSUxp = 0
        try:
            TATSUmem = await tat.ApiWrapper(key=TATSU).get_profile(peep.id)
            TATSUxp = int(TATSUmem.xp)
        except Exception as e:
            logP.warning(e)
        origXP = savedCache[peep.id]["invXP"][1]
        savedCache[peep.id]["invXP"][1] = TATSUxp
        logP.debug(
            (
                "Updating TatsuXP for "
                f"{peep.display_name}: {origXP} -> {TATSUxp}"
            )
        )
        try:
            shared_dyVars.tatsuUpdateList.remove(peep)
            mes += f"Updated {peep.display_name}\n"
        except ValueError as e:
            logP.warning(e)
            mes += str(e) + "\n"
    save(roleTo.guild.id, savedCache)
    return mes


# function to get specified user's enhancement points
def count(
    peepList: typing.Union[list[discord.Member], discord.Member]
) -> tuple[int, float, float, list[int, int, float], dict, dict]:

    if isinstance(peepList, discord.Member):
        peepList = [peepList]

    try:
        pickle_file = load(peepList[0].guild.id)
    except Exception as e:
        print(e)
        logP.debug("Pickle file load failed")
        pickle_file = {}

    for peep in peepList:
        pickle_file.setdefault(peep.id, {"Name": peep.name})

        pickle_file[peep.id].setdefault("invXP", [0, 0, 0])

        ReSubXP = float(pickle_file[peep.id]["invXP"][-1])
        MEE6xp = int(pickle_file[peep.id]["invXP"][0])
        TATSUxp = int(pickle_file[peep.id]["invXP"][1])

        if MEE6xp or TATSUxp or ReSubXP:
            totXP = ReSubXP + MEE6xp + (TATSUxp / 2)
        else:
            totXP = float(0)

        if peep.display_name == "Geminel":
            totXP = round(totXP * float(GEM_DIFF), 3)

        gdv = lvlEqu(totXP)

        enhP = math.floor(gdv / 5) + 1

        currPatrol: dict = pickle_file[peep.id].setdefault("currPatrol", {})
        topStatistics: dict = pickle_file[peep.id].setdefault(
            "topStatistics", {}
        )

        lastTaskTime = currPatrol.setdefault("lastTaskTime", None)
        patrolStart = currPatrol.setdefault("patrolStart", None)
        patrolTasks = currPatrol.setdefault("patrolTasks", 0)

        totalTasks = topStatistics.setdefault("totalTasks", 0)
        totalPatrols = topStatistics.setdefault("totalPatrols", 0)
        longestPatrol = topStatistics.setdefault("longestPatrol", 0.0)
        mostActivePatrol = topStatistics.setdefault("mostActivePatrol", 0)
        firstTaskTime = topStatistics.setdefault("firstTaskTime", None)

        agg = pickle_file[peep.id].get("agg", baseDict["AGG"])

        logP.debug(
            (
                f"{peep.display_name}-"
                f" ReSubXP: {ReSubXP},"
                f" TATSUxp: {TATSUxp},"
                f" MEE6xp: {MEE6xp},"
                f" totXP: {totXP},"
                f" gdv: {gdv},"
                f" enhP: {enhP}"
                f" lastTaskTime: {lastTaskTime}"
                f" patrolTasks: {patrolTasks}"
                f" patrolStart: {patrolStart}"
                f" totalTasks: {totalTasks}"
                f" totalPatrols: {totalPatrols}"
                f" longestPatrol: {longestPatrol}"
                f" firstTaskTime: {firstTaskTime}"
                f" mostActivePatrol: {mostActivePatrol}"
                f" agg: {agg}"
            )
        )
        pickle_file[peep.id]["Name"] = peep.name
        pickle_file[peep.id]["enhP"] = enhP
        pickle_file[peep.id]["gdv"] = gdv
        pickle_file[peep.id]["totXP"] = totXP
        pickle_file[peep.id]["invXP"] = [MEE6xp, TATSUxp, ReSubXP]
        pickle_file[peep.id]["currPatrol"] = currPatrol
        pickle_file[peep.id]["topStatistics"] = topStatistics

    save(peepList[0].guild.id, pickle_file)
    if len(peepList) == 1:
        return (
            enhP,
            gdv,
            totXP,
            [MEE6xp, TATSUxp, ReSubXP],
            currPatrol,
            topStatistics,
            agg,
        )
    else:
        return pickle_file


def countIdList(ctx: commands.Context, idList: list[int]):
    peepList = []
    for id in idList:
        addPeep = ctx.guild.get_member(id)
        if addPeep:
            peepList.append(addPeep)
    return count(peepList)


def getDesc(cmdName: str = ""):
    ret = ""
    if cmdName in cmdInf.keys():
        ret = cmdInf[cmdName]["Description"]
    if not ret:
        ret = "No Description"
    return ret


def getBrief(cmdName: str = ""):
    ret = ""
    if cmdName in cmdInf:
        ret = cmdInf[cmdName]["Brief"]
    if not ret:
        ret = "No Brief"
    return ret


async def remOnCall(onCallRole: discord.Role, activeTimeMax: int):
    notActive = {}
    memberDict = load(onCallRole.guild.id)
    currTime = time.time()
    currentlyPatrolling = 0
    for key, val in memberDict.items():
        currPatrol = val.get("currPatrol", {})
        lastTaskTime = currPatrol.get("lastTaskTime", None)

        if lastTaskTime:
            currentlyPatrolling += 1
            sinceLastTask = int(round(currTime - lastTaskTime))
            logP.debug(f"Time since last task is: {sinceLastTask}")
            if sinceLastTask > activeTimeMax:
                member = get(onCallRole.guild.members, id=int(key))
                if member:
                    notActive[member] = sinceLastTask

    membersFinishingPatrol = set(onCallRole.members) & set(notActive.keys())
    for peep in membersFinishingPatrol:
        await peep.remove_roles(onCallRole)


async def remOnPatrol(
    patrolRole: discord.Role,
    onCallRole: discord.Role,
    streakerRole: discord.Role,
    activeTimeMax: int,
):
    notActive = {}
    memberDict = load(patrolRole.guild.id)
    currTime = time.time()
    currentlyPatrolling = 0
    for key, val in memberDict.items():
        currPatrol = val.get("currPatrol", {})
        lastTaskTime = currPatrol.get("lastTaskTime", None)

        if lastTaskTime:
            currentlyPatrolling += 1
            lastPatrolTaskTime = int(round(currTime - lastTaskTime))
            patrolLength = int(
                round(currTime - currPatrol.get("patrolStart", lastTaskTime))
            )
            numPatrolTasks = currPatrol.get("patrolTasks", 0)
            logP.debug(f"Time since last task is: {lastPatrolTaskTime}")

            member = get(patrolRole.guild.members, id=int(key))
            hourlyPing = lastPatrolTaskTime % (60 * 60)
            timeLeft = datetime.timedelta(
                seconds=int(activeTimeMax - lastPatrolTaskTime)
            )

            if lastPatrolTaskTime > activeTimeMax:
                if member:
                    notActive[member] = [patrolLength, numPatrolTasks]

            elif hourlyPing in range(50 * 60, 60 * 60):
                if (
                    isinstance(member, discord.Member)
                    and streakerRole in member.roles
                    and member.status != discord.Status.offline
                ):
                    await member.send(
                        (
                            f"[Attention host, system {str(member.id)[-3:]} "
                            "reporting. Your patrol will be ending "
                            f"in roughly {timeLeft}.]"
                        )
                    )

    membersFinishingPatrol = set(patrolRole.members) & set(notActive.keys())

    perPatrolMes = (
        f"{currentlyPatrolling}/{len(memberDict)} {SUPE_ROLE}'s have started a"
        f" patrol at some point in time and {len(membersFinishingPatrol)} "
        "are currently finishing their patrol. "
        f"{len(patrolRole.members)-len(membersFinishingPatrol)} are out on a "
        f"patrol now with {len(onCallRole.members)} on call."
    )

    logP.debug(perPatrolMes)

    for peep in membersFinishingPatrol:
        await peep.remove_roles(patrolRole)
        await peep.add_roles(onCallRole)
        memberDict[peep.id].setdefault("topStatistics", {})
        longestPatrol = memberDict[peep.id]["topStatistics"].get(
            "longestPatrol", 0
        )
        mostActivePatrol = memberDict[peep.id]["topStatistics"].get(
            "mostActivePatrol", 0
        )

        if longestPatrol < notActive[peep][0]:
            memberDict[peep.id]["topStatistics"]["longestPatrol"] = notActive[
                peep
            ][0]
        if mostActivePatrol < notActive[peep][1]:
            memberDict[peep.id]["topStatistics"][
                "mostActivePatrol"
            ] = notActive[peep][1]

    save(patrolRole.guild.id, memberDict)

    return perPatrolMes


async def rAddFunc(
    ctx: commands.Context, userList: list[discord.Member], incAmount: int = 1
):
    iniInc = incAmount
    for user in userList:
        incAmount = iniInc
        if not incAmount:
            pointTot = count(user)
            incAmount = pointTot[0]
        while incAmount:
            incAmount -= 1
            userSpent = spent([user])
            userEnhancements = userSpent[0][2]
            userHas = funcBuild(userEnhancements)
            pointTot = count(user)
            if pointTot[0] < userHas[0] + 1:
                await ctx.send(
                    (
                        f"{user} does not have enough points "
                        "to further enhance with."
                    )
                )
                break
            randPlusBuild = genBuild(userHas[0] + 1, "", userEnhancements)
            randPlus = funcBuild(randPlusBuild)
            await toAdd(ctx, user, randPlus[2])


def genBuild(val: int = 0, typ: str = "", iniBuild: list = None) -> list[str]:
    build = []
    buildFinal = []
    floor = 0
    pickList = [
        x
        for x in leader.keys()
        if leader[x] not in restrictedList and x not in reqResList
    ]

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

    iniSplit = {}

    if not iniBuild:
        iniBuild = []
        searchBuild = [typ + str(checkInt)]
    else:
        iniBuild = trimShrtList(iniBuild)
        if funcBuild(iniBuild)[0] > val:
            return iniBuild
        searchBuild = trimShrtList([typ + str(checkInt)] + iniBuild.copy())

        for item in iniBuild:
            iniSplit[item[:3]] = int(item[3:])
    prevBuild = iniBuild.copy()
    maxTyp = []

    testMax = True
    maxSearch = [typ + str(10)] + searchBuild
    while testMax:
        maxBuild = funcBuild(trimShrtList(maxSearch))
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
        if not pickList:
            maxBuild = funcBuild(trimShrtList(maxSearch))
            testMax = False
            val = maxBuild[0]
    if maxTyp:
        searchBuild = searchBuild + maxTyp.copy()
        searchBuild.append(typ + str(checkInt))

    prevBuildsDict = {}
    while building:
        searchBuild = trimShrtList(searchBuild)
        want = prevBuildsDict.setdefault(
            tuple(searchBuild),
            funcBuild(searchBuild),
        )
        trimmed = trim(want[1])

        searchBuild = []

        for group in trimmed:
            rank = group[0]
            name = group[1]
            shrt = [x for x in leader.keys() if leader[x] == name]
            if shrt:
                shrt = shrt[0]
            searchBuild.append(str(shrt) + str(rank))
        searchBuild = trimShrtList(searchBuild)

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
            while (
                tuple(searchBuild) in prevBuildsDict.keys()
                and prevBuildsDict[tuple(searchBuild)][0] > val
            ):
                temp = trimShrtList([typ + str(checkInt)] + maxTyp)
                failedBuild = prevBuildsDict.setdefault(
                    tuple(temp),
                    funcBuild(temp),
                )
                checkPrev = prevBuildsDict.setdefault(
                    tuple(prevBuild),
                    funcBuild(prevBuild),
                )
                if checkPrev[0] > val:
                    return iniBuild

                searchBuild = prevBuild.copy()
                splitBuild = [[int(x[3:]), x[:3]] for x in searchBuild]
                toAdd = toAddToFrom(splitBuild, failedBuild[2])
                if not toAdd:
                    groupToAdd = []
                    while not groupToAdd:
                        toInc = toIncFromTo(splitBuild, failedBuild[2], floor)
                        if toInc:
                            groupToAdd = toInc[0]
                        else:
                            floor += 1
                            if floor == 11:
                                return exitGenBuild(prevBuildsDict, val)
                    shrt = groupToAdd[1]
                    rank = groupToAdd[0]

                else:

                    shrt = toAdd[0]
                    rank = 1
                    if leader[shrt] in restrictedList:
                        rank = 0
                checkInt -= 1
                searchBuild.append(shrt + str(rank))
                searchBuild = trimShrtList(searchBuild)

    for group in build:
        rank = group[0]
        name = group[1]
        shrt = [x for x in leader.keys() if leader[x] == name]
        if shrt:
            shrt = shrt[0]

        buildFinal.append(str(shrt) + str(rank))
    logP.info(f"Tested {len(prevBuildsDict)} builds")
    return buildFinal


# restrict list from members to members with SUPEROLE
def isSuper(
    bot: commands.Bot, guildList: list[discord.User]
) -> list[discord.Member]:
    guilds = bot.guilds
    supeGuildList = []
    foundRole = []

    logP.debug(f"Guild list is: {guilds}")

    for guild in guilds:
        logP.debug(f"iter through: {guild}")
        posRole = get(guild.roles, name=SUPE_ROLE)
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


async def sendMessage(location: Messageable, mes):
    """
    What are you sending and where is it going?
    This function will friut ninja your message to discord message
    length standards and send it to the specified location.

    Parameters
    ----------
    location : Messageable
        The location to send the message. A messagable type is a Discord type
        that has the attribute send.
    mes : Str | Discord.Embed | list[Discord.Embed]
        The message to be sent. Can be a string that will be split by line
        into 2000 character chunks, or a Discord.Embed that will be split by
        24 field chunks, or a list of Discord.Embed that will be split.
    """
    taskList = []
    if isinstance(mes, list):
        embList = [x for x in mes if isinstance(x, discord.Embed)]
        stringList = [x for x in mes if isinstance(x, str)]
        chkdStringList = []

        for emb in pageEmbedList(embList):
            if emb:
                embDict: dict = emb.to_dict()
                task = asyncio.create_task(
                    location.send(
                        embed=discord.Embed.from_dict(copy.deepcopy(embDict))
                    )
                )
                taskList.append(task)

        for string in stringList:
            chkdStringList += splitString(string)
        if chkdStringList:
            for string in chkdStringList:
                task = asyncio.create_task(location.send(string))
                taskList.append(task)

    elif isinstance(mes, discord.Embed):
        for emb in pageEmbed(mes):
            if emb:
                embDict: dict = emb.to_dict()
                task = asyncio.create_task(
                    location.send(
                        embed=discord.Embed.from_dict(copy.deepcopy(embDict))
                    )
                )
                taskList.append(task)

    elif isinstance(mes, str):
        # minMessages = math.floor(mesLength / 2000) + 1
        mesList = splitString(mes)
        for message in mesList:
            if message:
                task = asyncio.create_task(location.send(message))
                taskList.append(task)

    await asyncio.gather(*taskList)


def splitString(mes: str, length: int = 2000) -> list[str]:
    mesList = []
    mesSplit = mes.splitlines(True)
    mesList = splitFunc(mesSplit, length)
    return mesList


def embedBelowMaxLen(
    mes: discord.Embed, addField: discord.embeds.EmbedProxy, lenCheck=6000
):
    if embedLen(mes, addField) < lenCheck:
        return True
    return False


def embedLen(emb: discord.Embed, addField: discord.embeds.EmbedProxy = None):
    fields = [
        emb.title,
        emb.description,
        emb.footer.text,
        emb.author.name,
    ]
    if addField:
        fields.extend([addField.name])
        fields.extend([addField.value])
    fields.extend([field.name for field in emb.fields])
    fields.extend([field.value for field in emb.fields])
    total = ""
    for item in fields:
        total += str(item) if str(item) != "Embed.Empty" else ""
    return len(total)


def pageEmbedList(embedList: list[discord.Embed]):
    for embed in embedList:
        for emb in pageEmbed(embed):
            yield emb


def pageEmbed(mes: discord.Embed, maxFields=24):
    totFields = 0
    newMes = discord.Embed(title=mes.title, description=mes.description)
    if mes.author:
        newMes.set_author(
            name=mes.author.name,
            url=mes.author.url,
            icon_url=mes.author.icon_url,
        )
    if mes.thumbnail:
        newMes.set_thumbnail(url=mes.thumbnail.url)
    newMes.set_footer(text=mes.footer.text, icon_url=mes.footer.icon_url)

    for field in mes.fields:
        if not field:
            continue
        if totFields + 1 > maxFields or not embedBelowMaxLen(
            newMes,
            field,
        ):
            yield newMes
            totFields = 0
            newMes.clear_fields()
        newMes.add_field(name=field.name, value=field.value)
        totFields += 1

    yield newMes


def splitFunc(mesList: list[str], maxLen: int = 2000):
    currMes = ""
    retList = []
    for mes in mesList:
        if len(mes) + len(currMes) <= maxLen:
            currMes += mes
            continue
        else:
            if currMes:
                retList.append(currMes)
            if len(mes) <= maxLen:
                currMes = mes
                continue
            splitupMes = mes.split(" ")
            if len(splitupMes) > 1:
                for i, bit in enumerate(splitupMes):
                    splitupMes[i] = bit + " "
                retList += splitFunc(splitupMes)
                currMes = ""
                continue
            else:
                retList += splitFunc(mes)
                currMes = ""
                continue
    retList.append(currMes)
    return retList


def pickWeightedSupe(
    ctx: commands.Context,
    roles: list[discord.Role],
    weights: list[int],
    numPicks: int = 1,
) -> list[discord.Member]:

    if len(roles) != len(weights):
        raise Exception("Number of roles and weights do not match.")
    toRet = []

    if numPicks == -1:
        toRet += roles[-1].members
        if ctx.author in toRet:
            toRet.remove(ctx.author)

    elif numPicks:
        if numPicks < 0:
            numPicks = 0
        roleSets: list[list[discord.Member]] = []
        for role in roles:
            toAppend = role.members
            if ctx.author in toAppend:
                toAppend.remove(ctx.author)
            roleSets.append(toAppend)

        while numPicks:
            numPicks -= 1

            toAdd = None
            while not toAdd:
                pickRole = random.choices(roleSets, weights)
                if isinstance(pickRole, list):
                    pickRole = pickRole[0]
                if pickRole:
                    toAdd = random.choice(pickRole)
            toRet.append(toAdd)

            for roleList in roleSets:
                if toAdd in roleList:
                    roleList.remove(toAdd)

    return toRet


def blToStr(buildList):
    ret = ""
    playerEhnList = [masterEhnDict[x]["Name"] for x in buildList]
    addBot = [x for x in playerEhnList if x in restrictedList]
    for item in addBot:
        playerEhnList.remove(item)
    for ehn in sorted(
        playerEhnList,
        key=lambda x: int(x.split()[1]),
        reverse=True,
    ):
        ret += f"{ehn}\n"
    for ehn in addBot:
        ret += f"{ehn}\n"
    return ret


def strList(dualList):
    retList = []
    for item in dualList:
        typ = item[1]
        rank = item[0]
        shrtTyp = [x for x in leader.keys() if leader[x] == typ]
        if isinstance(shrtTyp, list):
            shrtTyp = shrtTyp[0]
        retList.append(f"{shrtTyp}{rank}")
    return retList


class genOppNPC:
    def __init__(
        self,
        bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot],
        baseVal,
    ) -> None:
        self.bot = bot
        self.picUrl = self.bot.user.display_avatar.url
        self.power, self.desc = self.rollPower()
        self.n, self.gender = self.rollName()
        self.bV = baseVal
        self.bL = self.rollBuild()
        self.reRoll()

    def reRoll(self):
        self.rank, self.task = self.rollRank()

    def rollBuild(self):
        return genBuild(
            self.bV, [x for x in leader if leader[x] == self.power][0]
        )

    def rollName(self):
        roll = random.choice(activeDic["person"])
        return str(roll[0]).capitalize(), str(roll[1])

    def rollPower(self):
        retPower = random.choice(list(powerTypes.keys())[:15])
        retDesc = random.choice(activeDic[retPower])
        if retDesc[0] == " ":
            retDesc = retDesc[1:]
        return str(retPower), str(retDesc)

    def rollRank(self):
        roll = random.choices(
            taskVar["taskOpt"][0],
            cum_weights=taskVar["taskWeight"],
        )
        if isinstance(roll, list):
            roll = roll[0]
        retRank = roll
        retTask = random.choice(random.choice(activeDic[str(roll).lower()]))
        if retTask[0] == " ":
            retTask = retTask[1:]
        return str(retRank), str(retTask)


def rollTask(bot, peep: discord.member):
    peepCount = spent([peep])
    opponent = genOppNPC(bot, peepCount[0][1])
    return opponent


def genderPick(gender: str, typ: str):
    genDict = genDictAll[typ]
    ret = ""
    if gender[0] in genDict.keys() and gender not in ["random", "r"]:
        ret = genDict[gender[0]]
    if not ret:
        ret = random.choice(genDict["r"])

    return str(ret)


def trimShrtList(buildList: list[str]):
    foundDict = {}
    for item in buildList:
        typ = item[:3]
        rank = int(item[3:])
        if typ not in foundDict.keys() or rank > foundDict[typ]:
            foundDict[typ] = rank
    retList = [f"{x}{foundDict[x]}" for x in foundDict.keys()]
    return sorted(retList, key=lambda x: (-int(x[3:]), str(x[:3])))


def duelMoveView(reactionList: list):
    compList = discord.ui.View()
    for reac in reactionList:
        styl, row = duelButtonType(reac[1])
        compList.add_item(
            discord.ui.Button(
                emoji=reac[0], style=styl, custom_id=reac[2], row=row
            )
        )
    return compList


def duelButtonType(styl: str):
    retStyl = discord.ButtonStyle.grey
    retRow = 0
    if styl == "Attack":
        retStyl = discord.ButtonStyle.blurple
        retRow = 1
    elif styl == "Defend":
        retStyl = discord.ButtonStyle.green
        retRow = 2
    elif styl == "Utility":
        retStyl = discord.ButtonStyle.grey
        retRow = 3
    elif styl == "Quit":
        retStyl = discord.ButtonStyle.red
        retRow = 4
    return retStyl, retRow


def toAddToFrom(toBuild: list, fromBuild: list):
    toBuildShrt = [x[1] for x in toBuild]
    fromBuildTyp = [x[1] for x in fromBuild]

    fromBuildShrt = []
    for item in fromBuildTyp:
        fromBuildShrt += [x for x in leader.keys() if leader[x] == item]

    toRet = list(set(fromBuildShrt) - set(toBuildShrt))

    return toRet


def toIncFromTo(toBuild: list, fromBuildList: list, floor: int):
    fromBuild = [
        [x[0], y]
        for x in fromBuildList
        for y in leader.keys()
        if leader[y] == x[1]
    ]
    fromBuildDict = {}
    for item in fromBuild:
        fromBuildDict[item[1]] = item[0]
    toRet = []
    for item in toBuild:
        rank = item[0]
        shrt = item[1]
        if floor > rank and floor <= fromBuildDict.setdefault(shrt, rank):
            toRet.append([floor, shrt])
    return toRet


def exitGenBuild(searchedBuilds: dict, val: int):
    largestSafeBuilds = sorted(
        [
            [searchedBuilds[x][0], x]
            for x in searchedBuilds.keys()
            if searchedBuilds[x][0] < val
        ],
        key=lambda x: -int(x[0]),
    )
    largestSafeBuild = largestSafeBuilds[0]
    return largestSafeBuild[1]


def buildFromString(givenString: str):
    fixArg = givenString.replace(" ", ",")
    fixArg = fixArg.replace(";", ",")
    buildList = [x.strip() for x in fixArg.split(",") if x.strip()]
    return buildList


def checkDefined(ctx: commands.Context, buildType: typing.Union[int, str]):
    gen = None
    cost = None
    build = []
    if isinstance(buildType, str):
        if buildType.lower() == "rand":
            buildType = 0

        elif buildType.lower() == "self":
            gen = spent([ctx.author])[0]
            cost = gen[1]
            build = gen[2]

        else:
            # peepBuild is a quoted build
            gen = funcBuild(buildFromString(buildType))
            cost = gen[0]
            build = strList(gen[2])
    return buildType, cost, build


def checkUndefined(
    ctx: commands.Context,
    peepBuild: typing.Union[int, str],
    notPeepBuild: typing.Union[int, str],
    defCost: int,
):

    # peepBuild requires notPeepBuild to be evaluated
    if isinstance(notPeepBuild, int) or notPeepBuild.lower() == "rand":
        # notPeepBuild is not defined and peepBuild should use defCost
        cost = max(0, peepBuild + defCost)

    else:
        # calculate the cost of notPeepBuild to use as
        # the baseCost for p1Cost instead of defCost as baseCost
        if notPeepBuild.lower() == "self":
            otherGen = spent([ctx.author])[0]
            otherCost = otherGen[1]

        else:
            # notPeepBuild is a quoted build
            otherGen = funcBuild(buildFromString(notPeepBuild))
            otherCost = otherGen[0]

        cost = max(0, peepBuild + otherCost)
    build = genBuild(cost)
    return build, cost


def winPercent(varList: list[str]):
    mes = ""
    varCount = typing.Counter(varList)
    totalNum = len(varList)
    mes += f"({totalNum}) "
    for key, val in varCount.items():
        mes += f"{key}: {val/totalNum:.0%}, "
    return mes[:-2]


def dictShrtBuild(shrtBuild: list[str]):
    retDict = {}
    for item in shrtBuild:
        retDict[item[:3]] = int(item[3:])
    return retDict


def savePers(
    pers: genOppNPC,
    toSave=True,
    cache_file=getLoc("persistent.sqlite3", "data"),
):
    # add persistent to genOppNPC list in a file named "persistent.sqlite3"
    # if persistent is already in the list, update the persistent's
    # win/loss count
    # if persistent is not in the list, add persistent to the list

    try:
        pers.bot = None
        with SqliteDict(cache_file) as mydict:
            if pers.n in mydict.iterkeys():
                prevSave = mydict[str(pers.n)]

                prevSave["win"] += int(bool(toSave))
                prevSave["loss"] += int(not bool(toSave))

                mydict[str(pers.n)] = prevSave

            elif toSave:
                mydict[str(pers.n)] = {
                    "win": 1,
                    "loss": 0,
                    "peep": pers,
                }
            mydict.commit()
    except Exception as ex:
        logP.warning(["Error during storing data (Possibly unsupported):", ex])


def loadAllPers(
    bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot],
    cache_file=getLoc("persistent.sqlite3", "data"),
):
    # load persistent from file named "persistent.sqlite3"
    # return a list of players
    try:
        persList: list[tuple[genOppNPC, int, int]] = []
        with SqliteDict(cache_file) as mydict:
            for key, val in mydict.iteritems():
                val["peep"].bot = bot
                persList.append(
                    [
                        val["peep"],
                        val["win"],
                        val["loss"],
                    ]
                )
        return persList
    except Exception as ex:
        logP.warning(["Error during loading data (Possibly unsupported):", ex])
        return False


def compareBuild(hasBuild, wantsBuild):
    remRoles = []
    wantStrBuild = strList(wantsBuild)
    hasStrBuild = strList(hasBuild)
    if not wantStrBuild == hasStrBuild:
        for item in hasStrBuild:
            if item not in wantStrBuild:
                remRoles.append(masterEhnDict[item]["Name"])
    return remRoles


def getGuildSupeRoles(ctx: commands.Context):
    toManage: list[tuple[discord.Role, dict[str]]] = []
    lowestRank = 100
    highestRank = 0
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
        else:
            roleShort = masterEhnDict[roleShort[0]]

        # fetch enhancement rank
        roleRank = roleShort["Rank"]
        logP.debug(f"Role rank is: {roleRank}")

        # check for restricted roles
        if not roleRank:
            logP.debug("Role rank zero")
            continue

        # Code getting to here means the role is
        # one that could need to be moved by the bot
        toManage.append((role, roleShort))
        if role.position < lowestRank:
            lowestRank = role.position
        if role.position > highestRank:
            highestRank = role.position
    return toManage, lowestRank, highestRank


def calcRolePos(ctx: commands.Context, roleToFind: discord.Role):
    toManage, lowestRank, highestRank = getGuildSupeRoles(ctx)
    foundIndex = 1
    toManage.sort(
        key=lambda x: (-int(x[1]["Rank"]), SORT_ORDER.index(x[1]["Type"])),
        reverse=True,
    )
    for i, (role, roleShort) in enumerate(toManage):
        if role == roleToFind:
            foundIndex += i
            break
    return max(1, lowestRank + foundIndex)


def sublist(ls1, ls2):
    """
    >>> sublist([], [1,2,3])
    True
    >>> sublist([1,2,3,4], [2,5,3])
    True
    >>> sublist([1,2,3,4], [0,3,2])
    False
    >>> sublist([1,2,3,4], [1,2,5,6,7,8,5,76,4,3])
    False

    https://stackoverflow.com/questions/35964155/checking-if-list-is-a-sublist/35964184

    answered Mar 12 '16 at 22:37
    L3viathan
    """

    def get_all_in(one, another):
        for element in one:
            if element in another:
                yield element

    for x1, x2 in zip(get_all_in(ls1, ls2), get_all_in(ls2, ls1)):
        if x1 != x2:
            return False

    return True


def getHelpers(
    ctx: commands.Context,
    taskShrt,
    taskAdd,
    aidPick=None,
    aidWeight=AID_WEIGHT,
):
    if not aidPick:
        patrolRole = get(ctx.guild.roles, id=int(ROLE_ID_PATROL))
        supRole = get(ctx.guild.roles, name=SUPE_ROLE)
        onCallRole = get(ctx.guild.roles, id=int(ROLE_ID_CALL))

        aidPick = [patrolRole, onCallRole, supRole]

    if taskAdd:
        logP.debug(f"Guild has {len(ctx.message.guild.roles)} roles")
        addPeeps = pickWeightedSupe(ctx, aidPick, aidWeight, taskAdd)
        xpList = [[x, taskShrt["Aid"]] for x in addPeeps[:taskAdd]]
        xpList.append([ctx.author, 1])
    else:
        addPeeps = ""
        xpList = [[ctx.author, 1]]
    return xpList


def buffStrGen(
    buffDict: dict,
    peepName: str,
    aidNames: list[str],
    isBot=False,
):
    aidStr = str(aidNames)
    if isBot:
        aidStr = f"{len(aidNames)} helper{pluralInt(len(aidNames))}"
    peepEmb = discord.Embed(
        title="Granted Buffs",
        description=f"{peepName} is receiving aid from {aidStr} and gains:",
    )
    for key, val in buffDict.items():
        peepEmb.add_field(name=key, value=val)
    return peepEmb


def saveTime(givenTime: float, fileName: str = getLoc("uptime.json", "data")):
    # add given time to the time list in the file
    # return the time list
    try:
        with open(fileName, "r") as f:
            timeList = json.load(f)
    except Exception as ex:
        logP.warning(f"Error during loading data: {ex}")
        timeList = []
    timeList.append(givenTime)
    with open(fileName, "w") as f:
        json.dump(timeList, f)
    return timeList


def histUptime(
    timelineSquares: int = 100, fileName: str = getLoc("uptime.json", "data")
):
    currTime = time.time()
    saveTime(currTime)
    timeList: list[float] = []
    try:
        with open(fileName, "r") as f:
            timeList = json.load(f)
    except Exception as ex:
        logP.warning(f"Error during loading data: {ex}")

    retStr = ""
    offline: list[list[float]] = []
    online: list[list[float]] = []
    timeLine = []
    currTime = time.time()
    currCheck = currTime
    timelineStr = ""

    timeChar = ["🟥", "🟩"]
    # [
    #   [0, 1],
    #   [1, 2],
    #   [2, 3],
    # ]

    for t in timeList[::-1]:
        if currCheck - t > 90:
            if not offline or not offline[-1][0] == currCheck:
                offline.append([t, currCheck])
            else:
                offline[-1][0] = t
        else:
            if not online or not online[-1][0] == currCheck:
                online.append([t, currCheck])
            else:
                online[-1][0] = t
        currCheck = float(t)

    online.reverse()
    offline.reverse()

    timeLine = sorted(online + offline, key=lambda x: x[0])
    startChar = True if timeLine[0] == online[0] else False

    totalTime = currTime - currCheck
    onlineTime = sum([x[1] - x[0] for x in online])
    offlineTime = sum([x[1] - x[0] for x in offline])
    uptime = onlineTime / totalTime * 100

    longestUp = max([x[1] - x[0] for x in online])

    minTimePeriod = totalTime / max(1, timelineSquares)
    for period in timeLine:
        timelineStr += timeChar[int(startChar)] * max(
            1, int((period[1] - period[0]) / minTimePeriod)
        )
        startChar = not startChar

    retStr += f"**Total Uptime:** {totalTime:.2f} seconds\n"
    retStr += f"**Online Uptime:** {onlineTime:.2f} seconds\n"
    retStr += f"**Offline Uptime:** {offlineTime:.2f} seconds\n"
    retStr += f"**Uptime:** {uptime:.2f}%\n"
    retStr += f"**Longest Online:** {longestUp:.2f} seconds\n"
    retStr += (
        f"**Timeline:** {len(timelineStr)} squares\n"
        f"online periods: {len(online)}, offline periods: {len(offline)}\n"
        f"{fixStrLineLenTen(timelineStr)} "
    )

    return retStr


def fixStrLineLenTen(str: str):
    return re.sub(r"(.{10})(?!$)", r"\g<1>\n", str)
