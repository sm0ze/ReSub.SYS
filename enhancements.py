# enhancements.py

from power import power, powerTypes, rankColour, patList, listEnhancements, restrictedList
import functools
import os

DEBUG = 0
TEST = 0

if DEBUG:
    print("{} DEBUG TRUE".format(os.path.basename(__file__)))
#if DEBUG: print()
if TEST:
    print("{} TEST TRUE".format(os.path.basename(__file__)))
#if TEST: print()

LoE = listEnhancements()


def eleCountUniStr(list):
    # count number of unique strings in nested list
    #count = 0
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
                #count += rec[0]

                for uni in rec[1]:

                    if DEBUG:
                        print('FuncEleCountUniStr - ' +
                              'Unique req list: ' + str(uni))
                    if uni not in uniList:
                        uniList.append(uni)
                        #count += 1
        else:

            if DEBUG:
                print('FuncEleCountUniStr - ' +
                      'Add count with string: ' + str(ele))

            if ele not in uniList:

                uniList.append(ele)
                #count += 1

        # if len(uniList) < count:

        #    count = len(uniList)
    if DEBUG:
        print('FuncEleCountUniStr - ' + 'returns cost: ' +
              str(len(uniList)) + ' and list: ' + str(uniList))
    return len(uniList), uniList


def cost(inName, inDict=power):
    # calculate number of prerequisites +1 to get cost of power in points

    required = []
    # required prerequisites

    if DEBUG:
        print('FuncCost - ' + str(inName) +
              ' has requisites: ' + str(inDict[inName]['Prereq']))

    for req in inDict[inName]['Prereq']:

        if req not in required:

            if DEBUG:
                print('FuncCost - ' + str(req) +
                      ' requisite has name: ' + str(inDict[req]['Name']))
            required.append(inDict[req]['Name'])
            subReq = cost(req, inDict)[2]

            if subReq:

                required.append(subReq)
    ans = eleCountUniStr(required)
    if DEBUG:
        print('ans before restricted list = {}'.format(ans))
    """if ans[0]:
        if DEBUG: print("required = {}, restrictedList = {}".format(required, restrictedList))
        restrictedCount = [x for x in ans[1] if x in restrictedList]
        if DEBUG: print('restricted count = {}'.format(restrictedCount))
        ansTot = ans[0] - len(restrictedCount)
        if DEBUG: print('pre total cost of {} instead of {}'.format(ansTot, ans[0]))
    else:"""
    ansTot = ans[0]
    if DEBUG:
        print('FuncCost - ' + str(ans))
    # enhancement cost = ans[0]+1
    # unique prereq string = ans[1]
    return ansTot + 1, ans[1], required


def trim(pList, inDict=power):
    # function to remove lower ranked enhancements from the list
    if DEBUG:
        print("funcTrim - " + "Start of function")
    tierDict = {}
    trimList = []
    if DEBUG:
        print("funcTrim - " + "plist = {}".format(pList))
    for pow in pList:
        powRank = [inDict[x]['Rank']
                   for x in inDict.keys() if inDict[x]['Name'] == pow][0]
        powType = [inDict[x]['Type']
                   for x in inDict.keys() if inDict[x]['Name'] == pow][0]
        if DEBUG:
            print("Enhancement: {}, Type: {}, Rank: {}".format(
                pow, powType, powRank))
        if not powType in tierDict.keys():
            tierDict[powType] = powRank
            if DEBUG:
                print("funcTrim - " +
                      "{} of rank {} added to dict".format(powType, powRank))
        elif powRank > tierDict[powType]:
            if DEBUG:
                print("funcTrim - " + "{} of rank {} increased to {}".format(powType,
                      tierDict[powType], powRank))
            tierDict[powType] = powRank
    for key, val in tierDict.items():
        trimList.append([val, key])

    if DEBUG:
        print("funcTrim - " +
              "dict tierDict: {}\n\ttrimList: {}".format(tierDict, trimList))
    return sorted(trimList, reverse=True, key=lambda x: x[0])


def reqEnd(endList):
    if DEBUG:
        print("funcReqEnd - " + "{}".format(endList))
    if len(endList[1]) == 0:
        reqStr = 'Which has no prerequisites.'
    else:
        if DEBUG:
            print("funcReqEnd - " + "{}".format(endList[1]))
        reqStr = 'Which requires at minimum:\n\n'
        for req in endList[1]:
            reqName = power[req[1][:3].lower() + str(req[0])]['Name']
            reqStr += '{}\n'.format(reqName)
    if DEBUG:
        print("funcReqEnd - " + "End of function")
    return reqStr


def testCost(testPower, dictlist):
    # test function to ensure cost function is working
    costReq = cost(testPower, dictlist)
    print('FuncTestCost - ' + testPower + ' of name: "' + dictlist[testPower]['Name'] + '" costs: ' + str(
        costReq[0]) + ' and has these prerequisites: ' + str(sorted(costReq[1])))


if TEST:
    basic = cost('reg10')
    print("does required = unilist: " + str(basic[1] == basic[2]))
    print("{}".format(trim(basic[1])))
