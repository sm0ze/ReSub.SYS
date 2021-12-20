# py

import math
import random
import time
import typing

import discord
import tatsu
from discord.ext import commands
from discord.ext.commands.converter import MemberConverter
from discord.utils import get
from mee6_py_api import API
from sqlitedict import SqliteDict

import log
from sharedDicts import (
    leader,
    masterEhnDict,
    rankColour,
    remList,
    restrictedList,
    cmdInf,
)
from sharedVars import (
    GEMDIFF,
    HOSTNAME,
    SAVEFILE,
    STARTCHANNEL,
    SUPEROLE,
    TATSU,
)

logP = log.get_logger(__name__)

STRCHNL = None

SLEEP = False


# count number of unique strings in nested list
# and return count and unnested set
# TODO rewrite messy implementation ?and? every call of this function
def eleCountUniStr(varList, reqursion: bool = False):
    uniList = []
    if not reqursion:
        logP.debug(f"List of {len(varList)} elements to make unique")
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
    if not reqursion:
        logP.debug(f"List of {len(uniList)} elements to return")
    return len(uniList), uniList


# calculate number of prerequisites +1 to get cost of enhancement
def cost(inName: str, inDict: dict = masterEhnDict):
    required = []

    logP.debug(f"{inName} has requisites: {inDict[inName]['Prereq']}")

    # for each prereq given enhancement has
    for req in inDict[inName]["Prereq"]:
        # check for restricted enhancement, as those are not counted
        if req not in required:
            logP.debug(
                str(req) + " requisite has name: " + str(inDict[req]["Name"])
            )

            # save prereq full name for later
            required.append(inDict[req]["Name"])

            # check for prereq' prereqs
            subReq = cost(req, inDict)[2]

            # save prereq' prereqs
            if subReq:
                required.append(subReq)

    # trim list of prereqs to remove duplicates
    ans = eleCountUniStr(required)
    logP.debug(f"ans before restricted list length: {len(ans)}")

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
        logP.debug(f"Enhancement: {pow}, Type: {powType}, Rank: {powRank}")

        # if enhancement not already counted, add it to dictionary
        if powType not in tierDict.keys():
            tierDict[powType] = powRank
            logP.debug(f"{powType} of rank {powRank} added to dict")

        # else if enhancment greater in rank than already counted enhancement
        # edit dictionary
        elif powRank > tierDict[powType]:
            logP.debug(
                f"{powType} of rank {tierDict[powType]} increased to {powRank}"
            )
            tierDict[powType] = powRank

    # add key value pairs in dictionary to a list of lists
    for key, val in tierDict.items():
        trimList.append([val, key])

    # return sorted trimmed list of highest ranked enhancements, descending
    logP.debug(f"dict tierDict: {tierDict}")
    logP.debug(f"trimList: {trimList}")
    return sorted(trimList, reverse=True, key=lambda x: x[0])


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
        logP.debug(f"Build command item: {item}")
        # fetch enhancement prereqs and cost
        temCost = cost(item)
        logP.debug(f"Build command prereq cost length: {len(temCost)}")

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
    return costTot, nameList, reqList


# function to grab number of enhancement points
# spent by each user in given list
def spent(
    memList: list[discord.Member],
) -> list[list[discord.Member, int, list[str]]]:
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
        retList.append([peep, pointCount, supeRoles])

    logP.debug(f"retlist is: {retList}")
    return retList


async def dupeError(
    mes: discord.Embed,
    ctx: commands.Context,
    channel: typing.Union[discord.TextChannel, discord.Thread],
):
    author = nON(ctx.author)
    autID = ctx.author.id
    currTime = time.localtime()
    currTimeStr = (
        f"{currTime.tm_year:04d}.{currTime.tm_mon:02d}."
        f"{currTime.tm_mday:02d}_{currTime.tm_hour:02d}."
        f"{currTime.tm_min:02d}.{currTime.tm_sec:02d}"
    )

    errMes = (
        f"At {currTimeStr}, {author} ({autID}) "
        f"produced this error on {HOSTNAME}: "
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
            if int(x.id) == int(STARTCHANNEL)
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


# dirty little function to avoid 'if user.nick else user.name'
def nON(user: discord.Member) -> str:
    if user.nick:
        return user.nick
    else:
        return user.name


async def dupeMes(bot, channel=None, mes: str = None):
    global STRCHNL
    if not STRCHNL:
        STRCHNL = await getSendLoc(STARTCHANNEL, bot, "channel")
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
    self, ctx: commands.Context, memList: str = ""
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
            logP.debug("trying to find: {posMem}")
            grabMem = await MemberConverter().convert(ctx, posMem)
            if grabMem:
                grabList.append(grabMem)

    # else use the command caller themself
    else:
        grabList.append(ctx.message.author)
        logP.debug(f"Author is: {grabList}")
    logP.debug(f"fixed grablist: {grabList}")

    # return: mentioned users || named users || message author
    return grabList


def save(key: int, value: dict, cache_file=SAVEFILE):
    try:
        with SqliteDict(cache_file) as mydict:
            mydict[key] = value  # Using dict[key] to store
            mydict.commit()  # Need to commit() to actually flush the data
        logP.debug(f"saved {key} of length: {len(value)}")
    except Exception as ex:
        logP.warning(["Error during storing data (Possibly unsupported):", ex])


def load(key: int, cache_file=SAVEFILE) -> dict:
    try:
        with SqliteDict(cache_file) as mydict:
            # No need to use commit(), since we are only loading data!
            value = mydict[key]
        logP.debug(f"Loaded with key {key} length: {len(value)}")
        return value
    except Exception as ex:
        logP.warning(["Error during loading data:", ex])


def lvlEqu(givVar: float = 0, inv=0) -> float:
    if inv:
        calVar = (20 * math.pow(givVar, 2)) / 1.25
        logP.debug(f"{givVar:0.2g} GDV is equivalent to {calVar:,} XP")
    else:
        calVar = math.sqrt((1.25 * givVar) / 20)
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
    for peep in ctx.message.author.guild.members:
        if SUPEROLE not in [x.name for x in peep.roles]:
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
    mes = discord.Embed(title="Cutting roles")

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
        sendMes += f"{nON(peep)} has been cut down to size!"
        mes.add_field(name=f"{nON(peep)}", value=sendMes)
    await ctx.send(embed=mes)
    return


async def toAdd(ctx: commands.Context, user: discord.Member, givenBuild: list):
    # the guild role names grabbed from shorthand to add to user
    addList = [
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
                f"Cannot add enhancements as {nON(user)} "
                f"does not have {cantAdd}"
            )
        )
        return

    # guild role list with name and id attributes
    guildRoles = await user.guild.fetch_roles()

    # iterate through roles to add to user
    sendMes = ""
    for role in addList:
        logP.debug(f"Trying to add role: {role}")

        # check for if user has enhancement role already
        roleId = get(guildRoles, name=role)
        if roleId in user.roles:
            logP.debug(f"{nON(user)} already has the role {roleId}")
            continue

        # role names to add will have format "Rank *Rank* *Type*"
        roleRank = role.split()[1]
        logP.debug(f"{roleId}, {roleRank}")

        # check for role already in guild role list, create it if required
        if not roleId:
            colour = rankColour[int(roleRank)]
            logP.debug(f"colour for rank {roleRank} is: {colour}")
            roleId = await user.guild.create_role(name=role, color=colour)

        # add requested role to user
        await user.add_roles(roleId)
        sendMes += f"{nON(user)} now has {roleId}!\n"

    # trim the user of excess roles
    # debug("TO CUT")
    # await cut(ctx, [user])
    if not sendMes:
        await ctx.send(("You cannot add enhancements with that selection"))
    else:
        await ctx.send(sendMes)


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
        pointTot = await countOf(group[0])

        if hideFull:
            if group[1] >= pointTot[0]:
                skipped += 1
                continue
        await ctx.send(
            (
                f"{nON(group[0])} has {group[1]} "
                f"enhancement{pluralInt(group[1])} active out "
                f"of {pointTot[0]} "
                f"enhancement{pluralInt(pointTot[0])} "
                "available."
            )
        )
    if skipped:
        await ctx.send(
            f"{len(supeUsers)} members scanned. {skipped} members skipped."
        )
    if len(supeUsers) > 10:
        await ctx.send("Point scanning finished.")


# function to get specified user's enhancement points
async def count(
    peepList: typing.Union[list[discord.Member], discord.Member],
    tatFrc: int = 0,
) -> tuple[int, float, float, list[int, int, float], float]:
    tat = tatsu.wrapper

    if isinstance(peepList, discord.Member):
        peepList = [peepList]

    try:
        pickle_file = load(peepList[0].guild.id)
    except Exception as e:
        print(e)
        logP.debug("Pickle file load failed")
        pickle_file = {}

    for peep in peepList:
        if tatFrc:
            MEE6xp = await API(peep.guild.id).levels.get_user_xp(peep.id)
            TATSUmem = await tat.ApiWrapper(key=TATSU).get_profile(peep.id)
        else:
            TATSUmem = None
            MEE6xp = int(0)

        if pickle_file and peep.id in pickle_file.keys():
            ReSubXP = float(pickle_file[peep.id]["invXP"][-1])
        else:
            ReSubXP = float(0)

        if hasattr(TATSUmem, "xp"):
            TATSUxp = int(TATSUmem.xp)
            if not TATSUxp:
                TATSUxp = int(0)
        else:
            TATSUxp = int(0)

        if not MEE6xp:
            MEE6xp = int(0)
            if peep.id in pickle_file.keys():
                if pickle_file[peep.id]["invXP"][0]:
                    MEE6xp = int(pickle_file[peep.id]["invXP"][0])

        if not TATSUxp:
            TATSUxp = int(0)
            if peep.id in pickle_file.keys():
                if pickle_file[peep.id]["invXP"][0]:
                    TATSUxp = int(pickle_file[peep.id]["invXP"][1])

        if MEE6xp or TATSUxp or ReSubXP:
            totXP = ReSubXP + MEE6xp + (TATSUxp / 2)
        else:
            totXP = float(0)
        if nON(peep) == "Geminel":
            totXP = round(totXP * float(GEMDIFF), 3)

        gdv = lvlEqu(totXP)

        enhP = math.floor(gdv / 5) + 1
        lastTaskTime = pickle_file[peep.id].get("lastTaskTime")
        logP.debug(
            (
                f"{nON(peep)}-"
                f" ReSubXP: {ReSubXP},"
                f" TATSUxp: {TATSUxp},"
                f" MEE6xp: {MEE6xp},"
                f" totXP: {totXP},"
                f" gdv: {gdv},"
                f" enhP: {enhP}"
                f" lastTaskTime: {lastTaskTime}"
            )
        )
        pickle_file[peep.id] = {
            "Name": peep.name,
            "enhP": enhP,
            "gdv": gdv,
            "totXP": totXP,
            "invXP": [MEE6xp, TATSUxp, ReSubXP],
            "lastTaskTime": lastTaskTime,
        }
    save(peepList[0].guild.id, pickle_file)

    return enhP, gdv, totXP, [MEE6xp, TATSUxp, ReSubXP], lastTaskTime


async def countOf(
    peep: discord.Member,
) -> tuple[int, float, float, list[int, int, float], float]:
    try:
        valDict = load(peep.guild.id)
        logP.debug("valDict loaded")
        shrt = valDict[peep.id]
        logP.debug(f"shrt: {shrt}")

        invXP = shrt.get("invXP")

        return (
            int(shrt.get("enhP")),
            float(shrt.get("gdv")),
            float(shrt.get("totXP")),
            invXP,
            float(shrt.get("lastTaskTime")),
        )
    except Exception as e:
        logP.warning(e)
        logP.debug("End countOf - fail load")
        return await count(peep)


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


async def finPatrol(activeRole: discord.Role, activeTimeMax: int):
    notActive = []
    memberDict = load(activeRole.guild.id)
    currTime = time.time()
    patrolStart = 0
    for key, val in memberDict.items():
        logP.debug(val)
        lastPatrolStart = val.get("lastTaskTime")

        if lastPatrolStart:
            patrolStart += 1
            lastPatrolStart = int(round(currTime - lastPatrolStart))
            logP.debug(f"Time since last patrol start is: {lastPatrolStart}")
            if lastPatrolStart > activeTimeMax:
                member = get(activeRole.guild.members, id=int(key))
                (notActive.append(member) if member else None)

    membersFinishingPatrol = set(activeRole.members) & set(notActive)

    perPatrolMes = (
        f"{patrolStart}/{len(memberDict)} {SUPEROLE}'s have started a patrol "
        f"at some point in time and {len(membersFinishingPatrol)} are "
        "currently finishing their patrol. "
        f"{len(activeRole.members)-len(membersFinishingPatrol)} are out on a "
        f"patrol now. There are {len(notActive)} Patrol Veterans either "
        "starting to or already resting."
    )

    logP.debug(perPatrolMes)

    for peep in membersFinishingPatrol:
        await peep.remove_roles(activeRole)
