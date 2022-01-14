# battle.py

import asyncio
import random
import typing
from collections import namedtuple

import discord
from discord.ext import commands

import log
from sharedConsts import (
    ASKALL,
    ASKNPC,
    ASKSELF,
    AVHIT,
    DRAWDEF,
    HIHIT,
    HITRANGE,
    LOHIT,
    WOUDMG,
)
from sharedDicts import (
    baseDict,
    bonusDict,
    leader,
    masterEhnDict,
    moveOpt,
    replaceDict,
    statCalcDict,
    attackRollDict,
    multiTypDict,
)
from sharedFuncs import funcBuild, intNPC, nON, sendMessage, spent

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
        self.pic = npcDict[picVar]
        self.bL = [x for x in npcEhn if int(x[3:])]


class player:
    def __init__(
        self,
        member: typing.Union[discord.Member, NPC, intNPC],
        bot,
    ) -> None:
        self.bot = bot

        if isinstance(member, discord.Member):
            self.p = member
            self.n = nON(member)
            self.sG = spent([member])
            self.bL = self.sG[0][2]
            self.npc = False
            self.pic = self.p.display_avatar
        elif isinstance(member, NPC):
            self.p = None
            self.n = member.n
            self.sG = None
            self.bL = member.bL
            self.npc = True
            self.pic = member.pic
        elif isinstance(member, intNPC):
            self.p = None
            self.n = member.n
            self.sG = None
            self.bL = member.bL
            self.npc = True
            self.pic = member.pic

        self.fB = funcBuild(self.bL)
        self.bC = self.fB[0]
        self.stats = self.fB[2]

        self.t = int(0)
        self.play = False

        self.iniCalc()

        addHP = baseDict["HP"] + self.calcStat("HP")

        self.hp = addHP
        self.totHP = addHP

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

    async def genBuff(self, place: discord.abc.Messageable):
        bonus = int(self.bC / 5)
        if bonus:
            if self._str + self._mem > 5:
                hpBonus = 3 * bonus
                self.totHP += hpBonus
                self.hp = self.totHP
                await place.send(f"Buffed HP by: {hpBonus}")

            elif (
                self._vis + self._olf + self._aur + self._spe + self._cel > 10
            ):
                atBonus = 0.5 * bonus
                hpBonus = 1.5 * bonus

                self.totHP += hpBonus
                self.hp = self.totHP

                self.pa += atBonus
                self.ma += atBonus

                await place.send(
                    f"Buffed MA & PA by: {atBonus}.\nBuffed HP by: {hpBonus}"
                )

            else:
                self.pa += bonus
                self.ma += bonus
                await place.send(f"Buffed MA & PA by: {bonus}")


class battler:
    def __init__(
        self,
        bot,
        memberList: list[typing.Union[discord.Member, NPC, intNPC]],
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
                await sendMessage(mes, peep.p)
        if toThrd:
            await sendMessage(mes, thrd)

    async def findPlayers(self, dontAsk):
        for peep in self.playerList:
            if isinstance(peep, player):
                if not peep.npc:
                    if not peep.p.bot:
                        if dontAsk == ASKSELF and (peep is self.playerList[0]):
                            await peep.ask(self.playerList)
                        elif dontAsk in [ASKALL, ASKNPC]:
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

        if peep.tired == 5:
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
        if peep.conDef >= DRAWDEF:
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

    def decAtk(self, Attack, peep):
        # norm attack value
        decAtk = max(
            [[Attack.phys, "physical"], [Attack.ment, "mental"]],
            key=lambda x: x[0],
        )
        atk = float(decAtk[0])
        atkStr = decAtk[1]

        # desperate attack value
        decDAtk = max(
            [
                [Attack.phys + peep.pa, "physical"],
                [Attack.ment + peep.ma, "mental"],
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

        atk, atkStr, dAtk, dAtkStr = self.decAtk(Attack, peep)

        decCritDesp = max(
            [
                [Attack.phys + 2 * peep.pa, "physical"],
                [Attack.ment + 2 * peep.ma, "mental"],
            ],
            key=lambda x: x[0],
        )
        critDesp = float(decCritDesp[0])
        critDespStr = decCritDesp[1]

        # peep stamina after norm attack
        staAftA = peep.sta - normSta

        # num of available focusses with a norm attack
        fAA = staAftA if staAftA > 0 else 0

        # peep stamina after desp attack
        staAftD = peep.sta - despSta

        # num of available focusses with a desp attack
        fAD = staAftD if staAftD > 0 else 0

        # notPeep's hp next peep turn
        nextHP = notPeep.hp + notPeep.rec

        # if peep at max stamina
        maxSta = bool(peep.sta == peep.totSta)

        # if notPeep is one norm hit from loss
        oneHit = bool(notPeep.hp <= atk)

        # if notPeep is one desp hit from loss
        oneDespHit = bool(notPeep.hp <= dAtk)

        canAt = bool(staAftA >= 0)
        canDespAt = bool(staAftD >= 0)

        HPS = notPeep.rec * (peep.totSta / (peep.staR + 1))

        if Attack.hitChance < LOHIT:
            # lowhit func
            logP.debug(f"lowHit: {Attack.hitChance}")
            if oneHit and Attack.hitChance + baseDict["FOC"] * fAA > 50:
                while Attack.hitChance < LOHIT and peep.sta > normSta:
                    peep.focus()
                    Attack = self.adp(peep, notPeep)
                # then normal attack
            elif oneDespHit and Attack.hitChance + baseDict["FOC"] * fAD > 50:
                while Attack.hitChance < LOHIT and peep.sta > despSta:
                    peep.focus()
                    Attack = self.adp(peep, notPeep)
                desperate = 1
                # then desp attaack
            elif maxSta:
                if atk < HPS and dAtk < HPS:
                    typeMove = "Defend"
                elif oneHit or atk > HPS:
                    while Attack.hitChance < LOHIT and peep.sta >= normSta:
                        peep.focus()
                        Attack = self.adp(peep, notPeep)
                    # then normal attack
                else:
                    while Attack.hitChance < AVHIT and peep.sta > despSta:
                        peep.focus()
                        Attack = self.adp(peep, notPeep)
                    desperate = 1
                    # then desp attaack
            else:
                typeMove = "Defend"

            atk, atkStr, dAtk, dAtkStr = self.decAtk(Attack, peep)

        elif Attack.hitChance <= AVHIT:
            # avhit func
            logP.debug(f"avHit: {Attack.hitChance}")
            if oneHit and canAt:
                peep.focusTill(normSta)
                # then normal attack
            elif oneDespHit and canDespAt:
                peep.focusTill(despSta)
                desperate = 1
                # then desperate attack
            elif maxSta:
                if atk < HPS and dAtk < HPS:
                    typeMove = "Defend"
                elif nextHP <= dAtk * 2:
                    desperate = 1
                    # then desperate attack
                else:
                    desperate = 1
                    # then desperate attack
            elif atk > notPeep.rec * 2:
                pass
                # then Normal attack
            else:
                typeMove = "Defend"

        elif Attack.hitChance < HIHIT:
            # highhit func
            logP.debug(f"highHit: {Attack.hitChance}")
            if oneHit and canAt:
                peep.focusTill(normSta)
                # then normal hit
            elif oneDespHit and canDespAt:
                peep.focusTill(despSta)
                desperate = 1
                # then desperate attack
            elif maxSta:
                if atk < HPS and dAtk < HPS:
                    typeMove = "Defend"
                elif nextHP <= dAtk * 2:
                    desperate = 1
                    # then desperate attack
                elif dAtk < notPeep.rec * ((despSta * 2) / (peep.staR + 1)):
                    peep.focus()
                    desperate = 1
                    # then desperate attack
                else:
                    desperate = 1
                    # then desperate attack
            elif staAftA >= 1 and atk > notPeep.rec * 2:
                pass
                # then normal attack
            else:
                typeMove = "Defend"

        else:
            logP.debug(f"critHit: {Attack.hitChance}")
            # crithit func
            if oneHit and canAt:
                peep.focusTill(normSta)
                # then normal attack
            elif notPeep.hp <= critDesp and canDespAt:
                peep.focusTill(despSta)
                desperate = 1
                moveStr = critDespStr
                # then desperate attack
            elif maxSta:
                if atk < HPS and dAtk < HPS and critDesp < HPS:
                    typeMove = "Defend"
                elif critDesp * 2 >= nextHP:
                    desperate = 1
                    moveStr = critDespStr
                    # then desperate attack
                elif dAtk < notPeep.rec * ((despSta * 2) / (peep.staR + 1)):
                    peep.focus()
                    desperate = 1
                    moveStr = critDespStr
                    # then desperate attack
                else:
                    desperate = 1
                    moveStr = critDespStr
            elif staAftA >= 1 and atk > notPeep.rec * 2:
                pass
                # then normal attack
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

        multiBase = int(baseDict["FOC"] + attacker.acc - defender.eva)
        multiRangeStart = multiBase - HITRANGE
        multiRangeStop = multiBase + HITRANGE

        multiRange = [
            float(attackRollDict[x])
            for x in range(multiRangeStart, multiRangeStop)
        ]

        multi = round(random.choice(multiRange), 3)
        typHit = multiTypDict.get(multi, "mistaken")

        logP.debug(f"Hit is '{typHit}' for '{multi}'")

        mes += f"a {typHit}:{multi} {'hit' if not riposte else 'riposte'}"

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

            if attDmg > WOUDMG:
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

            if attDmg > WOUDMG:
                defender.wou = True

            mes += f" for {attDmg:0.3g} mental damage.\n\n"
            logP.debug(f"mental attack is a: {typHit}, for: {attDmg}")

        if multi < -0.5:
            typDesp = 1 if multi == 1.5 else 0
            mes += "\n" + self.attack(defender, attacker, "", typDesp, True)

        return mes

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
