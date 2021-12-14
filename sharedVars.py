import os
import socket
import time

import dotenv

import log

logP = log.get_logger(__name__)


# function to grab a discord bot token
# from user if one is not found in the .env
def askToken(var: str) -> str:
    tempToken = input("Enter your {}: ".format(var))
    with open(".env", "a+") as f:
        f.write("{}={}\n".format(var, tempToken))
    return tempToken


HOSTNAME = socket.gethostname()
logP.info("Name of host for program is: {}".format(HOSTNAME))


# .env variables that are not shared with github and other users.
# Use your own if testing this with your own bot
# TOKEN is the discord bot token to authorise this code for the ReSub.SYS bot
dotenv.load_dotenv()
dotenv_file = dotenv.find_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SAVEFILE = os.getenv("SAVEFILE")
STARTCHANNEL = os.getenv("STARTCHANNEL")
ERRORTHREAD = os.getenv("ERRORTHREAD")
TATSU = os.getenv("TATSU_TOKEN")

if not TOKEN:
    logP.warning("No Discord Token")
    TOKEN = askToken("DISCORD_TOKEN")
if not SAVEFILE:
    logP.warning("No saveFile name")
    SAVEFILE = askToken("SAVEFILE")
if not STARTCHANNEL:
    logP.warning("No Discord channel id to post bot status messages set")
    STARTCHANNEL = askToken("STARTCHANNEL")
if not ERRORTHREAD:
    logP.warning("No Discord thread id to post error messages to set")
    ERRORTHREAD = askToken("ERRORTHREAD")
if not TATSU:
    TATSU = askToken("TATSU_TOKEN")

logP.debug("All .env Tokens loaded")


def setGemDiff(var: float):
    os.environ["GEMDIFF"] = str(var)
    dotenv.set_key(dotenv_file, "GEMDIFF", os.environ["GEMDIFF"])


SUPEROLE = "Supe"
MANAGER = "System"  # manager role name for guild
CMDPREFIX = "~"
STARTTIME = time.time()
HIDE = False
COMMANDSROLES = [SUPEROLE]  # guild role(s) for using these bot commands
MANAGERROLES = [MANAGER]

LOWESTROLE = 2  # bot sorts roles by rank from position of int10 to LOWESTROLE
LEADLIMIT = 12
NEWCALC = 1
DL_ARC_DUR = 60


DEFDUELOPP = 159985870458322944
ROUNDLIMIT = 50
PLAYERTURNWAIT = 30
BOTTURNWAIT = 60

global GEMDIFF
GEMDIFF = os.getenv("GEMDIFF")
if not GEMDIFF:
    GEMDIFF = 0.5
TASKCD = 60 * 30


VERSION = 0
