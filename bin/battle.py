# battle.py

import asyncio
import datetime
import random
import time
import typing
from collections import namedtuple

import discord
from discord.ext import commands
from discord.utils import get
from numpy import mean

import bin.log as log
from bin.exceptions import noFields, notADuel
from bin.shared.consts import (
    AID_WEIGHT,
    ASK_ALL,
    ASK_NPC,
    ASK_SELF,
    BOT_TURN_WAIT,
    DL_ARC_DUR,
    DRAW_DEF,
    HIT_RANGE,
    HOST_NAME,
    PLAYER_TURN_WAIT,
    ROLE_ID_CALL,
    ROLE_ID_PATROL,
    ROUND_LIMIT,
    STATS_HP_AG,
    STATS_HP_DMG,
    STATS_HYBRID_AG,
    STATS_HYBRID_DMG,
    SUPE_ROLE,
)
from bin.shared.dicts import (
    activeDic,
    attackRollDict,
    baseDict,
    bonusDict,
    leader,
    masterEhnDict,
    moveOpt,
    multiTypDict,
    replaceDict,
    restrictedList,
    statCalcDict,
    taskVar,
)
from bin.shared.funcs import (
    aOrAn,
    buffStrGen,
    checkDefined,
    checkUndefined,
    count,
    dictShrtBuild,
    duelMoveView,
    funcBuild,
    genBuild,
    genOppNPC,
    pickWeightedSupe,
    pluralInt,
    savePers,
    sendMessage,
    spent,
    winPercent,
)

logP = log.get_logger(__name__)

statMes = """{17}
HP: {0:0.3g}/{9:0.3g} (**{13}%**) + {5:0.3g} ({18}%)
Sta: **{10:0.3g}**/{12:0.3g} +{11:0.3g}
P: {1:0.3g}A/{2:0.3g}D
M: {3:0.3g}A/{4:0.3g}D
Acc/Eva({16}): {6:0.3g}/{7:0.3g}
Swi: {14:0.3g}/{15:0.3g} +{8:0.3g}"""


adpMes = """Acc: PA🗡️/MA😠
Eva: PD🛡️/MD😎
```{:> #04.2f}: {:> 02.3g}/{:> 02.3g}
{:> #04.2f}: {:> 02.3g}/{:> 02.3g}```"""

DELIM = 16

rendHP = {
    "empt": "░",
    "partLo": "▒",
    "partHi": "▓",
    "full": "█",
}


class NPC:
    def __init__(
        self,
        bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot],
        npcDict: dict,
    ) -> None:
        self.bot = bot
        picVar = "avatar"

        if picVar not in npcDict.keys():
            npcDict[picVar] = self.bot.user.display_avatar

        npcEhn = [
            f"{x}{npcDict[x]}"
            for x in npcDict.keys()
            if x not in ["name", "id", "index", picVar]
        ]

        self.n = str(npcDict["name"])
        self.picUrl = str(npcDict[picVar])
        self.bL = [x for x in npcEhn if int(x[3:])]


class player:
    def __init__(
        self,
        member: typing.Union[discord.Member, NPC, genOppNPC],
        bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot],
    ) -> None:
        self.bot = bot

        if isinstance(member, discord.Member):
            self.p = member
            self.n = member.display_name
            self.sG = spent([member])
            self.bL = self.sG[0][2]
            self.npc = False
            self.picUrl = self.p.display_avatar.url
            self.agg: float = count(member)[6]
        elif isinstance(member, NPC):
            self.p = None
            self.n = member.n
            self.sG = None
            self.bL = member.bL
            self.npc = True
            self.picUrl = member.picUrl
            self.agg = baseDict["AGG"]
        elif isinstance(member, genOppNPC):
            self.p = None
            self.n = member.n
            self.sG = None
            self.bL = member.bL
            self.npc = True
            self.picUrl = member.picUrl
            self.agg = baseDict["AGG"]

        self.fB = funcBuild(self.bL)
        self.bC = self.fB[0]
        self.stats = self.fB[2]

        self.t = int(0)
        self.play = False

        self.iniCalc()

        addHP = baseDict["HP"] + self.calcStat("HP")

        self.totHP = addHP
        self.hp = self.totHP

        self.rec = baseDict["REC"] + self.calcStat("Rec")

        self.sta = baseDict["STA"] + self.calcStat("Sta")
        self.totSta = baseDict["STATOT"] + self.calcStat("StaTot")
        self.staR = baseDict["STAR"] + self.calcStat("StaR")

        self.pa = baseDict["PA"] + self.calcStat("PA")
        self.pd = baseDict["PD"] + self.calcStat("PD")

        self.ma = baseDict["MA"] + self.calcStat("MA")
        self.md = baseDict["MD"] + self.calcStat("MD")

        self.hAcc = self.calcStat("Acc")
        self.acc = baseDict["ACC"] + self.hAcc

        self.hEva = self.calcStat("Eva")
        self.eva = baseDict["EVA"] + self.hEva

        self.swi = baseDict["SWI"] + self.calcStat("Swi")
        self.totSwi = baseDict["SWITOT"]

        self.swiNow = int(0)
        self.defending = str("")
        self.conDef = int(0)
        self.noDef = bool(False)
        self.tired = int(0)
        self.missTurn = int(0)

        self.weak = bool(False)

        self.focusNumNow = int(0)
        self.focusNumLast = int(0)

        self.dT = 0.0

        self.wou = False

    def iniCalc(self) -> None:
        statDict = {}
        for enhan in self.bL:
            logP.debug(f"enhan: {enhan}")
            name = enhan[:3]
            rank = int(masterEhnDict[enhan]["Rank"])
            if name not in statDict.keys():
                logP.debug(f"Add: {name}, {rank}")
                statDict[name] = rank
            elif rank > statDict[name]:
                logP.debug(f"Update: {name}, {rank}")
                statDict[name] = rank

        for type in leader.keys():
            if type not in statDict.keys():
                logP.debug(f"Added type: {type}")
                statDict[type] = 0

        logP.debug(f"{self.n} stats are: {statDict}")

        self._str = int(statDict["str"])
        self._spe = int(statDict["spe"])
        self._end = int(statDict["end"])
        self._mem = int(statDict["mem"])
        self._cel = int(statDict["cel"])
        self._cla = int(statDict["cla"])
        self._reg = int(statDict["reg"])
        self._pai = int(statDict["pai"])
        self._inv = int(statDict["inv"])
        self._vis = int(statDict["vis"])
        self._aur = int(statDict["aur"])
        self._olf = int(statDict["olf"])
        self._gus = int(statDict["gus"])
        self._tac = int(statDict["tac"])
        self._pro = int(statDict["pro"])
        self._omn = int(statDict["omn"])
        self._4th = int(statDict["4th"])
        self._int = int(statDict["int"])

    def calcStat(self, statType) -> float:
        ret = float(0)
        ret += addCalc(self, statType)
        ret += addBonus(self, statType)
        logP.debug(f"Adding to: {statType}, {ret}")
        return ret

    def bStat(self):
        stats = namedtuple(
            "stats",
            [
                "hp",
                "pa",
                "pd",
                "ma",
                "md",
                "rec",
                "acc",
                "eva",
                "swi",
                "totHP",
                "sta",
                "staR",
                "totSta",
                "percentHP",
                "swiNow",
                "totSwi",
                "focusNum",
                "hpRender",
                "hpRecPer",
            ],
        )
        ret = stats(
            self.hp,
            self.pa,
            self.pd,
            self.ma,
            self.md,
            self.rec,
            self.acc,
            self.eva,
            self.swi,
            self.totHP,
            self.sta,
            self.staR,
            self.totSta,
            self.hpPer(),
            self.swiNow,
            self.totSwi,
            self.focusNumNow + self.focusNumLast,
            self.hpRender(),
            self.recPer(),
        )
        return ret

    def hpPer(self):
        return round((self.hp / self.totHP) * 100)

    def recPer(self):
        return round((self.rec / self.totHP) * 100)

    def hpRender(self, blocks: int = DELIM):
        ret = ""
        unchangedHP = self.hpPer()
        hpPerBlock = round(100 / blocks, 3)
        currPer = unchangedHP if unchangedHP > 0 else 0
        leftover = float(currPer) % hpPerBlock
        fullBlocks = round(currPer / hpPerBlock)
        isPartLeft = bool(leftover)
        emptyBlocks = blocks - fullBlocks
        if isPartLeft:
            emptyBlocks -= 1

        logP.debug(
            (
                f"Hp render for {self.n} is: [Blocks: {blocks}, "
                f"full: {fullBlocks}, part: {isPartLeft}, "
                f"empty: {emptyBlocks}]"
            )
        )

        ret += rendHP["full"] * fullBlocks
        if isPartLeft:
            if leftover >= 0.5 * hpPerBlock:
                ret += rendHP["partHi"]
            else:
                ret += rendHP["partLo"]
        ret += rendHP["empt"] * emptyBlocks

        return ret

    def statMessage(self):
        stats = self.bStat()
        return statMes.format(*stats)

    def defend(self, defType: str = "physical"):
        defAlr = False
        addOn = ""
        if not self.defending:
            self.defending = defType
            val = float(2)
            self.conDef += 1
        else:
            defType = self.defending
            val = float(0.5)
            defAlr = True

        if self.defending == "physical":
            if self.noDef and val == float(0.5):
                self.noDef = not self.noDef
                val = float(0)
            elif not self.noDef and val == float(2) and not self.pd:
                self.noDef = not self.noDef
                self.pd = 1.5

            self.pd = float(val * self.pd)

        elif self.defending == "mental":
            if self.noDef and val == float(0.5):
                self.noDef = not self.noDef
                val = float(0)
            elif not self.noDef and val == float(2) and not self.md:
                self.noDef = not self.noDef
                self.md = 1.5

            self.md = float(val * self.md)

        if defAlr:
            self.defending = ""
            addOn = "no longer "

        ret = f"{self.n} is {addOn}defending from {defType} attacks.\n\n"
        if not defAlr:
            self.recSta()
        return ret

    def recSta(self, val: int = 1) -> int:
        staStrt = self.sta
        self.sta += val
        while self.sta > self.totSta:
            self.focus()
        staEnd = self.sta
        return staEnd - staStrt

    def recHP(self, val: int = 1):
        strtHP = self.hp

        self.hp += (val) * (2 if self.wou else 1)

        if self.hp > self.totHP:
            self.hp = self.totHP

        endHP = self.hp

        if self.wou:
            self.wou = not self.wou

        return endHP - strtHP

    async def ask(self, duelList: list):
        if self.npc:
            return
        elif self.p.bot:
            return

        reactionList = ["✅", "❌"]

        mes = discord.Embed(title="Do you wish to play a duel?")
        for peep in duelList:
            if isinstance(peep, player):
                mes.add_field(name=peep.n, value=peep.statMessage())
        msg = await self.p.send(embed=mes)
        for reac in reactionList:
            await msg.add_reaction(reac)

        def check(reaction, user):
            return user.id == self.p.id and str(reaction.emoji) in reactionList

        active = True
        while active:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", timeout=30, check=check
                )
                if str(reaction.emoji) == "✅":
                    self.play = True
                    active = False
                elif str(reaction.emoji) == "❌":
                    self.play = False
                    active = False
            except asyncio.TimeoutError:
                await self.p.send("Timeout")
                active = False

    def beWeak(self, boo: bool):
        self.weak = boo
        mes = ""
        if self.weak:
            self.pd = self.pd / 2
            self.md = self.md / 2
            mes += (
                f" with {self.hpPer()}% HP and has halved "
                "defenses until their next turn. Their attack is "
            )
        else:
            self.md = self.md * 2
            self.pd = self.pd * 2
            mes += f"{self.n} no longer has lowered defenses.\n\n"
        return mes

    def focus(self, add: bool = True, foc: float = baseDict["FOC"]):
        if add:
            self.focusNumNow += 1
            self.sta -= 1
            self.eva += foc
            self.acc += foc
        else:
            while self.focusNumLast:
                self.focusNumLast -= 1
                self.eva -= foc
                self.acc -= foc
            self.focusNumLast = self.focusNumNow
            self.focusNumNow = 0

    def focusTill(self, num: int = 2):
        if self.sta > num:
            while self.sta > num:
                self.focus()

    async def genBuff(self, place: discord.abc.Messageable = None):
        bonus = int(self.bC / int(baseDict["BON"]))
        aggressiveStats = (
            self._vis
            + self._olf
            + self._aur
            + self._spe
            + self._cel
            + self._str
            + self._mem
        )
        hpBonus = 0.0
        atBonus = 0.0

        if bonus:
            if ((self._str + self._mem) > (self.bC * STATS_HP_DMG)) or (
                aggressiveStats > (self.bC * STATS_HP_AG)
            ):
                hpBonus = 4 * bonus

            elif ((self._str + self._mem) > (self.bC * STATS_HYBRID_DMG)) or (
                aggressiveStats > (self.bC * STATS_HYBRID_AG)
            ):
                atBonus = 0.5 * bonus
                hpBonus = 2 * bonus
            else:
                atBonus = bonus

            self.totHP += hpBonus
            self.hp = self.totHP

            self.pa += atBonus
            self.ma += atBonus

            if place:
                await place.send(
                    f"Buffed MA & PA by: {atBonus}.\nBuffed HP by: {hpBonus}"
                )

    def grabExtra(
        self,
        ctx: commands.Context,
        memberList: list[discord.Member],
        reGen=False,
    ):
        retDict = {}

        memberNames = [x.display_name for x in memberList]

        for member in memberList:
            if reGen:
                peep = player(
                    NPC_from_diff(
                        self.bot,
                        ctx,
                        0,
                        member,
                    ),
                    self.bot,
                )
            else:
                peep = player(member, self.bot)

            addHP = peep.calcStat("HP")
            self.totHP += addHP
            self.hp = self.totHP
            retDict["HP"] = retDict.get("HP", 0) + addHP

            addRec = peep.calcStat("Rec")
            self.rec += addRec
            retDict["Rec"] = retDict.get("Rec", 0) + addRec

            addSta = peep.calcStat("Sta")
            addStaTot = peep.calcStat("StaTot")
            addStaR = peep.calcStat("StaR")
            self.sta += addSta
            self.totSta += addStaTot
            self.staR += addStaR
            retDict["Sta"] = retDict.get("Sta", 0) + addSta
            retDict["StaTot"] = retDict.get("StaTot", 0) + addStaTot
            retDict["StaR"] = retDict.get("StaR", 0) + addStaR

            addPA = peep.calcStat("PA")
            addPD = peep.calcStat("PD")
            self.pa += addPA
            self.pd += addPD
            retDict["PA"] = retDict.get("PA", 0) + addPA
            retDict["PD"] = retDict.get("PD", 0) + addPD

            addMA = peep.calcStat("MA")
            addMD = peep.calcStat("MD")
            self.ma += addMA
            self.md += addMD
            retDict["MA"] = retDict.get("MA", 0) + addMA
            retDict["MD"] = retDict.get("MD", 0) + addMD

            addEva = peep.calcStat("Eva")
            addAcc = peep.calcStat("Acc")
            self.eva += addEva
            self.acc += addAcc
            retDict["Eva"] = retDict.get("Eva", 0) + addEva
            retDict["Acc"] = retDict.get("Acc", 0) + addAcc

            addSwi = peep.calcStat("Swi")
            self.swi += addSwi
            retDict["Swi"] = retDict.get("Swi", 0) + addSwi

        return (retDict, memberNames)


class battler:
    def __init__(
        self,
        bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot],
        memberList: list[typing.Union[discord.Member, NPC, genOppNPC]],
    ) -> None:

        self.playerList: list[player] = []
        self.totSwi = int(baseDict["SWITOT"])
        for peep in memberList:
            self.playerList.append(player(peep, bot))

    async def echoMes(self, mes, thrd, toThrd: bool = True):

        for peep in self.playerList:
            if not isinstance(peep, player):
                continue
            if peep.play:
                await sendMessage(peep.p, mes)
        if toThrd:
            await sendMessage(thrd, mes)

    async def findPlayers(self, dontAsk):
        for peep in self.playerList:
            if isinstance(peep, player):
                if not peep.npc:
                    if not peep.p.bot:
                        if dontAsk == ASK_SELF and (
                            peep is self.playerList[0]
                        ):
                            await peep.ask(self.playerList)
                        elif dontAsk in [ASK_ALL, ASK_NPC]:
                            await peep.ask(self.playerList)

    def nextRound(self) -> player:
        looping = True
        Who2Move = None
        playerUpList = []
        for peep in self.playerList:
            if peep.swiNow > self.totSwi:
                playerUpList.append(peep)
                looping = False

        while looping:
            for peep in self.playerList:
                peep.swiNow += peep.swi
                if peep.swiNow > self.totSwi:
                    playerUpList.append(peep)
                    looping = False

        pickList = [
            x
            for x in playerUpList
            if x and isinstance(x, player) and x.swiNow > self.totSwi
        ]

        pickList.sort(reverse=True, key=lambda x: x.swiNow)
        logP.debug(f"Picklist is of length: {len(pickList)}")

        if len(pickList) > 1:
            pick = (
                pickList[0]
                if pickList[0].swiNow > pickList[1].swiNow
                else "Multiple Choice"
            )
            if pick == "Multiple Choice":
                largestSwi = 0
                randList = []
                for x in pickList:
                    if x.swiNow > largestSwi:
                        randList.clear()
                        randList.append(x)
                        largestSwi = x.swiNow
                    elif x.swiNow == largestSwi:
                        randList.append(x)
                pick = random.choice(randList)
            Who2Move = pick
        else:
            Who2Move = pickList[0]

        Who2Move.swiNow = Who2Move.swiNow - self.totSwi

        return Who2Move

    def move(
        self,
        peep: player,
        defPeep: player,
        move: list[str] = None,
    ) -> tuple[str, typing.Union[player, None]]:
        logP.debug(f"Who2Move: {peep.n}")

        moveStr = self.turn(peep, defPeep, move)
        winner = None

        if peep.hp <= 0 or defPeep.hp <= 0:
            logP.debug(f"attPeep Hp: {peep.hp}, defPeep Hp: {defPeep.hp}")
            if peep.hp == defPeep.hp:
                winner = "Noone"
            elif peep.hp > defPeep.hp:
                winner = peep
            else:
                winner = defPeep

        return moveStr, winner

    def turn(self, peep: player, attPeep: player, move: list[str]) -> str:
        mes = ""
        if peep.focusNumNow or peep.focusNumLast:
            mes += (
                f"{peep.n} starts the turn with "
                f"{peep.focusNumLast+peep.focusNumNow} focus.\n\n"
            )
        if peep.missTurn:
            extraSta = 1
            mes += f"{peep.n} misses this turn due to exhaustion!\n\n"
            peep.recSta(extraSta)

        if peep.weak:
            mes += peep.beWeak(False)
        # if peep.defending:
        #     mes += peep.defend()

        desperate = move[0]
        typeMove = move[1]
        moveStr = move[2]

        if typeMove == "Attack" and not peep.missTurn:
            mes += self.attack(peep, attPeep, moveStr, desperate)
        elif typeMove == "Defend" and not peep.missTurn:
            mes += peep.defend(moveStr)
        else:
            if not peep.missTurn:
                staRec = 7
                mes += (
                    f"{peep.n} recovered this turn for {staRec} stamina.\n\n"
                )
                peep.sta += staRec

        peep.focus(False)

        if not peep.sta:
            peep.missTurn = int(2)
            peep.tired += 1
            mes += (
                f"{peep.n} has exhausted themself ({peep.tired}) "
                "and will miss a turn.\n\n"
            )

        mes += self.recover(peep)

        if False:  # peep.tired == 5:
            mes += f"{peep.n} has exhausted themself for the fifth time!\n\n"
            if attPeep.hp < 0:
                peep.hp = attPeep.hp
            else:
                peep.hp = float(0)

        if peep.focusNumNow or peep.focusNumLast:
            mes += (
                f"{peep.n} ends the turn with "
                f"{peep.focusNumLast+peep.focusNumNow} focus.\n\n"
            )

        if peep.missTurn:
            peep.missTurn -= 1
        if peep.conDef >= DRAW_DEF:
            mes += (
                f"{peep.n} has defended for 20 consecutive turns "
                "without attacking and tied this fight."
            )
            if attPeep.hp < 0:
                peep.hp = attPeep.hp
            else:
                peep.hp = float(0)
                attPeep.hp = float(0)
        return mes

    def decAtk(self, Attack, peep: player, notPeep: player):
        # pull average modifier
        multiRange = self.rangeFinder(peep, notPeep)
        avMod = mean(multiRange) + 1

        # aggression modifier
        agro = 10 - peep.agg

        # norm attack value
        decAtk = max(
            [
                [peep.pa * avMod - notPeep.pd - agro, "physical"],
                [peep.ma * avMod - notPeep.md - agro, "mental"],
            ],
            key=lambda x: x[0],
        )
        atk = float(decAtk[0])
        atkStr = decAtk[1]

        # desperate attack value
        decDAtk = max(
            [
                [peep.pa * (avMod + 1) - notPeep.pd - agro, "physical"],
                [peep.ma * (avMod + 1) - notPeep.md - agro, "mental"],
            ],
            key=lambda x: x[0],
        )
        dAtk = float(decDAtk[0])
        dAtkStr = decDAtk[1]

        return atk, atkStr, dAtk, dAtkStr

    def moveSelf(self, peep: player, notPeep: player):
        moveStr = ""
        desperate = 0
        typeMove = "Attack"

        Attack = self.adp(peep, notPeep)
        Defend = self.adp(notPeep, peep)

        normSta = moveOpt["physA"]["cost"]
        despSta = moveOpt["dPhysA"]["cost"]

        atk, atkStr, dAtk, dAtkStr = self.decAtk(Attack, peep, notPeep)

        # notPeep's hp next peep turn
        nextHP = notPeep.hp + notPeep.rec * 2

        # if notPeep is one norm hit from loss
        oneHit = bool(notPeep.hp <= atk)

        # if notPeep is one desp hit from loss
        oneDespHit = bool(notPeep.hp <= dAtk)

        # HPS of enemy compared to turns needed to recover sta,
        # +1 for doubled regen after being hit
        maxHPS = notPeep.rec * ((peep.totSta / (peep.staR + 1)) + 1)
        normHPS = notPeep.rec * ((normSta / (peep.staR + 1)) + 1)
        despHPS = notPeep.rec * ((despSta / (peep.staR + 1)) + 1)

        # AI time!
        if peep.sta >= 2:
            if oneHit:
                peep.focusTill(normSta)
            # then normal attack
            elif peep.sta >= 5:
                if oneDespHit:
                    peep.focusTill(despSta)
                    desperate = 1
                    # then desperate attack

                elif peep.sta == 10:
                    if dAtk < despHPS:
                        typeMove = "Defend"

                    elif nextHP > dAtk * 2 and dAtk > maxHPS:
                        peep.focusTill(despSta + 1)
                        desperate = 1
                        # then desperate attack

                    else:
                        desperate = 1
                        # then desperate attack
                else:
                    typeMove = "Defend"

            elif peep.sta > 2 and atk > normHPS:
                pass
                # then normal attack

            else:
                typeMove = "Defend"

        else:
            typeMove = "Defend"

        if typeMove == "Defend":
            # defend func
            despPhysDef = Defend.phys + notPeep.pa
            despMentDef = Defend.ment + notPeep.ma
            if despPhysDef > despMentDef:
                moveStr = "physical"
            elif despMentDef > despPhysDef:
                moveStr = "mental"
            else:
                moveStr = random.choice(["physical", "mental"])
        elif not moveStr:
            if desperate:
                moveStr = dAtkStr
            else:
                moveStr = atkStr

        return desperate, typeMove, moveStr

    def recover(self, peep: player) -> str:
        mes = ""
        staRec = peep.recSta(peep.staR)
        if staRec:
            """mes += (
                f"{peep.n} recovers {staRec} stamina for a "
                f"running total of {peep.sta}.\n"
            )"""
        heal = peep.recHP(peep.rec)
        if heal:
            mes += f"{peep.n} heals for {heal:0.3g}.\n\n"
        peep.t += 1
        return mes

    def attack(
        self,
        attacker: player,
        defender: player,
        attMove: str,
        desperate: bool = 0,
        riposte: bool = 0,
    ) -> str:
        mes = ""

        attacker.conDef = int(0)

        if desperate:
            typeAtt = "desperately "
            staCost = moveOpt["dPhysA"]["cost"]
        else:
            typeAtt = ""
            staCost = moveOpt["physA"]["cost"]
        if not riposte:
            attacker.sta -= staCost
            mes += f"{attacker.n} {typeAtt}attacks"
        else:
            mes += f"{attacker.n} {typeAtt}counterattacks"

        if not attMove:
            if attacker.pa - defender.pd > attacker.ma - defender.md:
                attMove = "physical"
            else:
                attMove = "mental"

        if not riposte and desperate and attacker.hpPer() > 50:
            mes += attacker.beWeak(True)
        else:
            mes += ", it is "

        multiRange = self.rangeFinder(attacker, defender)

        multi = round(random.choice(multiRange), 3)
        typHit = multiTypDict.get(multi, "mistaken")

        logP.debug(f"Hit is '{typHit}' for '{multi}'")

        mes += (
            f"{aOrAn(typHit).lower()} {typHit} ({multi}) "
            f"{'hit' if not riposte else 'riposte'}"
        )

        if attMove == "physical":
            attDmg = attackCalc(
                multi,
                attacker.pa,
                defender.pd,
                desperate,
            )
            if attDmg < int(0):
                attDmg = float(0)

            defender.dT += attDmg if defender.hp > attDmg else defender.hp
            defender.hp = defender.hp - attDmg

            if attDmg > float(baseDict["WOU"]):
                defender.wou = True

            mes += f" for {attDmg:0.3g} physical damage.\n\n"
            logP.debug(f"physical attack is a: {typHit}, for: {attDmg}")
        if attMove == "mental":
            attDmg = attackCalc(
                multi,
                attacker.ma,
                defender.md,
                desperate,
            )
            if attDmg < int(0):
                attDmg = float(0)

            defender.dT += attDmg if defender.hp > attDmg else defender.hp
            defender.hp = defender.hp - attDmg

            if attDmg > float(baseDict["WOU"]):
                defender.wou = True

            mes += f" for {attDmg:0.3g} mental damage.\n\n"
            logP.debug(f"mental attack is a: {typHit}, for: {attDmg}")

        if multi < -0.5:
            typDesp = 1 if multi <= -1.5 else 0
            mes += "\n" + self.attack(defender, attacker, "", typDesp, True)

        return mes

    def rangeFinder(self, attacker: player, defender: player):
        multiBase = int(attacker.acc - defender.eva)
        multiRangeStart = multiBase - HIT_RANGE
        multiRangeStop = multiBase + 1 + HIT_RANGE

        multiRange = [
            float(attackRollDict[x])
            for x in range(multiRangeStart, multiRangeStop)
        ]

        return multiRange

    def adp(self, at1: player, at2: player):
        adpStats = namedtuple("adpStats", ["hitChance", "phys", "ment"])
        phys = at1.pa - at2.pd
        ment = at1.ma - at2.md
        hitChance = at1.acc - at2.eva

        ret = adpStats(hitChance, phys, ment)
        return ret

    def adpStatMessage(self, at1: player, at2: player):
        adaptedAtt = self.adp(at1, at2)
        adaptedDef = self.adp(at2, at1)

        retList = [
            adaptedAtt.hitChance,
            adaptedAtt.phys,
            adaptedAtt.ment,
            adaptedDef.hitChance,
            adaptedDef.phys,
            adaptedDef.ment,
        ]
        ret = f"*{at1.n} Vs. {at2.n}*\n{adpMes.format(*retList)}\n"
        return ret

    def adpList(self, statsFor: player) -> str:
        ret = "**Adapted Stats**"
        for peep in self.playerList:
            if statsFor is peep:
                continue
            ret += f"\n{self.adpStatMessage(statsFor, peep)}"
        return ret

    def isPlay(self, peep: player):
        return "Playing" if peep.play else "NPC" if peep.npc else "Bot"


def attackCalc(
    multi: float = 0,
    attckDmg: float = 0,
    defense: float = 0,
    desperate: bool = 0,
) -> float:
    attVal = 1 + multi + int(desperate)
    ret = attVal * attckDmg - defense
    return round(ret, 3)


def addCalc(self, statType) -> float:
    ret = float(0)
    ignore = []
    for stat in statCalcDict.keys():
        statAm = getattr(self, f"_{stat}")
        if not statAm:
            continue
        if stat in replaceDict.keys():
            soft = getattr(self, f"_{stat}")
            hard = getattr(self, f"_{replaceDict[stat]}")
            logP.debug(
                str(
                    f"soft {stat} rank {soft}, "
                    + f"hard {replaceDict[stat]} rank {hard}"
                )
            )
            if soft >= hard:
                logP.debug(f"Adding {replaceDict[stat]} to ignore List")
                ignore.append(replaceDict[stat])
            else:
                logP.debug(f"Adding {stat} to ignore List")
                ignore.append(stat)

    logP.debug(f"ignore: {ignore}")

    for stat in statCalcDict.keys():
        statAm = getattr(self, f"_{stat}")
        if not statAm or stat in ignore:
            continue
        try:
            addStat = float(statCalcDict[stat][statType])
        except KeyError:
            addStat = 0.0
        if addStat:
            ret += float(statAm) * float(addStat)
            logP.debug(
                (
                    f"Adding rank {statAm} {stat} * {addStat} = "
                    f"{statAm * addStat} to {statType}."
                )
            )
    return ret


def addBonus(self, bonusType) -> float:
    ret = float(0)
    ignore = []
    for stat in bonusDict.keys():
        statAm = getattr(self, f"_{stat}")
        if not statAm:
            continue
        if stat in replaceDict.keys():
            soft = getattr(self, f"_{stat}")
            hard = getattr(self, f"_{replaceDict[stat]}")
            if soft == 10 and hard == 10:
                ignore.append(stat)

    logP.debug(f"ignore: {ignore}")

    for stat in bonusDict.keys():
        addBonus = bonusDict[stat][bonusType]
        if addBonus:
            bonusStat = getattr(self, f"_{stat}")
            if int(bonusStat) == 10 and stat not in ignore:
                ret += float(addBonus)
                logP.debug(
                    (
                        f"Adding a bonus of {addBonus} to {bonusType} "
                        f"for having 10 in {stat}"
                    )
                )
    return ret


def playerFromBuild(
    bot: typing.Union[commands.Bot, commands.AutoShardedBot],
    buildList: list[str],
    name: str,
):
    genNPC = NPCFromBuild(bot, buildList, name)
    return playerFromNPC(bot, genNPC)


def playerFromNPC(
    bot: typing.Union[commands.Bot, commands.AutoShardedBot], genNPC
):
    genPlay = player(genNPC, bot)
    return genPlay


def NPCFromBuild(
    bot: typing.Union[commands.Bot, commands.AutoShardedBot],
    buildList: list[str],
    name: str,
):
    FPC = {}
    FPC["name"] = name
    for item in buildList:
        typ = item[:3]
        rank = int(item[3:])
        FPC[typ] = int(rank)
    genNPC = NPC(
        bot,
        FPC,
    )
    return genNPC


async def startDuel(
    bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot],
    ctx: commands.Context,
    bat: battler,
    output: bool = True,
    saveOpp: genOppNPC = None,
):
    if output:
        titleString = ""
        for peep in bat.playerList:
            titleString += f"{peep.n}: {bat.isPlay(peep)} Vs. "
        titleString = titleString[:-5]

        mes = discord.Embed(title=titleString)

        for peep in bat.playerList:
            stats = peep.statMessage()
            adpStats = bat.adpList(peep)

            mes.add_field(
                name=f"{peep.n}",
                value=f"{stats}\n\n{adpStats}",
            )

        mes.set_footer(text=HOST_NAME, icon_url=bot.user.display_avatar)

        sentMes = await ctx.send(
            embed=mes,
        )

        thrd = await ctx.channel.create_thread(
            name=mes.title,
            message=sentMes,
            auto_archive_duration=DL_ARC_DUR,
            reason=mes.title,
        )

        mes.add_field(
            inline=False,
            name="TBD Move",
            value="Does Nothing.",
        )

    winner = None
    totRounds = int(0)
    while not winner:
        totRounds += 1
        Who2Move = bat.nextRound()

        move = None
        defPeep = None

        if Who2Move.defending:
            Who2Move.defend()
        if Who2Move.play and output:
            move, defPeep = await playerDuelInput(
                bot, ctx, totRounds, Who2Move, bat
            )

        if not move:
            if len(bat.playerList) == 2:
                if Who2Move is bat.playerList[0]:
                    defPeep = bat.playerList[1]
                else:
                    defPeep = bat.playerList[0]
            else:
                raise notADuel(
                    f"Expected a Duel with 2 players not {len(bat.playerList)}"
                )
            move = bat.moveSelf(Who2Move, defPeep)

        moveStr, winner = bat.move(Who2Move, defPeep, move)

        if output:
            for i, peep in enumerate(bat.playerList):
                stats = peep.statMessage()
                adpStats = bat.adpList(peep)

                mes.set_field_at(
                    i,
                    name=f"{peep.n}",
                    value=f"{stats}\n\n{adpStats}",
                )

            numFields = len(mes.fields)
            if not numFields:
                raise noFields()

            moveTxt = moveStr
            mes.set_field_at(
                numFields - 1,
                inline=False,
                name=f"{Who2Move.n} Move #{Who2Move.t} ",
                value=f"{moveTxt}",
            )

            mes.description = f"{totRounds}/{ROUND_LIMIT} Total Rounds"
            await bat.echoMes(mes, thrd)
        if not winner and totRounds >= ROUND_LIMIT:
            winner = "exhaustion"
        elif winner:
            if not winner == "Noone":
                totRounds = winner.t

    winnerName = winner.n if isinstance(winner, player) else winner
    if saveOpp:
        saveNew = not bool(winnerName == bat.playerList[0].n)
        savePers(saveOpp, saveNew)
    if output:
        damageMes = ""
        for peep in bat.playerList:
            damageMes += f"{peep.n} took {peep.dT:.4g} damage.\n"
        mes.clear_fields()
        mes.add_field(
            name=(
                f"Winner is {winnerName}"
                f" after {totRounds} move{pluralInt(totRounds)}."
            ),
            value=("Prize to be implemented.\n" + damageMes),
        )
        if isinstance(winner, player):
            mes.set_thumbnail(url=winner.picUrl)
        await bat.echoMes(mes, thrd)
        await bat.echoMes(f"<#{ctx.channel.id}>", thrd, False)
        await thrd.edit(archived=1)
        await ctx.send(embed=mes)
    return winnerName


async def playerDuelInput(
    bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot],
    ctx: commands.Context,
    totRounds: int,
    peep: player,
    battle: battler,
):
    if len(battle.playerList) == 2:
        if peep is battle.playerList[0]:
            notPeep = battle.playerList[1]
        else:
            notPeep = battle.playerList[0]
    else:
        raise notADuel(
            f"Expected a Duel with 2 players not {len(battle.playerList)}"
        )
    statsMes = peep.statMessage()
    statsMes += "\n\n" + battle.adpList(peep)
    stats2Mes = notPeep.statMessage()
    stats2Mes += "\n\n" + battle.adpList(notPeep)

    moveStr = ""
    reactionList = []
    moveList = []
    chosenMove = False

    for key in moveOpt.keys():
        moveCost = moveOpt[key]["cost"]
        if moveCost <= peep.sta:
            react = [
                moveOpt[key]["reaction"],
                moveOpt[key]["type"],
                key,
            ]
            moveStr += f"{react[0]}: ({moveCost}) {moveOpt[key]['name']}\n"
            moveList.append(key)
            reactionList.append(react)

    mes = discord.Embed(
        title="Game Stats",
        description=f"{totRounds}/{ROUND_LIMIT} Total Rounds",
    )
    mes.add_field(name="Your Current", value=statsMes)
    mes.add_field(name="Opponent", value=stats2Mes)
    mes.set_footer(text=HOST_NAME, icon_url=bot.user.display_avatar)
    if peep.missTurn:
        moveStr = "You are exhausted."
    mes.add_field(
        inline=False,
        name=f"Available Moves ({peep.sta} Stamina)",
        value=moveStr,
    )

    if notPeep.play:
        timeOut = PLAYER_TURN_WAIT
    else:
        timeOut = BOT_TURN_WAIT
    moveView = None
    if not peep.missTurn:
        moveView = duelMoveView(reactionList)
    msg: discord.Message = await peep.p.send(embed=mes, view=moveView)

    def check(interaction: discord.Interaction):
        return (
            interaction.user.id == peep.p.id
            and interaction.message.id == msg.id
        )

    moveString = ""
    while not peep.missTurn and not moveView.is_finished():
        try:
            interaction: discord.Interaction = await bot.wait_for(
                "interaction",
                timeout=timeOut,
                check=check,
            )
            move = interaction.data["custom_id"]
            desperate = moveOpt[move]["desperate"]
            typeMove = moveOpt[move]["type"]
            moveString = moveOpt[move]["moveStr"]
            chosenMove = True
            moveView.stop()
            await msg.edit(view=None)

        except asyncio.TimeoutError:
            moveView.stop()
            await msg.edit(view=None)
    if chosenMove and moveString != "MakeBot":
        if "Focus" == moveString:
            peep.focus()
            [desperate, typeMove, moveString], notPeep = await playerDuelInput(
                bot, ctx, totRounds, peep, battle
            )
    else:
        if moveString == "MakeBot":
            peep.play = False
        desperate, typeMove, moveString = battle.moveSelf(peep, notPeep)
    return [desperate, typeMove, moveString], notPeep


async def testBattle(
    bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot],
    ctx: commands.Context,
    peepBuild: typing.Union[int, str],
    notPeepBuild: typing.Union[int, str],
    generations: int,
    repeats: int,
    defCost: int,
    outType: int,
):
    mes = ""
    winnerList = []
    testStart = time.time()
    win: dict[int, dict] = {}
    loss: dict[int, dict] = {}
    totRound = int(0)

    for generation in range(generations):
        p1Build = []
        p2Build = []

        buffList = []

        peepBuild, p1Cost, p1Build = checkDefined(ctx, peepBuild)
        buff = False
        if not p1Build and isinstance(peepBuild, int):
            p1Build, p1Cost = checkUndefined(
                ctx, peepBuild, notPeepBuild, defCost
            )
            buff = True
        buffList.append(buff)

        notPeepBuild, p2Cost, p2Build = checkDefined(ctx, notPeepBuild)
        buff = False
        if not p2Build and isinstance(notPeepBuild, int):
            p2Build, p2Cost = checkUndefined(
                ctx, notPeepBuild, peepBuild, defCost
            )
            buff = True
        buffList.append(buff)

        p1FPC = NPCFromBuild(bot, p1Build, "Peep")
        p2FPC = NPCFromBuild(bot, p2Build, "NotPeep")
        if outType >= 1:
            mes += (
                f"Gen: {generation+1}\n"
                f"   {p1Cost}: {buffList[0]} - {p1Build}\n"
                f"   {p2Cost}: {buffList[1]} - {p2Build}\n"
            )
        roundList = []
        for round in range(repeats):
            bat = battler(bot, [p1FPC, p2FPC])
            for i, toBuff in enumerate(buffList):
                if toBuff:
                    await bat.playerList[i].genBuff()

            duelTask = asyncio.create_task(startDuel(bot, ctx, bat, False))
            await asyncio.wait_for(duelTask, timeout=60)
            winner = duelTask.result()
            totRound += 1
            winnerList.append(winner)
            roundList.append(winner)
            if winner == "Peep":
                win[totRound] = dictShrtBuild(p1Build)
                loss[totRound] = dictShrtBuild(p2Build)
            elif winner == "NotPeep":
                win[totRound] = dictShrtBuild(p2Build)
                loss[totRound] = dictShrtBuild(p1Build)
            else:
                win[totRound] = {}
                loss[totRound] = {}
            if outType >= 2:
                mes += f"    Round: {round+1} - {winner}\n"
        if outType >= 1:
            mes += f"      {winPercent(roundList)}\n"
    timeTaken = time.time() - testStart
    mes += f"\nTest took: {datetime.timedelta(seconds=int(timeTaken))}"
    if timeTaken > 120:
        mes += f" <@{ctx.author.id}>"

    winSum = {}
    lossSum = {}
    pickList = [x for x in leader.keys() if leader[x] not in restrictedList]
    for key in pickList:
        winSum.setdefault(key, [0, 0])
        lossSum.setdefault(key, [0, 0])
        for i in range(1, totRound + 1):
            winTemp = win[i].get(key, 0)
            lossTemp = loss[i].get(key, 0)
            winSum[key][0] += winTemp
            lossSum[key][0] += lossTemp
            if winTemp:
                winSum[key][1] += 1
            if lossTemp:
                lossSum[key][1] += 1

    embMes = discord.Embed(title=f"Totals {winPercent(winnerList)}")
    for key in pickList:
        weightedAv = (winSum[key][0] / totRound) - (lossSum[key][0] / totRound)
        embMes.add_field(
            name=(f"{leader[key]}: {weightedAv:0.2f}"),
            value=(
                f"{winSum[key][1]} winners, {lossSum[key][1]} losers\n"
                f"Winners total {winSum[key][0]} or  "
                f"WinAv of {winSum[key][0]/max(1,winSum[key][1]):0.2f} and "
                f"TotAv of {winSum[key][0]/totRound:0.2f}\n"
                f"Losers total of {lossSum[key][0]} or "
                f"LossAv of {lossSum[key][0]/max(1,lossSum[key][1]):0.2f} and "
                f"TotAv of {lossSum[key][0]/totRound:0.2f}\n"
            ),
        )
    await sendMessage(ctx, mes)
    await sendMessage(ctx, embMes)


async def testInteractiveBattle(
    bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot],
    ctx: commands.Context,
    peepBuild: typing.Union[int, str],
    notPeepBuild: typing.Union[int, str],
    gens: int,
    repeats: int,
    defCost: int,
    outType: int,
    taskRank: str,
):
    patrolRole = get(ctx.guild.roles, id=int(ROLE_ID_PATROL))
    supRole = get(ctx.guild.roles, name=SUPE_ROLE)
    onCallRole = get(ctx.guild.roles, id=int(ROLE_ID_CALL))

    mes = ""
    winnerList = []
    testStart = time.time()
    win: dict[int, dict] = {}
    loss: dict[int, dict] = {}
    totRound = int(0)

    aidPick = [patrolRole, onCallRole, supRole]
    taskAdd = taskVar["addP"][taskRank]
    for generation in range(gens):
        aidList = pickWeightedSupe(ctx, aidPick, AID_WEIGHT, taskAdd)
        p1Build = []
        p2Build = []

        peepBuild, p1Cost, p1Build = checkDefined(ctx, peepBuild)
        if not p1Build and isinstance(peepBuild, int):
            p1Build, p1Cost = checkUndefined(
                ctx, peepBuild, notPeepBuild, defCost
            )

        notPeepBuild, p2Cost, p2Build = checkDefined(ctx, notPeepBuild)
        if not p2Build and isinstance(notPeepBuild, int):
            p2Build, p2Cost = checkUndefined(
                ctx, notPeepBuild, peepBuild, defCost
            )

        p1FPC = NPCFromBuild(bot, p1Build, "Peep")
        p2FPC = NPCFromBuild(bot, p2Build, "NotPeep")
        if outType >= 1:
            mes += (
                f"Gen: {generation+1}\n"
                f"   {p1Cost} - {p1Build}\n"
                f"   {p2Cost} - {p2Build}\n"
            )
        roundList = []

        bat = battler(bot, [p1FPC, p2FPC])
        playerStats = await buffAidList(ctx, aidList, bat, False)

        if isinstance(playerStats, tuple):
            playerBuffs = playerStats[1]
            playerStats = playerStats[0]

            if outType >= 2:
                buffStr = [
                    x if isinstance(x, dict) else x.to_dict()
                    for x in playerBuffs
                ]
                buffStrMes = [f"      {x}\n" for x in buffStr]
                mes += "    Buffs:\n"
                for mesPart in buffStrMes:
                    mes += mesPart

        for round in range(repeats):
            bat = battler(bot, [p1FPC, p2FPC])
            bat.playerList = playerStats

            duelTask = asyncio.create_task(startDuel(bot, ctx, bat, False))
            await asyncio.wait_for(duelTask, timeout=60)
            winner = duelTask.result()
            totRound += 1
            winnerList.append(winner)
            roundList.append(winner)
            if winner == "Peep":
                win[totRound] = dictShrtBuild(p1Build)
                loss[totRound] = dictShrtBuild(p2Build)
            elif winner == "NotPeep":
                win[totRound] = dictShrtBuild(p2Build)
                loss[totRound] = dictShrtBuild(p1Build)
            else:
                win[totRound] = {}
                loss[totRound] = {}
            if outType >= 3:
                mes += f"    Round: {round+1} - {winner}\n"
        if outType >= 1:
            mes += f"      {winPercent(roundList)}\n"
    timeTaken = time.time() - testStart
    mes += f"\nTest took: {datetime.timedelta(seconds=int(timeTaken))}"
    if timeTaken > 120:
        mes += f" <@{ctx.author.id}>"

    winSum = {}
    lossSum = {}
    pickList = [x for x in leader.keys() if leader[x] not in restrictedList]
    for key in pickList:
        winSum.setdefault(key, [0, 0])
        lossSum.setdefault(key, [0, 0])
        for i in range(1, totRound + 1):
            winTemp = win[i].get(key, 0)
            lossTemp = loss[i].get(key, 0)
            winSum[key][0] += winTemp
            lossSum[key][0] += lossTemp
            if winTemp:
                winSum[key][1] += 1
            if lossTemp:
                lossSum[key][1] += 1

    embMes = discord.Embed(title=f"Totals {winPercent(winnerList)}")
    for key in pickList:
        weightedAv = (winSum[key][0] / totRound) - (lossSum[key][0] / totRound)
        embMes.add_field(
            name=(f"{leader[key]}: {weightedAv:0.2f}"),
            value=(
                f"{winSum[key][1]} winners, {lossSum[key][1]} losers\n"
                f"Winners total {winSum[key][0]} or  "
                f"WinAv of {winSum[key][0]/max(1,winSum[key][1]):0.2f} and "
                f"TotAv of {winSum[key][0]/totRound:0.2f}\n"
                f"Losers total of {lossSum[key][0]} or "
                f"LossAv of {lossSum[key][0]/max(1,lossSum[key][1]):0.2f} and "
                f"TotAv of {lossSum[key][0]/totRound:0.2f}\n"
            ),
        )
    await sendMessage(ctx, mes)
    await sendMessage(ctx, embMes)


def NPC_from_diff(
    bot: typing.Union[commands.bot.Bot, commands.bot.AutoShardedBot],
    ctx: commands.Context,
    diffVal: int,
    member=None,
):
    if not member:
        member = ctx.author
    authCount = count(member)
    genVal = authCount[0] + diffVal
    build = genBuild(genVal)

    peepName: list = random.choice(activeDic["person"])
    peepName = str(peepName[0]).capitalize()

    FPC = NPCFromBuild(bot, build, peepName)
    return FPC


async def buffAidList(ctx: commands.Context, aidList, bat: battler, out=True):
    if aidList:
        peepBuffDict, aidNames = bat.playerList[0].grabExtra(ctx, aidList)
        notPeepBuffDict = bat.playerList[1].grabExtra(ctx, aidList, True)[0]

        peepEmb = buffStrGen(peepBuffDict, bat.playerList[0].n, aidNames)

        notPeepEmb = buffStrGen(
            notPeepBuffDict, bat.playerList[1].n, aidNames, True
        )
        if out:
            retList: typing.Union[list[discord.Embed], list[dict]] = [
                peepEmb,
                notPeepEmb,
            ]
        else:
            retList = [peepBuffDict, notPeepBuffDict]
        return bat.playerList, retList

    else:
        if out:
            await bat.playerList[1].genBuff(ctx)
        else:
            await bat.playerList[1].genBuff()
        return bat.playerList
