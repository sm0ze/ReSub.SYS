# sharedFuncs.py

import math
import time
import typing

import discord
from discord.ext import commands
from discord.ext.commands.converter import MemberConverter
from sqlitedict import SqliteDict

import log
from power import leader, power
from sharedVars import HOSTNAME, SAVEFILE, STARTCHANNEL, SUPEROLE

logP = log.get_logger(__name__)

STRCHNL = None


# count number of unique strings in nested list
# and return count and unnested set
# TODO rewrite messy implementation ?and? every call of this function
def eleCountUniStr(varList, reqursion: bool = False):
    uniList = []
    if not reqursion:
        logP.debug("List of {} elements to make unique".format(len(varList)))
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
        logP.debug("List of {} elements to return".format(len(uniList)))
    return len(uniList), uniList


# calculate number of prerequisites +1 to get cost of enhancement
def cost(inName: str, inDict: dict = power):
    required = []

    logP.debug(
        "{} has requisites: {}".format(inName, inDict[inName]["Prereq"])
    )

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
    logP.debug("ans before restricted list length: {}".format(len(ans)))

    # total cost of given enhancement
    ansTot = ans[0]
    # enhancement cost = ansTot+1
    # unique prereq string = ans[1]
    return ansTot + 1, ans[1], required


# function to remove lower ranked enhancements from the list
def trim(pList, inDict=power):
    logP.debug("Start of trim function")
    tierDict = {}
    trimList = []
    logP.debug("list of length {} to trim".format(len(pList)))

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
        logP.debug(
            "Enhancement: {}, Type: {}, Rank: {}".format(pow, powType, powRank)
        )

        # if enhancement not already counted, add it to dictionary
        if powType not in tierDict.keys():
            tierDict[powType] = powRank
            logP.debug("{} of rank {} added to dict".format(powType, powRank))

        # else if enhancment greater in rank than already counted enhancement
        # edit dictionary
        elif powRank > tierDict[powType]:
            logP.debug(
                "{} of rank {} increased to {}".format(
                    powType, tierDict[powType], powRank
                )
            )
            tierDict[powType] = powRank

    # add key value pairs in dictionary to a list of lists
    for key, val in tierDict.items():
        trimList.append([val, key])

    # return sorted trimmed list of highest ranked enhancements, descending
    logP.debug("dict tierDict: {}".format(tierDict))
    logP.debug("trimList: {}".format(trimList))
    return sorted(trimList, reverse=True, key=lambda x: x[0])


# function to turn given list of [rank, enhancment]
# into str for discord message
def reqEnd(endList):
    logP.debug("{}".format(endList))

    # check for no prereqs
    if len(endList[1]) == 0:
        reqStr = "Build has no prerequisites."

    # otherwise add prereqs to message
    else:
        logP.debug("{}".format(endList[1]))
        reqStr = ""
        for req in endList[1]:
            reqName = power[toType(req[1]) + str(req[0])]["Name"]
            reqStr += "{}\n".format(reqName)

    # return message
    return reqStr


def toType(role: str):
    thing = [x for x in leader.keys() if role == leader[x]][0]
    logP.debug("Convert: {}, to: {}".format(role, thing))
    return thing


# from shorthand enhancement list return cost of build,
# role names and prerequisite roles
def funcBuild(
    buildList: list[str],
) -> tuple[int, list[str], list]:
    reqList = []
    nameList = []
    logP.debug("Build command buildList has length: {}".format(len(buildList)))

    # iterate through shorthand enhancements
    for item in buildList:
        logP.debug("Build command item: {}".format(item))
        # fetch enhancement prereqs and cost
        temCost = cost(item)
        logP.debug("Build command prereq cost length: {}".format(len(temCost)))

        # add this enhancement's prereqs to list
        reqList.append(temCost[2])

        # fetch full name for enhancement from shorthand
        tempName = power[item]["Name"]

        # add enhancement full name to lists
        reqList.append(tempName)
        nameList.append(tempName)
    logP.debug("Build command reqList is of length: {}".format(len(reqList)))

    # restrict nested prereq list to a set of prereqs
    temp = eleCountUniStr(reqList)

    # fetch highest ranked prereqs of each type in list
    reqList = trim([x for x in temp[1]])
    logP.debug("reqList len = {}".format(len(reqList)))

    # sum cost of build from prereqs
    costTot = 0
    for group in reqList:
        costTot += group[0]

    logP.debug("Total cost of build is: {}".format(costTot))
    # return cost of build, role names and prerequisite roles
    return costTot, nameList, reqList


# function to grab number of enhancement points
# spent by each user in given list
def spent(
    memList: list[discord.Member],
) -> list[list[discord.Member, int, list[str]]]:
    retList = []
    logP.debug("memList is: {}".format(memList))

    # iterate thorugh given list of users
    for peep in memList:
        supeRoles = []
        logP.debug("current user is: {}".format(peep))
        logP.debug("current user role list length: {}".format(len(peep.roles)))

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
        logP.debug("Supe roles: {}".format(supeRoles))

        # fetch point cost (including prereqs) of enhancements
        if supeRoles:
            pointCount = funcBuild(supeRoles)[0]
        else:
            pointCount = funcBuild([])[0]

        # add (user, total build cost, enhancmeent role names)
        # to list to return
        retList.append([peep, pointCount, supeRoles])

    logP.debug("retlist is: {}".format(retList))
    return retList


async def dupeError(
    mes: discord.Embed,
    ctx: commands.Context,
    channel: typing.Union[discord.TextChannel, discord.Thread],
):
    author = nON(ctx.author)
    autID = ctx.author.id
    currTime = time.localtime()
    currTimeStr = "{0:04d}.{1:02d}.{2:02d}_{3:02d}.{4:02d}.{5:02d}".format(
        currTime.tm_year,
        currTime.tm_mon,
        currTime.tm_mday,
        currTime.tm_hour,
        currTime.tm_min,
        currTime.tm_sec,
    )

    errMes = "At {}, {} ({}) produced this error on {}: ".format(
        currTimeStr, author, autID, HOSTNAME
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
    iterList = [x for y in bot.guilds for x in getattr(y, "{}s".format(attr))]
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
            "searching for {} in list of {} length or other"
            " list of length {} = {}"
        ).format(id, len(iterList), len(otherOpt), sendLoc)
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

    # return: mentioned users || named users || message author
    return grabList


def save(key: int, value: dict, cache_file=SAVEFILE):
    try:
        with SqliteDict(cache_file) as mydict:
            mydict[key] = value  # Using dict[key] to store
            mydict.commit()  # Need to commit() to actually flush the data
        logP.debug("saved {} of length: {}".format(key, len(value)))
    except Exception as ex:
        logP.warning(["Error during storing data (Possibly unsupported):", ex])


def load(key: int, cache_file=SAVEFILE) -> dict:
    try:
        with SqliteDict(cache_file) as mydict:
            # No need to use commit(), since we are only loading data!
            value = mydict[key]
        logP.debug("Loaded with key {} length: {}".format(key, len(value)))
        return value
    except Exception as ex:
        logP.warning(["Error during loading data:", ex])


def lvlEqu(givVar: float = 0, inv=0) -> float:
    if inv:
        calVar = (20 * math.pow(givVar, 2)) / 1.25
        logP.debug(
            "{:0.2g} GDV is equivalent to {:,} XP".format(givVar, calVar)
        )
    else:
        calVar = math.sqrt((1.25 * givVar) / 20)
        logP.debug(
            "{:,} XP is equivalent to {:0.2g} GDV".format(givVar, calVar)
        )
    return round(calVar, 2)


def aOrAn(inp: str):
    logP.debug(["input is: ", inp])
    ret = "A"
    if inp[0].lower() in "aeiou":
        ret = "An"
    logP.debug(["ret: ", ret])
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
