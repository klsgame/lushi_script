#-*- coding: utf-8 -*-

import sys, os, datetime, time, random

import pyautogui

from urllib import request

from winguiauto import findTopWindow
import win32gui

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

def set_top_window(title='魔兽世界'):
    top_windows = []
    
    def windowEnumerationHandler(hwnd, top_windows):
        top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
    
    win32gui.EnumWindows(windowEnumerationHandler, top_windows)
    for i in top_windows:
        if title in i[1].lower():
            win32gui.ShowWindow(i[0],5)
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


class Agent:

    def __init__(self, while_delay, hh_delay):
        self.hh_delay, self.while_delay = hh_delay, while_delay
        
        self.acc, self.state, self.no = 0, 'unknown', '0-0'
        self.shutdown_acc = 0
        
    def do_shutdown(self):
        print(_t(), 'acc:', self.acc, ', do_shutdown:', self.shutdown_acc)
        http_get('https://sctapi.ftqq.com/SCT193913TUNx0lH9vKbmWEsHHQuj7E9DX.send?title=shutdown_' + _tt('%Y-%m-%d_%H_%M_%S', False))
        autoshutdown = os.path.join(os.getcwd(), 'autoshutdown.bat')
        p = os.system("cmd.exe /c " + autoshutdown)
        time.sleep(1)

    def run(self, no=None):
        # http_get('https://sctapi.ftqq.com/SCT193913TUNx0lH9vKbmWEsHHQuj7E9DX.send?title=run_pve_break_' + _tt('%Y-%m-%d_%H_%M_%S', False))
        # self._check_image()
        self.run_pve_full(no, reward_count=3, max_member_ready=99, max_buf_ready=99, ext_reward=True)

    def run_test(self, no='1-1', nn=50):
        global rect

        print(_t(), 'run_test nn:', nn)

        self.acc, self.state, self.no = 0, 'init', no
        delay, is_first = 2.5, True

        self._check_image('run_test_init')
        
        while True:
            time.sleep((random.random() + delay) if delay > 0 else 0.3)
            states, rect = self.check_state()
            print(_t(), self.state + ':', states, delay)
            nn -= 1
            if nn <= 0:
                break

    def run_pve_full(self, no='1-1'):
        global rect

        print(_t(), 'run_pve_full no:', no)
        self.while_delay = self.while_delay / 1.0
        
        self.acc, self.state, self.no = 0, 'init', no
        delay, is_first = 0.2, True
        self.empty_acc = 0
        self.shutdown_acc = 0
        
        self._check_image('pve_full_init')
        
        while True:
            time.sleep((random.random() + delay) if delay > 0 else 0.3)
            
            self.state = 'before'
            print(_t(), 'state:', self.state, 'acc:', self.acc)
            pyautogui.press('1')
            time.sleep(0.8)
            
            self.state = 'after'
            found, pos = self.do_find_float()
            if not found:
                self.shutdown_acc += 1
                self._check_image('empty-%d' % (self.shutdown_acc, ))
                if self.shutdown_acc > 10:
                    self.do_shutdown()
                    self._check_image('shutdown')
                    break
                continue

            self.state = 'found'
            print(_t(), 'state:', self.state, 'pos:', self.pos, 'acc:', self.acc)


            time.sleep(self.while_delay)

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
    tip = "请启动wow，将wow调至窗口模式，分辨率设为1600x900，画质设为高 参考 w_pve.txt 修改配置文件"
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

    pyautogui.PAUSE = delay
    agent = Agent(while_delay=while_delay, hh_delay=hh_delay)

    try:
        lf = os.path.join(os.getcwd(), 'logs', 'w_pve%s[%d] %s.log' % ('_test ' if as_test else '', os.getpid(), _tt('%Y-%m-%d_%H_%M_%S', False)))
        sys.stdout = Logger(lf)

        print(_t(), 'no:', _no)
        agent.run(_no) if not as_test else agent.run_test(_no)
    finally:
        sys.stdout.reset()


if __name__ == '__main__':
    main()
