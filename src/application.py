import ctypes
from ctypes import wintypes
import win32con
import win32gui
import win32api

# 定义 Windows 结构体用于解析 lParam
class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class MINMAXINFO(ctypes.Structure):
    _fields_ = [
        ("ptReserved", POINT),
        ("ptMaxSize", POINT),
        ("ptMaxPosition", POINT),
        ("ptMinTrackSize", POINT), # 最小追踪尺寸（最小宽高）
        ("ptMaxTrackSize", POINT), # 最大追踪尺寸
    ]

from src.core.window import (
    createWc, createWindow, enable_dpi_awareness, enable_acrylic_win11,
)
from src.core.webview import WebView2
from src.bridge import Bridge, WM_HTTP_RESULT


class Application:
    CLASS_NAME = "hkhj5"
    WINDOW_TITLE = "好看韩剧5"
    WIDTH = 1200
    HEIGHT = 700
    HOME_URL = "http://127.0.0.1:5173/"

    def __init__(self):
        self.hwnd = None
        self.webview = None
        self.bridge = Bridge()

    # ---------- 窗口过程 ----------
    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_GETMINMAXINFO:
            info = MINMAXINFO.from_address(lparam)
            info.ptMinTrackSize.x = self.WIDTH
            info.ptMinTrackSize.y = self.HEIGHT
            return 0
        if msg == WM_HTTP_RESULT:
            self.bridge.on_http_result(wparam)
            return 0
        if msg == win32con.WM_SIZE:
            if self.webview:
                self.webview.resize()
            return 0
        if msg == win32con.WM_DESTROY:
            if self.webview:
                self.webview.destroy()
            self.bridge.shutdown()
            win32gui.PostQuitMessage(0)
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    # ---------- 入口 ----------
    def run(self):
        enable_dpi_awareness()
        hinstance = win32api.GetModuleHandle(None)

        createWc(self.CLASS_NAME, self.wnd_proc, hinstance)
        self.hwnd = createWindow(
            self.CLASS_NAME, 
            self.WINDOW_TITLE, 
            hinstance,
            self.WIDTH, 
            self.HEIGHT,
        )
        self.bridge.set_hwnd(self.hwnd)

        enable_acrylic_win11(self.hwnd)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        win32gui.UpdateWindow(self.hwnd)

        self.webview = WebView2(
            self.hwnd,
            on_message=self.bridge.on_web_message,
        )
        self.bridge.set_webview(self.webview)

        self.webview.init()
        self.webview.navigate(self.HOME_URL)

        win32gui.PumpMessages()