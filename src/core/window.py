import ctypes
from ctypes import wintypes
import win32api
import win32con
import win32gui
import os
import sys

def get_resource_path(relative: str) -> str:
    """
    返回资源的绝对路径。
    - 开发环境：相对于项目根目录
    - 打包后：相对于 exe 同级（onedir）或 _MEIPASS（单文件）
    """
    if getattr(sys, "frozen", False):
        # onedir：exe 所在目录
        base = os.path.dirname(sys.executable)
        # 单文件：_MEIPASS
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass and not os.path.exists(os.path.join(base, relative)):
            base = meipass
    else:
        # 开发环境：src/core/xxx.py → 上溯到项目根
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, relative)

# PROCESS_DPI_AWARENESS 枚举
PROCESS_DPI_UNAWARE = 0
PROCESS_SYSTEM_DPI_AWARE = 1
PROCESS_PER_MONITOR_DPI_AWARE = 2

def enable_dpi_awareness():
    """
    启用 Per-Monitor DPI 感知。
    必须在创建任何窗口之前调用，且整个进程只能调用一次。
    """
    try:
        # Windows 8.1+：Per-Monitor DPI Aware（推荐）
        ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)
        return "per-monitor"
    except (AttributeError, OSError):
        pass

    try:
        # Windows Vista+：System DPI Aware（降级方案）
        ctypes.windll.user32.SetProcessDPIAware()
        return "system"
    except Exception:
        return None


_MDT_EFFECTIVE_DPI = 0

def _get_monitor_dpi(hmonitor):
    """获取指定 HMONITOR 的有效 DPI。失败返回 -1。"""
    try:
        shcore = ctypes.windll.shcore
        shcore.GetDpiForMonitor.argtypes = [
            wintypes.HMONITOR,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_uint),
            ctypes.POINTER(ctypes.c_uint),
        ]
        shcore.GetDpiForMonitor.restype = ctypes.c_long

        dpiX = ctypes.c_uint()
        dpiY = ctypes.c_uint()

        hr = shcore.GetDpiForMonitor(
            wintypes.HMONITOR(int(hmonitor)),
            _MDT_EFFECTIVE_DPI,
            ctypes.byref(dpiX),
            ctypes.byref(dpiY),
        )
        if hr == 0:
            return dpiX.value
    except (AttributeError, OSError, TypeError):
        pass
    return -1


def _get_system_dpi():
    """系统 DPI，失败回退到 96。"""
    try:
        user32 = ctypes.windll.user32
        user32.GetDpiForSystem.restype = ctypes.c_uint
        return user32.GetDpiForSystem()
    except (AttributeError, OSError):
        pass
    try:
        gdi32 = ctypes.windll.gdi32
        user32 = ctypes.windll.user32
        hdc = user32.GetDC(0)
        try:
            return gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
        finally:
            user32.ReleaseDC(0, hdc)
    except Exception:
        return 96


def createWindow(CLASS_NAME: str, WINDOW_TITLE: str, hinstance,
                 width=900, height=600):
    hmonitor = win32api.MonitorFromPoint(
        (0, 0),
        win32con.MONITOR_DEFAULTTONEAREST,
    )
    monitor = win32api.GetMonitorInfo(hmonitor)

    dpi = _get_monitor_dpi(hmonitor)
    if dpi <= 0:
        dpi = _get_system_dpi()
    scale = dpi / 96.0

    phys_w = int(round(width * scale))
    phys_h = int(round(height * scale))

    left, top, right, bottom = monitor["Work"]
    x = left + (right - left - phys_w) // 2
    y = top + (bottom - top - phys_h) // 2

    return win32gui.CreateWindowEx(
        0,
        CLASS_NAME,
        WINDOW_TITLE,
        win32con.WS_OVERLAPPEDWINDOW,
        x, y, phys_w, phys_h,
        0, 0,
        hinstance,
        None,
    )

def createWc(CLASS_NAME: str, wnd_proc, hinstance):
    ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)

    wc = win32gui.WNDCLASS()
    wc.hInstance = hinstance
    wc.lpszClassName = CLASS_NAME
    wc.lpfnWndProc = wnd_proc
    wc.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
    wc.hbrBackground = win32con.COLOR_WINDOW + 1

    return win32gui.RegisterClass(wc)