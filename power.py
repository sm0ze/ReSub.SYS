# power.py
# this file is a dictionary and other lengthy constant variables dump

import pandas as pd

DEBUG = 0


def debug(*args):
    if DEBUG:
        print(*args)


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
        "end": 1,
        "reaction": "🗡️",
    },
    "mentA": {
        "name": "Mental Attack",
        "desperate": 0,
        "type": "Attack",
        "moveStr": "Mental",
        "cost": 2,
        "end": 1,
        "reaction": "😠",
    },
    "dPhysA": {
        "name": "Desperate Physical Attack",
        "desperate": 1,
        "type": "Attack",
        "moveStr": "Physical",
        "cost": 5,
        "end": 1,
        "reaction": "⚔️",
    },
    "dMentA": {
        "name": "Desperate Mental Attack",
        "desperate": 1,
        "type": "Attack",
        "moveStr": "Mental",
        "cost": 5,
        "end": 1,
        "reaction": "🤯",
    },
    "physD": {
        "name": "Physical Defense",
        "desperate": 0,
        "type": "Defend",
        "moveStr": "Physical",
        "cost": 0,
        "end": 1,
        "reaction": "🛡️",
    },
    "mentD": {
        "name": "Mental Defense",
        "desperate": 0,
        "type": "Defend",
        "moveStr": "Mental",
        "cost": 0,
        "end": 1,
        "reaction": "😎",
    },
}
"""
"focus": {
        "desperate": 0,
        "type": "Utility",
        "moveStr": "Focus",
        "cost": 1,
        "end": 0,
        "reaction": "😤",
    },
}"""


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


cmdInf = {
    "about": {
        "brief": "-quick blurb for info about the bot.",
        "description": (
            "-quick blurb for info about the bot. Also has the "
            "hostname of the os the bot is running on for "
            "troubleshooting."
        ),
    },
    "add": {
        "brief": (
            "-Allows host to add enhancements and their prereqs to themself."
        ),
        "description": (
            "-Use the shorthand enhancement codes separated by "
            "commas to add to host's build.\nExample: For a build "
            "with Rank 4 Regeneration and Rank 4 Mental Celerity "
            "the shorthand would be 'reg4, cel4'. The bot will "
            "attempt to add those 2 enhancements and their "
            "prerequisites to the host if they have enough "
            "enhancement points."
        ),
    },
    "build": {
        "brief": "-Total points required and their prerequisite enhancements.",
        "description": (
            "-Use the shorthand enhancement codes separated by "
            "commas to find a builds total enhancement cost and "
            "prerequisites.\nExample: For a build with Rank 4 "
            "Regeneration and Rank 4 Mental Celerity the "
            "shorthand would be 'reg4, cel4'."
        ),
    },
    "clean": {
        "brief": (
            "-Allows a host to reset their enhancements for " "reallocation."
        ),
        "description": (
            "-This command will remove all Supe related roles "
            "from the host so they can start a new build."
        ),
    },
    "convert": {
        "brief": "-Converts between GDV and XP values.",
        "description": (
            '-Converts between GDV and XP values.\n"~convert x" '
            'will convert x from XP to GDV\n"~convert x 1" will '
            "convert x from GDV to XP."
        ),
    },
    "end": {
        "brief": "-Kills the bot.",
        "description": (
            "-Kills the bot. sm0ze will have to turn it back on "
            "again... That is why he is the only one able to use "
            "this command :P"
        ),
    },
    "list": {
        "brief": "-Lists all available enhancements.",
        "description": (
            "-Lists all available enhancements. It also lets you "
            "know how many ranks of each enhancement there are as "
            "well as the 3 letter shorthand."
        ),
    },
    "moveRoles": {
        "brief": (
            "-Repositions the server roles so they are in the correct "
            "tier order."
        ),
        "description": (
            "-Repositions the server roles so they are in the "
            "correct tier order. Does not sort the roles within "
            "the tier."
        ),
    },
    "pause": {
        "brief": "-Puts the bot to sleep, 'resume' to wake.",
        "description": (
            "-Puts the bot to sleep, 'resume' to wake. This "
            "command mainly exists so that the 24/7 bot does not "
            "need to be killed when updating/troubleshooting and "
            "can just be restarted."
        ),
    },
    "points": {
        "brief": (
            "-Shows target host's available and spent enhancement " "points."
        ),
        "description": (
            "-Shows target host's available and spent enhancement "
            "points.\nThis command can take multiple users as "
            "arguments as long as they are separated by commas. "
            "It is also possible to mention all users you wish to "
            "get the points of.\nIf no arguments are provided the "
            "command defaults to the command caller's points."
        ),
    },
    "restart": {
        "brief": "-Tells the bot to reboot.",
        "description": (
            "-Tells the bot to reboot. It will be back soon, " "do not worry."
        ),
    },
    "roleInf": {
        "brief": "-Gives role info, such as position and colour.",
        "description": (
            "-Gives role info, such as position and colour. Can "
            "only take one role as an argument, requres correct "
            "spelling and capitalisation."
        ),
    },
    "role": {
        "brief": "-Allows user to add freely available roles to themselves.",
        "description": (
            "-Allows user to add freely available roles to "
            "themselves.\n Currently the list to pick "
            "from is: {}"
        ).format(freeRoles),
    },
    "run": {
        "brief": "-tells user where the bot is running.",
        "description": (
            "-just the hostname of the os the bot is running on "
            "for troubleshooting."
        ),
    },
    "start": {
        "brief": (
            "-Use this command to get a walkthrough for host's "
            "first enhancement."
        ),
        "description": (
            "-Use this command to get a walkthrough for host's first "
            "enhancement.\nIf you have no idea how to use the bot, this"
            " is a good place to start."
        ),
    },
    "task": {
        "brief": "-Grants host a task to complete.",
        "description": (
            "-Grants host a task to complete.\nTask may be of "
            "type minor, moderate, major or imperative. Completion of task "
            "will grant the host 100% GDV with partial GDV given to those "
            "that help. Different number of maximum additional helpers for "
            "different task tiers of respectively 0, 1, 3 and All System hosts"
        ),
    },
    "top": {
        "brief": "-Shows the top hosts by their enhancements.",
        "description": (
            "-Shows the top hosts by their enhancements.\nA "
            "variable 'enh' can be given if user would like to get the top "
            "hosts of a specific enhancement."
        ),
    },
    "trimAll": {
        "brief": "-Trims excess low rank roles from all supes.",
        "description": (
            "-Trims excess low rank roles from all supes. Some users like the "
            "role bloat, so do not abuse this command.",
        ),
    },
    "trim": {
        "brief": (
            "-Allows a host to remove duplicate enhancements of a "
            "lower rank."
        ),
        "description": (
            "-Allows a host to remove duplicate enhancements of "
            "a lower rank from themself."
        ),
    },
    "update": {
        "brief": "-Pulls the latest update from github.",
        "description": (
            "-Pulls the latest update from github. If you ain't "
            "sm0ze, why do you care about this command?"
        ),
    },
    "upload": {
        "brief": "-Uploads the memberlist xp value cache.",
        "description": (
            "-Uploads the memberlist xp value cache. Server ID as "
            "Key will return a dictionary with keys of different member IDs. "
            "This makes the ReSub Bot a server specific XP bot."
        ),
    },
    "uptime": {
        "brief": "-Shows how long the bot has been online and logged in.",
        "description": (
            "-Shows how long the bot has been online and logged "
            "in. Highscores are always fun!"
        ),
    },
    "xpGrab": {
        "brief": "-Shows the command callers XP total.",
        "description": (
            "-Shows the command callers XP total. total xp is calculated "
            "with: MEE6 + 0.5*TATSU + ReSub. Can also be used to ensure the "
            "python modules for getting user info is still working."
        ),
    },
}

power = {
    "sup0": {"Name": "Supe", "Type": "Supe", "Rank": 0, "Prereq": []},
    "sys0": {"Name": "System", "Type": "System", "Rank": 0, "Prereq": []},
    "aut0": {"Name": "Authors", "Type": "Authors", "Rank": 0, "Prereq": []},
}


def remove_values_from_list(the_list, val):
    return [value for value in the_list if str(value) != val]


sheet_names = [
    [taskVar["taskOpt"][0][x], taskVar["taskOpt"][1][x]]
    for x in range(0, len(taskVar["taskOpt"][0]))
]
debug(sheet_names)
for sheetL in sheet_names:
    urlToken = sheetL[1]
    sheet = sheetL[0]
    debug("sheet name is: ", sheet)
    debug("url token is: ", urlToken)
    url = (
        "https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx="
        "out:csv&sheet={}"
    ).format(urlToken, sheet)
    debug("At URL: ", url)
    try:
        frame = None
        frame = pd.read_csv(url)
    except Exception as e:
        print(e)
        continue

    for i in frame:
        debug("i in frame is: ", i, type(i))
        if i.startswith("Unnamed"):
            debug("skipping: ", i)
            continue
        currList = remove_values_from_list([x for x in frame[i]], "nan")
        debug("Current list of {} is: ".format(i), currList)
        posTask[sheet][i] = currList
debug(posTask)

for statsheet in statsheetNom:
    statUrlID = statsheet[1]
    statsheetName = statsheet[0]
    debug("sheet name is: ", statsheetName)
    debug("url token is: ", statUrlID)
    statUrl = (
        "https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx="
        "out:csv&sheet={}"
    ).format(statUrlID, statsheetName)

    debug("At URL: ", statUrl)
    try:
        frame = None
        frame = pd.read_csv(statUrl)
    except Exception as e:
        print(e)
        continue

    for tup in frame.itertuples():
        # debug("index", index)
        # debug("row", row)
        debug("tuple", tup)
        shrt = [x[0] for x in leader.items() if x[1] == tup.Role]
        if shrt:
            shrt = shrt[0]
        debug("shrt", shrt)
        for i in range(1, 11):
            power[str(shrt) + str(i)] = {
                "Name": "Rank {} {}".format(i, tup.Role),
                "Type": "{}".format(tup.Role),
                "Rank": i,
                "Prereq": [],
            }
            if power[str(shrt) + str(i)]["Type"] == "Intelligence":
                power[str(shrt) + str(i)]["Name"] += " (only for Systems)"
            if i > 1:
                power[str(shrt) + str(i)]["Prereq"].append(
                    str(shrt) + str(i - 1)
                )
        for ite in tup._fields:
            debug("ite", ite, getattr(tup, ite))
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
        debug(sett)
