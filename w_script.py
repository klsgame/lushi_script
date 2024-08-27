# -*- coding: utf-8 -*-

import datetime
import os
import random
import sys
import time
from urllib import request

import winsound

import pyautogui
import win32gui

from winguiauto import findTopWindow, getCursorInfo, getPixel

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


def _tt(fmt='%Y-%m-%d %H:%M:%S.%f', fix=True, now=None):
    now = now if now else datetime.datetime.now()
    tmp = now.strftime(fmt)
    if not fix:
        return tmp

    arr = tmp.split('.', 2)
    if len(arr) == 2:
        ms = int(arr[1] + '0' * (6 - len(arr[1])))
        ret = arr[0] + '.' + '{:0>3d}'.format(int(ms / 1000))
    else:
        ret = arr[0] + '.000'

    return ret


def find_wow_window():
    global G_HWND, G_RECT

    hwnd = G_HWND if G_HWND else findTopWindow("魔兽世界")
    G_HWND = hwnd if hwnd else None

    if not G_HWND:
        return G_RECT, None, None

    t_rect = G_RECT if G_RECT else win32gui.GetWindowPlacement(hwnd)[-1]
    G_RECT = t_rect

    return t_rect


def set_top_window(title='魔兽世界'):
    top_windows = []

    def windowEnumerationHandler(hwnd, _top_windows):
        _top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(windowEnumerationHandler, top_windows)
    for i in top_windows:
        if title in i[1].lower():
            win32gui.ShowWindow(i[0], 5)
            win32gui.SetForegroundWindow(i[0])
            return True
    else:
        return False


def http_get(url):
    try:
        response = request.urlopen(url)
        return response.status, response.read()
    except Exception as ex:
        return 500, 'Err: %r => %s' % (type(ex), ex)


rect = [0, 0]
_tp = lambda pos=None, y=None: pos if isinstance(pos, (tuple, list)) else (pos, y)

r_moveTo = lambda *args, **kwgs: pyautogui.moveTo(*args, **kwgs)
r_click = lambda *args, **kwgs: pyautogui.click(*args, **kwgs)
x_moveTo = lambda pos=None, y=None, **kwgs: pyautogui.moveTo(rect[0] + _tp(pos, y)[0],
                                                             rect[1] + _tp(pos, y)[1], **kwgs)
x_click = lambda pos=None, y=None, **kwgs: pyautogui.click(rect[0] + _tp(pos, y)[0],
                                                           rect[1] + _tp(pos, y)[1], **kwgs)


def _next_pos(mid, nn, wn, hn):
    pos = [mid[0], mid[1]]
    op, k = 0, 1
    while nn > 0:
        j = k
        while nn > 0 and j > 0:
            on = op % 4
            if on == 0:
                pos[0] += wn
            elif on == 1:
                pos[1] += hn
            elif on == 2:
                pos[0] -= wn
            elif on == 3:
                pos[1] -= hn
            j -= 1
            nn -= 1
        op += 1
        k = (k + 1) if op % 2 == 0 else k

    return pos[0], pos[1]


class Agent:

    def __init__(self, mpos, cpos=None, first_bait=300, key_fish='1', key_bait='2', key_auto='',
                 tmax=16.9, tmin=3.5, wh=(1600, 1200)):
        self.first_bait = first_bait
        self.mpos = mpos
        self.key_fish, self.key_bait, self.key_auto = key_fish, key_bait, key_auto
        self.tmax, self.tmin = tmax, tmin

        self.acc, self.state, self.no = 0, 'unknown', '0-0'
        self.check_pos, self.shutdown_acc = None, 0
        
        if cpos and cpos[0] > 0 and cpos[1] > 0:
            self.check_pos = cpos
            
        self.width, self.height = wh

    def do_shutdown(self):
        print(_t('error'), 'shutdown acc:', self.acc, ', do_shutdown:', self.shutdown_acc)
        http_get(
            'https://sctapi.ftqq.com/SCT193913TUNx0lH9vKbmWEsHHQuj7E9DX.send?title=shutdown_' + _tt('%Y-%m-%d_%H_%M_%S',
                                                                                                    False))
        autoshutdown = os.path.join(os.getcwd(), 'autoshutdown.bat')
        os.system("cmd.exe /c " + autoshutdown)
        time.sleep(1)

    def run(self, no=None):
        # http_get('https://sctapi.ftqq.com/SCT193913TUNx0lH9vKbmWEsHHQuj7E9DX.send?title=run_pve_break_' + _tt(
        # '%Y-%m-%d_%H_%M_%S', False)) self._check_image()
        self.run_pve_full(no)

    def run_test(self, no='0-0', nn=50):
        global rect

        print(_t(), 'run_test nn:', nn)

        self.acc, self.state, self.no = 0, 'init', no
        delay, is_first = 2.5, True

        set_top_window()
        self._check_image('run_test_init')

        while True:
            rect = find_wow_window()

            time.sleep((random.random() + delay) if delay > 0 else 0.3)

            flags, hcursor, mpos = getCursorInfo()
            rgb = getPixel(self.mpos[0], self.mpos[1])
            print(_t(), 'no:', self.no, 'mpos:', mpos, 'rgb:', rgb, 'hcursor:', hcursor)

            nn -= 1
            if nn <= 0:
                break

    def get_box_mid(self, _rect, h=0.32, w=0.30):
        t = _rect[1] + self.height * 0.5 * h
        d = _rect[1] + self.height * 0.5 - self.height * 0.5 * h
        l = _rect[0] + self.width * w
        r = _rect[0] + self.width - self.width * w
        mid = (int((l + r) / 2), int((t + d) / 2))
        ww, hh = mid[0] - l, mid[1] - t

        return mid, ww, hh
    
    def do_find_float(self, _rect, t_start, cursor, hstep=2.5, wstep=5.9):
        mid, ww, hh = self.get_box_mid(_rect)
        
        nn, pos, wn, hn = 0, mid, int(ww / wstep), int(hh / hstep)
        while time.time() - t_start <= self.tmax and abs(pos[0] - mid[0]) <= ww and abs(pos[1] - mid[1]) <= hh:
            x_moveTo(pos)
            time.sleep(0.04)
            _, hcursor, mpos = getCursorInfo()
            # print(_t(), 'no:', self.no, 'mpos:', mpos, 'hcursor:', hcursor)
            if hcursor != cursor:
                return True, mpos

            nn += 1
            pos = _next_pos(mid, nn, wn, hn)
            time.sleep(0.03)

        return False, (0, 0)

    def do_wait_bite(self, t_start):
        t = time.time()
        while t - t_start <= self.tmax:
            time.sleep(0.1)
            rgb = getPixel(self.mpos[0], self.mpos[1])
            t = time.time()
            if rgb[0] < 100 or rgb[1] < 100 or rgb[2] < 100:
                if t - t_start < self.tmin:
                    continue
                return True

        return False

    def check_shutdown_acc(self, shutdown_acc, limit=30):
        if shutdown_acc > limit:
            self._check_image('shutdown')
            self.do_shutdown()
            return True
            
        return False
        
    def run_pve_full(self, no='0-0'):
        global rect

        print(_t(), 'run_pve_full no:', no, 'first_bait:', self.first_bait)
        
        self.acc, self.state, self.no = 0, 'init', no
        delay, self.shutdown_acc = 0.3, 0

        set_top_window()
        self._check_image('pve_full_init')

        t_bait, cursor = time.time(), 0
        while True:
            rect = find_wow_window()

            time.sleep((random.random() + delay) / 3.0 if delay > 0 else 0.3)

            found, check, t_start = False, '', time.time()
            if t_start - t_bait > self.first_bait:
                self.state = 'bait'
                t_bait = t_start
                time.sleep(0.8)
                pyautogui.press(self.key_bait)
                print(_t(), 'state:', self.state, 'press:', self.key_bait, 'acc:', self.acc)
                self.first_bait = 603
                time.sleep(2.3)

            if not self.key_auto:
                x_moveTo(self.width / 2, self.height / 2 + 40)
                _, cursor, _ = getCursorInfo()

            self.state = 'ready'
            pyautogui.press(self.key_fish)
            print(_t(), 'state:', self.state, 'press:', self.key_fish, 'acc:', self.acc)
            time.sleep(0.4)

            if self.key_auto:
                if self.check_pos or self.acc >= 3:
                    self.state = 'check'
                    if self.check_pos:
                        mpos = (rect[0]+self.check_pos[0], rect[1]+self.check_pos[1])
                    else:
                        _, _, mpos = getCursorInfo()
                        
                    rgb = getPixel(mpos[0], mpos[1])
                    cpos = (mpos[0]-rect[0], mpos[1]-rect[1])

                    if self.check_pos is None:
                        print(_t(), 'state:', self.state, 'cpos:', cpos, 'rgb:', rgb, 'acc:', self.acc)
                        if rgb[0] < 20 and rgb[2] < 20 and rgb[1] > 120:
                            self.check_pos = cpos

                    if rgb[0] > 50 or rgb[2] > 50 or rgb[1] < 120:
                        check = 'retry'

                if check == '':
                    self.state = 'auto'
                    print(_t(), 'state:', self.state, 'acc:', self.acc)
                    found = self.do_wait_bite(t_start)
                    if found:
                        self.state = 'got'
                        print(_t(), 'state:', self.state, 'press:', self.key_auto, 'acc:', self.acc)
                        time.sleep(0.1)
                        pyautogui.press(self.key_auto)
                        time.sleep(0.1)
            else:
                self.state = 'find'
                found, pos = self.do_find_float(rect, t_start, cursor)
                if found:
                    self.state = 'found'
                    print(_t(), 'state:', self.state, 'pos:', pos, 'acc:', self.acc)
                    found = self.do_wait_bite(t_start)
                    if found:
                        self.state = 'got'
                        print(_t(), 'state:', self.state, 'pos:', pos, 'acc:', self.acc)
                        time.sleep(0.05)
                        pyautogui.click()
                        time.sleep(0.05)
                        r_click(pos)

            if found:
                self.acc += 1
                self.shutdown_acc = 0
                time.sleep(0.4)
                continue

            set_top_window() if check == '' else None
            self.state = 'empty' if check == '' else check
            self.shutdown_acc += 0.1 if check == 'retry' else 1
            print(_t(), 'state:', self.state, 'acc:', self.acc, 'shutdown_acc: %.2f' % (self.shutdown_acc, ))
            self._check_image('%s-%d' % (self.state, int(self.shutdown_acc*10))) if int(self.shutdown_acc*10) % 30 == 0 else None
            if self.check_shutdown_acc(self.shutdown_acc):
                break

    def _check_image(self, tag='', pp='tmp', level='warn'):
        fname = os.path.join(os.getcwd(), pp,
                             '[%d] %s [%s].png' % (os.getpid(), _tt('%Y-%m-%d_%H_%M_%S', False), tag or 'unknown'))
        print(_t(level), 'acc:', self.acc, ', fname:', fname)
        image = pyautogui.screenshot()
        image.save(fname)


class Logger(object):
    def __init__(self, filename="default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        if self.log:
            self.log.write(message)
            self.log.flush()

    def flush(self):
        pass

    def reset(self):
        self.log.flush()
        self.log.close()
        self.log = None


def main(cfg='w_script.txt', as_test=0, _first_bait=None):
    tip = "请将wow调至 1600x1200 窗口模式，鱼饵剩余:"
    _first_bait = pyautogui.prompt(text=tip, default='0')
    _first_bait = _first_bait.strip() if _first_bait else _first_bait
    if _first_bait is None:
        return

    with open(cfg, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    line_num = 3
    assert len(lines) >= line_num, 'must has ' + str(line_num) + ' lines: keys, delay, first_bait'
    keys, delay, first_bait = lines[:line_num]

    keys = keys.split('#')[0].strip().split(' ')
    assert len(keys) >= 2, 'keys must as key_fish key_bait key_auto'
    _cpos = keys[3].strip() if len(keys) > 3 else '0-0'
    cpos = (int(_cpos.split('-')[0]), int(_cpos.split('-')[1])) if '-' in _cpos else (0, 0)
    
    delay = float(delay.split('#')[0].strip())
    first_bait = float(first_bait.split('#')[0].strip())
    first_bait = float(_first_bait) if _first_bait.isdigit() else first_bait

    _mpos = (lines[line_num]).split('#')[0].strip() if len(lines) > line_num else '0-0'
    mpos = (int(_mpos.split('-')[0]), int(_mpos.split('-')[1])) if '-' in _mpos else (0, 0)
    
    try:
        lf = os.path.join(os.getcwd(), 'logs', 'w_script%s[%d-%d] %s.log' % (
            '_test ' if as_test else '', os.getpid(), os.getppid(), _tt('%Y-%m-%d_%H_%M_%S', False)))
        sys.stdout = Logger(lf)

        if mpos and mpos[0] > 0 and mpos[1] > 0:
            rgb = getPixel(mpos[0], mpos[1])
            print(_t(), 'config _mpos:', _mpos, 'mpos:', mpos, 'rgb:', rgb)
        else:
            time.sleep(3)
            _, _, mpos = getCursorInfo()
            rgb = getPixel(mpos[0], mpos[1])
            winsound.Beep(600, 500)
            print(_t(), 'found _mpos:', _mpos, 'mpos:', mpos, 'rgb:', rgb)
                   
        pyautogui.PAUSE = delay
        agent = Agent(key_fish=keys[0], key_bait=keys[1], key_auto=keys[2] if len(keys) > 2 else '', 
            first_bait=first_bait, mpos=mpos, cpos=cpos)

 
        agent.run(_mpos) if not as_test else agent.run_test(_mpos)
    finally:
        sys.stdout.reset()


if __name__ == '__main__':
    main()
