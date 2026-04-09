from enum import Enum


class ServerRegion(str, Enum):
    GLOBAL = "GLOBAL"
    JP = "JP"
    BOTH = "BOTH"


class UnitRole(str, Enum):
    DPS = "DPS"
    SUPPORT = "SUPPORT"
    TANK = "TANK"
    HEALER = "HEALER"
    BREAKER = "BREAKER"


class DamageType(str, Enum):
    PHYSICAL = "PHYSICAL"
    MAGIC = "MAGIC"
    HYBRID = "HYBRID"


class EquipSlotType(str, Enum):
    WEAPON = "WEAPON"
    ARMOR = "ARMOR"
    SUPPORT = "SUPPORT"
    HEAL = "HEAL"


class TierGrade(str, Enum):
    SSS = "SSS"
    SS = "SS"
    S = "S"
    A = "A"
    B = "B"
    C = "C"


class ContentMode(str, Enum):
    STORY = "STORY"
    ARENA = "ARENA"
    DUNGEON_OF_TRIALS = "DUNGEON_OF_TRIALS"
    CREST_PALACE = "CREST_PALACE"
    SUMMONERS_ROAD = "SUMMONERS_ROAD"
    MAGICAL_MINES = "MAGICAL_MINES"
    GRAND_CRUSADE = "GRAND_CRUSADE"
    RAID = "RAID"
    COLLAB = "COLLAB"


class CompStyle(str, Enum):
    SUSTAIN = "SUSTAIN"
    NUKE = "NUKE"
    AUTO_FARM = "AUTO_FARM"
    ARENA = "ARENA"
    BREAKER = "BREAKER"
    SUPPORT_CENTRIC = "SUPPORT_CENTRIC"
