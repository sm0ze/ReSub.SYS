# power.py
# this file is a dictionary and other lengthy constant variables dump

import pandas as pd

import log

logP = log.get_logger(__name__)

urltoAdd = (
    "https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet={}"
)


statsToken = "1JIJjDzFjtuIU2k0jk1aHdMr2oErD_ySoFm7-iFEBOV0"
statsheetNom = [["Requirements", statsToken]]
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
    "addP": {"Minor": 0, "Moderate": 1, "Major": 3, "Imperative": 5},
}

genDictAll = {
    "they": {"m": "he", "f": "she", "r": ["he", "she", "they"]},
    "their": {"m": "his", "f": "her", "r": ["his", "her", "their"]},
    "them": {"m": "him", "f": "her", "r": ["him", "her", "them"]},
}

rsltDict = {
    "Error": [0, 0.5],
    "sufficient": [0.5, 0.6],
    "good": [0.6, 0.7],
    "great": [0.7, 0.8],
    "spectacular": [0.8, 0.9],
    "superlative": [0.9, 1.0],
}

multiTypDict = {
    -1.5: "parried",
    -1: "deflected",
    -0.66: "blocked",
    -0.33: "weak",
    0: "normal",
    0.33: "good",
    0.66: "great",
    1: "spectacular",
    1.5: "superlative",
    2: "flawless",
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
        "moveStr": "physical",
        "cost": 2,
        "reaction": "🗡️",
    },
    "mentA": {
        "name": "Mental Attack",
        "desperate": 0,
        "type": "Attack",
        "moveStr": "mental",
        "cost": 2,
        "reaction": "😠",
    },
    "dPhysA": {
        "name": "Desperate Physical Attack",
        "desperate": 1,
        "type": "Attack",
        "moveStr": "physical",
        "cost": 5,
        "reaction": "⚔️",
    },
    "dMentA": {
        "name": "Desperate Mental Attack",
        "desperate": 1,
        "type": "Attack",
        "moveStr": "mental",
        "cost": 5,
        "reaction": "🤯",
    },
    "physD": {
        "name": "Physical Defense",
        "desperate": 0,
        "type": "Defend",
        "moveStr": "physical",
        "cost": 0,
        "reaction": "🛡️",
    },
    "mentD": {
        "name": "Mental Defense",
        "desperate": 0,
        "type": "Defend",
        "moveStr": "mental",
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

freeRoles = ["Ping Unto Me My Daily Quack", "Supe", "Patrol_Reminder.exe"]

reqResList = ["int", "4th", "omn"]

cmdInf = {}

masterEhnDict = {
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
    logP.debug(f"At URL: {url}")
    try:
        frame = None
        frame = pd.read_csv(url)
    except Exception as e:
        logP.warning(e)
        continue

    for i in frame:
        if i.startswith("Unnamed"):
            continue
        currList = remove_values_from_list([x for x in frame[i]], "nan")
        posTask[sheet][i] = currList
        logP.debug(f"{sheet} list of {i} is of length {len(currList)}")

for statsheet in statsheetNom:
    statUrlID = statsheet[1]
    statsheetName = statsheet[0]
    statUrl = urltoAdd.format(statUrlID, statsheetName)

    logP.debug(f"At URL: {statUrl}")
    try:
        frame = None
        frame = pd.read_csv(statUrl)
    except Exception as e:
        logP.warning(e)
        continue

    for tup in frame.itertuples():
        shrt = [x[0] for x in leader.items() if x[1] == tup.Role]
        if shrt:
            shrt = shrt[0]
        for i in range(1, 11):
            enhNum = str(shrt) + str(i)
            masterEhnDict[enhNum] = {
                "Name": f"Rank {i} {tup.Role}",
                "Type": f"{tup.Role}",
                "Rank": i,
                "Prereq": [],
            }
            if masterEhnDict[enhNum]["Type"] == "Intelligence":
                masterEhnDict[enhNum]["Name"] += " (only for Systems)"
            if i > 1:
                masterEhnDict[enhNum]["Prereq"].append(str(shrt) + str(i - 1))
        for ite in tup._fields:
            if str(getattr(tup, ite)) == str("nan"):
                continue
            if str(ite).lower().startswith("three"):
                masterEhnDict[str(shrt) + str(4)]["Prereq"].append(
                    str(getattr(tup, ite)).lower()
                )
            elif str(ite).lower().startswith("six"):
                masterEhnDict[str(shrt) + str(7)]["Prereq"].append(
                    str(getattr(tup, ite)).lower()
                )
            elif str(ite).lower().startswith("nine"):
                masterEhnDict[str(shrt) + str(10)]["Prereq"].append(
                    str(getattr(tup, ite)).lower()
                )
    masterEhnDict["omn1"]["Prereq"].append("aut0")
    masterEhnDict["int1"]["Prereq"].append("sys0")
    masterEhnDict["4th1"]["Prereq"].append("aut0")
    for sett in masterEhnDict.items():
        logP.debug(sett)


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
baseDict: dict[str, float] = {}

urlList = [
    [urlStats, statCalcDict, "statCalcDict"],
    [urlBonus, bonusDict, "bonusDict"],
]

for url, dic, dicName in urlList:
    try:
        frame = None
        frame = pd.read_csv(url)
    except Exception as e:
        logP.warning(e)
    for tup in frame.itertuples():
        shrt = [x[0] for x in leader.items() if x[1] == tup.Role]
        if shrt:
            shrt = shrt[0]
            dic[shrt] = {}
            for name, value in tup._asdict().items():
                logP.debug(
                    f"To: {dicName}, adding: [{shrt}][{name}] = {value}"
                )
                dic[shrt][name] = value


try:
    frame = None
    frame = pd.read_csv(urlReplace)
except Exception as e:
    logP.warning(e)
for tup in frame.itertuples():
    shrt = [x[0] for x in leader.items() if x[1] == tup.Role]
    if shrt:
        shrt = shrt[0]
        shrt2 = [x[0] for x in leader.items() if x[1] == tup.ReplaceWith]
        if shrt2:
            shrt2 = shrt2[0]
            logP.debug(f"replace '{shrt}' with '{shrt2}'")
            replaceDict[shrt] = shrt2

try:
    frame = None
    frame = pd.read_csv(urlBase)
except Exception as e:
    logP.warning(e)

for tup in frame.itertuples():
    baseDict[tup.Constant] = float(tup.BaseStat)
    logP.debug(f"Adding Base: {tup.Constant} of {tup.BaseStat}, to dict")

npcDict = {}
npcSheet = "NPC"
npcToken = "1GAs0JctnNcWHTiCb7YPZk-9CtEd53RtDKb5VLPE_PbM"
npcUrl = urltoAdd.format(npcToken, npcSheet)

try:
    frame = None
    frame = pd.read_csv(npcUrl)
except Exception as e:
    logP.warning(e)

for tup in frame.itertuples():
    npcDict[str(tup.ID)] = {}
    for ite in tup._fields:
        loc = str(ite).lower() if str(ite) != str("_18") else "4th"
        if str(getattr(tup, ite)) == str("nan"):
            continue
        npcDict[str(tup.ID)][loc] = getattr(tup, ite)
    logP.debug(f"Added NPC: {npcDict[str(tup.ID)]}")
logP.info(f"Added {len(npcDict)} NPCs")


descSheet = "BotDescriptions"
descToken = "1Pw96S2rvfRlNuPqbSkGpHDtEkIqQlK5_QGy6lTmMexI"
descUrl = urltoAdd.format(descToken, descSheet)

try:
    frame = None
    frame = pd.read_csv(descUrl)
except Exception as e:
    logP.warning(e)

for tup in frame.itertuples():
    cmdInf[tup.Command] = {}
    for ite in tup._fields:
        if str(getattr(tup, ite)) == str("nan"):
            cmdInf[tup.Command][ite] = ""
        else:
            cmdInf[tup.Command][ite] = getattr(tup, ite)
    logP.debug(f"Added Command description: {cmdInf[tup.Command]}")
logP.info(f"Added {len(cmdInf)} command descriptions.")


activeDic = {}

interactiveSheet = "Interactive"
interactiveToken = "12F0NDWn6dAiavMPH7f1ADDfFwUZx4JWn9KhWC4kQOag"
interactiveUrl = urltoAdd.format(interactiveToken, interactiveSheet)

try:
    frame = None
    frame = pd.read_csv(interactiveUrl)
except Exception as e:
    logP.warning(e)

powers = 0
ranks = 0
for tup in frame.itertuples():
    if str(tup.Power) != str("nan") and str(tup.Descriptor) != str("nan"):
        activeDic[tup.Power] = str(tup.Descriptor).split(";")
        powers += 1

    if str(tup.Rank) != str("nan") and str(tup.Task) != str("nan"):
        activeDic.setdefault(tup.Rank, [])
        activeDic[tup.Rank].append(str(tup.Task).split(";"))
        ranks += 1

    if str(tup.Person) != str("nan") and str(tup.Gender) != str("nan"):
        activeDic.setdefault("person", [])
        activeDic["person"].append([tup.Person, tup.Gender])

logP.info(
    (
        f"Imported for Interactive Tasks: {powers} Powers, "
        f"{len(activeDic['person'])} Peeps, {ranks} Ranks"
    )
)


attackSheet = "BotAttack"
attackUrl = urltoAdd.format(statsToken, attackSheet)

attackRollDict = {}

try:
    frame = None
    frame = pd.read_csv(attackUrl)
except Exception as e:
    logP.warning(e)

for tup in frame.itertuples():
    attackRollDict[int(tup.Roll)] = float(tup.Mod)

logP.info(f"Loaded {len(attackRollDict)} vals into attackRollDict")


tutorialSheet = "Tutorial"
tutorialToken = "1ESiyR28hw3WSLTxx95H2kenk43PoZ5iPEnh8hnqZ2W8"
tutorialUrl = urltoAdd.format(tutorialToken, tutorialSheet)

tutDict = {}


def nanCheck(val):
    if str(val).lower() == "nan":
        return ""
    return val


try:
    frame = None
    frame = pd.read_csv(tutorialUrl)
except Exception as e:
    logP.warning(e)

for tup in frame.itertuples():
    if not nanCheck(tup.Step):
        continue
    tutDict[int(tup.Step)] = {
        "cmd": tup.Command,
        "arg": nanCheck(tup.Arguments),
        "txt": tup.Tutorial,
    }
logP.info(f"Loaded {len(tutDict)} steps into tutDict")

logP.info("Finished csv download and input.")
