# battle.py
import discord

from BossSystemExecutable import nON, debug
from enhancements import funcBuild, spent
from power import power, leader

HP = 10
ST = 5
PA = 1
PD = 0
MA = 1
MD = 0
AC = 95
EV = 5
ACT = 10


class player:
    def __init__(self, member: discord.Member) -> None:
        self.p = member
        self.n = nON(member)

        self.sG = spent([member])
        self.fB = funcBuild(self.sG[0][2])
        self.stats = self.fB[2]

        self.iniCalc()

        self.hp = HP + self.calcHP()
        self.st = ST
        self.rec = self.calcREC()
        self.pa = PA + self.calcPA()
        self.pd = PD + self.calcPD()
        self.ma = MA + self.calcMA()
        self.md = MD + self.calcMD()
        self.ac = AC + self.calcAC()
        self.ev = EV + self.calcEV()
        self.act = ACT + self.calcACT()

    def iniCalc(self):
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
        return 5 * self._pai + self._reg

    def calcREC(self) -> int:
        return 2 * self._reg

    def calcPA(self) -> int:
        # Physical Attack - Str/4th 4 Spd 2 (60)
        if self._4th > self._str:
            co = self._4th
        else:
            co = self._str
        return self._spe * 1 + co * 4

    def calcPD(self) -> int:
        # Physical Defense - End 4 Spd 2 (60)
        return self._end * 4 + self._spe * 1

    def calcMA(self) -> int:
        # Mental Attack - Mem/Int 4 Cel 2 (60)
        if self._int > self._mem:
            co = self._int
        else:
            co = self._mem
        return self._cel * 1 + co * 4

    def calcMD(self) -> int:
        # Mental Defense - Cla 4 Cel 2 (60)
        return self._cla * 4 + self._cel * 1

    def calcAC(self) -> int:
        # Accuracy - Vis/Omn 4 Aur/Olf 3 Gus/Tac 1 Pro 2 (100)
        if self._omn > self._vis:
            co = self._omn
        else:
            co = self._vis
        return (
            4 * co
            + 3 * (self._aur + self._olf)
            + 2 * self._pro
            + 1 * (self._gus + self._tac)
        )

    def calcEV(self) -> int:
        # Evasion - Inv 4 Aur/Olf 1 Gus/Tac 3 Pro 2 (100)
        return (
            4 * self._inv
            + 3 * (self._tac + self._gus)
            + 2 * self._pro
            + 1 * (self._aur + self._olf)
        )

    def calcACT(self) -> int:
        return self._spe + self._cel

    def bStat(self):
        return (
            self.hp,
            self.pa,
            self.pd,
            self.ma,
            self.md,
            self.rec,
            self.ac,
            self.ev,
            self.act,
        )


class battler:
    def __init__(
        self, member1: discord.Member, member2: discord.Member
    ) -> None:
        self.p1 = player(member1)
        self.p2 = player(member2)
        self.n1 = nON(member1)
        self.n2 = nON(member2)
