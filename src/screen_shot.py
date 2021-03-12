import io
import json
# import logging

from enum import Enum
# from collections import namedtuple
from discord import Embed
from itertools import islice
from ss_types import *
from ss_entity import *
from log_config import *

# Scale = namedtuple('Scale', ['xF', 'yF'])
logger = get_logger(__name__)

class ScreenShot():
    def __init__(self, text_annotations):
        self.ss_type   = ScreenShot.guessType(text_annotations)

        self.fields    = {}
        self.em_fields = {}
        self.taStack   = text_annotations
        self.taZero    = self.taStack.pop(0)
        taZeroBp       = BoundingPoly.fromVertices(self.taZero['boundingPoly']['vertices'])
        self.ss_border = ScreenShot.guessBorder(BorderType.ZERO, taZeroBp)

        bTop    = (taZeroBp.bottom + taZeroBp.top) * self.ss_border.pctYt
        bBot    = (taZeroBp.bottom + taZeroBp.top) * self.ss_border.pctYb
        hGuess  = (taZeroBp.bottom + taZeroBp.top) - (bTop + bBot)

        bLeft   = (taZeroBp.right + taZeroBp.left) * self.ss_border.pctXl
        bRight  = (taZeroBp.right + taZeroBp.left) * self.ss_border.pctXr
        wGuess  = (taZeroBp.right + taZeroBp.left) - (bLeft + bRight)

        sTop  = bTop
        sLeft = bLeft
        logger.debug("hGuess: %s wGuess: %s sTop: %s bGuess: %s" % (hGuess, wGuess, sTop, self.ss_border))
        for slice in self.ss_type.slices:
            slHeight = hGuess * slice.pctY

            logger.debug("Slice: %s top: %s height: %s"  % (slice, sTop, slHeight))
            slAnno = self.gatherSliceAnnotations(sTop, slHeight)
            logger.debug("    Annotations: %s"  % (len(slAnno)))
            if len(slAnno) == 0:
                continue

            slFields = {}
            for field in slice.fields:
                fWidth = wGuess * field.pctX
                fLeft  = field.anchor.lMult*wGuess - (field.anchor.offsetMult*fWidth)
                fRight = fLeft + fWidth
                fBp = BoundingPoly( sTop, fLeft, (sTop + slHeight), fRight)
                logger.debug("Field: %s poly: %s" % (field, fBp))
                slFields[field] = fBp

            for slTa in slAnno:
                for field, fBp in slFields.items():
                    if fBp.contains(BoundingPoly.fromVertices(slTa['boundingPoly']['vertices'])):
                        fDesc = slTa['description']
                        try:
                            self.fields[field].append(fDesc)
                        except KeyError:
                            logger.debug("Creating key: %s" % (field.label))
                            self.fields[field] = [fDesc]
            sTop += slHeight

        for fType, fDesc in self.fields.items():
            if fType.entity != None:
                eCls = entity_factory(fType.entity)
                ent = eCls(fDesc)
                logger.debug("ft: %s entT: %s ent: %s" % (fType.label, fType.entity, ent))
                self.em_fields[fType.label] = ent

        # self.p1      = Player(self.fields[VSlice.PLAYER1], self.fields[VSlice.P1_POWR], self.fields[VSlice.P1_SHIP])
        # self.p2      = Player(self.fields[VSlice.PLAYER2], self.fields[VSlice.P2_POWR], self.fields[VSlice.P2_SHIP])
        # self.status  = Status(self.fields[VSlice.STATUS])
        # self.p1      = Player(self.fields[VSlice.PLAYER1], self.fields[VSlice.P1_POWR])
        # self.p2      = Player(self.fields[VSlice.PLAYER2], self.fields[VSlice.P2_POWR])
        # self.system  = System(self.fields[VSlice.SYSTEM])
        # self.rewards = Rewards(self.fields[VSlice.REWARDS])
        #
        # if self.p1.leader:
        #     self.ss_type   = SSType.ARMADA_SUMMARY
        #
        # self.em_fields = {'p1': self.p1, self.status.value:self.system, 'p2':self.p2}
        # self.em_fields = {'p1': self.p1, 'System':self.system, 'p2':self.p2}

    def to_embed(self):
        desc = []
        # embed_color = self.rewards.color
        # desc.append(self.status.value)
        # if self.status.defeat:
        #     desc.append(self.rewards.value)
        #     if self.system.sys_type.roe_flag:
        #         desc.append(self.system.sys_type.label)
        #         embed_color = self.system.sys_type.color

        em = Embed.from_dict({
            'title': self.ss_type.label,
            'description': ' '.join(desc),
            'type':  'rich',
            'color': 0xbe2ceb
        })

        for name, value in self.em_fields.items():
            logger.debug("Em Field name: %s value: %s" % (name, value))
            value.as_embed_field(em, name)

        return em


    def gatherSliceAnnotations(self, slTop, slHeight):
        # logger.debug("gatherSliceAnnotations - slTop: %s slHeight: %s stackLen: %s" % (slTop, slHeight, len(self.taStack)))
        slAnn = []
        stTop = slTop
        while (len(self.taStack) > 0):
            logger.debug("stTop: %s stackLen: %s" % ((stTop >= slHeight), (len(self.taStack) > 0)))
            nextTaBp = BoundingPoly.fromVertices(self.taStack[0]['boundingPoly']['vertices'])
            logger.debug("    nextTaBp: %s" % (nextTaBp))
            if nextTaBp.top >= slTop and nextTaBp.bottom <= (slTop+slHeight):
                matchAnn = self.taStack.pop(0)
                logger.debug("    matchAnn: %s" % (matchAnn))

                slAnn.append(matchAnn)
            else:
                logger.debug("    breakAnn: %s" % (self.taStack[0]))
                break

        return slAnn

    @classmethod
    def guessBorder(self, curBType, taZeroBp):
        # print("guessBorder - curBType: %s taZeroBp: %s" % (curBType, taZeroBp))
        hGuess  = taZeroBp.bottom + taZeroBp.top
        wGuess  = taZeroBp.right + taZeroBp.left
        for bType in BorderType:
            if bType.value > curBType.value:
                bTop = bType.pctYt * (taZeroBp.bottom + taZeroBp.top)
                # print("    taZeroBp.top: %s bTop: %s" % (taZeroBp.top, bTop))
                if bTop > 0 and taZeroBp.top > bTop:
                    return bType
                bLeft = bType.pctXl * (taZeroBp.right + taZeroBp.left)
                # print("    taZeroBp.left: %s bLeft: %s" % (taZeroBp.left, bLeft))
                if bLeft > 0 and taZeroBp.left > bLeft:
                    return bType
        return curBType

    @classmethod
    def guessType(self, text_annotations):
        ann_cnt = len(text_annotations)
        if ann_cnt == 0:
            return None
        for sst in SSType:
            sstMin = (sst.anno_mean - sst.anno_dev)
            sstMax = (sst.anno_mean + sst.anno_dev)
            print("guessType - ann: %s sstMin: %s sstMax: %s, sst: %s" % (ann_cnt, sstMin, sstMax, sst))
            if sstMin <= ann_cnt <= sstMax:
                return sst

        return SSType.BATTLE_REPORT
