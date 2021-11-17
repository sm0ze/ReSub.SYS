# enhancements.py

import functools
import os

from power import *

DEBUG = 0
TEST = 0


def debug(*args):
    if DEBUG:
        print(*args)


debug("{} DEBUG TRUE".format(os.path.basename(__file__)))


if TEST:
    print("{} TEST TRUE".format(os.path.basename(__file__)))
#if TEST: print("".format())


# count number of unique strings in nested list and return count and unnested set
# TODO rewrite messy implementation ?and? every call of this function
def eleCountUniStr(list):
    uniList = []

    for ele in list:
        debug('FuncEleCountUniStr - ' + 'element is: ' + str(ele))

        if type(ele) == type([]):
            if not ele == []:
                debug('FuncEleCountUniStr - ' + "RECURSE HERE")

                rec = eleCountUniStr(ele)
                debug('FuncEleCountUniStr - ' + str(rec))

                for uni in rec[1]:
                    debug('FuncEleCountUniStr - ' +
                          'Unique req list: ' + str(uni))

                    if uni not in uniList:
                        uniList.append(uni)
        else:
            debug('FuncEleCountUniStr - ' +
                  'Add count with string: ' + str(ele))

            if ele not in uniList:
                uniList.append(ele)

    debug('FuncEleCountUniStr - ' + 'returns cost: ' +
          str(len(uniList)) + ' and list: ' + str(uniList))
    return len(uniList), uniList


# calculate number of prerequisites +1 to get cost of enhancement
def cost(inName, inDict=power):
    required = []

    debug('FuncCost - ' + str(inName) +
          ' has requisites: ' + str(inDict[inName]['Prereq']))

    # for each prereq given enhancement has
    for req in inDict[inName]['Prereq']:
        # check for restriced enhancement, as those are not counted
        if req not in required:
            debug('FuncCost - ' + str(req) +
                  ' requisite has name: ' + str(inDict[req]['Name']))

            # save prereq full name for later
            required.append(inDict[req]['Name'])

            # check for prereq' prereqs
            subReq = cost(req, inDict)[2]

            # save prereq' prereqs
            if subReq:
                required.append(subReq)

    # trim list of prereqs to remove duplicates
    ans = eleCountUniStr(required)
    debug('ans before restricted list = {}'.format(ans))

    # total cost of given enhancement
    ansTot = ans[0]
    debug('FuncCost - ' + str(ans))
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
        powRank = [inDict[x]['Rank']
                   for x in inDict.keys() if inDict[x]['Name'] == pow][0]
        powType = [inDict[x]['Type']
                   for x in inDict.keys() if inDict[x]['Name'] == pow][0]
        debug("Enhancement: {}, Type: {}, Rank: {}".format(
            pow, powType, powRank))

        # if enhancement not already counted, add it to dictionary
        if not powType in tierDict.keys():
            tierDict[powType] = powRank
            debug("funcTrim - " +
                  "{} of rank {} added to dict".format(powType, powRank))

        # else if enhancment greater in rank than already counted enhancement, edit dictionary
        elif powRank > tierDict[powType]:
            debug("funcTrim - " + "{} of rank {} increased to {}".format(powType,
                                                                         tierDict[powType], powRank))
            tierDict[powType] = powRank

    # add key value pairs in dictionary to a list of lists
    for key, val in tierDict.items():
        trimList.append([val, key])

    # return sorted trimmed list of highest ranked enhancements, descending
    debug("funcTrim - " +
          "dict tierDict: {}\n\ttrimList: {}".format(tierDict, trimList))
    return sorted(trimList, reverse=True, key=lambda x: x[0])


# function to turn given list of [rank, enhancment] into str for discord message
def reqEnd(endList):
    debug("funcReqEnd - " + "{}".format(endList))

    # check for no prereqs
    if len(endList[1]) == 0:
        reqStr = 'Build has no prerequisites.'

    # otherwise add prereqs to message
    else:
        debug("funcReqEnd - " + "{}".format(endList[1]))
        reqStr = ''
        for req in endList[1]:
            reqName = power[toType(req[1]) + str(req[0])]['Name']
            reqStr += '{}\n'.format(reqName)
    debug("funcReqEnd - " + "End of function")

    # return message
    return reqStr


def toType(role):
    debug(role)
    thing = [x for x in leader.keys() if role == leader[x]][0]
    debug(thing)
    return thing
