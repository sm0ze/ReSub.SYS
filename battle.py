# battle.py
import asyncio
import typing
import discord
import random
from BossSystemExecutable import nON
from enhancements import funcBuild, spent
from power import power, leader  # , moveOpt
import pandas as pd

DEBUG = 0


def debug(*args):
    if DEBUG:
        print(*args)


HP = 15
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

statMes = """HP: {0}/{9}
Sta: {10}/{12} +{11}
PA: {1}
PD: {2}
MA: {3}
MD: {4}
Rec: {5}
Acc: {6}
Eva: {7}
Swi: {8}"""


adpMes = "\n\nAdapted PA: {0}\n Adapted MA: {1}\nAdapted Hit Chance: {2}"

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
    def __init__(self, member: discord.Member, bot) -> None:
        self.bot = bot
        self.p = member
        self.n = nON(member)
        self.t = int(0)
        self.play = False

        self.sG = spent([member])
        self.fB = funcBuild(self.sG[0][2])
        self.stats = self.fB[2]

        self.iniCalc()

        addHP = float(HP + self.calcStat("HP"))

        self.hp = addHP
        self.totHP = addHP

        self.rec = REC + self.calcStat("Rec")

        self.sta = STA + self.calcStat("Sta")
        self.totSta = STATOT + self.calcStat("StaTot")
        self.staR = STAR + self.calcStat("StaR")

        self.pa = PA + self.calcStat("PA")
        self.pd = PD + self.calcStat("PD")

        self.ma = MA + self.calcStat("MA")
        self.md = MD + self.calcStat("MD")

        self.acc = ACC + self.calcStat("Acc")
        self.eva = EVA + self.calcStat("Eva")

        self.swi = SWI + self.calcStat("Swi")

        self.swiNow = 0
        self.defending = ""
        self.tired = 0
        self.missTurn = False

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
        ret = (
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
            self.pd = int(val * self.pd)
        if self.defending == "Mental":
            self.md = int(val * self.md)

        if defAlr:
            self.defending = ""
            addOn = "no longer "

        self.recSta()
        ret = "{} is {}defending from {} attacks.\n".format(
            self.n, addOn, defType
        )
        return ret

    def recSta(self, val: int = 1):
        self.sta += val
        if self.sta > self.totSta:
            self.sta = self.totSta

    def recHP(self, val: int = 1):
        self.hp += val
        if self.hp > self.totHP:
            self.hp = self.totHP

    async def ask(
        self,
        opp: str = "ReSub.SYS",
    ):
        if self.p.bot:
            return

        reactionList = ["✅", "❌"]
        mes = discord.Embed(title="Do you wish to play against {}".format(opp))
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
                debug("reaction", reaction, "user", user)
                if str(reaction.emoji) == "✅":
                    self.play = True
                    active = False
                elif str(reaction.emoji) == "❌":
                    self.play = False
                    active = False
            except asyncio.TimeoutError:
                await self.p.send("Timeout")
                active = False


class battler:
    def __init__(
        self, bot, member1: discord.Member, member2: discord.Member
    ) -> None:
        self.p1 = player(member1, bot)
        self.n1 = nON(member1)

        self.p2 = player(member2, bot)
        self.n2 = nON(member2)

        self.p1Adp = self.adpStatMessage(self.p1, self.p2)
        self.p2Adp = self.adpStatMessage(self.p2, self.p1)

    async def echoMes(self, mes, thrd):
        if self.p1.play:
            await self.p1.p.send(embed=mes)
        if self.p2.play:
            await self.p2.p.send(embed=mes)
        await thrd.send(embed=mes)

    async def findPlayers(self):
        if not self.p1.p.bot:
            await self.p1.ask(self.p2.n)
        if not self.p1.p.bot:
            await self.p2.ask(self.p1.n)

    def nextRound(self) -> list[typing.Union[player, None]]:
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
        p1Move: list[str] = None,
        p2Move: list[str] = None,
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
                moves[0] += self.turn(self.p1, self.p2, p1Move)
                if self.p2.hp > 0 and self.p1.hp > 0:
                    moves[1] = self.turn(self.p2, self.p1, p2Move)
            else:
                moves[1] = "{} attacks first!\n".format(self.p2.n)
                moves[1] += self.turn(self.p2, self.p1, p2Move)
                if self.p2.hp > 0 and self.p1.hp > 0:
                    moves[0] = self.turn(self.p1, self.p2, p1Move)
        else:
            for peep in Who2Move:
                if not peep:
                    continue
                if peep == self.p1:
                    moves[0] = self.turn(self.p1, self.p2, p1Move)
                else:
                    moves[1] = self.turn(self.p2, self.p1, p2Move)

        if self.p1.hp <= 0 or self.p2.hp <= 0:
            debug("p1 Hp:", self.p1.hp, "p2 Hp:", self.p2.hp)
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
            mes += "{} misses this turn due to exhaustion!\n".format(peep.n)
        if peep.defending:
            mes += peep.defend()

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
                mes += "{} recovered this turn for {} stamina.\n".format(
                    peep.n, staRec
                )
                peep.sta += staRec

        if not peep.sta:
            peep.missTurn = True
            peep.tired += 1
            mes += (
                "{} has exhausted themself ({}) and will miss a turn.\n"
            ).format(peep.n, peep.tired)

        mes += self.recover(peep)

        if peep.tired == 3:
            mes += "{} has exhausted themself for the third time!".format(
                peep.n
            )
            if attPeep.hp < 0:
                peep.hp = attPeep.hp - 1
            else:
                peep.hp = 0

        if peep.missTurn:
            peep.missTurn = False
        return mes

    def moveSelf(self, peep: player, notPeep: player):
        desperate = 0
        typeMove = "Defend"
        moveStr = ""
        phys, ment, hitChance = self.adp(peep, notPeep)

        if peep.sta > 5:
            desperate = 1

        if hitChance and (phys > 0 or ment > 0 or desperate):
            if peep.sta > 2:
                typeMove = "Attack"
            if phys >= ment:
                moveStr = "Physical"
            else:
                moveStr = "Mental"

        return desperate, typeMove, moveStr

    def recover(self, peep: player) -> str:
        mes = ""
        startSta = peep.sta
        peep.recSta(peep.staR)
        staRec = peep.sta - startSta
        if staRec:
            mes += "{} recovers {} stamina for a total of {}.\n".format(
                peep.n, staRec, peep.sta
            )

        if peep.totHP > peep.hp:
            strtHp = peep.hp
            peep.recHP(peep.rec)
            heal = peep.hp - strtHp
            if heal:
                mes += "{} heals for {}.\n".format(peep.n, heal)
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
        mes += "{} {}attacks for {} stamina.\n".format(
            attacker.n, typeAtt, staCost
        )

        if not attMove:
            if attacker.pa - defender.pd > attacker.ma - defender.md:
                attMove = "Physical"
            else:
                attMove = "Mental"

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

        if attMove == "Physical":
            attDmg = attackCalc(
                multi,
                attacker.pa,
                defender.pd,
                desperate,
            )
            if attDmg < int(0):
                attDmg = int(0)
            defender.hp = defender.hp - attDmg
            mes += "{} physically attacks {} for {} damage.\n".format(
                attacker.n, defender.n, attDmg
            )
            debug("physical attack is a:", hit, "for", attDmg)
        if attMove == "Mental":
            attDmg = attackCalc(
                multi,
                attacker.ma,
                defender.md,
                desperate,
            )
            if attDmg < int(0):
                attDmg = int(0)
            defender.hp = defender.hp - attDmg
            mes += "{} mentally attacks {} for {} damage.\n".format(
                attacker.n,
                defender.n,
                attDmg,
            )
            debug("mental attack is a:", hit, "for", attDmg)

        return mes

    def adp(self, at1: player, at2: player):
        phys = at1.pa - at2.pd
        ment = at1.ma - at2.md
        hitChance = at1.acc - at2.eva
        if phys < 0:
            phys = 0
        if ment < 0:
            ment = 0
        if hitChance < 0:
            hitChance = 0

        ret = (phys, ment, hitChance)
        return ret

    def adpStatMessage(self, at1: player, at2: player):
        adaptedStats = self.adp(at1, at2)
        return adpMes.format(*adaptedStats)


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
        try:
            addStat = statCalcDict[stat][statType]
        except KeyError:
            addStat = None
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
