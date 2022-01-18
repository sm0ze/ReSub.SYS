import os
import socket
import time

import dotenv

import log

logP = log.get_logger(__name__)


# function to grab a discord bot token
# from user if one is not found in the .env
def askToken(var: str) -> str:
    tempToken = input(f"Enter your {var}: ")
    with open(".env", "a+") as j:
        j.write(f"{var}={tempToken}\n")
    return tempToken


HOST_NAME = socket.gethostname().lower()
logP.info(f"Name of host for program is: {HOST_NAME}")

COMMANDS_ON = True

# .env variables that are not shared with github and other users.
# Use your own if testing this with your own bot
# TOKEN is the discord bot token to authorise this code for the ReSub.SYS bot
dotenv.load_dotenv()
dotenv_file = dotenv.find_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SAVE_FILE = os.getenv("SAVEFILE")
START_CHANNEL = os.getenv("STARTCHANNEL")
ERROR_THREAD = os.getenv("ERRORTHREAD")
TATSU = os.getenv("TATSU_TOKEN")

if not TOKEN:
    logP.warning("No Discord Token")
    TOKEN = askToken("DISCORD_TOKEN")
if not SAVE_FILE:
    logP.warning("No saveFile name")
    SAVE_FILE = askToken("SAVEFILE")
if not START_CHANNEL:
    logP.warning("No Discord channel id to post bot status messages set")
    START_CHANNEL = askToken("STARTCHANNEL")
if not ERROR_THREAD:
    logP.warning("No Discord thread id to post error messages to set")
    ERROR_THREAD = askToken("ERRORTHREAD")
if not TATSU:
    TATSU = askToken("TATSU_TOKEN")

logP.debug("All .env Tokens loaded")


def setGemDiff(var: float):
    os.environ["GEMDIFF"] = str(var)
    dotenv.set_key(dotenv_file, "GEMDIFF", os.environ["GEMDIFF"])


SUPE_ROLE = "Supe"
MANAGER = "System"  # manager role name for guild
STREAKER = "Patrol_Reminder.exe"
ROLE_ID_PATROL = 922408216644698162
ROLE_ID_CALL = 925197249179418654

CMD_PREFIX = "~"
START_TIME = time.time()
HIDE = False
COMMANDS_ROLES = [SUPE_ROLE]  # guild role(s) for using these bot commands
MANAGER_ROLES = [MANAGER]

LOWEST_ROLE = 2  # bot sorts roles by rank from position of int10 to LOWESTROLE
LEAD_LIMIT = 12
DL_ARC_DUR = 60

TASK_CD = 60 * 30
TIME_TILL_ON_CALL = TASK_CD * 4 + 60 * 60
ACTIVE_SEC = 60 * 60 * 24 * 7

DEFAULT_DUEL_OPP = 572301609305112596
ROUND_LIMIT = 100
DRAW_DEF = 20
PLAYER_TURN_WAIT = 30
BOT_TURN_WAIT = 60

GEM_DIFF = os.getenv("GEMDIFF")
if not GEM_DIFF:
    GEM_DIFF = 0.5

ASK_SELF = 0
ASK_NOONE = 1
ASK_ALL = 2
ASK_NPC = 3

HIT_RANGE = 15
LO_HIT = -19
AV_HIT = -8
HI_HIT = 19

WOU_DMG = 5

STATS_HP_DMG = 0.1
STATS_HP_AG = 0.5
STATS_HYBRID_DMG = 0.05
STATS_HYBRID_AG = 0.35

VERSION = 0
