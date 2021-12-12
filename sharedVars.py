import os
import socket

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
