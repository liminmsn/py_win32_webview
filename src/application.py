from pathlib import Path
import sys
import ctypes
from ctypes import wintypes
import http.server
import socketserver
import threading
from functools import partial

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
        ("ptMinTrackSize", POINT),   # 最小追踪尺寸（最小宽高）
        ("ptMaxTrackSize", POINT),   # 最大追踪尺寸
    ]

from src.core.window import (
    createWc, createWindow, enable_dpi_awareness, enable_acrylic_win11, get_window_prop
)
from src.core.webview import WebView2
from src.bridge import Bridge, WM_HTTP_RESULT


# ---------- 资源路径 ----------
def get_www_dir() -> Path:
    """返回 resources/www 目录（开发环境 & PyInstaller 打包都适用）"""
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent
    return base / "resources" / "www"


# ---------- 本地静态 HTTP 服务 ----------
class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    """静默的静态文件处理器：不打印每次请求，且给 SPA 兜底到 index.html"""
    def log_message(self, format, *args):
        pass  # 关闭访问日志

    def send_head(self):
        # 若路径不存在且不是以文件扩展名结尾，则回退到 index.html（支持前端路由）
        path = self.translate_path(self.path)
        if not Path(path).exists() and "." not in Path(self.path).name:
            self.path = "/index.html"
        return super().send_head()


def start_static_server(directory: str, port: int = 0):
    """后台线程启动静态文件服务，返回 (httpd, 实际端口)。port=0 表示自动分配"""
    handler = partial(_QuietHandler, directory=directory)
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), handler)
    httpd.daemon_threads = True
    httpd.allow_reuse_address = True
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    return httpd, httpd.server_address[1]


DEV = False


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
        self._httpd = None          # 本地静态服务
        self._server_port = None

    # ---------- 窗口过程 ----------
    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_GETMINMAXINFO:
            info = MINMAXINFO.from_address(lparam)
            min_width = get_window_prop(hwnd, "MinWidth", self.WIDTH)
            min_height = get_window_prop(hwnd, "MinHeight", self.HEIGHT)
            info.ptMinTrackSize.x = min_width
            info.ptMinTrackSize.y = min_height
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
            if self._httpd:
                try:
                    self._httpd.shutdown()
                    self._httpd.server_close()
                except Exception:
                    pass
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

        if DEV:
            print("[navigate] DEV ->", self.HOME_URL)
            self.webview.navigate(self.HOME_URL)
        else:
            www = get_www_dir()
            index = www / "index.html"
            print("[www]", www, "index exists =", index.exists())
            if not index.exists():
                raise FileNotFoundError(f"index.html 未找到: {index}")

            self._httpd, self._server_port = start_static_server(str(www), port=0)
            url = f"http://127.0.0.1:{self._server_port}/index.html"
            print("[navigate] LOCAL ->", url)
            self.webview.navigate(url)

        win32gui.PumpMessages()