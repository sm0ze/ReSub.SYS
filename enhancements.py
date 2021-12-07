# enhancements.py
import time
import typing
import discord
from discord.ext import commands
from power import power, leader

from BossSystemExecutable import HOSTNAME, STARTCHANNEL, nON

DEBUG = 0


def debug(*args):
    if DEBUG:
        print(*args)


# count number of unique strings in nested list
# and return count and unnested set
# TODO rewrite messy implementation ?and? every call of this function
def eleCountUniStr(varList):
    uniList = []

    for ele in varList:
        debug("FuncEleCountUniStr - " + "element is: " + str(ele))
        if isinstance(ele, list):
            if ele:
                debug("FuncEleCountUniStr - " + "RECURSE HERE")

                rec = eleCountUniStr(ele)
                debug("FuncEleCountUniStr - " + str(rec))

                for uni in rec[1]:
                    debug(
                        "FuncEleCountUniStr - "
                        + "Unique req list: "
                        + str(uni)
                    )

                    if uni not in uniList:
                        uniList.append(uni)
        else:
            debug(
                "FuncEleCountUniStr - " + "Add count with string: " + str(ele)
            )

            if ele not in uniList:
                uniList.append(ele)

    debug(
        "FuncEleCountUniStr - "
        + "returns cost: "
        + str(len(uniList))
        + " and list: "
        + str(uniList)
    )
    return len(uniList), uniList


# calculate number of prerequisites +1 to get cost of enhancement
def cost(inName: str, inDict: dict = power):
    required = []

    debug(
        "FuncCost - "
        + str(inName)
        + " has requisites: "
        + str(inDict[inName]["Prereq"])
    )

    # for each prereq given enhancement has
    for req in inDict[inName]["Prereq"]:
        # check for restriced enhancement, as those are not counted
        if req not in required:
            debug(
                "FuncCost - "
                + str(req)
                + " requisite has name: "
                + str(inDict[req]["Name"])
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
    debug("ans before restricted list = {}".format(ans))

    # total cost of given enhancement
    ansTot = ans[0]
    debug("FuncCost - " + str(ans))
    # enhancement cost = ansTot+1
    # unique prereq string = ans[1]
    return ansTot + 1, ans[1], required


# function to remove lower ranked enhancements from the list
def trim(pList, inDict=power):
    debug("funcTrim - " + "Start of function")
    tierDict = {}
    trimList = []
    debug("funcTrim - " + "plist = {}".format(pList))

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
        debug(
            "Enhancement: {}, Type: {}, Rank: {}".format(pow, powType, powRank)
        )

        # if enhancement not already counted, add it to dictionary
        if powType not in tierDict.keys():
            tierDict[powType] = powRank
            debug(
                "funcTrim - "
                + "{} of rank {} added to dict".format(powType, powRank)
            )

        # else if enhancment greater in rank than already counted enhancement
        # edit dictionary
        elif powRank > tierDict[powType]:
            debug(
                "funcTrim - "
                + "{} of rank {} increased to {}".format(
                    powType, tierDict[powType], powRank
                )
            )
            tierDict[powType] = powRank

    # add key value pairs in dictionary to a list of lists
    for key, val in tierDict.items():
        trimList.append([val, key])

    # return sorted trimmed list of highest ranked enhancements, descending
    debug(
        "funcTrim - "
        + "dict tierDict: {}\n\ttrimList: {}".format(tierDict, trimList)
    )
    return sorted(trimList, reverse=True, key=lambda x: x[0])


# function to turn given list of [rank, enhancment]
# into str for discord message
def reqEnd(endList):
    debug("funcReqEnd - " + "{}".format(endList))

    # check for no prereqs
    if len(endList[1]) == 0:
        reqStr = "Build has no prerequisites."

    # otherwise add prereqs to message
    else:
        debug("funcReqEnd - " + "{}".format(endList[1]))
        reqStr = ""
        for req in endList[1]:
            reqName = power[toType(req[1]) + str(req[0])]["Name"]
            reqStr += "{}\n".format(reqName)
    debug("funcReqEnd - " + "End of function")

    # return message
    return reqStr


def toType(role: str):
    debug(role)
    thing = [x for x in leader.keys() if role == leader[x]][0]
    debug(thing)
    return thing


# from shorthand enhancement list return cost of build,
# role names and prerequisite roles
def funcBuild(
    buildList: list[str],
) -> tuple[int, list[str], list]:
    debug("Start funcBuild")
    reqList = []
    nameList = []
    debug("Build command buildList = {}".format(buildList))

    # iterate through shorthand enhancements
    for item in buildList:
        debug("Build command item = {}".format(item))
        # fetch enhancement prereqs and cost
        temCost = cost(item)
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
    temp = eleCountUniStr(reqList)
    debug("temp = {}".format(temp))

    # fetch highest ranked prereqs of each type in list
    reqList = trim([x for x in temp[1]])
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
def spent(
    memList: list[discord.Member],
) -> list[list[discord.Member, int, list[str]]]:
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


async def dupeError(
    mes,
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
    if isinstance(channel, discord.Thread):
        if channel.archived:
            await channel.edit(archived=0)

    await channel.send(
        "At {}, {}({}) produced this error on {}:".format(
            currTimeStr, author, autID, HOSTNAME
        )
    )
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

    debug(
        "searching for {} in {} or {} = {}".format(
            id, iterList, otherOpt, sendLoc
        )
    )

    if isinstance(sendLoc, list):
        if sendLoc:
            sendLoc = sendLoc[0]
    return sendLoc
