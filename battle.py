# battle.py
import discord
import random
from BossSystemExecutable import nON
from enhancements import funcBuild, spent
from power import power, leader
import pandas as pd

DEBUG = 0


def debug(*args):
    if DEBUG:
        print(*args)


HP = 10
REC = 0
STA = 5
STATOT = 10
STAR = 1
PA = 1
PD = 0
MA = 1
MD = 0
ACC = 95
EVA = 5
SWI = 10

statsToken = "1JIJjDzFjtuIU2k0jk1aHdMr2oErD_ySoFm7-iFEBOV0"

statsName = "BotStats"
bonusName = "BotBonus"

replaceName = "BotReplace"
urlStats = (
    "https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=" "out:csv&sheet={}"
).format(statsToken, statsName)
urlBonus = (
    "https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=" "out:csv&sheet={}"
).format(statsToken, bonusName)
urlReplace = (
    "https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=" "out:csv&sheet={}"
).format(statsToken, replaceName)


statCalcDict = {}
bonusDict = {}

urlList = [[urlStats, statCalcDict], [urlBonus, bonusDict]]


class player:
    def __init__(self, member: discord.Member) -> None:
        self.p = member
        self.n = nON(member)
        self.t = int(0)

        self.sG = spent([member])
        self.fB = funcBuild(self.sG[0][2])
        self.stats = self.fB[2]

        self.iniCalc()

        addHP = float(HP + self.calcStat("HP"))

        self.hp = addHP
        self.totHP = addHP

        self.rec = REC + self.calcStat("Rec")

        self.sta = STA
        self.totSta = STATOT
        self.staR = STAR + self.calcStat("StaR")

        self.pa = PA + self.calcStat("PA")
        self.pd = PD + self.calcStat("PD")

        self.ma = MA + self.calcStat("MA")
        self.md = MD + self.calcStat("MD")

        self.acc = ACC + self.calcStat("Acc")
        self.eva = EVA + self.calcStat("Eva")

        self.swi = SWI + self.calcStat("Swi")

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

    def calcStat(self, statType) -> int:
        ret = int(0)
        ret += addCalc(self, statType)
        ret += addBonus(self, statType)
        debug("Adding to", statType, ret)
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
            self.staR,
            self.totSta,
        )


class battler:
    def __init__(
        self, member1: discord.Member, member2: discord.Member
    ) -> None:
        self.p1 = player(member1)
        self.n1 = nON(member1)

        self.p2 = player(member2)
        self.n2 = nON(member2)

        self.p1Adp = self.adp(self.p1, self.p2)
        self.p2Adp = self.adp(self.p2, self.p1)

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
                moves[0] = "{} attacks first!\n".format(self.p1.n)
                moves[0] += self.turn(self.p1, self.p2)
                if self.p2.hp > 0:
                    moves[1] = self.turn(self.p2, self.p1)
            else:
                moves[1] = "{} attacks first!\n".format(self.p2.n)
                moves[1] += self.turn(self.p2, self.p1)
                if self.p1.hp > 0:
                    moves[0] = self.turn(self.p1, self.p2)
        else:
            for peep in Who2Move:
                if not peep:
                    continue
                if peep == self.p1:
                    moves[0] = self.turn(self.p1, self.p2)
                else:
                    moves[1] = self.turn(self.p2, self.p1)

        if self.p1.hp <= 0 or self.p2.hp <= 0:
            debug("p1 Hp:", self.p1.hp, "p2 Hp:", self.p2.hp)
            if self.p1.hp == self.p2.hp:
                moves[2] = "Noone"
            elif self.p1.hp > self.p2.hp:
                moves[2] = self.p1.n
            else:
                moves[2] = self.p2.n

        return moves

    def turn(self, peep: player, attPeep: player) -> str:
        mes = ""
        move = "None"
        desperate = 0
        mes += self.recover(peep)
        if peep.sta > 5:
            desperate = 1
        if peep.sta > 2:
            mes += self.attack(peep, attPeep, move, desperate)
        else:
            staRec = 7
            mes += "{} recovered this turn for {} stamina.".format(
                peep.n, staRec
            )
            peep.sta += staRec
        return mes

    def recover(self, peep: player) -> str:
        mes = ""
        if peep.t:
            startSta = peep.sta
            peep.sta += peep.staR
            if peep.sta > peep.totSta:
                peep.sta = peep.totSta
            staRec = peep.sta - startSta
            if staRec:
                mes += "{} recovers {} stamina for a total of {}.\n".format(
                    peep.n, staRec, peep.sta
                )
        peep.t += 1

        if peep.totHP > peep.hp:
            strtHp = peep.hp
            peep.hp += peep.rec
            if peep.hp > peep.totHP:
                peep.hp = peep.totHP
            heal = peep.hp - strtHp
            mes += "{} heals for {}.\n".format(peep.n, heal)
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
        mes += "{} {}attacks for {} stamina.\n".format(
            attacker.n, typeAtt, staCost
        )

        if attMove == "None":
            if attacker.pa - defender.pd > attacker.ma - defender.md:
                attMove = "PhysA"
            else:
                attMove = "MentA"

        attChance = attacker.acc - defender.eva
        critChance = 0
        dblCritChance = 0
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
            multi = int(0)
        else:
            if critChance > 100:
                dblCritChance = critChance - 100
                critChance = 100
            normChance = 100 - critChance
            debug("normChance", normChance, "critChance", critChance)
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
                debug("dblCritChance", dblCritChance, "notDblCrit", notDblCrit)
                hit = random.choices(
                    ["Critical", "Double Critical"],
                    [notDblCrit, dblCritChance],
                )
                if "Critical" in hit:
                    multi = int(2)
                else:
                    notTriCrit = 100 - triCritChance
                    debug(
                        "triCritChance",
                        triCritChance,
                        "notTriCrit",
                        notTriCrit,
                    )
                    hit = random.choices(
                        ["Double Critical", "Triple Critical"],
                        [notTriCrit, triCritChance],
                    )
                    if "Double Critical" in hit:
                        multi = int(3)
                    else:
                        multi = int(4)
        mes += "{}'s attack is a {} attack.\n".format(attacker.n, hit[0])

        if attMove == "PhysA":
            attDmg = attackCalc(
                multi,
                attacker.pa,
                defender.pd,
                desperate,
            )
            if attDmg < int(0):
                attDmg = int(0)
            defender.hp = defender.hp - attDmg
            mes += "{} physically attacks {} for {} damage.".format(
                attacker.n, defender.n, attDmg
            )
            debug("physical attack is a:", hit, "for", attDmg)
        if attMove == "MentA":
            attDmg = attackCalc(
                multi,
                attacker.ma,
                defender.md,
                desperate,
            )
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

    def adp(self, at1: player, at2: player):
        phys = at1.pa - at2.pd
        ment = at1.ma - at2.md
        if phys < 0:
            phys = 0
        if ment < 0:
            ment = 0
        return phys, ment


def attackCalc(
    multi: int = 0,
    attckDmg: int = 0,
    defense: int = 0,
    desperate: bool = 0,
) -> int:
    if multi and desperate:
        multi += 1
    ret = multi * attckDmg - defense
    return ret


def addCalc(self, statType) -> int:
    ret = int(0)
    ignore = []
    for stat in statCalcDict.keys():
        statAm = getattr(self, "_{}".format(stat))
        if not statAm:
            continue
        if stat in replaceDict.keys():
            soft = getattr(self, "_{}".format(stat))
            hard = getattr(self, "_{}".format(replaceDict[stat]))
            debug(
                "soft {} rank".format(stat),
                soft,
                "hard {} rank".format(replaceDict[stat]),
                hard,
            )
            if soft > hard:
                debug("Adding {} to ignore List".format(replaceDict[stat]))
                ignore.append(replaceDict[stat])
    debug("ignore", ignore)

    for stat in statCalcDict.keys():
        statAm = getattr(self, "_{}".format(stat))
        if not statAm or stat in ignore:
            continue
        addStat = statCalcDict[stat][statType]
        if addStat:
            ret += statAm * addStat
            debug(
                "Adding rank {} {} * {} = {} to {}.".format(
                    statAm,
                    stat,
                    addStat,
                    statAm * addStat,
                    statType,
                )
            )
    return ret


def addBonus(self, bonusType) -> int:
    ret = int(0)
    for stat in bonusDict.keys():
        addBonus = bonusDict[stat][bonusType]
        if addBonus:
            bonusStat = getattr(self, "_{}".format(stat))
            if bonusStat == 10:
                ret += addBonus
                debug(
                    "Adding a bonus of {} to {} for having 10 in {}".format(
                        addBonus,
                        bonusType,
                        bonusStat,
                    )
                )
    return ret


for url, dic in urlList:
    try:
        frame = None
        frame = pd.read_csv(url)
    except Exception as e:
        print(e)
    for tup in frame.itertuples():
        debug("tuple", tup)
        shrt = [x[0] for x in leader.items() if x[1] == tup.Role]
        if shrt:
            shrt = shrt[0]
            dic[shrt] = {}
            for name, value in tup._asdict().items():
                debug("name", name, "value", value)
                dic[shrt][name] = value
        debug("shrt", shrt)
    debug("dic", dic)

replaceDict = {}
try:
    frame = None
    frame = pd.read_csv(urlReplace)
except Exception as e:
    print(e)
for tup in frame.itertuples():
    debug(tup)
    shrt = [x[0] for x in leader.items() if x[1] == tup.Role]
    if shrt:
        shrt = shrt[0]
        shrt2 = [x[0] for x in leader.items() if x[1] == tup.ReplaceWith]
        if shrt2:
            shrt2 = shrt2[0]
            debug("replace '{}' with '{}'".format(shrt, shrt2))
            replaceDict[shrt] = shrt2
debug("replaceDict", replaceDict)
