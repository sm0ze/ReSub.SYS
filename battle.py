# battle.py

import asyncio
import random
import typing
from collections import namedtuple

import discord

import log
from sharedFuncs import funcBuild, nON, spent
from power import (
    leader,
    moveOpt,
    power,
    baseDict,
    statCalcDict,
    replaceDict,
    bonusDict,
)

logP = log.get_logger(__name__)

statMes = """{17}
HP:\t{0:0.2g}/{9:0.2g} (**{13}%**) + {5} ({18}%)
Sta: **{10}**/{12} +{11}
P: {1}A/{2:0.2g}D
M: {3}A/{4:0.2g}D
Acc/Eva({16}): {6}/{7}
Swi: {14}/{15} +{8}"""


adpMes = """

**Adapted Stats**
Hit%: PA/MA
{2}%: {0:0.2g}/{1:0.2g}"""

DELIM = 16

rendHP = {
    "empt": "░",
    "partLo": "▒",
    "partHi": "▓",
    "full": "█",
}


class player:
    def __init__(
        self,
        member,
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
        else:
            self.p = None
            self.n = member[0]
            self.sG = None
            self.bL = member[-1]
            self.npc = True
            self.pic = member[1]

        self.fB = funcBuild(self.bL)
        self.stats = self.fB[2]

        self.t = int(0)
        self.play = False

        self.iniCalc()

        addHP = float(int(baseDict["HP"]) + self.calcStat("HP"))

        self.hp = addHP
        self.totHP = addHP

        self.rec = int(baseDict["REC"]) + self.calcStat("Rec")

        self.sta = int(baseDict["STA"]) + self.calcStat("Sta")
        self.totSta = int(baseDict["STATOT"]) + self.calcStat("StaTot")
        self.staR = int(baseDict["STAR"]) + self.calcStat("StaR")

        self.pa = int(baseDict["PA"]) + self.calcStat("PA")
        self.pd = float(int(baseDict["PD"]) + self.calcStat("PD"))

        self.ma = int(baseDict["MA"]) + self.calcStat("MA")
        self.md = float(int(baseDict["MD"]) + self.calcStat("MD"))

        self.acc = int(baseDict["ACC"]) + self.calcStat("Acc")
        self.eva = int(baseDict["EVA"]) + self.calcStat("Eva")

        self.swi = int(baseDict["SWI"]) + self.calcStat("Swi")
        self.totSwi = int(baseDict["SWITOT"])

        self.swiNow = int(0)
        self.defending = str("")
        self.noDef = bool(False)
        self.tired = int(0)
        self.missTurn = int(0)

        self.weak = bool(False)

        self.focusNum = int(0)
        self.focused = False

    def iniCalc(self) -> None:
        statDict = {}
        for enhan in self.bL:
            logP.debug(f"enhan: {enhan}")
            name = enhan[:3]
            rank = int(power[enhan]["Rank"])
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

    def calcStat(self, statType) -> int:
        ret = int(0)
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
            self.focusNum,
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

    def defend(self, defType: str = "Physical"):
        defAlr = False
        addOn = ""
        if not self.defending:
            self.defending = defType
            val = float(2)
        else:
            defType = self.defending
            val = float(0.5)
            defAlr = True

        if self.defending == "Physical":
            if self.noDef and val == float(0.5):
                self.noDef = not self.noDef
                val = float(0)
            elif not self.noDef and val == float(2) and not self.pd:
                self.noDef = not self.noDef
                self.pd = 1.5

            self.pd = float(val * self.pd)

        elif self.defending == "Mental":
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

        ret = f"{self.n} is {addOn}defending from {defType} attacks"
        if not defAlr:
            ret += f" and recovers {self.recSta()} additional stamina.\n"
        else:
            ret += ".\n"
        return ret

    def recSta(self, val: int = 1) -> int:
        staStrt = self.sta
        self.sta += val
        if self.sta > self.totSta:
            self.sta = self.totSta
        staEnd = self.sta
        return staEnd - staStrt

    def recHP(self, val: int = 1):
        strtHP = self.hp
        self.hp += val
        if self.hp > self.totHP:
            self.hp = self.totHP
        endHP = self.hp
        return endHP - strtHP

    async def ask(
        self,
    ):
        if self.npc:
            return
        elif self.p.bot:
            return

        reactionList = ["✅", "❌"]
        mes = discord.Embed(title="Do you wish to play a duel?")
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
                f"{self.n} has {self.hpPer()}% HP and has halved "
                "defenses until their next turn.\n"
            )
        else:
            self.md = self.md * 2
            self.pd = self.pd * 2
            mes += f"{self.n} no longer has lowered defenses.\n"
        return mes

    def focus(self, inc: bool = True):
        self.focused = bool(False)
        if inc:
            self.focusNum += 1
            self.sta -= 1
            self.eva += 5
            self.acc += 5
        else:
            while self.focusNum:
                self.focusNum -= 1
                self.eva -= 5
                self.acc -= 5

    def focusTill(self, num: int = 2):
        if self.sta > num:
            while self.sta > num:
                self.focus()


class battler:
    def __init__(self, bot, member1: discord.Member, member2) -> None:
        self.p1 = player(member1, bot)
        self.n1 = self.p1.n

        self.p2 = player(member2, bot)
        self.n2 = self.p2.n

        self.totSwi = int(baseDict["SWITOT"])

    async def echoMes(self, mes, thrd, toThrd: bool = True):
        if isinstance(mes, discord.Embed):
            if self.p1.play:
                await self.p1.p.send(embed=mes)
            if self.p2.play:
                await self.p2.p.send(embed=mes)
            if toThrd:
                await thrd.send(embed=mes)
        elif isinstance(mes, str):
            if self.p1.play:
                await self.p1.p.send(mes)
            if self.p2.play:
                await self.p2.p.send(mes)
            if toThrd:
                await thrd.send(mes)

    async def findPlayers(self, dontAsk, playList: list[player] = None):
        if not playList:
            playList = [self.p1, self.p2]

        for peep in playList:
            if not peep.npc:
                if not peep.p.bot:
                    if not dontAsk == 1:
                        await peep.ask()

    def nextRound(self) -> list[typing.Union[player, None]]:
        # TODO rewrite for more than 2 peeps
        p1Swi = self.p1.swiNow
        p2Swi = self.p2.swiNow
        Who2Move = [None, None]
        while p1Swi < self.totSwi and p2Swi < self.totSwi:
            p1Swi += self.p1.swi
            p2Swi += self.p2.swi
            logP.debug(f"p1Swi: {p1Swi}, p2Swi: {p2Swi}")

        if p1Swi == p2Swi:
            playerSwi = random.sample(
                [[p1Swi, 0, self.p1], [p2Swi, 1, self.p2]], k=2
            )
        else:
            playerSwi = sorted(
                [[p1Swi, 0, self.p1], [p2Swi, 1, self.p2]],
                key=lambda x: x[0],
                reverse=True,
            )

        for peep in playerSwi:
            if peep[0] >= self.totSwi:
                peep[0] -= self.totSwi
                Who2Move[peep[1]] = peep[2]
                break

        self.p1.swiNow = p1Swi
        self.p2.swiNow = p2Swi

        return Who2Move

    def move(
        self,
        Who2Move: list[player],
        p1Move: list[str] = None,
        p2Move: list[str] = None,
    ):
        logP.debug(f"Who2Move: {Who2Move}")
        moves = ["Does Nothing.", "Does Nothing.", None]
        if self.p1 in Who2Move and self.p2 in Who2Move:
            if self.p1.swiNow == self.p2.swiNow:
                first = random.choice(Who2Move)
            elif self.p1.swiNow > self.p2.swiNow:
                first = self.p1
            else:
                first = self.p2

            if first == self.p1:
                moves[0] = f"{self.p1.n} moves first!\n"
                moves[0] += self.turn(self.p1, self.p2, p1Move)
                if self.p2.hp > 0 and self.p1.hp > 0:
                    moves[1] = self.turn(self.p2, self.p1, p2Move)
            else:
                moves[1] = f"{self.p2.n} moves first!\n"
                moves[1] += self.turn(self.p2, self.p1, p2Move)
                if self.p2.hp > 0 and self.p1.hp > 0:
                    moves[0] = self.turn(self.p1, self.p2, p1Move)
        else:
            for peep in Who2Move:
                if not peep:
                    continue
                if peep == self.p1:
                    moves[0] = f"{self.p1.n} moves!\n"
                    moves[0] += self.turn(self.p1, self.p2, p1Move)
                else:
                    moves[1] = f"{self.p2.n} moves!\n"
                    moves[1] += self.turn(self.p2, self.p1, p2Move)

        if self.p1.hp <= 0 or self.p2.hp <= 0:
            logP.debug(f"p1 Hp: {self.p1.hp}, p2 Hp: {self.p2.hp}")
            if self.p1.hp == self.p2.hp:
                moves[2] = "Noone"
            elif self.p1.hp > self.p2.hp:
                moves[2] = self.p1.n
            else:
                moves[2] = self.p2.n

        return moves

    def turn(self, peep: player, attPeep: player, move: list[str]) -> str:
        mes = ""
        if peep.missTurn:
            extraSta = 1
            mes += f"{peep.n} misses this turn due to exhaustion!\n"
            mes += (
                f"This exhaustion means {peep.n} recovers an "
                f"additional {peep.recSta(extraSta)} stamina this turn.\n"
            )
        elif peep.weak:
            mes += peep.beWeak(False)
        # if peep.defending:
        #     mes += peep.defend()

        if not move:
            move = self.moveSelf(peep, attPeep)

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
                mes += f"{peep.n} recovered this turn for {staRec} stamina.\n"
                peep.sta += staRec

        if peep.focusNum and not peep.focused:
            peep.focused = bool(True)
        elif peep.focusNum and peep.focused:
            peep.focus(False)

        if not peep.sta:
            peep.missTurn = int(2)
            peep.tired += 1
            mes += (
                f"{peep.n} has exhausted themself ({peep.tired}) "
                "and will miss a turn.\n"
            )

        mes += self.recover(peep)

        if peep.tired == 3:
            mes += f"{peep.n} has exhausted themself for the third time!"
            if attPeep.hp < 0:
                peep.hp = attPeep.hp - 1
            else:
                peep.hp = float(0)

        if peep.missTurn:
            peep.missTurn -= 1
        return mes

    def moveSelf(self, peep: player, notPeep: player):
        moveStr = "Physical"
        desperate = 0
        typeMove = "Attack"

        Attack = self.adp(peep, notPeep)
        Defend = self.adp(notPeep, peep)

        normSta = moveOpt["physA"]["cost"]
        despSta = moveOpt["dPhysA"]["cost"]

        # norm attack value
        atk = Attack.phys

        # desperate attack value
        dAtk = Attack.phys + peep.pa

        critDesp = Attack.phys + 2 * peep.pa

        if Attack.ment > atk:
            moveStr = "Mental"
        elif Attack.ment == atk:
            moveStr = random.choice(["Physical", "Mental"])

        if moveStr == "Mental":
            # update attack values for mental attacks
            atk = Attack.ment
            dAtk = Attack.ment + peep.ma
            critDesp = Attack.ment + 2 * peep.ma

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

        if Attack.hitChance <= 50:
            # lowhit func
            logP.debug(f"lowHit: {Attack.hitChance}")
            if oneHit and Attack.hitChance + 5 * fAA > 50:
                while Attack.hitChance < 50 and peep.sta > normSta:
                    peep.focus()
                    Attack = self.adp(peep, notPeep)
                # then normal attack
            elif oneDespHit and Attack.hitChance + 5 * fAD > 50:
                while Attack.hitChance < 50 and peep.sta > despSta:
                    peep.focus()
                    Attack = self.adp(peep, notPeep)
                desperate = 1
                # then desp attaack
            elif maxSta:
                if oneHit or (
                    atk > notPeep.rec * (peep.totSta / (peep.staR + 1))
                ):
                    peep.focusTill(normSta)
                    # then normal attack
                else:
                    peep.focusTill(despSta)
                    desperate = 1
                    # then desp attaack
            else:
                typeMove = "Defend"

            if moveStr == "Mental":
                # update attack values for mental attacks
                atk = Attack.ment
                dAtk = Attack.ment + peep.ma
            else:
                atk = Attack.phys
                dAtk = Attack.phys + peep.pa

        elif Attack.hitChance < 75:
            # avhit func
            logP.debug(f"avHit: {Attack.hitChance}")
            if oneHit and nextHP > atk and canAt:
                peep.focusTill(normSta + 1)
                # then normal attack
            elif oneHit and staAftA >= 2:
                peep.focusTill(normSta + 1)
                # then normal attack
            elif oneDespHit and nextHP > dAtk and canDespAt:
                peep.focusTill(despSta)
                desperate = 1
                # then desperate attack
            elif oneDespHit and staAftD >= 2:
                peep.focusTill(despSta + 1)
                desperate = 1
                # then desperate attack
            elif maxSta:
                if nextHP <= dAtk * 2:
                    desperate = 1
                    # then desperate attack
                elif atk > notPeep.rec * (10 / (peep.rec + 1)):
                    pass
                    # then Normal attack
                else:
                    desperate = 1
                    # then desperate attack
            else:
                typeMove = "Defend"

        elif Attack.hitChance < 150:
            # highhit func
            logP.debug(f"highHit: {Attack.hitChance}")
            if oneHit and canAt:
                peep.focusTill(normSta + 1)
                # then normal hit
            elif oneDespHit and canDespAt:
                peep.focusTill(despSta + 1)
                desperate = 1
                # then desperate attack
            elif maxSta:
                if nextHP <= dAtk * 2:
                    desperate = 1
                    # then desperate attack
                elif dAtk < notPeep.rec * (10 / (peep.rec + 1)):
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
                peep.focusTill(normSta + 1)
                # then normal attack
            elif oneDespHit and canDespAt:
                peep.focusTill(despSta + 1)
                desperate = 1
                # then desperate attack
            elif notPeep.hp <= critDesp and staAftD >= 2:
                peep.focus()
                desperate = 1
                # then desperate attack
            elif maxSta:
                if critDesp * 2 >= nextHP:
                    desperate = 1
                    # then desperate attack
                elif critDesp < notPeep.rec * (10 / (peep.rec + 1)):
                    peep.focus()
                    desperate = 1
                    # then desperate attack
                else:
                    desperate = 1
            elif staAftA >= 1 and atk > notPeep.rec * 2:
                pass
                # then normal attack
            else:
                typeMove = "Defend"

        if typeMove == "Defend":
            # defend func
            if Defend.phys > Defend.ment:
                moveStr = "Physical"
            elif Defend.ment > Defend.phys:
                moveStr = "Mental"
            else:
                moveStr = random.choice(["Physical", "Mental"])

        return desperate, typeMove, moveStr

    def recover(self, peep: player) -> str:
        mes = ""
        staRec = peep.recSta(peep.staR)
        if staRec:
            mes += (
                f"{peep.n} recovers {staRec} stamina for a "
                f"running total of {peep.sta}.\n"
            )

        heal = peep.recHP(peep.rec)
        if heal:
            mes += f"{peep.n} heals for {heal:0.2g}.\n"
        peep.t += 1
        return mes

    def attack(
        self,
        attacker: player,
        defender: player,
        attMove: str,
        desperate: bool = 0,
    ) -> str:
        mes = ""

        if desperate:
            typeAtt = "desperately "
            staCost = 5
        else:
            typeAtt = ""
            staCost = 2

        attacker.sta -= staCost
        mes += f"{attacker.n} {typeAtt}attacks for {staCost} stamina.\n"

        if not attMove:
            if attacker.pa - defender.pd > attacker.ma - defender.md:
                attMove = "Physical"
            else:
                attMove = "Mental"

        if desperate and attacker.hpPer() > 50:
            mes += attacker.beWeak(True)

        attChance = attacker.acc - defender.eva
        critChance = 0
        dblCritChance = 0
        if attChance > 100:
            critChance = attChance - 100
            attChance = 100
        if attChance < 0:
            attChance = 0
        missChance = 100 - attChance
        logP.debug(f"attChance: {attChance}, missChance: {missChance}")
        hit = random.choices(
            ["Hit", "Missed"],
            [attChance, missChance],
        )
        if "Missed" in hit:
            multi = int(0)
        else:
            if critChance > 100:
                dblCritChance = critChance - 100
                critChance = 100
            normChance = 100 - critChance
            logP.debug(f"normChance: {normChance}, critChance: {critChance}")
            hit = random.choices(
                ["Normal", "Critical"], [normChance, critChance]
            )
            if "Normal" in hit:
                multi = int(1)
            else:
                if dblCritChance > 100:
                    triCritChance = dblCritChance - 100
                    dblCritChance = 100
                notDblCrit = 100 - dblCritChance
                logP.debug(
                    f"dblCritChance: {dblCritChance}, notDblCrit: {notDblCrit}"
                )
                hit = random.choices(
                    ["Critical", "Double Critical"],
                    [notDblCrit, dblCritChance],
                )
                if "Critical" in hit:
                    multi = int(2)
                else:
                    notTriCrit = 100 - triCritChance
                    logP.debug(
                        (
                            f"triCritChance: {triCritChance}, "
                            f"notTriCrit: {notTriCrit}"
                        )
                    )
                    hit = random.choices(
                        ["Double Critical", "Triple Critical"],
                        [notTriCrit, triCritChance],
                    )
                    if "Double Critical" in hit:
                        multi = int(3)
                    else:
                        multi = int(4)
        mes += f"{attacker.n}'s attack is a {hit[0]} attack.\n"

        if attMove == "Physical":
            attDmg = attackCalc(
                multi,
                attacker.pa,
                defender.pd,
                desperate,
            )
            if attDmg < int(0):
                attDmg = float(0)
            defender.hp = defender.hp - attDmg
            mes += (
                f"{attacker.n} physically attacks {defender.n} "
                f"for {attDmg:0.2g} damage.\n"
            )
            logP.debug(f"physical attack is a: {hit}, for: {attDmg}")
        if attMove == "Mental":
            attDmg = attackCalc(
                multi,
                attacker.ma,
                defender.md,
                desperate,
            )
            if attDmg < int(0):
                attDmg = float(0)
            defender.hp = defender.hp - attDmg
            mes += (
                f"{attacker.n} mentally attacks {defender.n} "
                f"for {attDmg:0.2g} damage.\n"
            )
            logP.debug(f"mental attack is a: {hit}, for: {attDmg}")

        return mes

    def adp(self, at1: player, at2: player):
        adpStats = namedtuple("adpStats", ["phys", "ment", "hitChance"])
        phys = at1.pa - at2.pd
        ment = at1.ma - at2.md
        hitChance = at1.acc - at2.eva

        ret = adpStats(phys, ment, hitChance)
        return ret

    def adpStatMessage(self, at1: player, at2: player):

        adaptedStats = self.adp(at1, at2)
        return adpMes.format(*adaptedStats)

    def isPlay(self, peep: player):
        return "Playing" if peep.play else "NPC" if peep.npc else "Bot"


def attackCalc(
    multi: int = 0,
    attckDmg: int = 0,
    defense: float = 0,
    desperate: bool = 0,
) -> float:
    if multi and desperate:
        multi += 1
    ret = multi * attckDmg - defense
    return ret


def addCalc(self, statType) -> int:
    ret = int(0)
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
            if soft > hard:
                logP.debug(f"Adding {replaceDict[stat]} to ignore List")
                ignore.append(replaceDict[stat])
    logP.debug(f"ignore: {ignore}")

    for stat in statCalcDict.keys():
        statAm = getattr(self, f"_{stat}")
        if not statAm or stat in ignore:
            continue
        try:
            addStat = statCalcDict[stat][statType]
        except KeyError:
            addStat = None
        if addStat:
            ret += statAm * addStat
            logP.debug(
                (
                    f"Adding rank {statAm} {stat} * {addStat} = "
                    f"{statAm * addStat} to {statType}."
                )
            )
    return ret


def addBonus(self, bonusType) -> int:
    ret = int(0)
    for stat in bonusDict.keys():
        addBonus = bonusDict[stat][bonusType]
        if addBonus:
            bonusStat = getattr(self, f"_{stat}")
            if bonusStat == 10:
                ret += addBonus
                logP.debug(
                    (
                        f"Adding a bonus of {addBonus} to {bonusType} "
                        f"for having 10 in {bonusStat}"
                    )
                )
    return ret
