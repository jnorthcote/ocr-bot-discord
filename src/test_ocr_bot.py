import io
import requests
import time
import filetype
import json
import unittest

from gvis_lib import *
from screen_shot import ScreenShot, VSlice

class TestSectionScaling(unittest.TestCase):


    # def test_ss_guess_type_url(self):
    #     sst = None
    #
    #     # ta_dict = annotate_image_url('https://media.discordapp.net/attachments/702459881223094332/707209177025609768/Screen_Shot_2020-04-29_at_5.30.45_AM.png')
    #     # ta_dict = annotate_image_url('https://cdn.discordapp.com/attachments/702459881223094332/705033838195245177/Screen_Shot_2020-04-29_at_5.30.45_AM.png')
    #     # ta_dict = annotate_image_url('https://cdn.discordapp.com/attachments/702459881223094332/702870754772910220/Screen_Shot_2020-04-22_at_11.08.16_PM.png')
    #     # ta_dict = annotate_image_url('https://cdn.discordapp.com/attachments/702459881223094332/707609870324596806/Screen_Shot_2020-05-05_at_7.41.41_PM.png')
    #
    #     sst = ScreenShot.guessType(ta_dict['textAnnotations'])
    #     print("sst: %s" % (sst))

    # def test_ss_guess_type(self):
    #     sst = None
    #
    #     # with open('data/test_image_y_border.json',) as f:
    #     # with open('data/uri_crop_new_base.json',) as f:
    #     # with open('data/test_armada_victory.json',) as f:
    #     with open('data/test_arm_bl.json',) as f:
    #         data = json.load(f)
    #         sst = ScreenShot.guessType(data['textAnnotations'])
    #     print("sst: %s" % (sst))

    def test_armada_victory(self):
        ss = None
        with open('data/test_arm_bl.json',) as f:
            data = json.load(f)
            ss = ScreenShot(data['textAnnotations'])

        for k, v in ss.__dict__["fields"].items():
            print("k: %s v: %s" % (k, v))

        em = ss.to_embed()
        for k,v in em.to_dict().items():
            print("k: %s v: %s" % (k, v))


# class TestSectionScaling(unittest.TestCase):
#
    # def test_armada_victory(self):
    #     ss = None
    #     with open('data/test_armada_victory.json',) as f:
    #         data = json.load(f)
    #         ss = ScreenShot(data['textAnnotations'])
    #
    #     for k, v in ss.__dict__["fields"].items():
    #         print("k: %s v: %s" % (k, v))
    #
    #     em = ss.to_embed()
    #     for k,v in em.to_dict().items():
    #         print("k: %s v: %s" % (k, v))

    # def test_image_scale(self):
    #     with open('data/uri_crop_new_base.json',) as f:
    #         data = json.load(f)
    #         ss = ScreenShot(data['textAnnotations'])


    # def test_image_y_border(self):
    #     with open('data/test_image_y_border.json',) as f:
    #         data = json.load(f)
    #         ss = ScreenShot(data['textAnnotations'])
            # print(' '.join(ss.fields[VSlice.STATUS]))

    # def test_iphone_scale(self):
    #     with open('data/iphone/test_iphone_scale.json',) as f:
    #         data = json.load(f)
    #         ss = ScreenShot(data['textAnnotations'])

    # def test_image_scale(self):
    #     with open('data/test_image_scale_0.json',) as f:
    #         data = json.load(f)
    #         ss = ScreenShot(data['textAnnotations'], 1080, 540)
    #
    # def test_image_scale_full(self):
    #     with open('data/test_image_scale.json',) as f:
    #         data = json.load(f)
    #         ss = ScreenShot(data['textAnnotations'], 1080, 540)

    # def test_image_scale_status(self):
    #     with open('data/test_image_scale_status.json',) as f:
    #         data = json.load(f)
    #         ss = ScreenShot(data['textAnnotations'], 1080, 540)

    # def test_image_scale_player(self):
    #     with open('data/test_image_scale_player.json',) as f:
    #         data = json.load(f)
    #         ss = ScreenShot(data['textAnnotations'], 1080, 540)
    #         self.assertEqual(' '.join(ss.fields[SectionType.PLAYER1]), '22 [SHYT] TeabagTheDbag')
    #         print(' '.join(ss.fields[SectionType.PLAYER2]))

    # def test_image_scale_cargo(self):
    #     with open('data/test_image_scale_cargo.json',) as f:
    #         data = json.load(f)
    #         ss = ScreenShot(data['textAnnotations'], 1080, 540)
    #         print(' '.join(ss.fields[SectionType.CARGO]))

    # def test_image_scale_cargo2(self):
    #     with open('data/test_image_scale_cargo2.json',) as f:
    #         data = json.load(f)
    #         ss = ScreenShot(data['textAnnotations'])
    #         print(' '.join(ss.fields[SectionType.CARGO]))

    # def test_image_scale_system(self):
    #     with open('data/test_image_scale_system.json',) as f:
    #         data = json.load(f)
    #         ss = ScreenShot(data['textAnnotations'], 1080, 540)
    #         print(' '.join(ss.fields[SectionType.SYSTEM]))


if __name__ == '__main__':
    unittest.main()
