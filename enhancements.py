# enhancements.py

import functools
import os

from power import (patList, power, powerTypes, rankColour, remList,
                   restrictedList)

DEBUG = 0
TEST = 0

if DEBUG:
    print("{} DEBUG TRUE".format(os.path.basename(__file__)))
#if DEBUG: print("".format())
if TEST:
    print("{} TEST TRUE".format(os.path.basename(__file__)))
#if TEST: print("".format())


# count number of unique strings in nested list and return count and unnested set
# TODO rewrite messy implementation ?and? every call of this function
def eleCountUniStr(list):
    uniList = []

    for ele in list:
        if DEBUG:
            print('FuncEleCountUniStr - ' + 'element is: ' + str(ele))

        if type(ele) == type([]):
            if not ele == []:
                if DEBUG:
                    print('FuncEleCountUniStr - ' + "RECURSE HERE")

                rec = eleCountUniStr(ele)
                if DEBUG:
                    print('FuncEleCountUniStr - ' + str(rec))

                for uni in rec[1]:
                    if DEBUG:
                        print('FuncEleCountUniStr - ' +
                              'Unique req list: ' + str(uni))

                    if uni not in uniList:
                        uniList.append(uni)
        else:
            if DEBUG:
                print('FuncEleCountUniStr - ' +
                      'Add count with string: ' + str(ele))

            if ele not in uniList:
                uniList.append(ele)

    if DEBUG:
        print('FuncEleCountUniStr - ' + 'returns cost: ' +
              str(len(uniList)) + ' and list: ' + str(uniList))
    return len(uniList), uniList


# calculate number of prerequisites +1 to get cost of enhancement
def cost(inName, inDict=power):
    required = []

    if DEBUG:
        print('FuncCost - ' + str(inName) +
              ' has requisites: ' + str(inDict[inName]['Prereq']))

    # for each prereq given enhancement has
    for req in inDict[inName]['Prereq']:
        # check for restriced enhancement, as those are not counted
        if req not in required:
            if DEBUG:
                print('FuncCost - ' + str(req) +
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
    if DEBUG:
        print('ans before restricted list = {}'.format(ans))

    # total cost of given enhancement
    ansTot = ans[0]
    if DEBUG:
        print('FuncCost - ' + str(ans))
    # enhancement cost = ansTot+1
    # unique prereq string = ans[1]
    return ansTot + 1, ans[1], required


# function to remove lower ranked enhancements from the list
def trim(pList, inDict=power):
    if DEBUG:
        print("funcTrim - " + "Start of function")
    tierDict = {}
    trimList = []
    if DEBUG:
        print("funcTrim - " + "plist = {}".format(pList))

    # iterate thorugh list of given enhancements
    for pow in pList:
        # fetch enhancement attrs
        powRank = [inDict[x]['Rank']
                   for x in inDict.keys() if inDict[x]['Name'] == pow][0]
        powType = [inDict[x]['Type']
                   for x in inDict.keys() if inDict[x]['Name'] == pow][0]
        if DEBUG:
            print("Enhancement: {}, Type: {}, Rank: {}".format(
                pow, powType, powRank))

        # if enhancement not already counted, add it to dictionary
        if not powType in tierDict.keys():
            tierDict[powType] = powRank
            if DEBUG:
                print("funcTrim - " +
                      "{} of rank {} added to dict".format(powType, powRank))

        # else if enhancment greater in rank than already counted enhancement, edit dictionary
        elif powRank > tierDict[powType]:
            if DEBUG:
                print("funcTrim - " + "{} of rank {} increased to {}".format(powType,
                      tierDict[powType], powRank))
            tierDict[powType] = powRank

    # add key value pairs in dictionary to a list of lists
    for key, val in tierDict.items():
        trimList.append([val, key])

    # return sorted trimmed list of highest ranked enhancements, descending
    if DEBUG:
        print("funcTrim - " +
              "dict tierDict: {}\n\ttrimList: {}".format(tierDict, trimList))
    return sorted(trimList, reverse=True, key=lambda x: x[0])


# function to turn given list of [rank, enhancment] into str for discord message
def reqEnd(endList):
    if DEBUG:
        print("funcReqEnd - " + "{}".format(endList))

    # check for no prereqs
    if len(endList[1]) == 0:
        reqStr = 'Which has no prerequisites.'

    # otherwise add prereqs to message
    else:
        if DEBUG:
            print("funcReqEnd - " + "{}".format(endList[1]))
        reqStr = 'Which requires at minimum:\n\n'
        for req in endList[1]:
            reqName = power[req[1][:3].lower() + str(req[0])]['Name']
            reqStr += '{}\n'.format(reqName)
    if DEBUG:
        print("funcReqEnd - " + "End of function")

    # return message
    return reqStr