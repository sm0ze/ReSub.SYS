# power.py
# this file is just for the power dictionary

DEBUG = 0
TEST = 0

if DEBUG:
    print("{} DEBUG TRUE".format(os.path.basename(__file__)))
#if DEBUG: print()
if TEST:
    print("{} TEST TRUE".format(os.path.basename(__file__)))
#if TEST: print()

# blank entry
# '': {'Name': '', 'Rank': , 'Prereq': []},

patList = ['Supe', 'Precognition', 'Precognition+', 'Precognition++',
           'Boss System', 'System', 'First Rivals', 'Author']

powerTypes = {'Strength': 10, 'Speed': 10, 'Endurance': 10, 'Memory': 10, 'Mental Celerity': 10, 'Mental Clarity': 10, 'Regeneration': 10, 'Pain Tolerance': 10,
              'Invisibility': 10, 'Vision': 10, 'Aural Faculty': 10, 'Olfactory Sense': 10, 'Gustatory Ability': 10, 'Tactile Reception': 10, 'Proprioception': 10, '4th Wall Breaker*': 10, 'Intelligence*': 10}

rankColour = {1: 0xffffff, 2: 0xcfceeb, 3: 0xaeaddf, 4: 0x8c8bd8, 5: 0x6c6bc7,
              6: 0x4c4ab9, 7: 0x3b38b3, 8: 0x2c29aa, 9: 0x1b188d, 10: 0x0a0863}

restrictedList = ['System', 'Author']


class enhancementPower():
    def __init__(self, id: str, name: str, rank: int, prereq: list, type: str):
        self.id = id
        self.name = name
        self.rank = rank
        self.prereq = prereq
        self.type = type
        #self.colour = colour


power = {
    'sup0': {'Name': 'Supe', 'Type': 'Supe', 'Rank': 0, 'Prereq': []},
    'sys0': {'Name': 'System', 'Type': 'System', 'Rank': 0, 'Prereq': []},
    'aut0': {'Name': 'Author', 'Type': 'Author', 'Rank': 0, 'Prereq': []},

    'str1': {'Name': 'Rank 1 Strength', 'Type': 'Strength', 'Rank': 1, 'Prereq': []},
    'spe1': {'Name': 'Rank 1 Speed', 'Type': 'Speed', 'Rank': 1, 'Prereq': []},
    'end1': {'Name': 'Rank 1 Endurance', 'Type': 'Endurance', 'Rank': 1, 'Prereq': []},
    'mem1': {'Name': 'Rank 1 Memory', 'Type': 'Memory', 'Rank': 1, 'Prereq': []},
    'cel1': {'Name': 'Rank 1 Mental Celerity', 'Type': 'Celerity', 'Rank': 1, 'Prereq': []},
    'cla1': {'Name': 'Rank 1 Mental Clarity', 'Type': 'Clarity', 'Rank': 1, 'Prereq': []},
    'reg1': {'Name': 'Rank 1 Regeneration', 'Type': 'Regeneration', 'Rank': 1, 'Prereq': []},
    'pai1': {'Name': 'Rank 1 Pain Tolerance', 'Type': 'Pain Tolerance',  'Rank': 1, 'Prereq': []},
    'inv1': {'Name': 'Rank 1 Invisibility', 'Type': 'Invisibility', 'Rank': 1, 'Prereq': []},
    'vis1': {'Name': 'Rank 1 Vision', 'Type': 'Vision', 'Rank': 1, 'Prereq': []},
    'aur1': {'Name': 'Rank 1 Aural Faculty', 'Type': 'Aural Faculty', 'Rank': 1, 'Prereq': []},
    'olf1': {'Name': 'Rank 1 Olfactory Sense', 'Type': 'Olfactory Sense', 'Rank': 1, 'Prereq': []},
    'gus1': {'Name': 'Rank 1 Gustatory Ability', 'Type': 'Gustatory Ability', 'Rank': 1, 'Prereq': []},
    'tac1': {'Name': 'Rank 1 Tactile Reception', 'Type': 'Tactile Reception', 'Rank': 1, 'Prereq': []},
    'pro1': {'Name': 'Rank 1 Proprioception', 'Type': 'Proprioception', 'Rank': 1, 'Prereq': []},

    'int1': {'Name': 'Rank 1 Intelligence (only for Systems)', 'Type': 'Intelligence', 'Rank': 1, 'Prereq': ['sys0']},
    '4th1': {'Name': 'Rank 1 4th Wall Breaker', 'Type': '4th Wall Breaker', 'Rank': 1, 'Prereq': ['aut0']},

    'str2': {'Name': 'Rank 2 Strength', 'Type': 'Strength', 'Rank': 2, 'Prereq': ['str1']},
    'spe2': {'Name': 'Rank 2 Speed', 'Type': 'Speed', 'Rank': 2, 'Prereq': ['spe1']},
    'end2': {'Name': 'Rank 2 Endurance', 'Type': 'Endurance', 'Rank': 2, 'Prereq': ['end1']},
    'mem2': {'Name': 'Rank 2 Memory', 'Type': 'Memory', 'Rank': 2, 'Prereq': ['mem1']},
    'cel2': {'Name': 'Rank 2 Mental Celerity', 'Type': 'Celerity', 'Rank': 2, 'Prereq': ['cel1']},
    'cla2': {'Name': 'Rank 2 Mental Clarity', 'Type': 'Clarity', 'Rank': 2, 'Prereq': ['cla1']},
    'reg2': {'Name': 'Rank 2 Regeneration', 'Type': 'Regeneration', 'Rank': 2, 'Prereq': ['reg1']},
    'pai2': {'Name': 'Rank 2 Pain Tolerance', 'Type': 'Pain Tolerance', 'Rank': 2, 'Prereq': ['pai1']},
    'inv2': {'Name': 'Rank 2 Invisibility', 'Type': 'Invisibility', 'Rank': 2, 'Prereq': ['inv1']},
    'vis2': {'Name': 'Rank 2 Vision', 'Type': 'Vision', 'Rank': 2, 'Prereq': ['vis1']},
    'aur2': {'Name': 'Rank 2 Aural Faculty', 'Type': 'Aural Faculty', 'Rank': 2, 'Prereq': ['aur1']},
    'olf2': {'Name': 'Rank 2 Olfactory Sense', 'Type': 'Olfactory Sense', 'Rank': 2, 'Prereq': ['olf1']},
    'gus2': {'Name': 'Rank 2 Gustatory Ability', 'Type': 'Gustatory Ability', 'Rank': 2, 'Prereq': ['gus1']},
    'tac2': {'Name': 'Rank 2 Tactile Reception', 'Type': 'Tactile Reception', 'Rank': 2, 'Prereq': ['tac1']},
    'pro2': {'Name': 'Rank 2 Proprioception', 'Type': 'Proprioception', 'Rank': 2, 'Prereq': ['pro1']},

    'int2': {'Name': 'Rank 2 Intelligence (only for Systems)', 'Type': 'Intelligence', 'Rank': 2, 'Prereq': ['int1']},
    '4th2': {'Name': 'Rank 2 4th Wall Breaker', 'Type': '4th Wall Breaker', 'Rank': 2, 'Prereq': ['4th1']},

    'str3': {'Name': 'Rank 3 Strength', 'Type': 'Strength', 'Rank': 3, 'Prereq': ['str2']},
    'spe3': {'Name': 'Rank 3 Speed', 'Type': 'Speed', 'Rank': 3, 'Prereq': ['spe2']},
    'end3': {'Name': 'Rank 3 Endurance', 'Type': 'Endurance', 'Rank': 3, 'Prereq': ['end2']},
    'mem3': {'Name': 'Rank 3 Memory', 'Type': 'Memory', 'Rank': 3, 'Prereq': ['mem2']},
    'cel3': {'Name': 'Rank 3 Mental Celerity', 'Type': 'Celerity', 'Rank': 3, 'Prereq': ['cel2']},
    'cla3': {'Name': 'Rank 3 Mental Clarity', 'Type': 'Clarity', 'Rank': 3, 'Prereq': ['cla2']},
    'reg3': {'Name': 'Rank 3 Regeneration', 'Type': 'Regeneration', 'Rank': 3, 'Prereq': ['reg2']},
    'pai3': {'Name': 'Rank 3 Pain Tolerance', 'Type': 'Pain Tolerance', 'Rank': 3, 'Prereq': ['pai2']},
    'inv3': {'Name': 'Rank 3 Invisibility', 'Type': 'Invisibility', 'Rank': 3, 'Prereq': ['inv2']},
    'vis3': {'Name': 'Rank 3 Vision', 'Type': 'Vision', 'Rank': 3, 'Prereq': ['vis2']},
    'aur3': {'Name': 'Rank 3 Aural Faculty', 'Type': 'Aural Faculty', 'Rank': 3, 'Prereq': ['aur2']},
    'olf3': {'Name': 'Rank 3 Olfactory Sense', 'Type': 'Olfactory Sense', 'Rank': 3, 'Prereq': ['olf2']},
    'gus3': {'Name': 'Rank 3 Gustatory Ability', 'Type': 'Gustatory Ability', 'Rank': 3, 'Prereq': ['gus2']},
    'tac3': {'Name': 'Rank 3 Tactile Reception', 'Type': 'Tactile Reception', 'Rank': 3, 'Prereq': ['tac2']},
    'pro3': {'Name': 'Rank 3 Proprioception', 'Type': 'Proprioception', 'Rank': 3, 'Prereq': ['pro2']},

    'int3': {'Name': 'Rank 3 Intelligence (only for Systems)', 'Type': 'Intelligence', 'Rank': 3, 'Prereq': ['int2']},
    '4th3': {'Name': 'Rank 3 4th Wall Breaker', 'Type': '4th Wall Breaker', 'Rank': 3, 'Prereq': ['4th2']},

    'str4': {'Name': 'Rank 4 Strength', 'Type': 'Strength', 'Rank': 4, 'Prereq': ['str3', 'end1', 'pro1', 'reg1']},
    'spe4': {'Name': 'Rank 4 Speed', 'Type': 'Speed', 'Rank': 4, 'Prereq': ['spe3', 'vis1', 'pro1', 'cel1']},
    'end4': {'Name': 'Rank 4 Endurance', 'Type': 'Endurance', 'Rank': 4, 'Prereq': ['end3', 'str1', 'tac1', 'pai1']},
    'mem4': {'Name': 'Rank 4 Memory', 'Type': 'Memory', 'Rank': 4, 'Prereq': ['mem3', 'cla1', 'cel1']},
    'cel4': {'Name': 'Rank 4 Mental Celerity', 'Type': 'Celerity', 'Rank': 4, 'Prereq': ['cel3', 'spe1', 'mem1', 'cla1']},
    'cla4': {'Name': 'Rank 4 Mental Clarity', 'Type': 'Clarity', 'Rank': 4, 'Prereq': ['cla3', 'end1', 'mem1', 'cel1']},
    'reg4': {'Name': 'Rank 4 Regeneration', 'Type': 'Regeneration', 'Rank': 4, 'Prereq': ['reg3', 'spe1', 'pro1', 'pai1']},
    'pai4': {'Name': 'Rank 4 Pain Tolerance', 'Type': 'Pain Tolerance', 'Rank': 4, 'Prereq': ['pai3', 'tac1']},
    'inv4': {'Name': 'Rank 4 Invisibility', 'Type': 'Invisibility', 'Rank': 4, 'Prereq': ['inv3', 'cla1', 'cel1', 'pro1']},
    'vis4': {'Name': 'Rank 4 Vision', 'Type': 'Vision', 'Rank': 4, 'Prereq': ['vis3', 'cla1', 'cel1']},
    'aur4': {'Name': 'Rank 4 Aural Faculty', 'Type': 'Aural Faculty', 'Rank': 4, 'Prereq': ['aur3', 'cla1', 'cel1']},
    'olf4': {'Name': 'Rank 4 Olfactory Sense', 'Type': 'Olfactory Sense', 'Rank': 4, 'Prereq': ['olf3', 'cla1', 'cel1']},
    'gus4': {'Name': 'Rank 4 Gustatory Ability', 'Type': 'Gustatory Ability', 'Rank': 4, 'Prereq': ['gus3', 'cla1', 'cel1']},
    'tac4': {'Name': 'Rank 4 Tactile Reception', 'Type': 'Tactile Reception', 'Rank': 4, 'Prereq': ['tac3', 'cla1', 'cel1']},
    'pro4': {'Name': 'Rank 4 Proprioception', 'Type': 'Proprioception', 'Rank': 4, 'Prereq': ['pro3', 'cla1', 'cel1']},

    'int4': {'Name': 'Rank 4 Intelligence (only for Systems)', 'Type': 'Intelligence', 'Rank': 4, 'Prereq': ['int3', 'mem1', 'cel1', 'cla1']},
    '4th4': {'Name': 'Rank 4 4th Wall Breaker', 'Type': '4th Wall Breaker', 'Rank': 4, 'Prereq': ['4th3', 'int1']},

    'str5': {'Name': 'Rank 5 Strength', 'Type': 'Strength', 'Rank': 5, 'Prereq': ['str4']},
    'spe5': {'Name': 'Rank 5 Speed', 'Type': 'Speed', 'Rank': 5, 'Prereq': ['spe4']},
    'end5': {'Name': 'Rank 5 Endurance', 'Type': 'Endurance', 'Rank': 5, 'Prereq': ['end4']},
    'mem5': {'Name': 'Rank 5 Memory', 'Type': 'Memory', 'Rank': 5, 'Prereq': ['mem4']},
    'cel5': {'Name': 'Rank 5 Mental Celerity', 'Type': 'Celerity', 'Rank': 5, 'Prereq': ['cel4']},
    'cla5': {'Name': 'Rank 5 Mental Clarity', 'Type': 'Clarity', 'Rank': 5, 'Prereq': ['cla4']},
    'reg5': {'Name': 'Rank 5 Regeneration', 'Type': 'Regeneration', 'Rank': 5, 'Prereq': ['reg4']},
    'pai5': {'Name': 'Rank 5 Pain Tolerance', 'Type': 'Pain Tolerance', 'Rank': 5, 'Prereq': ['pai4']},
    'inv5': {'Name': 'Rank 5 Invisibility', 'Type': 'Invisibility', 'Rank': 5, 'Prereq': ['inv4']},
    'vis5': {'Name': 'Rank 5 Vision', 'Type': 'Vision', 'Rank': 5, 'Prereq': ['vis4']},
    'aur5': {'Name': 'Rank 5 Aural Faculty', 'Type': 'Aural Faculty', 'Rank': 5, 'Prereq': ['aur4']},
    'olf5': {'Name': 'Rank 5 Olfactory Sense', 'Type': 'Olfactory Sense', 'Rank': 5, 'Prereq': ['olf4']},
    'gus5': {'Name': 'Rank 5 Gustatory Ability', 'Type': 'Gustatory Ability', 'Rank': 5, 'Prereq': ['gus4']},
    'tac5': {'Name': 'Rank 5 Tactile Reception', 'Type': 'Tactile Reception', 'Rank': 5, 'Prereq': ['tac4']},
    'pro5': {'Name': 'Rank 5 Proprioception', 'Type': 'Proprioception', 'Rank': 5, 'Prereq': ['pro4']},

    'int5': {'Name': 'Rank 5 Intelligence (only for Systems)', 'Type': 'Intelligence', 'Rank': 5, 'Prereq': ['int4']},
    '4th5': {'Name': 'Rank 5 4th Wall Breaker', 'Type': '4th Wall Breaker', 'Rank': 5, 'Prereq': ['4th4']},

    'str6': {'Name': 'Rank 6 Strength', 'Type': 'Strength', 'Rank': 6, 'Prereq': ['str5']},
    'spe6': {'Name': 'Rank 6 Speed', 'Type': 'Speed', 'Rank': 6, 'Prereq': ['spe5']},
    'end6': {'Name': 'Rank 6 Endurance', 'Type': 'Endurance', 'Rank': 6, 'Prereq': ['end5']},
    'mem6': {'Name': 'Rank 6 Memory', 'Type': 'Memory', 'Rank': 6, 'Prereq': ['mem5']},
    'cel6': {'Name': 'Rank 6 Mental Celerity', 'Type': 'Celerity', 'Rank': 6, 'Prereq': ['cel5']},
    'cla6': {'Name': 'Rank 6 Mental Clarity', 'Type': 'Clarity', 'Rank': 6, 'Prereq': ['cla5']},
    'reg6': {'Name': 'Rank 6 Regeneration', 'Type': 'Regeneration', 'Rank': 6, 'Prereq': ['reg5']},
    'pai6': {'Name': 'Rank 6 Pain Tolerance', 'Type': 'Pain Tolerance', 'Rank': 6, 'Prereq': ['pai5']},
    'inv6': {'Name': 'Rank 6 Invisibility', 'Type': 'Invisibility', 'Rank': 6, 'Prereq': ['inv5']},
    'vis6': {'Name': 'Rank 6 Vision', 'Type': 'Vision', 'Rank': 6, 'Prereq': ['vis5']},
    'aur6': {'Name': 'Rank 6 Aural Faculty', 'Type': 'Aural Faculty', 'Rank': 6, 'Prereq': ['aur5']},
    'olf6': {'Name': 'Rank 6 Olfactory Sense', 'Type': 'Olfactory Sense', 'Rank': 6, 'Prereq': ['olf5']},
    'gus6': {'Name': 'Rank 6 Gustatory Ability', 'Type': 'Gustatory Ability', 'Rank': 6, 'Prereq': ['gus5']},
    'tac6': {'Name': 'Rank 6 Tactile Reception', 'Type': 'Tactile Reception', 'Rank': 6, 'Prereq': ['tac5']},
    'pro6': {'Name': 'Rank 6 Proprioception', 'Type': 'Proprioception', 'Rank': 6, 'Prereq': ['pro5']},

    'int6': {'Name': 'Rank 6 Intelligence (only for Systems)', 'Type': 'Intelligence', 'Rank': 6, 'Prereq': ['int5']},
    '4th6': {'Name': 'Rank 6 4th Wall Breaker', 'Type': '4th Wall Breaker', 'Rank': 6, 'Prereq': ['4th5']},

    'str7': {'Name': 'Rank 7 Strength', 'Type': 'Strength', 'Rank': 7, 'Prereq': ['str6', 'end3', 'pro3', 'reg3']},
    'spe7': {'Name': 'Rank 7 Speed', 'Type': 'Speed', 'Rank': 7, 'Prereq': ['spe6', 'end1', 'pro3', 'cel3']},
    'end7': {'Name': 'Rank 7 Endurance', 'Type': 'Endurance', 'Rank': 7, 'Prereq': ['end6', 'str3', 'tac3', 'pai3']},
    'mem7': {'Name': 'Rank 7 Memory', 'Type': 'Memory', 'Rank': 7, 'Prereq': ['mem6', 'spe1', 'cla3', 'cel3']},
    'cel7': {'Name': 'Rank 7 Mental Celerity', 'Type': 'Celerity', 'Rank': 7, 'Prereq': ['cel6', 'spe3', 'mem3', 'cla3']},
    'cla7': {'Name': 'Rank 7 Mental Clarity', 'Type': 'Clarity', 'Rank': 7, 'Prereq': ['cla6', 'end3', 'mem3', 'cel3']},
    'reg7': {'Name': 'Rank 7 Regeneration', 'Type': 'Regeneration', 'Rank': 7, 'Prereq': ['reg6', 'spe3', 'pro3', 'pai3']},
    'pai7': {'Name': 'Rank 7 Pain Tolerance', 'Type': 'Pain Tolerance', 'Rank': 7, 'Prereq': ['pai6', 'end1', 'tac3', 'reg1']},
    'inv7': {'Name': 'Rank 7 Invisibility', 'Type': 'Invisibility', 'Rank': 7, 'Prereq': ['inv6', 'pro3', 'cla3', 'cel3']},
    'vis7': {'Name': 'Rank 7 Vision', 'Type': 'Vision', 'Rank': 7, 'Prereq': ['vis6', 'mem1', 'cla3', 'cel3']},
    'aur7': {'Name': 'Rank 7 Aural Faculty', 'Type': 'Aural Faculty', 'Rank': 7, 'Prereq': ['aur6', 'mem1', 'cla3', 'cel3']},
    'olf7': {'Name': 'Rank 7 Olfactory Sense', 'Type': 'Olfactory Sense', 'Rank': 7, 'Prereq': ['olf6', 'mem1', 'cla3', 'cel3']},
    'gus7': {'Name': 'Rank 7 Gustatory Ability', 'Type': 'Gustatory Ability', 'Rank': 7, 'Prereq': ['gus6', 'mem1', 'cla3', 'cel3']},
    'tac7': {'Name': 'Rank 7 Tactile Reception', 'Type': 'Tactile Reception', 'Rank': 7, 'Prereq': ['tac6', 'pro1', 'cla3', 'cel3']},
    'pro7': {'Name': 'Rank 7 Proprioception', 'Type': 'Proprioception', 'Rank': 7, 'Prereq': ['pro6', 'mem3', 'cla3', 'cel3']},

    'int7': {'Name': 'Rank 7 Intelligence (only for Systems)', 'Type': 'Intelligence', 'Rank': 7, 'Prereq': ['int6', 'mem3', 'cel3', 'cla3']},
    '4th7': {'Name': 'Rank 7 4th Wall Breaker', 'Type': '4th Wall Breaker', 'Rank': 7, 'Prereq': ['4th6', 'int3']},

    'str8': {'Name': 'Rank 8 Strength', 'Type': 'Strength', 'Rank': 8, 'Prereq': ['str7']},
    'spe8': {'Name': 'Rank 8 Speed', 'Type': 'Speed', 'Rank': 8, 'Prereq': ['spe7']},
    'end8': {'Name': 'Rank 8 Endurance', 'Type': 'Endurance', 'Rank': 8, 'Prereq': ['end7']},
    'mem8': {'Name': 'Rank 8 Memory', 'Type': 'Memory', 'Rank': 8, 'Prereq': ['mem7']},
    'cel8': {'Name': 'Rank 8 Mental Celerity', 'Type': 'Celerity', 'Rank': 8, 'Prereq': ['cel7']},
    'cla8': {'Name': 'Rank 8 Mental Clarity', 'Type': 'Clarity', 'Rank': 8, 'Prereq': ['cla7']},
    'reg8': {'Name': 'Rank 8 Regeneration', 'Type': 'Regeneration', 'Rank': 8, 'Prereq': ['reg7']},
    'pai8': {'Name': 'Rank 8 Pain Tolerance', 'Type': 'Pain Tolerance', 'Rank': 8, 'Prereq': ['pai7']},
    'inv8': {'Name': 'Rank 8 Invisibility', 'Type': 'Invisibility', 'Rank': 8, 'Prereq': ['inv7']},
    'vis8': {'Name': 'Rank 8 Vision', 'Type': 'Vision', 'Rank': 8, 'Prereq': ['vis7']},
    'aur8': {'Name': 'Rank 8 Aural Faculty', 'Type': 'Aural Faculty', 'Rank': 8, 'Prereq': ['aur7']},
    'olf8': {'Name': 'Rank 8 Olfactory Sense', 'Type': 'Olfactory Sense', 'Rank': 8, 'Prereq': ['olf7']},
    'gus8': {'Name': 'Rank 8 Gustatory Ability', 'Type': 'Gustatory Ability', 'Rank': 8, 'Prereq': ['gus7']},
    'tac8': {'Name': 'Rank 8 Tactile Reception', 'Type': 'Tactile Reception', 'Rank': 8, 'Prereq': ['tac7']},
    'pro8': {'Name': 'Rank 8 Proprioception', 'Type': 'Proprioception', 'Rank': 8, 'Prereq': ['pro7']},

    'int8': {'Name': 'Rank 8 Intelligence (only for Systems)', 'Type': 'Intelligence', 'Rank': 8, 'Prereq': ['int7']},
    '4th8': {'Name': 'Rank 8 4th Wall Breaker', 'Type': '4th Wall Breaker', 'Rank': 8, 'Prereq': ['4th7']},

    'str9': {'Name': 'Rank 9 Strength', 'Type': 'Strength', 'Rank': 9, 'Prereq': ['str8']},
    'spe9': {'Name': 'Rank 9 Speed', 'Type': 'Speed', 'Rank': 9, 'Prereq': ['spe8']},
    'end9': {'Name': 'Rank 9 Endurance', 'Type': 'Endurance', 'Rank': 9, 'Prereq': ['end8']},
    'mem9': {'Name': 'Rank 9 Memory', 'Type': 'Memory', 'Rank': 9, 'Prereq': ['mem8']},
    'cel9': {'Name': 'Rank 9 Mental Celerity', 'Type': 'Celerity', 'Rank': 9, 'Prereq': ['cel8']},
    'cla9': {'Name': 'Rank 9 Mental Clarity', 'Type': 'Clarity', 'Rank': 9, 'Prereq': ['cla8']},
    'reg9': {'Name': 'Rank 9 Regeneration', 'Type': 'Regeneration', 'Rank': 9, 'Prereq': ['reg8']},
    'pai9': {'Name': 'Rank 9 Pain Tolerance', 'Type': 'Pain Tolerance', 'Rank': 9, 'Prereq': ['pai8']},
    'inv9': {'Name': 'Rank 9 Invisibility', 'Type': 'Invisibility', 'Rank': 9, 'Prereq': ['inv8']},
    'vis9': {'Name': 'Rank 9 Vision', 'Type': 'Vision', 'Rank': 9, 'Prereq': ['vis8']},
    'aur9': {'Name': 'Rank 9 Aural Faculty', 'Type': 'Aural Faculty', 'Rank': 9, 'Prereq': ['aur8']},
    'olf9': {'Name': 'Rank 9 Olfactory Sense', 'Type': 'Olfactory Sense', 'Rank': 9, 'Prereq': ['olf8']},
    'gus9': {'Name': 'Rank 9 Gustatory Ability', 'Type': 'Gustatory Ability', 'Rank': 9, 'Prereq': ['gus8']},
    'tac9': {'Name': 'Rank 9 Tactile Reception', 'Type': 'Tactile Reception', 'Rank': 9, 'Prereq': ['tac8']},
    'pro9': {'Name': 'Rank 9 Proprioception', 'Type': 'Proprioception', 'Rank': 9, 'Prereq': ['pro8']},

    'int9': {'Name': 'Rank 9 Intelligence (only for Systems)', 'Type': 'Intelligence', 'Rank': 9, 'Prereq': ['int8']},
    '4th9': {'Name': 'Rank 9 4th Wall Breaker', 'Type': '4th Wall Breaker', 'Rank': 9, 'Prereq': ['4th8']},

    'str10': {'Name': 'Rank 10 Strength', 'Type': 'Strength', 'Rank': 10, 'Prereq': ['str9', 'end6', 'reg6', 'pai3', 'pro6']},
    'spe10': {'Name': 'Rank 10 Speed', 'Type': 'Speed', 'Rank': 10, 'Prereq': ['spe9', 'end3', 'vis3', 'cel6', 'pro6']},
    'end10': {'Name': 'Rank 10 Endurance', 'Type': 'Endurance', 'Rank': 10, 'Prereq': ['end9', 'str6', 'tac6', 'pai6']},
    'mem10': {'Name': 'Rank 10 Memory', 'Type': 'Memory', 'Rank': 10, 'Prereq': ['mem9', 'spe3', 'cla6', 'cel6']},
    'cel10': {'Name': 'Rank 10 Mental Celerity', 'Type': 'Celerity', 'Rank': 10, 'Prereq': ['cel9', 'spe6', 'mem6', 'cla6']},
    'cla10': {'Name': 'Rank 10 Mental Clarity', 'Type': 'Clarity', 'Rank': 10, 'Prereq': ['cla9', 'end6', 'mem6', 'cel6']},
    'reg10': {'Name': 'Rank 10 Regeneration', 'Type': 'Regeneration', 'Rank': 10, 'Prereq': ['reg9', 'spe6', 'mem3', 'pai6', 'pro6']},
    'pai10': {'Name': 'Rank 10 Pain Tolerance', 'Type': 'Pain Tolerance', 'Rank': 10, 'Prereq': ['pai9', 'end3', 'tac6', 'reg3']},
    'inv10': {'Name': 'Rank 10 Invisibility', 'Type': 'Invisibility', 'Rank': 10, 'Prereq': ['inv9', 'mem3', 'cla6', 'cel6', 'pro6']},
    'vis10': {'Name': 'Rank 10 Vision', 'Type': 'Vision', 'Rank': 10, 'Prereq': ['vis9', 'mem3', 'cla6', 'cel6']},
    'aur10': {'Name': 'Rank 10 Aural Faculty', 'Type': 'Aural Faculty', 'Rank': 10, 'Prereq': ['aur9', 'mem3', 'cla6', 'cel6']},
    'olf10': {'Name': 'Rank 10 Olfactory Sense', 'Type': 'Olfactory Sense', 'Rank': 10, 'Prereq': ['olf9', 'mem3', 'cla6', 'cel6']},
    'gus10': {'Name': 'Rank 10 Gustatory Ability', 'Type': 'Gustatory Ability', 'Rank': 10, 'Prereq': ['gus9', 'mem3', 'cla6', 'cel6']},
    'tac10': {'Name': 'Rank 10 Tactile Reception', 'Type': 'Tactile Reception', 'Rank': 10, 'Prereq': ['tac9', 'pai3', 'cla6', 'cel6', 'pro3']},
    'pro10': {'Name': 'Rank 10 Proprioception', 'Type': 'Proprioception', 'Rank': 10, 'Prereq': ['pro9', 'mem6', 'cla6', 'cel6']},

    'int10': {'Name': 'Rank 10 Intelligence (only for Systems)', 'Type': 'Intelligence', 'Rank': 10, 'Prereq': ['int9', 'mem6', 'cel6', 'cla6']},
    '4th10': {'Name': 'Rank 10 4th Wall Breaker', 'Type': '4th Wall Breaker', 'Rank': 10, 'Prereq': ['4th9', 'int6']}
}


class enhancementList():
    def __init__(self):
        return

    def getName(self, nom: str):
        for nomId in [x for x in dir(self) if len(x) < 5]:
            print("possible id = {}".format(nomId))
            nomIdObj = getattr(self, str(nomId))

            nomIdName = getattr(nomIdObj, 'id')
            if DEBUG:
                print("object: {} has with attribute name: {}".format(
                    nomIdObj, nomIdName))

            if DEBUG:
                print("Comparing {} to {}".format(nom, nomIdName))
            if str(nom) == str(nomIdName):
                return nomIdObj.name
        return 0

    def getId(self, nom: str):
        for nomId in [x for x in dir(self) if len(x) < 5]:
            print("possible id = {}".format(nomId))
            nomIdObj = getattr(self, str(nomId))

            nomIdName = getattr(nomIdObj, 'name')
            if DEBUG:
                print("object: {} has with attribute name: {}".format(
                    nomIdObj, nomIdName))

            if DEBUG:
                print("Comparing {} to {}".format(nom, nomIdName))
            if str(nom) == str(nomIdName):
                return nomIdObj.id
        return 0


def listEnhancements():
    list = enhancementList()
    for powerId in power.keys():
        setattr(list, powerId, enhancementPower(
            id=powerId, name=power[powerId]['Name'], rank=power[powerId]['Rank'], prereq=power[powerId]['Prereq'], type=power[powerId]['Type']))
    return list


if DEBUG:
    powList = listEnhancements()
    print(dir(powList))
    print(powList.getName('reg1'))

    print(powList.getId('Rank 1 Regeneration'))
