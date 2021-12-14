# power.py
# this file is a dictionary and other lengthy constant variables dump

import pandas as pd
import log


logP = log.get_logger(__name__)

urltoAdd = (
    "https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet={}"
)

statsheetNom = [
    ["Requirements", "1JIJjDzFjtuIU2k0jk1aHdMr2oErD_ySoFm7-iFEBOV0"]
]
taskVar = {
    "taskOpt": [
        ["Minor", "Moderate", "Major", "Imperative"],
        [
            "1LfSqavVskaKWM0yhKO1ZyqU1154TuYwPzt_3eFZOymQ",
            "1ZS3or-b1uA0-Btv0oiZQkT7Nu12NMNkP-fRdE2dcHTw",
            "1TKeG8wNanj_tUfFgRVPj020cfY1F22e0Jn-lh345nXM",
            "1B3YIU6O6FuoUFl5snlMh8DF4OgbpYo4kxqv6YGXw_HY",
        ],
    ],
    "taskWeight": [60, 85, 95, 100],
}

rsltDict = {
    "Error": [0, 0.5],
    "sufficient": [0.5, 0.6],
    "good": [0.6, 0.7],
    "great": [0.7, 0.8],
    "spectacular": [0.8, 0.9],
    "superlative": [0.9, 1.0],
}
posTask = {
    "Minor": {
        "Worth": [200, 400],
        "Add": 0,
        "Aid": 0,
    },
    "Moderate": {
        "Worth": [400, 600],
        "Add": 1,
        "Aid": 0.5,
    },
    "Major": {
        "Worth": [600, 800],
        "Add": 3,
        "Aid": 0.5,
    },
    "Imperative": {
        "Worth": [800, 1000],
        "Add": -1,
        "Aid": 0.25,
    },
}

# removal emoji list
remList = [
    "( ╥﹏╥) ノシ",
    "(ᗒᗣᗕ)՞",
    "ʕ ಡ ﹏ ಡ ʔ",
    "●︿●",
    "(︶︹︺)",
    "(´°ω°)",
    "ू(ʚ̴̶̷́ .̠ ʚ̴̶̷̥̀ ू)",
    "( ◔ ʖ̯ ◔ )",
    "(ˊ̥̥̥̥̥ ³ ˋ̥̥̥̥̥)",
    "(¬▂¬)",
    "(ﾉ -益-)ﾉ︵ ┻━┻",
    "(╯°□°）╯",
]

moveOpt = {
    "physA": {
        "name": "Physical Attack",
        "desperate": 0,
        "type": "Attack",
        "moveStr": "Physical",
        "cost": 2,
        "reaction": "🗡️",
    },
    "mentA": {
        "name": "Mental Attack",
        "desperate": 0,
        "type": "Attack",
        "moveStr": "Mental",
        "cost": 2,
        "reaction": "😠",
    },
    "dPhysA": {
        "name": "Desperate Physical Attack",
        "desperate": 1,
        "type": "Attack",
        "moveStr": "Physical",
        "cost": 5,
        "reaction": "⚔️",
    },
    "dMentA": {
        "name": "Desperate Mental Attack",
        "desperate": 1,
        "type": "Attack",
        "moveStr": "Mental",
        "cost": 5,
        "reaction": "🤯",
    },
    "physD": {
        "name": "Physical Defense",
        "desperate": 0,
        "type": "Defend",
        "moveStr": "Physical",
        "cost": 0,
        "reaction": "🛡️",
    },
    "mentD": {
        "name": "Mental Defense",
        "desperate": 0,
        "type": "Defend",
        "moveStr": "Mental",
        "cost": 0,
        "reaction": "😎",
    },
    "focus": {
        "name": "Focus",
        "desperate": 0,
        "type": "Utility",
        "moveStr": "Focus",
        "cost": 1,
        "reaction": "😤",
    },
    "quit": {
        "name": "Retire",
        "desperate": 0,
        "type": "Quit",
        "moveStr": "MakeBot",
        "cost": 0,
        "reaction": "🎮",
    },
}


# list of roles that give user extra enhancement points, +1 for each match
patList = [
    "Supe",
    "Precoggnition",
    "Precoggnition+",
    "Precoggnition++",
    "Boss System",
    "System",
    "Major Task Tier",
    "Authors",
    "Ping Unto Me My Daily Quack",
]

# dictionary of the different types of enhancements and the total number of
# ranks available for each. * modifier for enhancements with extra restrictions
powerTypes = {
    "Strength": 10,
    "Speed": 10,
    "Endurance": 10,
    "Memory": 10,
    "Mental Celerity": 10,
    "Mental Clarity": 10,
    "Regeneration": 10,
    "Pain Tolerance": 10,
    "Invisibility": 10,
    "Vision": 10,
    "Aural Faculty": 10,
    "Olfactory Sense": 10,
    "Gustatory Ability": 10,
    "Tactile Reception": 10,
    "Proprioception": 10,
    "Omniscience*": 10,
    "4th Wall Breaker*": 10,
    "Intelligence*": 10,
}

leader = {
    "str": "Strength",
    "spe": "Speed",
    "end": "Endurance",
    "mem": "Memory",
    "cel": "Mental Celerity",
    "cla": "Mental Clarity",
    "reg": "Regeneration",
    "pai": "Pain Tolerance",
    "inv": "Invisibility",
    "vis": "Vision",
    "aur": "Aural Faculty",
    "olf": "Olfactory Sense",
    "gus": "Gustatory Ability",
    "tac": "Tactile Reception",
    "pro": "Proprioception",
    "omn": "Omniscience",
    "4th": "4th Wall Breaker",
    "int": "Intelligence",
    "sys": "System",
    "aut": "Authors",
}

# the different hexcodes for the colour of each role by rank
rankColour = {
    1: 0xFFFFFF,
    2: 0xCFCEEB,
    3: 0xAEADDF,
    4: 0x8C8BD8,
    5: 0x6C6BC7,
    6: 0x4C4AB9,
    7: 0x3B38B3,
    8: 0x2C29AA,
    9: 0x1B188D,
    10: 0x0A0863,
}

# restricted roles, should correspond with * moifiers in powerTypes
# and cannot be added by the bot
restrictedList = ["System", "Authors"]

freeRoles = ["Ping Unto Me My Daily Quack", "Supe"]


cmdInf = {}

power = {
    "sup0": {"Name": "Supe", "Type": "Supe", "Rank": 0, "Prereq": []},
    "sys0": {"Name": "System", "Type": "System", "Rank": 0, "Prereq": []},
    "aut0": {"Name": "Authors", "Type": "Authors", "Rank": 0, "Prereq": []},
}


def remove_values_from_list(the_list, val):
    return [value for value in the_list if str(value) != val]


logP.info("Starting csv download and input...")
sheet_names = [
    [taskVar["taskOpt"][0][x], taskVar["taskOpt"][1][x]]
    for x in range(0, len(taskVar["taskOpt"][0]))
]
for sheetL in sheet_names:
    urlToken = sheetL[1]
    sheet = sheetL[0]
    url = urltoAdd.format(urlToken, sheet)
    logP.debug("At URL: {}".format(url))
    try:
        frame = None
        frame = pd.read_csv(url)
    except Exception as e:
        print(e)
        continue

    for i in frame:
        if i.startswith("Unnamed"):
            continue
        currList = remove_values_from_list([x for x in frame[i]], "nan")
        posTask[sheet][i] = currList
        logP.debug(
            "{} list of {} is of length {}".format(sheet, i, len(currList))
        )

for statsheet in statsheetNom:
    statUrlID = statsheet[1]
    statsheetName = statsheet[0]
    statUrl = urltoAdd.format(statUrlID, statsheetName)

    logP.debug("At URL: {}".format(statUrl))
    try:
        frame = None
        frame = pd.read_csv(statUrl)
    except Exception as e:
        print(e)
        continue

    for tup in frame.itertuples():
        shrt = [x[0] for x in leader.items() if x[1] == tup.Role]
        if shrt:
            shrt = shrt[0]
        for i in range(1, 11):
            enhNum = str(shrt) + str(i)
            power[enhNum] = {
                "Name": "Rank {} {}".format(i, tup.Role),
                "Type": "{}".format(tup.Role),
                "Rank": i,
                "Prereq": [],
            }
            if power[enhNum]["Type"] == "Intelligence":
                power[enhNum]["Name"] += " (only for Systems)"
            if i > 1:
                power[enhNum]["Prereq"].append(str(shrt) + str(i - 1))
        for ite in tup._fields:
            if str(getattr(tup, ite)) == str("nan"):
                continue
            if str(ite).lower().startswith("three"):
                power[str(shrt) + str(4)]["Prereq"].append(
                    str(getattr(tup, ite)).lower()
                )
            elif str(ite).lower().startswith("six"):
                power[str(shrt) + str(7)]["Prereq"].append(
                    str(getattr(tup, ite)).lower()
                )
            elif str(ite).lower().startswith("nine"):
                power[str(shrt) + str(10)]["Prereq"].append(
                    str(getattr(tup, ite)).lower()
                )
    power["omn1"]["Prereq"].append("aut0")
    power["int1"]["Prereq"].append("sys0")
    power["4th1"]["Prereq"].append("aut0")
    for sett in power.items():
        logP.debug(sett)


statsToken = "1JIJjDzFjtuIU2k0jk1aHdMr2oErD_ySoFm7-iFEBOV0"

statsName = "BotStats"
bonusName = "BotBonus"

replaceName = "BotReplace"

baseName = "BotBase"

urlStats = urltoAdd.format(statsToken, statsName)
urlBonus = urltoAdd.format(statsToken, bonusName)
urlReplace = urltoAdd.format(statsToken, replaceName)

urlBase = urltoAdd.format(statsToken, baseName)

statCalcDict = {}
bonusDict = {}
replaceDict = {}
baseDict = {}

urlList = [
    [urlStats, statCalcDict, "statCalcDict"],
    [urlBonus, bonusDict, "bonusDict"],
]

for url, dic, dicName in urlList:
    try:
        frame = None
        frame = pd.read_csv(url)
    except Exception as e:
        print(e)
    for tup in frame.itertuples():
        shrt = [x[0] for x in leader.items() if x[1] == tup.Role]
        if shrt:
            shrt = shrt[0]
            dic[shrt] = {}
            for name, value in tup._asdict().items():
                logP.debug(
                    "To: {}, adding: [{}][{}] = {}".format(
                        dicName, shrt, name, value
                    )
                )
                dic[shrt][name] = value


try:
    frame = None
    frame = pd.read_csv(urlReplace)
except Exception as e:
    print(e)
for tup in frame.itertuples():
    shrt = [x[0] for x in leader.items() if x[1] == tup.Role]
    if shrt:
        shrt = shrt[0]
        shrt2 = [x[0] for x in leader.items() if x[1] == tup.ReplaceWith]
        if shrt2:
            shrt2 = shrt2[0]
            logP.debug("replace '{}' with '{}'".format(shrt, shrt2))
            replaceDict[shrt] = shrt2

try:
    frame = None
    frame = pd.read_csv(urlBase)
except Exception as e:
    print(e)

for tup in frame.itertuples():
    baseDict[tup.Constant] = tup.BaseStat
    logP.debug(
        "Adding Base: {} of {}, to dict".format(tup.Constant, tup.BaseStat)
    )

npcDict = {}
npcSheet = "NPC"
npcToken = "1GAs0JctnNcWHTiCb7YPZk-9CtEd53RtDKb5VLPE_PbM"
npcUrl = urltoAdd.format(npcToken, npcSheet)

try:
    frame = None
    frame = pd.read_csv(npcUrl)
except Exception as e:
    print(e)

for tup in frame.itertuples():
    npcDict[str(tup.ID)] = {}
    for ite in tup._fields:
        loc = str(ite).lower() if str(ite) != str("_18") else "4th"
        if str(getattr(tup, ite)) == str("nan"):
            continue
        npcDict[str(tup.ID)][loc] = getattr(tup, ite)
    logP.debug("Added NPC: {}".format(npcDict[str(tup.ID)]))


descSheet = "BotDescriptions"
descToken = "1Pw96S2rvfRlNuPqbSkGpHDtEkIqQlK5_QGy6lTmMexI"
descUrl = urltoAdd.format(descToken, descSheet)

try:
    frame = None
    frame = pd.read_csv(descUrl)
except Exception as e:
    print(e)

for tup in frame.itertuples():
    cmdInf[tup.Command] = {}
    for ite in tup._fields:
        if str(getattr(tup, ite)) == str("nan"):
            cmdInf[tup.Command][ite] = "No Description"
        else:
            cmdInf[tup.Command][ite] = getattr(tup, ite)
    logP.debug("Added Command description: {}".format(cmdInf[tup.Command]))

logP.info("Finished csv download and input.")
