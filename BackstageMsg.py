#! /usr/bin env python3
# -*- coding:utf-8 -*-
# 后台键盘模拟

import time
import win32api
import win32con
import win32gui
import math


class BackstageKeyBoard(object):
    def __init__(self, hwnd, _log=None, _print=False):
        self.hwnd = hwnd
        self._print = _print
        self.key_map = {
            "0": 49, "1": 50, "2": 51, "3": 52, "4": 53, "5": 54, "6": 55, "7": 56, "8": 57, "9": 58,
            'F1': 112, 'F2': 113, 'F3': 114, 'F4': 115, 'F5': 116, 'F6': 117, 'F7': 118, 'F8': 119,
            'F9': 120, 'F10': 121, 'F11': 122, 'F12': 123, 'F13': 124, 'F14': 125, 'F15': 126, 'F16': 127,
            "A": 65, "B": 66, "C": 67, "D": 68, "E": 69, "F": 70, "G": 71, "H": 72, "I": 73, "J": 74,
            "K": 75, "L": 76, "M": 77, "N": 78, "O": 79, "P": 80, "Q": 81, "R": 82, "S": 83, "T": 84,
            "U": 85, "V": 86, "W": 87, "X": 88, "Y": 89, "Z": 90,
            'BACKSPACE': 8, 'TAB': 9, 'TABLE': 9, 'CLEAR': 12, 'ENTER': 13, 'SHIFT': 16, 'CTRL': 17,
            'CONTROL': 17, 'ALT': 18, 'ALTER': 18, 'PAUSE': 19, 'BREAK': 19, 'CAPSLK': 20, 'CAPSLOCK': 20, 'ESC': 27,
            'SPACE': 32, 'SPACEBAR': 32, 'PGUP': 33, 'PAGEUP': 33, 'PGDN': 34, 'PAGEDOWN': 34, 'END': 35, 'HOME': 36,
            'LEFT': 37, 'UP': 38, 'RIGHT': 39, 'DOWN': 40, 'SELECT': 41, 'PRTSC': 42, 'printSCREEN': 42, 'SYSRQ': 42,
            'SYSTEMREQUEST': 42, 'EXECUTE': 43, 'SNAPSHOT': 44, 'INSERT': 45, 'DELETE': 46, 'HELP': 47, 'WIN': 91,
            'WINDOWS': 91, 'NMLK': 144,
            'NUMLK': 144, 'NUMLOCK': 144, 'SCRLK': 145,
            '[': 219, ']': 221, '+': 107, '-': 109}
        self._log = _log
        # self.printLog('BackstageKeyBoard init')

    def printLog(self, content):
        if self._log:
            self._log.printLog(content)
        else:
            print(content) if self._print else None

    # 后台模拟方法1——使用SendMessage（默认）  ############################################

    # 模拟一次按键的输入，间隔值默认0.1S
    def pressKey(self, key: str, interval=0.1):
        self.keyDown(key)
        time.sleep(interval)
        self.keyUp(key)

    # 模拟一次组合键的输入，间隔值默认0.1S
    def pressKeys(self, keys, interval=0.1):
        for i in range(0, len(keys), 1):
            self.keyDown(keys[i])
        time.sleep(interval)
        for i in range(0, len(keys), 1):
            self.keyUp(keys[i])

    # 模拟一个按键的按下
    def keyDown(self, key: str):
        self.printLog('keyDown: ' + str(key))
        key_code = self.key_map[key.upper()]
        win32api.SendMessage(self.hwnd, win32con.WM_KEYDOWN, key_code, 0)

    # 模拟一个按键的弹起
    def keyUp(self, key: str):
        self.printLog('keyUp: ' + str(key))
        key_code = self.key_map[key.upper()]
        win32api.SendMessage(self.hwnd, win32con.WM_KEYUP, key_code, 0)

    # 模拟输入一段文本
    def inputText(self, text: str):
        self.printLog('input text: ' + text)
        for ch in text:
            win32gui.SendMessage(self.hwnd, win32con.WM_CHAR, ord(ch), 0)
            time.sleep(0.05)

    # 后台模拟方法2——使用PostMessage  ############################################

    # 模拟一次按键的输入，间隔值默认0.1S
    def pressKey_2(self, key: str, interval=0.1):
        self.keyDown_2(key)
        time.sleep(interval)
        self.keyUp_2(key)

    # 模拟一次组合键的输入，间隔值默认0.1S
    def pressKeys_2(self, keys, interval=0.1):
        for i in range(0, len(keys), 1):
            self.keyDown_2(keys[i])
        time.sleep(interval)
        for i in range(0, len(keys), 1):
            self.keyUp_2(keys[i])

    # 模拟一个按键的按下
    def keyDown_2(self, key: str):
        self.printLog('keyDown_2: ' + str(key))
        key_code = self.key_map[key.upper()]
        win32api.PostMessage(self.hwnd, win32con.WM_KEYDOWN, key_code, 0)

    # 模拟一个按键的弹起
    def keyUp_2(self, key: str):
        self.printLog('keyUp_2: ' + str(key))
        key_code = self.key_map[key.upper()]
        win32api.PostMessage(self.hwnd, win32con.WM_KEYUP, key_code, 0)

    # 模拟输入一段文本
    def inputText_2(self, text: str):
        self.printLog('input_2 text: ' + text)
        for ch in text:
            win32gui.PostMessage(self.hwnd, win32con.WM_CHAR, ord(ch), 0)
            time.sleep(0.05)


class BackstageMouse(object):
    def __init__(self, hwnd, _log=None):
        self.hwnd = hwnd
        self.log = _log
        # self.printLog('BackstageMouse init')

    def printLog(self, content):
        if self.log:
            self.log.printLog(content)
        else:
            print(content)

    # 聚焦句柄对应的窗口
    def focusHwnd(self):
        pass
        # win32gui.SetForegroundWindow(self.hwnd)

    # 后台模拟方法1——使用SendMessage（默认）  ############################################

    # 模拟鼠标的移动
    def move(self, x, y):
        point = win32api.MAKELONG(int(x), int(y))
        win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, point)

    # 模拟鼠标的按键按下
    def clickDown(self, x, y, button="l"):
        point = win32api.MAKELONG(int(x), int(y))
        button = button.lower()
        if button == "l":
            win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, point)
        elif button == "m":
            win32api.SendMessage(self.hwnd, win32con.WM_MBUTTONDOWN, win32con.MK_MBUTTON, point)
        elif button == "r":
            win32api.SendMessage(self.hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, point)
        self.printLog('clickDown x: ' + str(x) + ', y: ' + str(y))

    # 模拟鼠标的按键抬起
    def clickUp(self, x, y, button="l"):
        point = win32api.MAKELONG(int(x), int(y))
        button = button.lower()
        if button == "l":
            win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)
        elif button == "m":
            win32api.SendMessage(self.hwnd, win32con.WM_MBUTTONUP, win32con.MK_MBUTTON, point)
        elif button == "r":
            win32api.SendMessage(self.hwnd, win32con.WM_RBUTTONUP, win32con.MK_RBUTTON, point)
        self.printLog('clickUp x: ' + str(x) + ', y: ' + str(y))

    # 模拟鼠标的点击
    def click(self, x, y, button="l", interval=0.1):
        point = win32api.MAKELONG(int(x), int(y))
        button = button.lower()
        if button == "l":
            win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, point)
            time.sleep(interval)
            win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)
        elif button == "m":
            win32api.SendMessage(self.hwnd, win32con.WM_MBUTTONDOWN, win32con.MK_MBUTTON, point)
            time.sleep(interval)
            win32api.SendMessage(self.hwnd, win32con.WM_MBUTTONUP, win32con.MK_MBUTTON, point)
        elif button == "r":
            win32api.SendMessage(self.hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, point)
            time.sleep(interval)
            win32api.SendMessage(self.hwnd, win32con.WM_RBUTTONUP, win32con.MK_RBUTTON, point)
        self.printLog('clicked x: ' + str(x) + ', y: ' + str(y))

    # 模拟鼠标的左键双击
    def doubleClick(self, x, y):
        point = win32api.MAKELONG(int(x), int(y))
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDBLCLK, win32con.MK_LBUTTON, point)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)
        self.printLog('doubleClick x: ' + str(x) + ', y: ' + str(y))

    # 模拟鼠标移动到坐标，并进行左键单击
    def moveToPosClick(self, x, y):
        point = win32api.MAKELONG(int(x), int(y))
        win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, point)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, point)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)
        self.printLog('moveToPosClick x: ' + str(x) + ', y: ' + str(y))

    # 模拟鼠标移动到坐标，并进行左键双击
    def moveToPosDoubleClick(self, x, y):
        point = win32api.MAKELONG(int(x), int(y))
        win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, point)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDBLCLK, win32con.MK_LBUTTON, point)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)
        self.printLog('moveToPosDoubleClick x: ' + str(x) + ', y: ' + str(y))

    # 模拟鼠标使用滚轮向上滚动
    # 需要聚焦到窗口
    def wheelUp(self, x, y):
        self.focusHwnd()
        point = win32api.MAKELONG(int(x), int(y))
        win32api.PostMessage(self.hwnd, win32con.WM_MOUSEWHEEL, win32con.WHEEL_DELTA * 5, point)
        self.printLog('wheelDown x: ' + str(x) + ', y: ' + str(y))

    # 模拟鼠标使用滚轮向下滚动
    # 需要聚焦到窗口
    def wheelDown(self, x, y):
        self.focusHwnd()
        point = win32api.MAKELONG(int(x), int(y))
        win32api.PostMessage(self.hwnd, win32con.WM_MOUSEWHEEL, win32con.WHEEL_DELTA * 5, point)
        self.printLog('wheelDown x: ' + str(x) + ', y: ' + str(y))

    # 模拟鼠标的左键拖动(即在第一个点按下，拖动至第二个点抬起)
    # @step 步长，模拟拖动会将一个操作分开多次来模拟，次数=拖动的长度/步长
    # @delay 拖动时间，默认0.5秒
    # @isNeedBtnUp 是否需要弹起鼠标，默认是，若不弹起可通过多次调用实现轨迹拖动
    def slide(self, x1, y1, x2, y2, isNeedBtnUp=True, step=20, delay=0.5):
        offsetX = x2 - x1
        offsetY = y2 - y1
        count = int(math.sqrt(offsetX * offsetX + offsetY * offsetY) / step)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON,
                             win32api.MAKELONG(int(x1), int(y1)))
        point2 = (0, 0)
        for i in range(count):
            point2 = win32api.MAKELONG(int(x1 + offsetX / count * (i + 1)), int(y1 + offsetY / count * (i + 1)))
            win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, point2)
            time.sleep(delay / count)
        if isNeedBtnUp:
            win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, point2)
        self.printLog('slide x1: ' + str(x1) + ', y1: ' + str(y1) + ', x2: ' + str(x2) + ', y2: ' + str(y2))

    # 后台模拟方法2——使用PostMessage  ############################################

    # 模拟鼠标的移动
    def move_2(self, x, y):
        point = win32api.MAKELONG(int(x), int(y))
        win32api.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, point)

    # 模拟鼠标的按键按下
    def clickDown_2(self, x, y, button="l"):
        point = win32api.MAKELONG(int(x), int(y))
        button = button.lower()
        if button == "l":
            win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, point)
        elif button == "m":
            win32api.PostMessage(self.hwnd, win32con.WM_MBUTTONDOWN, win32con.MK_MBUTTON, point)
        elif button == "r":
            win32api.PostMessage(self.hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, point)
        self.printLog('clickDown_2 x: ' + str(x) + ', y: ' + str(y))

    # 模拟鼠标的按键抬起
    def clickUp_2(self, x, y, button="l"):
        point = win32api.MAKELONG(int(x), int(y))
        button = button.lower()
        if button == "l":
            win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)
        elif button == "m":
            win32api.PostMessage(self.hwnd, win32con.WM_MBUTTONUP, win32con.MK_MBUTTON, point)
        elif button == "r":
            win32api.PostMessage(self.hwnd, win32con.WM_RBUTTONUP, win32con.MK_RBUTTON, point)
        self.printLog('clickUp_2 x: ' + str(x) + ', y: ' + str(y))

    # 模拟鼠标的点击
    def click_2(self, x, y, button="l", interval=0.1):
        point = win32api.MAKELONG(int(x), int(y))
        button = button.lower()
        if button == "l":
            win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, point)
            time.sleep(interval)
            win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)
        elif button == "m":
            win32api.PostMessage(self.hwnd, win32con.WM_MBUTTONDOWN, win32con.MK_MBUTTON, point)
            time.sleep(interval)
            win32api.PostMessage(self.hwnd, win32con.WM_MBUTTONUP, win32con.MK_MBUTTON, point)
        elif button == "r":
            win32api.PostMessage(self.hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, point)
            time.sleep(interval)
            win32api.PostMessage(self.hwnd, win32con.WM_RBUTTONUP, win32con.MK_RBUTTON, point)
        self.printLog('clicked_2 x: ' + str(x) + ', y: ' + str(y))

    # 模拟鼠标的左键双击
    def doubleClick_2(self, x, y):
        point = win32api.MAKELONG(int(x), int(y))
        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDBLCLK, win32con.MK_LBUTTON, point)
        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)
        self.printLog('doubleClick_2 x: ' + str(x) + ', y: ' + str(y))

    # 模拟鼠标移动到坐标，并进行左键单击
    def moveToPosClick_2(self, x, y):
        point = win32api.MAKELONG(int(x), int(y))
        win32api.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, point)
        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, point)
        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)
        self.printLog('moveToPosClick_2 x: ' + str(x) + ', y: ' + str(y))

    # 模拟鼠标移动到坐标，并进行左键双击
    def moveToPosDoubleClick_2(self, x, y):
        point = win32api.MAKELONG(int(x), int(y))
        win32api.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, point)
        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDBLCLK, win32con.MK_LBUTTON, point)
        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)
        self.printLog('moveToPosDoubleClick_2 x: ' + str(x) + ', y: ' + str(y))

    # 模拟鼠标的左键拖动(即在第一个点按下，拖动至第二个点抬起)
    def slide_2(self, x1, y1, x2, y2, step=20, delay=0.5):
        offsetX = x2 - x1
        offsetY = y2 - y1
        count = int(math.sqrt(offsetX * offsetX + offsetY * offsetY) / step)
        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON,
                             win32api.MAKELONG(int(x1), int(y1)))
        for i in range(count):
            point2 = win32api.MAKELONG(int(x1 + offsetX / count * (i + 1)), int(y1 + offsetY / count * (i + 1)))
            win32api.PostMessage(self.hwnd, win32con.WM_MOUSEMOVE, win32con.MK_LBUTTON, point2)
            time.sleep(delay / count)
        win32api.PostMessage(self.hwnd, win32con.WM_LBUTTONUP, 0, 0)
        self.printLog('slide_2 x1: ' + str(x1) + ', y1: ' + str(y1) + ', x2: ' + str(x2) + ', y2: ' + str(y2))
