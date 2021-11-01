# -*- coding: utf-8 -*-
import cv2
import time
import datetime
import os
import yaml
import psutil
import win32gui
import numpy as np

from types import SimpleNamespace
import pyautogui
from PIL import ImageGrab, Image

from winguiauto import findTopWindow


def _t(tag='info', now=None):
    now = now if now else datetime.datetime.now()
    tmp = now.strftime('%Y-%m-%d %H:%M:%S.%f')
    arr = tmp.split('.', 2)
    if len(arr) == 2:
        ms = int(arr[1] + '0' * (6 - len(arr[1])))
        ret = arr[0] + '.' + '{:0>3d}'.format(int(ms / 1000))
    else:
        ret = arr[0] + '.000'

    return ret + ' [' + tag.upper() + ']'


def set_top_window(title):
    top_windows = []
    chk = lambda hwnd, ll: ll.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(chk, top_windows)
    for i in top_windows:
        if title in i[1].lower():
            win32gui.ShowWindow(i[0], 5)
            win32gui.SetForegroundWindow(i[0])
            return True
    else:
        return False


def restart_game(lang):
    global G_HWND, G_RECT
    G_HWND, G_RECT = None, None
    
    if lang == 'eng':
        bn = 'Battle.net'
        hs = 'Hearthstone'
    elif lang == 'chs':
        bn = "战网"
        hs = "炉石传说"
    else:
        raise ValueError(f"Language {lang} not supported")

    icon_path = os.path.join(f'imgs_{lang}', 'icons', 'start_game_icon.png')
    icon = cv2.imread(icon_path)
    icon = cv2.cvtColor(np.array(icon), cv2.COLOR_BGR2GRAY)
    for p in psutil.process_iter():
        if p.name() == 'Hearthstone.exe':
            p.kill()
            print("hearthstone killed")
    time.sleep(10)
    bn_found = set_top_window(bn)
    if bn_found:
        while True:
            image = ImageGrab.grab()
            image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
            success, x, y, conf = find_icon_location(image, icon, 0.9)
            if success:
                pyautogui.click(x, y)
                time.sleep(5)
                set_top_window(hs)
                break


G_HWND = None
G_RECT = None


def find_lushi_window(title):
    global G_HWND, G_RECT

    hwnd = G_HWND if G_HWND else findTopWindow(title)
    G_HWND = hwnd

    rect = G_RECT if G_RECT else win32gui.GetWindowPlacement(hwnd)[-1]
    G_RECT = rect

    image = ImageGrab.grab(rect)
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    return rect, image


def find_icon_location(lushi, icon, confidence=0.9):
    result = cv2.matchTemplate(lushi, icon, cv2.TM_CCOEFF_NORMED)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
    if maxVal > confidence:
        (startX, startY) = maxLoc
        endX = startX + icon.shape[1]
        endY = startY + icon.shape[0]
        return True, (startX + endX) // 2, (startY + endY) // 2, maxVal
    else:
        return False, None, None, maxVal


class Agent:
    def __init__(self, lang):
        self.lang = lang
        self.icons = {}
        self.treasure_blacklist = {}
        self.heros_whitelist = {}
        

        if self.lang == 'eng':
            self.cfg_file = 'config_eng.yaml'
            self.img_folder = 'imgs_eng'
            self.title = 'hearthstone'
        elif self.lang == 'chs':
            self.cfg_file = 'config_chs.yaml'
            self.img_folder = "imgs_chs"
            self.title = "炉石传说"
        else:
            raise ValueError(f"Language {self.lang} is not supported yet")

        self.load_config()

        
    def load_config(self):
        found = False
        for p in psutil.process_iter():
            if p.name() == 'Hearthstone.exe':
                found = True
                break

        if not found:
            restart_game(self.lang)
            time.sleep(10)
            set_top_window(self.title)
            
        with open(self.cfg_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        self.basic = SimpleNamespace(**config['basic'])
        self.skill = SimpleNamespace(**config['skill'])
        self.locs = SimpleNamespace(**config['location'])
        pyautogui.PAUSE = self.basic.delay

        imgs = [img for img in os.listdir(os.path.join(self.img_folder, 'icons')) if img.endswith('.png')]
        for img in imgs:
            k = img.split('.')[0]
            v = cv2.cvtColor(cv2.imread(os.path.join(self.img_folder, 'icons', img)), cv2.COLOR_BGR2GRAY)
            self.icons[k] = v

        set_top_window(self.title)

        
    def check_state(self):
        lushi, image = find_lushi_window(self.title)
        output = {}

        try_keys = ['mercenaries', 'pvp', 'pvp_team']
        need_keys = try_keys + ['pvp_ready', 'member_not_ready', 'surrender', 'final_reward', 'final_reward2']
        first_check = [(kk, vv) for kk, vv in self.icons.items() if kk in try_keys]
        second_check = [(kk, vv) for kk, vv in self.icons.items() if kk not in try_keys and kk in need_keys]

        for k, v in first_check:
            success, click_loc, conf = self.find_icon_loc(v, lushi, image)
            if success:
                output[k] = (click_loc, conf)
                return output, lushi, image

        for k, v in second_check:
            success, click_loc, conf = self.find_icon_loc(v, lushi, image)
            if success:
                output[k] = (click_loc, conf)

        return output, lushi, image

    def find_icon_loc(self, icon, lushi, image):
        success, X, Y, conf = find_icon_location(image, icon, self.basic.confidence)
        if success:
            click_loc = (X + lushi[0], Y + lushi[1])
        else:
            click_loc = None
        return success, click_loc, conf

    def run_pvp(self):
        delay = 0.5
        empty_acc = 0

        self.basic.reward_count = 5
        while True:
            time.sleep((np.random.rand() + delay) if delay > 0 else 0.5)
            states, rect, screen = self.check_state()
            delay = delay if states else (delay + 1.8)
            delay = delay if delay < 9 else 9
            empty_acc = 0 if states else (empty_acc + 1)
            print(_t(), 'states:', states, empty_acc, delay)

            if empty_acc > 50:
                restart_game(self.lang)
                time.sleep(10)
                set_top_window(self.title)
                continue
                
            if 'mercenaries' in states:
                pyautogui.click(states['mercenaries'][0])
                continue

            if 'pvp' in states:
                pyautogui.click(states['pvp'][0])
                continue

            if 'pvp_team' in states:
                pyautogui.click(rect[0] + self.locs.team_select[0], rect[1] + self.locs.team_select[1])
                continue

            if 'pvp_ready' in states or 'member_not_ready' in states:
                delay = 0.5
                pyautogui.click(rect[0] + self.locs.options[0], rect[1] + self.locs.options[1])
                time.sleep(self.basic.pvp_delay)
                if self.basic.fast_surrender:
                    time.sleep(2.0)
                    pyautogui.click(rect[0] + self.locs.surrender[0], rect[1] + self.locs.surrender[1])
                else:
                    states, rect, screen = self.check_state()
                    if 'surrender' in states:
                        time.sleep(2.0)
                        pyautogui.click(states['surrender'][0])
                for _ in range(5):
                    time.sleep(0.8)
                    pyautogui.click(rect[0] + self.locs.empty[0], rect[1] + self.locs.empty[1])

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

                continue

            pyautogui.click(rect[0] + self.locs.empty[0], rect[1] + self.locs.empty[1])
            time.sleep(1.5)

def main():
    pyautogui.confirm(
        text="请启动炉石，将炉石调至窗口模式，分辨率设为1600x900，画质设为高; 请参考config修改配置文件")

    agent = Agent(lang='chs')
    agent.run_pvp()


if __name__ == '__main__':
    main()
