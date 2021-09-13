# enhancments.py

DEBUG = 0
TEST = 1

import functools
from power import power

def eleCountUniStr(list, uniList = []):
    count = 0

    for ele in list:
        if DEBUG: print('element is:' + str(ele))
        if type(ele) == type([]):
            if DEBUG: print("RECURSE HERE")
            rec = eleCountUniStr(ele)
            if DEBUG: print(rec)
            count += rec[0]
            for uni in rec[1]:
                if DEBUG: print(uni)
                if uni not in uniList:
                    uniList.append(uni)
        else:
            if DEBUG: print('Add count with: ' + str(ele))
            if ele not in uniList:
                uniList.append(ele)
            count += 1
        if len(uniList) < count:
            count = len(uniList)
    return count, uniList

def cost(inName, inDict):
    required = []

    if DEBUG : print(inName + ' has requisites: ' + str(inDict[inName]['Prereq']))

    for req in inDict[inName]['Prereq']:
        if req not in required:
            if DEBUG: print(req + ' requisite has name: ' + inDict[req]['Name'])
            required.append(inDict[req]['Name'])
            subReq = cost(req, inDict)[0]
            if subReq:
                required.append(subReq)

    return required, eleCountUniStr(required)

def testCost(testPower, dictlist):
    costReq = cost(testPower, dictlist)
    print(testPower + ' of name: "' + dictlist[testPower]['Name'] + '" costs: ' + str(costReq[1][0]+1) + ' and has these prerequisites: ' +str(sorted(costReq[1][1])))

#if TEST: testCost('regen4', power)
#if TEST: testCost('regen7', power)
#if TEST: testCost('regen10', power)
if TEST: testCost('touch10', power)
if TEST:
    basic = cost('regen10', power)
    print(basic[0] == basic[1][1])
