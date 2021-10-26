# -*- coding: utf-8 -*-
import pyautogui
import cv2
import time
import numpy as np
import os
import yaml
from types import SimpleNamespace

from util import find_lushi_window, find_icon_location, restart_game, set_top_window


class Agent:
    def __init__(self, lang):
        self.lang = lang
        self.icons = {}
        self.treasure_blacklist = {}
        self.heros_whitelist = {}
        self.load_config()

    def load_config(self):
        if self.lang == 'eng':
            cfg_file = 'config_eng.yaml'
            img_folder = 'imgs_eng'
            self.title = 'hearthstone'
        elif self.lang == 'chs':
            cfg_file = 'config_chs.yaml'
            img_folder = "imgs_chs"
            self.title = "炉石传说"
        else:
            raise ValueError(f"Language {self.lang} is not supported yet")

        with open(cfg_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        self.basic = SimpleNamespace(**config['basic'])
        self.skill = SimpleNamespace(**config['skill'])
        self.locs = SimpleNamespace(**config['location'])
        pyautogui.PAUSE = self.basic.delay

        imgs = [img for img in os.listdir(os.path.join(img_folder, 'icons')) if img.endswith('.png')]
        for img in imgs:
            k = img.split('.')[0]
            v = cv2.cvtColor(cv2.imread(os.path.join(img_folder, 'icons', img)), cv2.COLOR_BGR2GRAY)
            self.icons[k] = v

        imgs = [img for img in os.listdir(os.path.join(img_folder, 'treasure_blacklist')) if img.endswith('.png')]
        for img in imgs:
            k = img.split('.')[0]
            v = cv2.cvtColor(cv2.imread(os.path.join(img_folder, 'treasure_blacklist', img)), cv2.COLOR_BGR2GRAY)
            self.treasure_blacklist[k] = v

        imgs = [img for img in os.listdir(os.path.join(img_folder, 'heros_whitelist')) if img.endswith('.png')]
        for img in imgs:
            k = img.split('.')[0]
            v = cv2.cvtColor(cv2.imread(os.path.join(img_folder, 'heros_whitelist', img)), cv2.COLOR_BGR2GRAY)
            self.heros_whitelist[k] = v

        set_top_window(self.title)

    def check_state(self):
        lushi, image = find_lushi_window(self.title)
        output = {}
        for k, v in self.icons.items():
            success, click_loc, conf = self.find_icon_loc(v, lushi, image)
            if success:
                output[k] = (click_loc, conf)

        for k, v in self.treasure_blacklist.items():
            success, click_loc, conf = self.find_icon_loc(v, lushi, image)
            if success:
                output[k] = (click_loc, conf)

        for k, v in self.heros_whitelist.items():
            success, click_loc, conf = self.find_icon_loc(v, lushi, image)
            if success:
                output[k] = (click_loc, conf)

        return output, lushi, image

    def analyse_battle_field(self, screen):
        x1, y1, x2, y2 = self.locs.enemy_region
        img = screen[x1:x2, y1:y2]
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, thresh = cv2.threshold(img_gray, 250, 255, 0)
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(thresh)
        img_copy = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
        # print(stats)
        for i in range(1, num_labels):
            mask = labels == i
            if stats[i][-1] > 50:
                img_copy[:, :, 0][mask] = 255
                img_copy[:, :, 1][mask] = 255
                img_copy[:, :, 2][mask] = 255

        # img_data = pytesseract.image_to_boxes(img_copy, config='--oem 3 -c tessedit_char_whitelist={0123456789}')
        # Image.fromarray(img_copy)

    def find_icon_loc(self, icon, lushi, image):
        success, X, Y, conf = find_icon_location(image, icon, self.basic.confidence)
        if success:
            click_loc = (X + lushi[0], Y + lushi[1])
        else:
            click_loc = None
        return success, click_loc, conf

    def run_pvp(self):
        self.basic.reward_count = 5
        state = ""
        tic = time.time()
        while True:
            time.sleep(self.basic.delay + np.random.rand())
            states, rect, screen = self.check_state()
            print(states)

            if time.time() - tic > self.basic.longest_waiting:
                restart_game(self.lang)
                tic = time.time()
            if 'mercenaries' in states:
                pyautogui.click(states['mercenaries'][0])
                if state != "mercenaries":
                    state = "mercenaries"
                    tic = time.time()
                continue

            if 'pvp' in states:
                pyautogui.click(states['pvp'][0])
                if state != "pvp":
                    state = "pvp"
                    tic = time.time()
                continue

            if 'pvp_team' in states:
                tic = time.time()
                pyautogui.click(rect[0] + self.locs.team_select[0], rect[1] + self.locs.team_select[1])
                if state != "pvp_team":
                    state = "pvp_team"
                    tic = time.time()
                continue

            if 'pvp_ready' in states or 'member_not_ready' in states:
                print("Surrendering")
                pyautogui.click(rect[0] + self.locs.options[0], rect[1] + self.locs.options[1])
                time.sleep(self.basic.pvp_delay)
                if self.basic.fast_surrender:
                    pyautogui.click(rect[0] + self.locs.surrender[0], rect[1] + self.locs.surrender[1])
                else:
                    states, rect, screen = self.check_state()
                    if 'surrender' in states:
                        pyautogui.click(states['surrender'][0])
                for _ in range(5):
                    pyautogui.click(rect[0] + self.locs.empty[0], rect[1] + self.locs.empty[1])

                if state != "pvp_ready":
                    state = "pvp_ready"
                    tic = time.time()
                continue

            if 'final_reward' in states or 'final_reward2' in states:
                reward_locs = eval(self.locs.rewards[self.basic.reward_count])
                for loc in reward_locs:
                    pyautogui.moveTo(rect[0] + loc[0], rect[1] + loc[1])
                    pyautogui.click()
                pyautogui.moveTo(rect[0] + self.locs.rewards['confirm'][0], rect[1] + self.locs.rewards['confirm'][1])
                pyautogui.click()
                for _ in range(5):
                    pyautogui.click(rect[0] + self.locs.empty[0], rect[1] + self.locs.empty[1])
                if state != "final_reward":
                    state = "final_reward"
                    tic = time.time()
                continue

            if state != "":
                state = ""
                tic = time.time()

            pyautogui.click(rect[0] + self.locs.empty[0], rect[1] + self.locs.empty[1])


def main():
    agent = Agent(lang='chs')
    agent.run_pvp()


if __name__ == '__main__':
    main()
