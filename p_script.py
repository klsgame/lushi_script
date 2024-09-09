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


def getImgPixel(x, y):
    image = pyautogui.screenshot()
    color = image.getpixel((x, y))
    return color


def getImgState(_rect, mpos, cpos, acc):
    image = pyautogui.screenshot()
    xy = (_rect[0] + cpos[0], _rect[1] + cpos[1])
    rgb = image.getpixel(xy)
    if rgb[0] > 25 or rgb[2] > 65 or rgb[1] < 160:  # rgb(12, 186, 52)
        state = 'retry'
    else:
        state = 'battle'
        xy = (_rect[0] + mpos[0], _rect[1] + mpos[1])
        rgb = image.getpixel(xy)
        if rgb[0] > 55 and rgb[2] < 35 and rgb[1] < 40:  # rgb(62, 33, 25)
            state = 'auto'

    if (acc <= 10 and state == 'retry') or state == 'auto':
        print(_t(), 'state:', state, 'mpos:', mpos, 'cpos:', cpos, 'rgb:', rgb, 'acc:', acc)

    return state


class Agent:

    def __init__(self, mpos, cpos=None, key_macro='q', key_battle='wd', key_auto='f',
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

    def check_shutdown_acc(self, shutdown_acc, limit=30):
        if shutdown_acc > limit:
            self._check_image('shutdown')
            self.do_shutdown()
            return True

        return False

    def run_pve_full(self, no='0-0'):
        global rect

        print(_t(), 'run_pve_full no:', no)

        self.acc, self.state, self.no = 0, 'init', no
        delay, self.shutdown_acc = 0.3, 0

        set_top_window()
        self._check_image('pve_full_init')

        while True:
            self.acc += 1
            rect = find_wow_window()

            time.sleep((random.random() + delay) / 3.0 if delay > 0 else 0.3)

            self.state = getImgState(rect, self.mpos, self.check_pos, self.acc)
            if self.state in ['retry', 'init', 'ready']:
                pyautogui.press(self.key_macro)
                time.sleep(0.4)
                pyautogui.press(self.key_auto)
                time.sleep(0.4)
                pyautogui.press(self.key_macro)
                print(_t(), 'state:', self.state, 'press:', self.key_macro, 'acc:', self.acc)
                time.sleep(1.8)

            self.state = getImgState(rect, self.mpos, self.check_pos, self.acc)
            if self.state == 'retry':
                set_top_window()
                self.shutdown_acc += 0.1
                print(_t(), 'state:', self.state, 'acc:', self.acc, 'shutdown_acc: %.2f' % (self.shutdown_acc,))
                self._check_image('%s-%d' % (self.state, int(self.shutdown_acc * 10))) if int(
                    self.shutdown_acc * 10) % 30 == 0 else None
                if self.check_shutdown_acc(self.shutdown_acc):
                    break
                continue

            print(_t(), 'state:', self.state, 'acc:', self.acc)
            while self.state in ['battle', 'auto']:
                nn = 0
                retry_n = 0
                while nn < 100:
                    nn += 1
                    time.sleep(0.2)
                    self.state = getImgState(rect, self.mpos, self.check_pos, self.acc)
                    if self.state == 'retry':
                        retry_n += 1
                    if retry_n >= 5 or self.state == 'auto':
                        break

                if self.state == 'auto':
                    pyautogui.press(self.key_battle) if len(self.key_battle) == 1 else pyautogui.scroll(-3)
                    print(_t(), 'state:', self.state, 'press:', self.key_battle, 'acc:', self.acc)
                    time.sleep(1.8)

            self.state = 'ready'

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

    line_num = 3
    assert len(lines) >= line_num, 'must has ' + str(line_num) + ' lines: keys, delay, first_battle'
    keys, delay, first_battle = lines[:line_num]

    keys = keys.split('#')[0].strip().split(' ')
    assert len(keys) >= 2, 'keys must as key_macro key_battle key_auto'
    _cpos = keys[3].strip() if len(keys) > 3 else '0-0'
    cpos = (int(_cpos.split('-')[0]), int(_cpos.split('-')[1])) if '-' in _cpos else (0, 0)

    delay = float(delay.split('#')[0].strip())
    first_battle = float(first_battle.split('#')[0].strip())
    first_battle = float(_first_battle) if _first_battle.isdigit() else first_battle

    _mpos = (lines[line_num]).split('#')[0].strip() if len(lines) > line_num else '0-0'
    mpos = (int(_mpos.split('-')[0]), int(_mpos.split('-')[1])) if '-' in _mpos else (0, 0)

    try:
        lf = os.path.join(os.getcwd(), 'logs', 'p_script%s[%d-%d] %s.log' % (
            '_test ' if as_test else '', os.getpid(), os.getpid(), _tt('%Y-%m-%d_%H_%M_%S', False)))
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
