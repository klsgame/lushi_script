import pyautogui
import cv2
import time
from PIL import ImageGrab, Image
import numpy as np

import win32api
from winguiauto import findTopWindow
import win32gui
import win32con
import os

import datetime

G_HWND = None
G_RECT = None


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

def find_lushi_window():
    global G_HWND, G_RECT

    hwnd = G_HWND if G_HWND else findTopWindow("炉石传说")
    G_HWND = hwnd

    rect = G_RECT if G_RECT else win32gui.GetWindowPlacement(hwnd)[-1]
    G_RECT = rect

    image = ImageGrab.grab(rect)
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    return rect, image


def find_icon_location(k, lushi, icon, kk=0.8899):
    result = cv2.matchTemplate(lushi, icon, cv2.TM_CCOEFF_NORMED)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
    if maxVal > kk:
        (startX, startY) = maxLoc
        endX = startX + icon.shape[1]
        endY = startY + icon.shape[0]
        return True, (startX + endX) // 2, (startY + endY) // 2, maxVal
    else:
        return False, None, None, maxVal



_tp = lambda pos=None, y=None: pos if isinstance(pos, (tuple, list)) else (pos, y)
r_moveTo = lambda *args, **kwgs: pyautogui.moveTo(*args, **kwgs)
r_click = lambda *args, **kwgs: pyautogui.click(*args, **kwgs)

class Agent:

    def __init__(self, team_id, heros_id, skills_id, targets_id, hero_cnt, early_stop):
        self.icons = {}
        imgs = [img for img in os.listdir('imgs') if img.endswith('.png')]
        for img in imgs:
            k = img.split('.')[0]
            v = cv2.cvtColor(cv2.imread(os.path.join('imgs', img)), cv2.COLOR_BGR2GRAY)
            self.icons[k] = v

        self.team_id = team_id
        self.heros_id = heros_id
        self.skills_id = skills_id
        self.targets_id = targets_id
        self.hero_cnt = hero_cnt
        self.early_stop = early_stop

        self.hero_relative_locs = [
            (677, 632),
            (807, 641),
            (943, 641)
        ]

        self.enemy_mid_location = (850, 285)

        self.skill_relative_locs = [
            (653, 447),
            (801, 453),
            (963, 459),
        ]

        self.treasure_locs = [
            (707, 376), (959, 376), (1204, 376)
        ]
        self.treasure_collect_loc = (968, 765)

        self.visitor_locs = [
            (544, 426), (790, 420), (1042, 416)
        ]
        self.visitor_choose_loc = (791, 688)

        self.members_loc = (622, 1000, 900)

        self.drag2loc = (1213, 564)

        self.locs = {
            'left': [(452, 464), (558, 461), (473, 465)],
            'right': [(777, 478), (800, 459), (903, 469)]
        }

        self.finial_reward_locs = [
            (660, 314), (554, 687), (1010, 794), (1117, 405), (806, 525)
        ]

        self.select_travel_relative_loc = (1090, 674)

        self.team_locations = [(374, 324), (604, 330), (837, 324)]
        self.team_loc = self.team_locations[team_id]
        self.start_team_loc = (1190, 797)
        self.start_game_relative_loc = (1240, 742)
        # self.start_point_relative_loc = (646, 712)

        self.options_loc = (1579, 920)
        self.surrender_loc = (815, 363)

        self.start_battle_loc = (1327, 454)
        self.check_team_loc = (674, 885)
        self.give_up_loc = (929, 706)
        self.give_up_cfm_loc = (712, 560)

    def give_up(self, rect):
        pyautogui.click(self.check_team_loc[0] + rect[0], self.check_team_loc[1] + rect[1])
        time.sleep(0.1)
        pyautogui.click(self.give_up_loc[0] + rect[0], self.give_up_loc[1] + rect[1])
        time.sleep(0.1)
        pyautogui.click(self.give_up_cfm_loc[0] + rect[0], self.give_up_cfm_loc[1] + rect[1])

    def run(self):
        self.acc, self.state, self.no = 0, '', '2-6'
        delay, empty_acc, member_ready_acc, is_first = 0.5, 0, 0, True
        last_states = {}
        while True:
            time.sleep((np.random.rand() + delay) if delay > 0 else 0.3)
            states, rect = self.check_state()
            x_moveTo = lambda pos=None, y=None, **kwgs: pyautogui.moveTo(rect[0] + _tp(pos, y)[0], rect[1] + _tp(pos, y)[1], **kwgs)
            x_click = lambda pos=None, y=None, **kwgs: pyautogui.click(rect[0] + _tp(pos, y)[0], rect[1] + _tp(pos, y)[1], **kwgs)
            
            delay = delay if states else (delay + 0.1)
            empty_acc = 0 if states else (empty_acc + 1)
            delay = delay if delay < 3 else 3
            print(_t(), 'states:', states, empty_acc, delay)

            if empty_acc >= 10:
                empty_acc = 0
                self.give_up(rect)
                continue

            if 'boom' in states or 'blue_portal' in states or 'destroy' in states:
                self.give_up(rect)
                continue
                    
            map_not_ready = False
            if ('map_not_ready' in states or 'f-buf' in states or 'f-fh' in states or 'stranger' in states) and 'start_point' not in states:
                if last_states and 'treasure_list' in last_states:
                    self.give_up(rect)
                    continue
                    
                map_not_ready = True
                for b_icon in ['b-fs', 'b-zs', 'b-ck', 'b-fh']:
                    if b_icon in states and 'b-sp' not in states:
                        r_moveTo(states[b_icon][0])
                        r_click(states[b_icon][0])
                        map_not_ready = False
                        time.sleep(0.9)
                        x_moveTo(self.start_game_relative_loc)
                        r_click()
                        break

            if map_not_ready:
                has_break = True
                has_sp = False
                if 'b-sp' in states:
                    r_moveTo(states['b-sp'][0])
                    r_click(states['b-sp'][0])
                    time.sleep(0.9)
                    x_moveTo(self.start_game_relative_loc)
                    r_click()
                    
                time.sleep(1.5)
                new_states, rect = self.check_state()
                print(_t(), 'states_:', new_states, empty_acc, delay)

                for b_icon in ['b-fs', 'b-zs', 'b-ck', 'b-fh']:
                    if b_icon in new_states and 'b-sp' not in new_states:
                        r_moveTo(new_states[b_icon][0])
                        r_click(new_states[b_icon][0])
                        map_not_ready = False
                        time.sleep(0.9)
                        x_moveTo(self.start_game_relative_loc)
                        r_click()
                        has_break = False
                        break
                        
                if 'b-sp' in new_states:
                    r_moveTo(new_states['b-sp'][0])
                    r_click(new_states['b-sp'][0])
                    time.sleep(0.9)
                    x_moveTo(self.start_game_relative_loc)
                    r_click()
                        
                if 'start_game' in new_states and 'map_not_ready' not in new_states:
                    x_moveTo(self.start_game_relative_loc)
                    r_click()
                    time.sleep(10) if 'start_game' in new_states else time.sleep(1.0)
                    continue

                if 'boom' in new_states or 'blue_portal' in new_states or 'destroy' in new_states:
                    self.give_up(rect)
                    continue

                if 'stranger' in new_states:
                    x_click(self.start_game_relative_loc)
                    visitor_id = np.random.randint(0, 3)
                    visitor_loc = self.visitor_locs[visitor_id]
                    x_click(visitor_loc)
                    x_click(self.visitor_choose_loc)
                    time.sleep(2.0)
                    stranger_loc = new_states['stranger'][0]
                    r_click(stranger_loc[0], stranger_loc[1], clicks=2, interval=0.25)
                    print(_t(), 'Found stranger', new_states)
                    self.give_up(rect)
                    continue

                x_moveTo(self.start_game_relative_loc)
                r_click()
                
                if not has_sp and ('start_game' in new_states or not new_states):
                    time.sleep(10) if 'start_game' in new_states else time.sleep(1.0)
                    has_break = False

                if has_break:
                    self.give_up(rect)
                    continue

            last_states = states
            
            if 'visitor_list' in states:
                visitor_id = np.random.randint(0, 3)
                visitor_loc = self.visitor_locs[visitor_id]
                x_click(visitor_loc)
                x_click(self.visitor_choose_loc)
                time.sleep(2.0)
                stranger_loc = states['stranger'][0]
                r_click(stranger_loc[0], stranger_loc[1], clicks=2, interval=0.25)
                print(_t(), 'Found stranger', states)
                self.give_up(rect)
                continue

            if self.no in states:
                member_ready_acc = 0
                r_click(states[self.no][0])
                x_click(self.start_game_relative_loc)
                if not is_first:
                    time.sleep(0.6)
                    x_click(self.start_game_relative_loc)
                    time.sleep(0.6)
                    x_click(self.start_game_relative_loc)
                    time.sleep(0.6)
                    x_click(self.start_game_relative_loc)
                    time.sleep(0.6)
                    x_click(self.start_game_relative_loc)
                    time.sleep(0.6)
                    x_click(self.start_game_relative_loc)
                    time.sleep(0.6)
                    x_click(self.start_game_relative_loc)
                
                is_first = False
                continue

            if 'team_list' in states:
                x_click(self.team_loc)
                if 'team_lock' in states:
                    r_click(states['team_lock'][0])
                x_click(self.start_team_loc)
                time.sleep(0.3)
                continue

            if 'member_ready' in states:
                if 'ice_berg2' in states:
                    x_click(self.options_loc)
                    x_click(self.surrender_loc)
                    continue

                if self.hero_cnt > 3:
                    first_x, last_x, y = self.members_loc
                    for i, idx in enumerate(self.heros_id):
                        assert (self.hero_cnt - i - 1 > 0)
                        dis = (last_x - first_x) // (self.hero_cnt - i - 1)
                        loc = (first_x + dis * (idx - i), y)
                        x_click(loc)
                        x_moveTo(self.drag2loc)
                        r_click()

                r_click(states['member_ready'][0])
                member_ready_acc += 1
                delay = -0.5
                continue

            if 'battle_ready' in states:
                r_click(states['battle_ready'][0])
                continue

            if 'treasure_list' in states or 'treasure_replace' in states:
                treasure_loc_id = np.random.randint(0, 3)
                treasure_loc = self.treasure_locs[treasure_loc_id]
                if 'ice_berg' in states:
                    x_dis = np.abs(treasure_loc[0] + rect[0] - states['ice_berg'][0][0])
                    if x_dis < 100:
                        continue

                x_click(treasure_loc)
                x_click(self.treasure_collect_loc)
                
                if member_ready_acc >= 3:
                    time.sleep(0.9)
                    self.give_up(rect)
                    
                continue

            if 'skill_select' in states or 'not_ready_dots' in states:
                x_click(self.start_game_relative_loc)
                time.sleep(0.4)

                first_hero_loc = self.hero_relative_locs[0]
                x_click(first_hero_loc)
                for idx, skill_id, target_id in zip([0, 1, 2], self.skills_id, self.targets_id):
                    time.sleep(0.2)
                    hero_loc = (rect[0] + self.hero_relative_locs[idx][0], rect[1] + self.hero_relative_locs[idx][1])
                    x_click(self.skill_relative_locs[skill_id])

                    if target_id != -1:
                        x_click(self.enemy_mid_location)
                time.sleep(0.4)
                x_click(self.start_battle_loc)
                continue

            x_moveTo(self.start_game_relative_loc)
            r_click()
            
            time.sleep(10) if 'start_game' in states else time.sleep(1.0)


    def check_state(self, ext=False):
        self.acc += 1
        
        lushi, image = find_lushi_window()
        output_list = {}
        try_keys = ['battle_ready', 'member_ready', 'not_ready_dots', 'treasure_list', 'treasure_replace', 'skill_select', self.no]
        ext_keys = (try_keys + ['visitor_list']) if ext else try_keys
        
        ext_keys = ['b-fs', 'b-zs', 'b-ck', 'b-fh', 'b-sp', 'stranger', 'blue_portal', 'destroy', 'boom', 'f-buf', 'f-fh']
        ext_keys = ext_keys if ext else []
        base_keys = ['start_game', 'map_not_ready', 'start_point']
        base_keys = (base_keys + ['team_lock', 'team_list']) if self.acc % 5 == 1 else base_keys
        
        need_keys = try_keys + base_keys + ext_keys
        first_check = [(kk, vv) for kk, vv in self.icons.items() if kk in try_keys]
        second_check = [(kk, vv) for kk, vv in self.icons.items() if kk not in try_keys and kk in need_keys]

        for k, v in first_check:
            success, click_loc, conf = self.find_icon(k, v, lushi, image)
            if success:
                output_list[k] = (click_loc, conf)
                return output_list, lushi

        for k, v in second_check:
            success, click_loc, conf = self.find_icon(k, v, lushi, image)
            if success:
                output_list[k] = (click_loc, conf)

        return output_list, lushi

    def find_icon(self, k, icon, lushi, image):
        success, X, Y, conf = find_icon_location(k, image, icon)
        if success:
            click_loc = (X + lushi[0], Y + lushi[1])
        else:
            click_loc = None
        return success, click_loc, conf


def main():
    pyautogui.confirm(
        text="请启动炉石，将炉石调至窗口模式，分辨率设为1600x900，画质设为高; 程序目前只支持三个场上英雄，请确保上场英雄不会死且队伍满6人，否则脚本会出错；请参考config.txt修改配置文件")
    with open('config.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    team_id, heros_id, skills_id, targets_id, early_stop, delay = lines

    heros_id = [int(s.strip()) for s in heros_id.strip().split(' ') if not s.startswith('#')]
    skills_id = [int(s.strip()) for s in skills_id.strip().split(' ') if not s.startswith('#')]
    targets_id = [int(s.strip()) for s in targets_id.strip().split(' ') if not s.startswith('#')]
    team_id, hero_cnt = [int(s.strip()) for s in team_id.strip().split(' ') if not s.startswith('#')]
    early_stop = int(early_stop.split('#')[0].strip())
    delay = float(delay.split('#')[0].strip())

    print(_t(), 'heros_id:', heros_id, 'skills_id:', skills_id)
    assert (len(skills_id) == 3 and len(targets_id) == 3 and len(heros_id) == 3)
    assert (team_id in [0, 1, 2] and hero_cnt <= 6)

    pyautogui.PAUSE = delay

    agent = Agent(team_id=team_id, heros_id=heros_id, skills_id=skills_id, targets_id=targets_id, hero_cnt=hero_cnt,
                  early_stop=early_stop)
    agent.run()


if __name__ == '__main__':
    main()
