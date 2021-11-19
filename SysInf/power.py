# power.py
# this file is a dictionary and other lengthy constant variables dump

import os

import pandas as pd

DEBUG = 0
TEST = 0


def debug(*args):
    if DEBUG:
        print(*args)


debug("{} DEBUG TRUE".format(os.path.basename(__file__)))


if TEST:
    print("{} TEST TRUE".format(os.path.basename(__file__)))
# if TEST: print("".format())


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


# the enhancement dictionary. Holds each enhancement and their attributes.

# blank entry
# '': {'Name': '', 'Rank': , 'Prereq': []},
power = {
    "sup0": {"Name": "Supe", "Type": "Supe", "Rank": 0, "Prereq": []},
    "sys0": {"Name": "System", "Type": "System", "Rank": 0, "Prereq": []},
    "aut0": {"Name": "Authors", "Type": "Authors", "Rank": 0, "Prereq": []},
    "str1": {
        "Name": "Rank 1 Strength",
        "Type": "Strength",
        "Rank": 1,
        "Prereq": [],
    },
    "spe1": {"Name": "Rank 1 Speed", "Type": "Speed", "Rank": 1, "Prereq": []},
    "end1": {
        "Name": "Rank 1 Endurance",
        "Type": "Endurance",
        "Rank": 1,
        "Prereq": [],
    },
    "mem1": {
        "Name": "Rank 1 Memory",
        "Type": "Memory",
        "Rank": 1,
        "Prereq": [],
    },
    "cel1": {
        "Name": "Rank 1 Mental Celerity",
        "Type": "Mental Celerity",
        "Rank": 1,
        "Prereq": [],
    },
    "cla1": {
        "Name": "Rank 1 Mental Clarity",
        "Type": "Mental Clarity",
        "Rank": 1,
        "Prereq": [],
    },
    "reg1": {
        "Name": "Rank 1 Regeneration",
        "Type": "Regeneration",
        "Rank": 1,
        "Prereq": [],
    },
    "pai1": {
        "Name": "Rank 1 Pain Tolerance",
        "Type": "Pain Tolerance",
        "Rank": 1,
        "Prereq": [],
    },
    "inv1": {
        "Name": "Rank 1 Invisibility",
        "Type": "Invisibility",
        "Rank": 1,
        "Prereq": [],
    },
    "vis1": {
        "Name": "Rank 1 Vision",
        "Type": "Vision",
        "Rank": 1,
        "Prereq": [],
    },
    "aur1": {
        "Name": "Rank 1 Aural Faculty",
        "Type": "Aural Faculty",
        "Rank": 1,
        "Prereq": [],
    },
    "olf1": {
        "Name": "Rank 1 Olfactory Sense",
        "Type": "Olfactory Sense",
        "Rank": 1,
        "Prereq": [],
    },
    "gus1": {
        "Name": "Rank 1 Gustatory Ability",
        "Type": "Gustatory Ability",
        "Rank": 1,
        "Prereq": [],
    },
    "tac1": {
        "Name": "Rank 1 Tactile Reception",
        "Type": "Tactile Reception",
        "Rank": 1,
        "Prereq": [],
    },
    "pro1": {
        "Name": "Rank 1 Proprioception",
        "Type": "Proprioception",
        "Rank": 1,
        "Prereq": [],
    },
    "omn1": {
        "Name": "Rank 1 Omniscience",
        "Type": "Omniscience",
        "Rank": 1,
        "Prereq": ["aut0"],
    },
    "int1": {
        "Name": "Rank 1 Intelligence (only for Systems)",
        "Type": "Intelligence",
        "Rank": 1,
        "Prereq": ["sys0"],
    },
    "4th1": {
        "Name": "Rank 1 4th Wall Breaker",
        "Type": "4th Wall Breaker",
        "Rank": 1,
        "Prereq": ["aut0"],
    },
    "str2": {
        "Name": "Rank 2 Strength",
        "Type": "Strength",
        "Rank": 2,
        "Prereq": ["str1"],
    },
    "spe2": {
        "Name": "Rank 2 Speed",
        "Type": "Speed",
        "Rank": 2,
        "Prereq": ["spe1"],
    },
    "end2": {
        "Name": "Rank 2 Endurance",
        "Type": "Endurance",
        "Rank": 2,
        "Prereq": ["end1"],
    },
    "mem2": {
        "Name": "Rank 2 Memory",
        "Type": "Memory",
        "Rank": 2,
        "Prereq": ["mem1"],
    },
    "cel2": {
        "Name": "Rank 2 Mental Celerity",
        "Type": "Mental Celerity",
        "Rank": 2,
        "Prereq": ["cel1"],
    },
    "cla2": {
        "Name": "Rank 2 Mental Clarity",
        "Type": "Mental Clarity",
        "Rank": 2,
        "Prereq": ["cla1"],
    },
    "reg2": {
        "Name": "Rank 2 Regeneration",
        "Type": "Regeneration",
        "Rank": 2,
        "Prereq": ["reg1"],
    },
    "pai2": {
        "Name": "Rank 2 Pain Tolerance",
        "Type": "Pain Tolerance",
        "Rank": 2,
        "Prereq": ["pai1"],
    },
    "inv2": {
        "Name": "Rank 2 Invisibility",
        "Type": "Invisibility",
        "Rank": 2,
        "Prereq": ["inv1"],
    },
    "vis2": {
        "Name": "Rank 2 Vision",
        "Type": "Vision",
        "Rank": 2,
        "Prereq": ["vis1"],
    },
    "aur2": {
        "Name": "Rank 2 Aural Faculty",
        "Type": "Aural Faculty",
        "Rank": 2,
        "Prereq": ["aur1"],
    },
    "olf2": {
        "Name": "Rank 2 Olfactory Sense",
        "Type": "Olfactory Sense",
        "Rank": 2,
        "Prereq": ["olf1"],
    },
    "gus2": {
        "Name": "Rank 2 Gustatory Ability",
        "Type": "Gustatory Ability",
        "Rank": 2,
        "Prereq": ["gus1"],
    },
    "tac2": {
        "Name": "Rank 2 Tactile Reception",
        "Type": "Tactile Reception",
        "Rank": 2,
        "Prereq": ["tac1"],
    },
    "pro2": {
        "Name": "Rank 2 Proprioception",
        "Type": "Proprioception",
        "Rank": 2,
        "Prereq": ["pro1"],
    },
    "omn2": {
        "Name": "Rank 2 Omniscience",
        "Type": "Omniscience",
        "Rank": 2,
        "Prereq": ["omn1"],
    },
    "int2": {
        "Name": "Rank 2 Intelligence (only for Systems)",
        "Type": "Intelligence",
        "Rank": 2,
        "Prereq": ["int1"],
    },
    "4th2": {
        "Name": "Rank 2 4th Wall Breaker",
        "Type": "4th Wall Breaker",
        "Rank": 2,
        "Prereq": ["4th1"],
    },
    "str3": {
        "Name": "Rank 3 Strength",
        "Type": "Strength",
        "Rank": 3,
        "Prereq": ["str2"],
    },
    "spe3": {
        "Name": "Rank 3 Speed",
        "Type": "Speed",
        "Rank": 3,
        "Prereq": ["spe2"],
    },
    "end3": {
        "Name": "Rank 3 Endurance",
        "Type": "Endurance",
        "Rank": 3,
        "Prereq": ["end2"],
    },
    "mem3": {
        "Name": "Rank 3 Memory",
        "Type": "Memory",
        "Rank": 3,
        "Prereq": ["mem2"],
    },
    "cel3": {
        "Name": "Rank 3 Mental Celerity",
        "Type": "Mental Celerity",
        "Rank": 3,
        "Prereq": ["cel2"],
    },
    "cla3": {
        "Name": "Rank 3 Mental Clarity",
        "Type": "Mental Clarity",
        "Rank": 3,
        "Prereq": ["cla2"],
    },
    "reg3": {
        "Name": "Rank 3 Regeneration",
        "Type": "Regeneration",
        "Rank": 3,
        "Prereq": ["reg2"],
    },
    "pai3": {
        "Name": "Rank 3 Pain Tolerance",
        "Type": "Pain Tolerance",
        "Rank": 3,
        "Prereq": ["pai2"],
    },
    "inv3": {
        "Name": "Rank 3 Invisibility",
        "Type": "Invisibility",
        "Rank": 3,
        "Prereq": ["inv2"],
    },
    "vis3": {
        "Name": "Rank 3 Vision",
        "Type": "Vision",
        "Rank": 3,
        "Prereq": ["vis2"],
    },
    "aur3": {
        "Name": "Rank 3 Aural Faculty",
        "Type": "Aural Faculty",
        "Rank": 3,
        "Prereq": ["aur2"],
    },
    "olf3": {
        "Name": "Rank 3 Olfactory Sense",
        "Type": "Olfactory Sense",
        "Rank": 3,
        "Prereq": ["olf2"],
    },
    "gus3": {
        "Name": "Rank 3 Gustatory Ability",
        "Type": "Gustatory Ability",
        "Rank": 3,
        "Prereq": ["gus2"],
    },
    "tac3": {
        "Name": "Rank 3 Tactile Reception",
        "Type": "Tactile Reception",
        "Rank": 3,
        "Prereq": ["tac2"],
    },
    "pro3": {
        "Name": "Rank 3 Proprioception",
        "Type": "Proprioception",
        "Rank": 3,
        "Prereq": ["pro2"],
    },
    "omn3": {
        "Name": "Rank 3 Omniscience",
        "Type": "Omniscience",
        "Rank": 3,
        "Prereq": ["omn2"],
    },
    "int3": {
        "Name": "Rank 3 Intelligence (only for Systems)",
        "Type": "Intelligence",
        "Rank": 3,
        "Prereq": ["int2"],
    },
    "4th3": {
        "Name": "Rank 3 4th Wall Breaker",
        "Type": "4th Wall Breaker",
        "Rank": 3,
        "Prereq": ["4th2"],
    },
    "str4": {
        "Name": "Rank 4 Strength",
        "Type": "Strength",
        "Rank": 4,
        "Prereq": ["str3", "end1", "pro1", "reg1"],
    },
    "spe4": {
        "Name": "Rank 4 Speed",
        "Type": "Speed",
        "Rank": 4,
        "Prereq": ["spe3", "vis1", "pro1", "cel1"],
    },
    "end4": {
        "Name": "Rank 4 Endurance",
        "Type": "Endurance",
        "Rank": 4,
        "Prereq": ["end3", "str1", "tac1", "pai1"],
    },
    "mem4": {
        "Name": "Rank 4 Memory",
        "Type": "Memory",
        "Rank": 4,
        "Prereq": ["mem3", "cla1", "cel1"],
    },
    "cel4": {
        "Name": "Rank 4 Mental Celerity",
        "Type": "Mental Celerity",
        "Rank": 4,
        "Prereq": ["cel3", "spe1", "mem1", "cla1"],
    },
    "cla4": {
        "Name": "Rank 4 Mental Clarity",
        "Type": "Mental Clarity",
        "Rank": 4,
        "Prereq": ["cla3", "end1", "mem1", "cel1"],
    },
    "reg4": {
        "Name": "Rank 4 Regeneration",
        "Type": "Regeneration",
        "Rank": 4,
        "Prereq": ["reg3", "spe1", "pro1", "pai1"],
    },
    "pai4": {
        "Name": "Rank 4 Pain Tolerance",
        "Type": "Pain Tolerance",
        "Rank": 4,
        "Prereq": ["pai3", "tac1"],
    },
    "inv4": {
        "Name": "Rank 4 Invisibility",
        "Type": "Invisibility",
        "Rank": 4,
        "Prereq": ["inv3", "cla1", "cel1", "pro1"],
    },
    "vis4": {
        "Name": "Rank 4 Vision",
        "Type": "Vision",
        "Rank": 4,
        "Prereq": ["vis3", "cla1", "cel1"],
    },
    "aur4": {
        "Name": "Rank 4 Aural Faculty",
        "Type": "Aural Faculty",
        "Rank": 4,
        "Prereq": ["aur3", "cla1", "cel1"],
    },
    "olf4": {
        "Name": "Rank 4 Olfactory Sense",
        "Type": "Olfactory Sense",
        "Rank": 4,
        "Prereq": ["olf3", "cla1", "cel1"],
    },
    "gus4": {
        "Name": "Rank 4 Gustatory Ability",
        "Type": "Gustatory Ability",
        "Rank": 4,
        "Prereq": ["gus3", "cla1", "cel1"],
    },
    "tac4": {
        "Name": "Rank 4 Tactile Reception",
        "Type": "Tactile Reception",
        "Rank": 4,
        "Prereq": ["tac3", "cla1", "cel1"],
    },
    "pro4": {
        "Name": "Rank 4 Proprioception",
        "Type": "Proprioception",
        "Rank": 4,
        "Prereq": ["pro3", "cla1", "cel1"],
    },
    "omn4": {
        "Name": "Rank 4 Omniscience",
        "Type": "Omniscience",
        "Rank": 4,
        "Prereq": ["omn3", "vis1", "aur1", "pro1"],
    },
    "int4": {
        "Name": "Rank 4 Intelligence (only for Systems)",
        "Type": "Intelligence",
        "Rank": 4,
        "Prereq": ["int3", "cel1", "cla1"],
    },
    "4th4": {
        "Name": "Rank 4 4th Wall Breaker",
        "Type": "4th Wall Breaker",
        "Rank": 4,
        "Prereq": ["4th3", "end1", "spe1"],
    },
    "str5": {
        "Name": "Rank 5 Strength",
        "Type": "Strength",
        "Rank": 5,
        "Prereq": ["str4"],
    },
    "spe5": {
        "Name": "Rank 5 Speed",
        "Type": "Speed",
        "Rank": 5,
        "Prereq": ["spe4"],
    },
    "end5": {
        "Name": "Rank 5 Endurance",
        "Type": "Endurance",
        "Rank": 5,
        "Prereq": ["end4"],
    },
    "mem5": {
        "Name": "Rank 5 Memory",
        "Type": "Memory",
        "Rank": 5,
        "Prereq": ["mem4"],
    },
    "cel5": {
        "Name": "Rank 5 Mental Celerity",
        "Type": "Mental Celerity",
        "Rank": 5,
        "Prereq": ["cel4"],
    },
    "cla5": {
        "Name": "Rank 5 Mental Clarity",
        "Type": "Mental Clarity",
        "Rank": 5,
        "Prereq": ["cla4"],
    },
    "reg5": {
        "Name": "Rank 5 Regeneration",
        "Type": "Regeneration",
        "Rank": 5,
        "Prereq": ["reg4"],
    },
    "pai5": {
        "Name": "Rank 5 Pain Tolerance",
        "Type": "Pain Tolerance",
        "Rank": 5,
        "Prereq": ["pai4"],
    },
    "inv5": {
        "Name": "Rank 5 Invisibility",
        "Type": "Invisibility",
        "Rank": 5,
        "Prereq": ["inv4"],
    },
    "vis5": {
        "Name": "Rank 5 Vision",
        "Type": "Vision",
        "Rank": 5,
        "Prereq": ["vis4"],
    },
    "aur5": {
        "Name": "Rank 5 Aural Faculty",
        "Type": "Aural Faculty",
        "Rank": 5,
        "Prereq": ["aur4"],
    },
    "olf5": {
        "Name": "Rank 5 Olfactory Sense",
        "Type": "Olfactory Sense",
        "Rank": 5,
        "Prereq": ["olf4"],
    },
    "gus5": {
        "Name": "Rank 5 Gustatory Ability",
        "Type": "Gustatory Ability",
        "Rank": 5,
        "Prereq": ["gus4"],
    },
    "tac5": {
        "Name": "Rank 5 Tactile Reception",
        "Type": "Tactile Reception",
        "Rank": 5,
        "Prereq": ["tac4"],
    },
    "pro5": {
        "Name": "Rank 5 Proprioception",
        "Type": "Proprioception",
        "Rank": 5,
        "Prereq": ["pro4"],
    },
    "omn5": {
        "Name": "Rank 5 Omniscience",
        "Type": "Omniscience",
        "Rank": 5,
        "Prereq": ["omn4"],
    },
    "int5": {
        "Name": "Rank 5 Intelligence (only for Systems)",
        "Type": "Intelligence",
        "Rank": 5,
        "Prereq": ["int4"],
    },
    "4th5": {
        "Name": "Rank 5 4th Wall Breaker",
        "Type": "4th Wall Breaker",
        "Rank": 5,
        "Prereq": ["4th4"],
    },
    "str6": {
        "Name": "Rank 6 Strength",
        "Type": "Strength",
        "Rank": 6,
        "Prereq": ["str5"],
    },
    "spe6": {
        "Name": "Rank 6 Speed",
        "Type": "Speed",
        "Rank": 6,
        "Prereq": ["spe5"],
    },
    "end6": {
        "Name": "Rank 6 Endurance",
        "Type": "Endurance",
        "Rank": 6,
        "Prereq": ["end5"],
    },
    "mem6": {
        "Name": "Rank 6 Memory",
        "Type": "Memory",
        "Rank": 6,
        "Prereq": ["mem5"],
    },
    "cel6": {
        "Name": "Rank 6 Mental Celerity",
        "Type": "Mental Celerity",
        "Rank": 6,
        "Prereq": ["cel5"],
    },
    "cla6": {
        "Name": "Rank 6 Mental Clarity",
        "Type": "Mental Clarity",
        "Rank": 6,
        "Prereq": ["cla5"],
    },
    "reg6": {
        "Name": "Rank 6 Regeneration",
        "Type": "Regeneration",
        "Rank": 6,
        "Prereq": ["reg5"],
    },
    "pai6": {
        "Name": "Rank 6 Pain Tolerance",
        "Type": "Pain Tolerance",
        "Rank": 6,
        "Prereq": ["pai5"],
    },
    "inv6": {
        "Name": "Rank 6 Invisibility",
        "Type": "Invisibility",
        "Rank": 6,
        "Prereq": ["inv5"],
    },
    "vis6": {
        "Name": "Rank 6 Vision",
        "Type": "Vision",
        "Rank": 6,
        "Prereq": ["vis5"],
    },
    "aur6": {
        "Name": "Rank 6 Aural Faculty",
        "Type": "Aural Faculty",
        "Rank": 6,
        "Prereq": ["aur5"],
    },
    "olf6": {
        "Name": "Rank 6 Olfactory Sense",
        "Type": "Olfactory Sense",
        "Rank": 6,
        "Prereq": ["olf5"],
    },
    "gus6": {
        "Name": "Rank 6 Gustatory Ability",
        "Type": "Gustatory Ability",
        "Rank": 6,
        "Prereq": ["gus5"],
    },
    "tac6": {
        "Name": "Rank 6 Tactile Reception",
        "Type": "Tactile Reception",
        "Rank": 6,
        "Prereq": ["tac5"],
    },
    "pro6": {
        "Name": "Rank 6 Proprioception",
        "Type": "Proprioception",
        "Rank": 6,
        "Prereq": ["pro5"],
    },
    "omn6": {
        "Name": "Rank 6 Omniscience",
        "Type": "Omniscience",
        "Rank": 6,
        "Prereq": ["omn5"],
    },
    "int6": {
        "Name": "Rank 6 Intelligence (only for Systems)",
        "Type": "Intelligence",
        "Rank": 6,
        "Prereq": ["int5"],
    },
    "4th6": {
        "Name": "Rank 6 4th Wall Breaker",
        "Type": "4th Wall Breaker",
        "Rank": 6,
        "Prereq": ["4th5"],
    },
    "str7": {
        "Name": "Rank 7 Strength",
        "Type": "Strength",
        "Rank": 7,
        "Prereq": ["str6", "end3", "pro3", "reg3"],
    },
    "spe7": {
        "Name": "Rank 7 Speed",
        "Type": "Speed",
        "Rank": 7,
        "Prereq": ["spe6", "end1", "pro3", "cel3"],
    },
    "end7": {
        "Name": "Rank 7 Endurance",
        "Type": "Endurance",
        "Rank": 7,
        "Prereq": ["end6", "str3", "tac3", "pai3"],
    },
    "mem7": {
        "Name": "Rank 7 Memory",
        "Type": "Memory",
        "Rank": 7,
        "Prereq": ["mem6", "spe1", "cla3", "cel3"],
    },
    "cel7": {
        "Name": "Rank 7 Mental Celerity",
        "Type": "Mental Celerity",
        "Rank": 7,
        "Prereq": ["cel6", "spe3", "mem3", "cla3"],
    },
    "cla7": {
        "Name": "Rank 7 Mental Clarity",
        "Type": "Mental Clarity",
        "Rank": 7,
        "Prereq": ["cla6", "end3", "mem3", "cel3"],
    },
    "reg7": {
        "Name": "Rank 7 Regeneration",
        "Type": "Regeneration",
        "Rank": 7,
        "Prereq": ["reg6", "spe3", "pro3", "pai3"],
    },
    "pai7": {
        "Name": "Rank 7 Pain Tolerance",
        "Type": "Pain Tolerance",
        "Rank": 7,
        "Prereq": ["pai6", "end1", "tac3", "reg1"],
    },
    "inv7": {
        "Name": "Rank 7 Invisibility",
        "Type": "Invisibility",
        "Rank": 7,
        "Prereq": ["inv6", "pro3", "cla3", "cel3"],
    },
    "vis7": {
        "Name": "Rank 7 Vision",
        "Type": "Vision",
        "Rank": 7,
        "Prereq": ["vis6", "mem1", "cla3", "cel3"],
    },
    "aur7": {
        "Name": "Rank 7 Aural Faculty",
        "Type": "Aural Faculty",
        "Rank": 7,
        "Prereq": ["aur6", "mem1", "cla3", "cel3"],
    },
    "olf7": {
        "Name": "Rank 7 Olfactory Sense",
        "Type": "Olfactory Sense",
        "Rank": 7,
        "Prereq": ["olf6", "mem1", "cla3", "cel3"],
    },
    "gus7": {
        "Name": "Rank 7 Gustatory Ability",
        "Type": "Gustatory Ability",
        "Rank": 7,
        "Prereq": ["gus6", "mem1", "cla3", "cel3"],
    },
    "tac7": {
        "Name": "Rank 7 Tactile Reception",
        "Type": "Tactile Reception",
        "Rank": 7,
        "Prereq": ["tac6", "pro1", "cla3", "cel3"],
    },
    "pro7": {
        "Name": "Rank 7 Proprioception",
        "Type": "Proprioception",
        "Rank": 7,
        "Prereq": ["pro6", "mem3", "cla3", "cel3"],
    },
    "omn7": {
        "Name": "Rank 7 Omniscience",
        "Type": "Omniscience",
        "Rank": 7,
        "Prereq": ["omn6", "vis3", "aur3", "pro3"],
    },
    "int7": {
        "Name": "Rank 7 Intelligence (only for Systems)",
        "Type": "Intelligence",
        "Rank": 7,
        "Prereq": ["int6", "mem1", "cel3", "cla3"],
    },
    "4th7": {
        "Name": "Rank 7 4th Wall Breaker",
        "Type": "4th Wall Breaker",
        "Rank": 7,
        "Prereq": ["4th6", "end3", "spe3", "str1", "reg1"],
    },
    "str8": {
        "Name": "Rank 8 Strength",
        "Type": "Strength",
        "Rank": 8,
        "Prereq": ["str7"],
    },
    "spe8": {
        "Name": "Rank 8 Speed",
        "Type": "Speed",
        "Rank": 8,
        "Prereq": ["spe7"],
    },
    "end8": {
        "Name": "Rank 8 Endurance",
        "Type": "Endurance",
        "Rank": 8,
        "Prereq": ["end7"],
    },
    "mem8": {
        "Name": "Rank 8 Memory",
        "Type": "Memory",
        "Rank": 8,
        "Prereq": ["mem7"],
    },
    "cel8": {
        "Name": "Rank 8 Mental Celerity",
        "Type": "Mental Celerity",
        "Rank": 8,
        "Prereq": ["cel7"],
    },
    "cla8": {
        "Name": "Rank 8 Mental Clarity",
        "Type": "Mental Clarity",
        "Rank": 8,
        "Prereq": ["cla7"],
    },
    "reg8": {
        "Name": "Rank 8 Regeneration",
        "Type": "Regeneration",
        "Rank": 8,
        "Prereq": ["reg7"],
    },
    "pai8": {
        "Name": "Rank 8 Pain Tolerance",
        "Type": "Pain Tolerance",
        "Rank": 8,
        "Prereq": ["pai7"],
    },
    "inv8": {
        "Name": "Rank 8 Invisibility",
        "Type": "Invisibility",
        "Rank": 8,
        "Prereq": ["inv7"],
    },
    "vis8": {
        "Name": "Rank 8 Vision",
        "Type": "Vision",
        "Rank": 8,
        "Prereq": ["vis7"],
    },
    "aur8": {
        "Name": "Rank 8 Aural Faculty",
        "Type": "Aural Faculty",
        "Rank": 8,
        "Prereq": ["aur7"],
    },
    "olf8": {
        "Name": "Rank 8 Olfactory Sense",
        "Type": "Olfactory Sense",
        "Rank": 8,
        "Prereq": ["olf7"],
    },
    "gus8": {
        "Name": "Rank 8 Gustatory Ability",
        "Type": "Gustatory Ability",
        "Rank": 8,
        "Prereq": ["gus7"],
    },
    "tac8": {
        "Name": "Rank 8 Tactile Reception",
        "Type": "Tactile Reception",
        "Rank": 8,
        "Prereq": ["tac7"],
    },
    "pro8": {
        "Name": "Rank 8 Proprioception",
        "Type": "Proprioception",
        "Rank": 8,
        "Prereq": ["pro7"],
    },
    "omn8": {
        "Name": "Rank 8 Omniscience",
        "Type": "Omniscience",
        "Rank": 8,
        "Prereq": ["omn7"],
    },
    "int8": {
        "Name": "Rank 8 Intelligence (only for Systems)",
        "Type": "Intelligence",
        "Rank": 8,
        "Prereq": ["int7"],
    },
    "4th8": {
        "Name": "Rank 8 4th Wall Breaker",
        "Type": "4th Wall Breaker",
        "Rank": 8,
        "Prereq": ["4th7"],
    },
    "str9": {
        "Name": "Rank 9 Strength",
        "Type": "Strength",
        "Rank": 9,
        "Prereq": ["str8"],
    },
    "spe9": {
        "Name": "Rank 9 Speed",
        "Type": "Speed",
        "Rank": 9,
        "Prereq": ["spe8"],
    },
    "end9": {
        "Name": "Rank 9 Endurance",
        "Type": "Endurance",
        "Rank": 9,
        "Prereq": ["end8"],
    },
    "mem9": {
        "Name": "Rank 9 Memory",
        "Type": "Memory",
        "Rank": 9,
        "Prereq": ["mem8"],
    },
    "cel9": {
        "Name": "Rank 9 Mental Celerity",
        "Type": "Mental Celerity",
        "Rank": 9,
        "Prereq": ["cel8"],
    },
    "cla9": {
        "Name": "Rank 9 Mental Clarity",
        "Type": "Mental Clarity",
        "Rank": 9,
        "Prereq": ["cla8"],
    },
    "reg9": {
        "Name": "Rank 9 Regeneration",
        "Type": "Regeneration",
        "Rank": 9,
        "Prereq": ["reg8"],
    },
    "pai9": {
        "Name": "Rank 9 Pain Tolerance",
        "Type": "Pain Tolerance",
        "Rank": 9,
        "Prereq": ["pai8"],
    },
    "inv9": {
        "Name": "Rank 9 Invisibility",
        "Type": "Invisibility",
        "Rank": 9,
        "Prereq": ["inv8"],
    },
    "vis9": {
        "Name": "Rank 9 Vision",
        "Type": "Vision",
        "Rank": 9,
        "Prereq": ["vis8"],
    },
    "aur9": {
        "Name": "Rank 9 Aural Faculty",
        "Type": "Aural Faculty",
        "Rank": 9,
        "Prereq": ["aur8"],
    },
    "olf9": {
        "Name": "Rank 9 Olfactory Sense",
        "Type": "Olfactory Sense",
        "Rank": 9,
        "Prereq": ["olf8"],
    },
    "gus9": {
        "Name": "Rank 9 Gustatory Ability",
        "Type": "Gustatory Ability",
        "Rank": 9,
        "Prereq": ["gus8"],
    },
    "tac9": {
        "Name": "Rank 9 Tactile Reception",
        "Type": "Tactile Reception",
        "Rank": 9,
        "Prereq": ["tac8"],
    },
    "pro9": {
        "Name": "Rank 9 Proprioception",
        "Type": "Proprioception",
        "Rank": 9,
        "Prereq": ["pro8"],
    },
    "omn9": {
        "Name": "Rank 9 Omniscience",
        "Type": "Omniscience",
        "Rank": 9,
        "Prereq": ["omn8"],
    },
    "int9": {
        "Name": "Rank 9 Intelligence (only for Systems)",
        "Type": "Intelligence",
        "Rank": 9,
        "Prereq": ["int8"],
    },
    "4th9": {
        "Name": "Rank 9 4th Wall Breaker",
        "Type": "4th Wall Breaker",
        "Rank": 9,
        "Prereq": ["4th8"],
    },
    "str10": {
        "Name": "Rank 10 Strength",
        "Type": "Strength",
        "Rank": 10,
        "Prereq": ["str9", "end6", "reg6", "pai3", "pro6"],
    },
    "spe10": {
        "Name": "Rank 10 Speed",
        "Type": "Speed",
        "Rank": 10,
        "Prereq": ["spe9", "end3", "vis3", "cel6", "pro6"],
    },
    "end10": {
        "Name": "Rank 10 Endurance",
        "Type": "Endurance",
        "Rank": 10,
        "Prereq": ["end9", "str6", "tac6", "pai6"],
    },
    "mem10": {
        "Name": "Rank 10 Memory",
        "Type": "Memory",
        "Rank": 10,
        "Prereq": ["mem9", "spe3", "cla6", "cel6"],
    },
    "cel10": {
        "Name": "Rank 10 Mental Celerity",
        "Type": "Mental Celerity",
        "Rank": 10,
        "Prereq": ["cel9", "spe6", "mem6", "cla6"],
    },
    "cla10": {
        "Name": "Rank 10 Mental Clarity",
        "Type": "Mental Clarity",
        "Rank": 10,
        "Prereq": ["cla9", "end6", "mem6", "cel6"],
    },
    "reg10": {
        "Name": "Rank 10 Regeneration",
        "Type": "Regeneration",
        "Rank": 10,
        "Prereq": ["reg9", "spe6", "mem3", "pai6", "pro6"],
    },
    "pai10": {
        "Name": "Rank 10 Pain Tolerance",
        "Type": "Pain Tolerance",
        "Rank": 10,
        "Prereq": ["pai9", "end3", "tac6", "reg3"],
    },
    "inv10": {
        "Name": "Rank 10 Invisibility",
        "Type": "Invisibility",
        "Rank": 10,
        "Prereq": ["inv9", "mem3", "cla6", "cel6", "pro6"],
    },
    "vis10": {
        "Name": "Rank 10 Vision",
        "Type": "Vision",
        "Rank": 10,
        "Prereq": ["vis9", "mem3", "cla6", "cel6"],
    },
    "aur10": {
        "Name": "Rank 10 Aural Faculty",
        "Type": "Aural Faculty",
        "Rank": 10,
        "Prereq": ["aur9", "mem3", "cla6", "cel6"],
    },
    "olf10": {
        "Name": "Rank 10 Olfactory Sense",
        "Type": "Olfactory Sense",
        "Rank": 10,
        "Prereq": ["olf9", "mem3", "cla6", "cel6"],
    },
    "gus10": {
        "Name": "Rank 10 Gustatory Ability",
        "Type": "Gustatory Ability",
        "Rank": 10,
        "Prereq": ["gus9", "mem3", "cla6", "cel6"],
    },
    "tac10": {
        "Name": "Rank 10 Tactile Reception",
        "Type": "Tactile Reception",
        "Rank": 10,
        "Prereq": ["tac9", "pai3", "cla6", "cel6", "pro3"],
    },
    "pro10": {
        "Name": "Rank 10 Proprioception",
        "Type": "Proprioception",
        "Rank": 10,
        "Prereq": ["pro9", "mem6", "cla6", "cel6"],
    },
    "omn10": {
        "Name": "Rank 10 Omniscience",
        "Type": "Omniscience",
        "Rank": 10,
        "Prereq": ["omn9", "vis3", "aur3", "pro3", "olf3", "gus3", "tac3"],
    },
    "int10": {
        "Name": "Rank 10 Intelligence (only for Systems)",
        "Type": "Intelligence",
        "Rank": 10,
        "Prereq": ["int9", "mem3", "cel6", "cla6"],
    },
    "4th10": {
        "Name": "Rank 10 4th Wall Breaker",
        "Type": "4th Wall Breaker",
        "Rank": 10,
        "Prereq": ["4th9", "end6", "spe6", "str3", "reg3"],
    },
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
