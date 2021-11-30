# battle.py
import discord
import random
from BossSystemExecutable import nON
from enhancements import funcBuild, spent
from power import power, leader

DEBUG = 0


def debug(*args):
    if DEBUG:
        print(*args)


HP = 10
ST = 5
STAR = 1
PA = 1
PD = 0
MA = 1
MD = 0
AC = 95
EV = 5
SWI = 10


class player:
    def __init__(self, member: discord.Member) -> None:
        self.p = member
        self.n = nON(member)

        self.sG = spent([member])
        self.fB = funcBuild(self.sG[0][2])
        self.stats = self.fB[2]

        self.iniCalc()

        self.hp = float(HP + self.calcHP())
        self.totHP = float(HP + self.calcHP())

        self.rec = self.calcREC()

        self.sta = ST
        self.star = STAR + self.calcSTAR()

        self.pa = PA + self.calcPA()
        self.pd = PD + self.calcPD()

        self.ma = MA + self.calcMA()
        self.md = MD + self.calcMD()

        self.acc = AC + self.calcAC()
        self.eva = EV + self.calcEV()

        self.swi = SWI + self.calcSWI()

        self.swiNow = 0

    def iniCalc(self) -> None:
        statDict = {}
        for enhan in self.sG[0][2]:
            debug("enhan:", enhan)
            name = enhan[:3]
            rank = int(power[enhan]["Rank"])
            if name not in statDict.keys():
                debug("Add", name, rank)
                statDict[name] = rank
            elif rank > statDict[name]:
                debug("Up", name, rank)
                statDict[name] = rank

        debug(statDict)

        for type in leader.keys():
            debug("type:", type)
            if type not in statDict.keys():
                debug("added")
                statDict[type] = 0
        debug(statDict)
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

    def calcHP(self) -> int:
        # Health - Pai 5 (50) (+10/turn)
        ret = 5 * self._pai + self._reg
        if self._pai == 10:
            ret += self._pai
        return ret

    def calcREC(self) -> int:
        ret = 2 * self._reg
        return ret

    def calcSTAR(self) -> int:
        ret = 0
        if self._reg == 10:
            ret += int(1)
        return ret

    def calcPA(self) -> int:
        # Physical Attack - Str/4th 4 Spd 2 (60)
        if self._4th > self._str:
            co = self._4th
        else:
            co = self._str
        ret = self._spe * 1 + co * 4
        if self._spe == 10:
            ret += int(self._spe * 0.1)
        if co == 10:
            ret += 5
        return ret

    def calcPD(self) -> int:
        # Physical Defense - End 4 Spd 2 (60)
        ret = self._end * 4 + self._spe * 1
        if self._end == 10:
            ret += int(self._end * 0.5)
        return ret

    def calcMA(self) -> int:
        # Mental Attack - Mem/Int 4 Cel 2 (60)
        if self._int > self._mem:
            co = self._int
        else:
            co = self._mem
        ret = self._cel * 1 + co * 4
        if self._cel == 10:
            ret += int(self._cel * 0.1)
        if co == 10:
            ret += 5
        return ret

    def calcMD(self) -> int:
        # Mental Defense - Cla 4 Cel 2 (60)
        ret = self._cla * 4 + self._cel * 1
        if self._cla == 10:
            ret += int(self._cla * 0.5)
        return ret

    def calcAC(self) -> int:
        # Accuracy - Vis/Omn 4 Aur/Olf 3 Gus/Tac 1 Pro 2 (100)
        if self._omn > self._vis:
            co = self._omn
        else:
            co = self._vis
        ret = (
            4 * co
            + 3 * (self._aur + self._olf)
            + 2 * self._pro
            + 1 * (self._gus + self._tac)
        )
        if co == 10:
            ret += 8
        if self._aur == 10:
            ret += int(self._aur * 0.5)
        if self._olf == 10:
            ret += int(self._olf * 0.5)
        if self._gus == 10:
            ret += int(self._gus * 0.3)
        if self._tac == 10:
            ret += int(self._tac * 0.3)
        if self._pro == 10:
            ret += int(self._pro * 0.4)
        return ret

    def calcEV(self) -> int:
        # Evasion - Inv 4 Aur/Olf 1 Gus/Tac 3 Pro 2 (100)
        ret = (
            4 * self._inv
            + 3 * (self._tac + self._gus)
            + 2 * self._pro
            + 1 * (self._aur + self._olf)
        )
        if self._inv == 10:
            ret += int(self._inv * 0.8)
        if self._aur == 10:
            ret += int(self._aur * 0.3)
        if self._olf == 10:
            ret += int(self._olf * 0.3)
        if self._gus == 10:
            ret += int(self._gus * 0.5)
        if self._tac == 10:
            ret += int(self._tac * 0.5)
        if self._pro == 10:
            ret += int(self._pro * 0.4)
        return ret

    def calcSWI(self) -> int:
        ret = self._spe + self._cel
        if self._spe == 10:
            ret += int(self._spe * 0.2)
        if self._cel == 10:
            ret += int(self._cel * 0.2)
        return ret

    def bStat(self):
        return (
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
            self.star,
        )


class battler:
    def __init__(
        self, member1: discord.Member, member2: discord.Member
    ) -> None:
        self.p1 = player(member1)
        self.p2 = player(member2)
        self.n1 = nON(member1)
        self.n2 = nON(member2)

    def nextRound(self):
        p1Swi = self.p1.swiNow
        p2Swi = self.p2.swiNow
        Who2Move = [None, None]
        while p1Swi < 50 and p2Swi < 50:
            p1Swi += self.p1.swi
            p2Swi += self.p2.swi
            debug("p1Swi:", p1Swi, "p2Swi:", p2Swi)

        if p1Swi >= 50:
            p1Swi -= 50
            Who2Move[0] = self.p1
        if p2Swi >= 50:
            p2Swi -= 50
            Who2Move[1] = self.p2

        self.p1.swiNow = p1Swi
        self.p2.swiNow = p2Swi

        return Who2Move

    def move(
        self,
        Who2Move: list[player],
        p1Move: str = "None",
        p2Move: str = "None",
    ):
        debug("Who2Move", Who2Move)
        moves = ["Does Nothing.", "Does Nothing.", None]
        if self.p1 in Who2Move and self.p2 in Who2Move:
            if self.p1.swiNow == self.p2.swiNow:
                first = random.choice(Who2Move)
            elif self.p1.swiNow > self.p2.swiNow:
                first = self.p1
            else:
                first = self.p2

            if first == self.p1:
                moves[0] = self.attack(self.p1, self.p2, p1Move)
                if self.p2.hp > 0:
                    moves[1] = self.attack(self.p2, self.p1, p2Move)
            else:
                moves[1] = self.attack(self.p2, self.p1, p2Move)
                if self.p1.hp > 0:
                    moves[0] = self.attack(self.p1, self.p2, p1Move)
        else:
            for peep in Who2Move:
                if not peep:
                    continue
                if peep == self.p1:
                    moves[0] = self.attack(self.p1, self.p2, p1Move)
                else:
                    moves[1] = self.attack(self.p2, self.p1, p2Move)

        if self.p1.hp <= 0 or self.p2.hp <= 0:
            debug("p1 Hp:", self.p1.hp, "p2 Hp:", self.p2.hp)
            if self.p1.hp == self.p2.hp:
                moves[2] = "Noone"
            elif self.p1.hp > self.p2.hp:
                moves[2] = self.n1
            else:
                moves[2] = self.n2

        return moves

    def attack(self, attacker: player, defender: player, attMove: str):
        mes = ""

        if attMove == "None":
            if attacker.pa - defender.pd > attacker.ma - defender.md:
                attMove = "PhysA"
            else:
                attMove = "MentA"

        if attacker.totHP > attacker.hp:
            strtHp = attacker.hp
            attacker.hp += attacker.rec
            if attacker.hp > attacker.totHP:
                attacker.hp = attacker.totHP
            heal = attacker.hp - strtHp
            mes += "{} heals for {}.\n".format(attacker.n, heal)

        attChance = attacker.ac - defender.ev
        critChance = 0
        superChance = 0
        if attChance > 100:
            critChance = attChance - 100
            attChance = 100
        if attChance < 0:
            attChance = 0
        missChance = 100 - attChance
        debug("attChance", attChance, "missChance", missChance)
        hit = random.choices(
            ["Hit", "Missed"],
            [attChance, missChance],
        )
        if "Missed" in hit:
            multi = float(0)
        else:

            if critChance > 100:
                superChance = critChance - 100
                critChance = 100
            normChance = 100 - critChance
            debug("normChance", normChance, "critChance", critChance)
            hit = random.choices(
                ["Normal", "Critical"], [normChance, critChance]
            )
            if "Normal" in hit:
                multi = float(1)
            else:
                notSuper = 100 - superChance
                debug("superChance", superChance, "notSuper", notSuper)
                hit = random.choices(
                    ["Critical", "Super"], [notSuper, superChance]
                )
                if "Critical" in hit:
                    multi = float(1.5)
                else:
                    multi = float(2)
        mes += "{}'s attack is a {} attack.\n".format(attacker.n, hit[0])

        if attMove == "PhysA":
            attDmg = multi * (attacker.pa - defender.pd)
            if attDmg < int(0):
                attDmg = int(0)
            defender.hp = defender.hp - attDmg
            mes += "{} physically attacks {} for {} damage.".format(
                attacker.n, defender.n, attDmg
            )
            debug("physical attack is a:", hit, "for", attDmg)
        if attMove == "MentA":
            attDmg = multi * (attacker.ma - defender.md)
            if attDmg < int(0):
                attDmg = int(0)
            defender.hp = defender.hp - attDmg
            mes += "{} mentally attacks {} for {} damage.".format(
                attacker.n,
                defender.n,
                attDmg,
            )
            debug("mental attack is a:", hit, "for", attDmg)

        return mes
