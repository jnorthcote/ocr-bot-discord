import io
import json
import re

from enum import Enum
# from ss_entity import Player, Status, System, Rewards

class BoundingPoly():
    def __init__(self, top, left, bottom, right):
        self.top    = int(round(top))
        self.left   = int(round(left))
        self.bottom = int(round(bottom))
        self.right  = int(round(right))

    def __repr__(self):
        return "<BoundingPoly top:%s left:%s bottom:%s right:%s>" % (self.top, self.left, self.bottom, self.right)

    def __str__(self):
        return "top:%s left:%s bottom:%s right:%s" % (self.top, self.left, self.bottom, self.right)

    def to_scale(self, scale_factor):
        return BoundingPoly(self.top*scale_factor.yF, self.left*scale_factor.xF, self.bottom*scale_factor.yF, self.right*scale_factor.xF)

    def contains(bp1, bp2):
        xContain = bp1.left <= bp2.left <= bp2.right <= bp1.right
        yContain = bp1.top <= bp2.top <= bp2.bottom <= bp1.bottom
        return (xContain and yContain)

    @classmethod
    def fromVertices(cls, v):
        return cls(v[0]['y'],v[0]['x'],v[2]['y'],v[2]['x'])

class SystemType(bytes, Enum):
    """
    Coordinate with binary codes that can be indexed by the int code.
    """
    def __new__(cls, value, label, roe_flag, color, system_list):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.label = label
        obj.color = color
        obj.roe_flag = roe_flag
        obj.system_list = system_list
        return obj

    NORMAL     = (1, 'Normal', False, 0x424242, [])
    BORG_SPACE = (2, 'Borg Space', True, 0xe90909, ['Torra Sedra', 'Yoria-3', 'Zed Alpha'])

    @classmethod
    def fromName(cls, name):
        for st in SystemType:
            if name in st.system_list:
                return st

        return SystemType.NORMAL


class BorderType(bytes, Enum):
    """
    Coordinate with binary codes that can be indexed by the int code.
    """
    def __new__(cls, value, pctYt, pctYb, pctXl, pctXr):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.pctYt = pctYt
        obj.pctYb = pctYb
        obj.pctXl = pctXl
        obj.pctXr = pctXr
        return obj

    ZERO      = (1, 0.0,   0.0,  0.0, 0.0)
    BS_MACOS  = (2, 0.05, 0.05,  0.0, 0.0)
    IOS_NOTCH = (1, 0.0,   0.0, 0.04, 0.0)


class Anchor(bytes, Enum):
    """
    Coordinate with binary codes that can be indexed by the int code.
    """
    def __new__(cls, value, lMult, offsetMult):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.lMult = lMult
        obj.offsetMult = offsetMult
        return obj

    L = (1, 0.0, 0.0)
    R = (2, 1.0, 1.0)
    C = (3, 0.5, 0.5)

class VSlice(bytes, Enum):
    """
    Coordinate with binary codes that can be indexed by the int code.
    """
    def __new__(cls, value, label, pctX, anchor, entity):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.label = label
        obj.pctX = pctX
        obj.anchor = anchor
        obj.entity = entity
        return obj

    def __repr__(self):
        return "<VSlice label:%s pctX:%s>" % (self.label, self.pctX)

    def __str__(self):
        return "label:%s pctX:%s" % (self.label, self.pctX)

    STATUS   = (1,  'Status',  0.33, Anchor.C, 'Status')
    PLAYER1  = (2,  'Player1', 0.45, Anchor.L, 'Player')
    PLAYER2  = (3,  'Player2', 0.45, Anchor.R, 'Player')
    P1_POWR  = (4,  'Power1',   0.5, Anchor.L, None)
    P2_POWR  = (5,  'Power2',   0.5, Anchor.R, None)
    P1_SHIP  = (6,  'Ship1',    0.5, Anchor.L, None)
    P2_SHIP  = (7,  'Ship2',    0.5, Anchor.R, None)
    REWARDS  = (8,  'Rewards', 0.33, Anchor.C, 'Rewards')
    CARGO    = (9,  'Cargo',   0.33, Anchor.L, None)
    SYSTEM   = (10, 'System',  0.33, Anchor.R, 'System')
    BL_ROUND = (20, 'Round',   0.20, Anchor.C, None)
    BL_LEFT  = (21, 'BLLeft',  0.45, Anchor.L, None)
    BL_RIGHT = (22, 'BLRight', 0.45, Anchor.R, None)


class HSlice(bytes, Enum):
    """
    Coordinate with binary codes that can be indexed by the int code.
    """
    def __new__(cls, value, label, pctY, fields):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.label = label
        obj.pctY = pctY
        obj.fields = fields
        return obj

    def __repr__(self):
        return "<HSlice label:%s pctY:%s>" % (self.label, self.pctY)

    def __str__(self):
        return "label:%s pctY:%s" % (self.label, self.pctY)

    HEADER     = (1,   'Header',  0.10, [VSlice.PLAYER1, VSlice.STATUS, VSlice.PLAYER2])
    MATCHUP    = (5,   'Matchup', 0.11, [VSlice.P1_POWR, VSlice.P2_POWR])
    SUMMARY    = (10,  'Summary', 0.64, [VSlice.P1_SHIP, VSlice.P2_SHIP])
    A_SUMMARY  = (11,  'Armada Summary', 0.64, [])
    BATTLE_LOG = (20,  'Battle Log', 0.79, [VSlice.BL_ROUND, VSlice.BL_LEFT, VSlice.BL_RIGHT])
    FOOTER     = (255, 'Footer',  0.15, [VSlice.REWARDS, VSlice.CARGO, VSlice.SYSTEM])

class SSType(bytes, Enum):
    """
    Coordinate with binary codes that can be indexed by the int code.
    """
    def __new__(cls, value, label, anno_mean, anno_dev, slices):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.label = label
        obj.anno_mean = anno_mean
        obj.anno_dev = anno_dev
        obj.slices = slices
        return obj

    def __repr__(self):
        return "<SSType label:%s slices:%s>" % (self.label, self.slices)

    def __str__(self):
        return "label:%s pctY:%s" % (self.label, self.slices)

    BATTLE_REPORT  = (1, 'Battle Report',   30,  5, [HSlice.HEADER, HSlice.MATCHUP, HSlice.SUMMARY, HSlice.FOOTER])
    ARMADA_SUMMARY = (2, 'Armada Summary',  50,  5, [HSlice.HEADER, HSlice.MATCHUP, HSlice.A_SUMMARY, HSlice.FOOTER])
    BATTLE_LOG     = (3, 'Battle Log',     100, 25, [HSlice.HEADER, HSlice.MATCHUP, HSlice.BATTLE_LOG])

# class ESField(bytes, Enum):
#     """
#     Coordinate with binary codes that can be indexed by the int code.
#     """
#     def __new__(cls, value, label, es_field_name, raw_fields):
#         obj = bytes.__new__(cls, [value])
#         obj._value_ = value
#         obj.label = label
#         obj.es_field_name = es_field_name
#         obj.raw_fields = raw_fields
#         return obj
#
#     def __repr__(self):
#         return "<EmbedField label:%s pctX:%s>" % (self.label, self.es_field_name)
#
#     def __str__(self):
#         return "EmbedField:%s pctX:%s" % (self.label, self.es_field_name)
#
#     STATUS  = (1,  'Status', 'br_status', [VSlice.STATUS])
#     C1_NAME = (2,  'Player1', 'br_c1_name')
#     C2_NAME = (3,  'Player2', 'br_c2_name')
#     P1_POWR = (4,  'Power1',   0.5, Anchor.L, 'pcom1_power')
#     P2_POWR = (5,  'Power2',   0.5, Anchor.R, 'pcom2_power')
#     P1_SHIP = (6,  'Ship1',    0.5, Anchor.L, 'pcom1_ship')
#     P2_SHIP = (7,  'Ship2',    0.5, Anchor.R, 'pcom2_ship')
#     REWARDS = (8,  'Rewards', 0.33, Anchor.C, 'tss_rewards')
#     CARGO   = (9,  'Cargo',   0.33, Anchor.L, 'tss_cargo')
#     SYSTEM  = (10, 'System',  0.33, Anchor.R, 'tss_system')
