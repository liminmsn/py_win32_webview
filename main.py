import win32api
import win32con
import win32gui
import os

import ctypes
from ctypes import wintypes
user32 = ctypes.windll.user32
user32.LoadImageW.argtypes = [
    wintypes.HINSTANCE,
    wintypes.LPCWSTR,
    wintypes.UINT,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.UINT,
]
user32.LoadImageW.restype = wintypes.HANDLE
user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.SendMessageW.restype = wintypes.LPARAM

IMAGE_ICON = 1
LR_LOADFROMFILE = 0x00000010
LR_DEFAULTSIZE = 0x00000040
LR_SHARED     = 0x00008000

WM_SETICON = 0x0080
ICON_SMALL = 0
ICON_BIG   = 1

_hIconSmall = None
_hIconBig = None
_icon_handles = []   # 防止 GC

def _load_window_icons(ico_path):
    """加载 ico 里的两种尺寸图标（小图标给标题栏，大图标给 Alt+Tab/任务栏）。"""
    global _hIconSmall, _hIconBig
    # 小图标：按系统小图标尺寸（通常 16×16）
    sm_cx = user32.GetSystemMetrics(49)  # SM_CXSMICON
    sm_cy = user32.GetSystemMetrics(50)  # SM_CYSMICON
    # 大图标：按系统大图标尺寸（通常 32×32）
    lg_cx = user32.GetSystemMetrics(11)  # SM_CXICON
    lg_cy = user32.GetSystemMetrics(12)  # SM_CYICON
    _hIconSmall = user32.LoadImageW(        None, ico_path, IMAGE_ICON, sm_cx, sm_cy, LR_LOADFROMFILE    )
    _hIconBig = user32.LoadImageW(        None, ico_path, IMAGE_ICON, lg_cx, lg_cy, LR_LOADFROMFILE    )
    _icon_handles.extend([_hIconSmall, _hIconBig])

from src.core.window import createWc, createWindow,enable_dpi_awareness,get_resource_path
from src.core.webview import WebView2
webview = None

CLASS_NAME = "PythonWin32Window"
WINDOW_TITLE = "PythonWebView2"
width = 900
height = 600

def wnd_proc(hwnd, msg, wparam, lparam):
    global webview

    if msg == win32con.WM_SIZE:
        if webview:
            webview.resize()
        return 0

    if msg == win32con.WM_DESTROY:
        if webview:
            webview.destroy()
        win32gui.PostQuitMessage(0)
        return 0

    return win32gui.DefWindowProc(hwnd,msg,wparam,lparam)

def main():
    global webview
    enable_dpi_awareness()

    hinstance = win32api.GetModuleHandle(None)
    createWc(
        CLASS_NAME,
        wnd_proc,
        hinstance,
    )

    hwnd = createWindow(
        CLASS_NAME,
        WINDOW_TITLE,
        hinstance,
        width,
        height,
    )

    ico_path = get_resource_path(os.path.join("resources", "app.ico"))
    if os.path.isfile(ico_path):
        _load_window_icons(ico_path)
        user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, _hIconSmall)
        user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG,   _hIconBig)
    else:
        print(f"[App] 图标文件不存在：{ico_path}")
    win32gui.ShowWindow(hwnd,win32con.SW_SHOW)
    win32gui.UpdateWindow(hwnd)
    webview = WebView2(hwnd)
    webview.init()
    webview.navigate("http://127.0.0.1:5173/")

    win32gui.PumpMessages()
if __name__ == "__main__":
    main()