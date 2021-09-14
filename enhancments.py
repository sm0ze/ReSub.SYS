# enhancments.py

DEBUG = 0
TEST = 0

import functools
from power import power

def eleCountUniStr(list):
#count number of unique strings in nested list
    #count = 0
    uniList = []

    for ele in list:

        if DEBUG: print('FuncEleCountUniStr - ' + 'element is: ' + str(ele))

        if type(ele) == type([]):

            if not ele == []:
                if DEBUG: print('FuncEleCountUniStr - ' + "RECURSE HERE")
                rec = eleCountUniStr(ele)
                if DEBUG: print('FuncEleCountUniStr - ' + str(rec))
                #count += rec[0]

                for uni in rec[1]:

                    if DEBUG: print('FuncEleCountUniStr - ' + 'Unique req list: ' + str(uni))
                    if uni not in uniList:
                        uniList.append(uni)
                        #count += 1
        else:

            if DEBUG: print('FuncEleCountUniStr - ' + 'Add count with string: ' + str(ele))

            if ele not in uniList:

                uniList.append(ele)
                #count += 1

        #if len(uniList) < count:

        #    count = len(uniList)
    if DEBUG: print('FuncEleCountUniStr - ' + 'returns cost: ' + str(len(uniList)) +' and list:' + str(uniList))
    return len(uniList), uniList


def cost(inName, inDict=power):
#calculate number of prerequisites +1 to get cost of power in points

    required = []
    #required prerequisites

    if DEBUG : print('FuncCost - ' + str(inName) + ' has requisites: ' + str(inDict[inName]['Prereq']))

    for req in inDict[inName]['Prereq']:

        if req not in required:

            if DEBUG: print('FuncCost - ' + str(req) + ' requisite has name: ' + str(inDict[req]['Name']))
            required.append(inDict[req]['Name'])
            subReq = cost(req, inDict)[2]

            if subReq:

                required.append(subReq)
    ans = eleCountUniStr(required)
    if DEBUG: print('FuncCost - ' + str(ans))
    # enhancment cost = ans[0]+1
    # unique prereq string = ans[1]
    return ans[0]+1, ans[1], required


def testCost(testPower, dictlist):
#test function to ensure cost function is working
    costReq = cost(testPower, dictlist)
    print('FuncTestCost - ' + testPower + ' of name: "' + dictlist[testPower]['Name'] + '" costs: ' + str(costReq[0]) + ' and has these prerequisites: ' + str(sorted(costReq[1])))

#if TEST: testCost('regen4')
#if TEST: testCost('regen7')
#if TEST: testCost('regen10')
if TEST: testCost('touch10')
if TEST:
    basic = cost('regen10', power)
    print(basic[0] == basic[1][1])
