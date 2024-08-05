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

    def __init__(self, while_delay, hh_delay, mpos, key1='1', key2='2',
                 tmax=17.5):
        self.hh_delay, self.while_delay = hh_delay, while_delay
        self.mpos = mpos
        self.key1, self.key2 = key1, key2
        self.tmax = tmax

        self.acc, self.state, self.no = 0, 'unknown', '0-0'
        self.shutdown_acc = 0

        self.height = 1200
        self.width = 1600

    def do_shutdown(self):
        print(_t(), 'acc:', self.acc, ', do_shutdown:', self.shutdown_acc)
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

    def do_find_float(self, _rect, t_start, cursor, h=0.32, w=0.30, hstep=3.5, wstep=5.5):
        t = _rect[1] + self.height * 0.5 * h
        d = _rect[1] + self.height * 0.5 - self.height * 0.5 * h
        l = _rect[0] + self.width * w
        r = _rect[0] + self.width - self.width * w
        mid = (int((l + r) / 2), int((t + d) / 2))
        ww, hh = mid[0] - l, mid[1] - t

        nn, pos, wn, hn = 0, mid, int(ww / wstep), int(hh / hstep)
        while time.time() - t_start <= self.tmax and abs(pos[0] - mid[0]) <= ww and abs(pos[1] - mid[1]) <= hh:
            x_moveTo(pos)
            time.sleep(0.06)
            _, hcursor, mpos = getCursorInfo()
            # print(_t(), 'no:', self.no, 'mpos:', mpos, 'hcursor:', hcursor)
            if hcursor != cursor:
                return True, mpos

            nn += 1
            pos = _next_pos(mid, nn, wn, hn)
            time.sleep(0.03)

        return False, (0, 0)

    def do_wait_bite(self, t_start):
        while time.time() - t_start <= self.tmax:
            time.sleep(0.1)
            rgb = getPixel(self.mpos[0], self.mpos[1])
            if rgb[0] < 100 or rgb[1] < 100 or rgb[2] < 100:
                return True

        return False

    def run_pve_full(self, no='0-0'):
        global rect

        print(_t(), 'run_pve_full no:', no)
        self.while_delay = self.while_delay / 1.0

        self.acc, self.state, self.no = 0, 'init', no
        delay, is_first = 0.2, True
        self.shutdown_acc = 0

        set_top_window()
        self._check_image('pve_full_init')

        t_bait = time.time()
        while True:
            self.acc += 1
            rect = find_wow_window()
            time.sleep((random.random() + delay) / 3.0 if delay > 0 else 0.3)

            t_start = time.time()
            if t_start - t_bait > 603:
                self.state = 'bait'
                t_bait = t_start
                pyautogui.press(self.key2)
                print(_t(), 'state:', self.state, 'acc:', self.acc)
                time.sleep(2.3)

            x_moveTo(self.width / 2, self.height / 2 + 40)
            _, cursor, _ = getCursorInfo()

            self.state = 'ready'
            pyautogui.press(self.key1)
            print(_t(), 'state:', self.state, 'acc:', self.acc)
            time.sleep(0.1)

            self.state = 'find'
            found, pos = self.do_find_float(rect, t_start, cursor)
            if found:
                self.state = 'wait'
                print(_t(), 'state:', self.state, 'pos:', pos, 'acc:', self.acc)
                time.sleep(1.3)
                found = self.do_wait_bite(t_start)
                if found:
                    time.sleep(0.1)
                    pyautogui.click()
                    self.shutdown_acc = 0
                    time.sleep(0.3)

            if not found:
                set_top_window()
                self.state = 'error'
                print(_t(), 'state:', self.state, 'acc:', self.acc, 'shutdown_acc:', self.shutdown_acc)

                self.shutdown_acc += 1
                # self._check_image('empty-%d' % (self.shutdown_acc,))
                if self.shutdown_acc > 10:
                    self.do_shutdown()
                    self._check_image('shutdown')
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


def main(cfg='w_pve.txt', as_test=0):
    tip = "请启动wow，将wow调至窗口模式，分辨率设为1600x1200，画质设为高 参考 w_pve.txt 修改配置文件"
    if not pyautogui.confirm(text=tip) == "OK":
        return

    with open(cfg, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    line_num = 3
    assert len(lines) >= line_num, 'must has ' + str(line_num) + ' lines: while_delay, delay, hh_delay'
    while_delay, delay, hh_delay = lines[:line_num]

    while_delay = float(while_delay.split('#')[0].strip())
    delay = float(delay.split('#')[0].strip())
    hh_delay = float(hh_delay.split('#')[0].strip())

    _no = (lines[line_num]).split('#')[0].strip() if len(lines) > line_num else '0-0'

    try:
        lf = os.path.join(os.getcwd(), 'logs', 'w_pve%s[%d] %s.log' % (
            '_test ' if as_test else '', os.getpid(), _tt('%Y-%m-%d_%H_%M_%S', False)))
        sys.stdout = Logger(lf)

        time.sleep(3)
        flags, hcursor, mpos = getCursorInfo()
        rgb = getPixel(mpos[0], mpos[1])
        winsound.Beep(600, 500)

        pyautogui.PAUSE = delay
        agent = Agent(while_delay=while_delay, hh_delay=hh_delay, mpos=mpos)

        print(_t(), 'no:', _no, 'mpos:', mpos, 'rgb:', rgb, 'hcursor:', hcursor)
        agent.run(_no) if not as_test else agent.run_test(_no)
    finally:
        sys.stdout.reset()


if __name__ == '__main__':
    main()
