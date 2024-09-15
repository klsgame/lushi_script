# -*- coding: utf-8 -*-

from __future__ import print_function

import datetime
import os
import random
import sys
import time
from urllib import request

import winsound

import pyautogui
import win32gui

from winguiauto import findTopWindows, getCursorInfo, getPixel, WinGuiAutoError

from BackstageMsg import BackstageKeyBoard

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


def findLeftTopTopWindow(wantedText=None, wantedClass=None, selectionFunction=None):
    topWindows = findTopWindows(wantedText, wantedClass, selectionFunction)
    if topWindows:
        rects = [(h, win32gui.GetWindowPlacement(h)[-1]) for h in topWindows]
        leftTop, needHwnd = 1440+900, None
        for (hwnd, rect_) in rects:
            val = abs(rect_[0]) + abs(rect_[1])
            if val < leftTop:
                leftTop, needHwnd = val, hwnd
        return needHwnd if needHwnd else topWindows[-1]
    else:
        raise WinGuiAutoError("No top level window found for wantedText=" +
                              repr(wantedText) +
                              ", wantedClass=" +
                              repr(wantedClass) +
                              ", selectionFunction=" +
                              repr(selectionFunction))


def find_wow_window(acc=0):
    global G_HWND, G_RECT

    if acc % == 0 and acc > 20:
        G_HWND, G_RECT = None, None
        
    hwnd = G_HWND if G_HWND else findLeftTopTopWindow("魔兽世界")
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


rect = [0, 0, 1440, 900]
_tp = lambda pos=None, y=None: pos if isinstance(pos, (tuple, list)) else (pos, y)

r_moveTo = lambda *args, **kwgs: pyautogui.moveTo(*args, **kwgs)
r_click = lambda *args, **kwgs: pyautogui.click(*args, **kwgs)
x_moveTo = lambda pos=None, y=None, **kwgs: pyautogui.moveTo(rect[0] + _tp(pos, y)[0],
                                                             rect[1] + _tp(pos, y)[1], **kwgs)
x_click = lambda pos=None, y=None, **kwgs: pyautogui.click(rect[0] + _tp(pos, y)[0],
                                                           rect[1] + _tp(pos, y)[1], **kwgs)

USE_BACKS = True

x_press = lambda k: b_press(k) if USE_BACKS else \
    (pyautogui.scroll(-3 if k == 'wd' else 3) if k in ('wd', 'wu') else pyautogui.press(k))


def b_press(k):
    global rect, G_HWND
    x, y = int(rect[0] + rect[2] * 0.7), int(rect[1] + rect[3] * 0.7)
    if k in ('wd', 'wu'):
        pyautogui.scroll(-3 if k == 'wd' else 3, x, y)
    else:
        obj = BackstageKeyBoard(G_HWND)
        obj.pressKey(k)


def getImgPixel(x, y):
    image = pyautogui.screenshot()
    color = image.getpixel((x, y))
    return color


def sameColor(rgb, origin, limit=10):
    a = (origin[0] - limit, origin[1] - limit, origin[2] - limit)
    b = (origin[0] + limit, origin[1] + limit, origin[2] + limit)
    return (a[0] < rgb[0] < b[0]) and (a[1] < rgb[1] < b[1]) and (a[2] < rgb[2] < b[2])


def getImgState(_rect, mpos, cpos, acc, crgb_=(5, 112, 30), crgb2_=(0, 16, 0), mrgb_=(64, 8, 11)):
    image = pyautogui.screenshot()

    xy = (_rect[0] + cpos[0], _rect[1] + cpos[1])
    crgb = image.getpixel(xy)

    xy = (_rect[0] + mpos[0], _rect[1] + mpos[1])
    mrgb = image.getpixel(xy)

    if sameColor(crgb, crgb_) or sameColor(crgb, crgb2_):
        state = 'battle'
        if sameColor(mrgb, mrgb_):
            state = 'auto'
    else:
        state = 'retry'

    if (acc <= 10 and state == 'retry') or (acc <= 5 and state == 'auto'):
        print(_t(), state, f'{cpos[0]}-{cpos[1]}:', crgb, f'{mpos[0]}-{mpos[1]}:', mrgb, acc)

    return state


class Agent:

    def __init__(self, mpos, cpos=None, key_macro='wu', key_battle='wd', key_auto='wd',
                 tmax=16.9, tmin=3.5, wh=(1440, 900)):
        self.mpos = mpos
        self.key_macro, self.key_battle, self.key_auto = key_macro, key_battle, key_auto
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
            rgb = getImgPixel(mpos[0], mpos[1])
            cpos = (mpos[0] - rect[0], mpos[1] - rect[1])
            print(_t(), 'no:', self.no, 'cpos:', cpos, 'rgb:', rgb, 'hcursor:', hcursor)

            nn -= 1
            if nn <= 0:
                break

    def check_shutdown_acc(self, shutdown_acc, limit=20):
        if shutdown_acc > limit:
            self._check_image('shutdown')
            self.do_shutdown()
            return True

        return False

    def run_pve_full(self, no='0-0'):
        global rect

        _acc = lambda: '%d-%.2f' % (self.acc, self.shutdown_acc)
        print(_t(), 'run_pve_full no:', no)

        self.acc, self.state, self.no = 0, 'init', no
        delay, self.shutdown_acc = 0, 0.0

        USE_BACKS or set_top_window()
        self._check_image('pve_full_init')

        while True:
            self.acc += 1
            rect = find_wow_window(self.acc)

            time.sleep((random.random() + delay) / 3.0 if delay > 0 else 0.3)

            self.state = getImgState(rect, self.mpos, self.check_pos, self.acc)
            if self.state in ['retry', 'init']:
                x_press(self.key_macro)
                time.sleep(0.4)
                x_press(self.key_auto)
                time.sleep(0.4)
                x_press(self.key_macro)
                print(_t(), self.state, 'press:', self.key_macro, _acc())
                time.sleep(1.8)

            self.state = getImgState(rect, self.mpos, self.check_pos, self.acc)
            if self.state == 'retry':
                USE_BACKS or set_top_window()
                self.shutdown_acc += 0.1
                print(_t('error'), self.state, _acc())
                self._check_image('%s-%d' % (self.state, int(self.shutdown_acc * 10))) if int(
                    self.shutdown_acc * 10) % 30 == 0 else None
                if self.check_shutdown_acc(self.shutdown_acc):
                    break
                continue

            print(_t(), self.state, 'acc:', _acc())
            while self.state in ['battle', 'auto']:
                nn = 0
                retry_n = 0
                while nn < 100:
                    nn += 1
                    time.sleep(0.2)
                    self.state = getImgState(rect, self.mpos, self.check_pos, self.acc)
                    if self.state == 'retry':
                        retry_n += 1
                    if retry_n >= 3 or self.state == 'auto':
                        break

                if self.state == 'auto':
                    self.shutdown_acc = 0
                    x_press(self.key_battle)
                    time.sleep(1.8)

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


def main(cfg='p_script.txt', as_test=0, _first_battle=None):
    tip = "请将wow调至 1440x900 窗口模式，剩余:"
    _first_battle = '0' if not _first_battle else pyautogui.prompt(text=tip, default='0')
    _first_battle = _first_battle.strip() if _first_battle else _first_battle
    if _first_battle is None:
        return

    with open(cfg, 'r', encoding="utf-8") as f:
        lines = f.readlines()

    line_num = 2
    assert len(lines) >= line_num, 'must has ' + str(line_num) + ' lines: keys, delay'
    keys, delay = lines[:line_num]

    keys = keys.split('#')[0].strip().split(' ')
    assert len(keys) >= 2, 'keys must as key_macro key_battle key_auto'
    _cpos = keys[3].strip() if len(keys) > 3 else '0-0'
    cpos = (int(_cpos.split('-')[0]), int(_cpos.split('-')[1])) if '-' in _cpos else (0, 0)

    delay = float(delay.split('#')[0].strip())

    _mpos = (lines[line_num]).split('#')[0].strip() if len(lines) > line_num else '0-0'
    mpos = (int(_mpos.split('-')[0]), int(_mpos.split('-')[1])) if '-' in _mpos else (0, 0)

    try:
        lf = os.path.join(os.getcwd(), 'logs', 'p_script%s[%d-%d] %s.log' % (
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
        agent = Agent(key_macro=keys[0], key_battle=keys[1], key_auto=keys[2], mpos=mpos, cpos=cpos)

        agent.run(_mpos) if not as_test else agent.run_test(_mpos)
    finally:
        sys.stdout.reset() if hasattr(sys.stdout, 'reset') else None


if __name__ == '__main__':
    main()
