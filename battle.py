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
        if self._reg == 10:
            ret += int(self._reg * 0.5)
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

    def calcACT(self) -> int:
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
