import ctypes
from ctypes import wintypes
import win32api
import win32con
import win32gui
import os
import sys

user32 = ctypes.windll.user32

# SetPropW(HWND hWnd, LPCWSTR lpString, HANDLE hData)
user32.SetPropW.argtypes = [wintypes.HWND, wintypes.LPCWSTR, wintypes.HANDLE]
user32.SetPropW.restype = wintypes.BOOL
# GetPropW(HWND hWnd, LPCWSTR lpString)
user32.GetPropW.argtypes = [wintypes.HWND, wintypes.LPCWSTR]
user32.GetPropW.restype = wintypes.HANDLE
def set_window_prop(hwnd: int, prop_name: str, value: int) -> bool:
    """对应 C++ 的 SetPropW(hwnd, L"...", (HANDLE)value)"""
    # 将 int 强制转换为 HANDLE (void*) 内存指针对齐
    handle_val = ctypes.c_void_p(value)
    return bool(user32.SetPropW(hwnd, prop_name, handle_val))
def get_window_prop(hwnd: int, prop_name: str, default: int = 0) -> int:
    """对应 C++ 的 reinterpret_cast<LONG_PTR>(GetPropW(hwnd, L"..."))"""
    handle_res = user32.GetPropW(hwnd, prop_name)
    if handle_res is None:
        return default
    # 在 64 位系统上，HANDLE 返回为 int 类型的地址值，可以直接按 int 获取
    return handle_res
def remove_window_prop(hwnd: int, prop_name: str):
    """清理属性数据（窗口销毁前可选调用）"""
    return user32.RemovePropW(hwnd, prop_name)

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
    _hIconSmall = user32.LoadImageW(None, ico_path, IMAGE_ICON, sm_cx, sm_cy, LR_LOADFROMFILE    )
    _hIconBig = user32.LoadImageW(None, ico_path, IMAGE_ICON, lg_cx, lg_cy, LR_LOADFROMFILE    )
    _icon_handles.extend([_hIconSmall, _hIconBig])

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

# DWM API 相关常量
DWMWA_SYSTEMBACKDROP_TYPE = 38
DWMSBT_TRANSIENTWINDOW = 3   # 桌面亚克力（最亮的亚克力变体）
DWMSBT_MAINWINDOW = 2        # Mica 云母效果
DWMSBT_TABBEDWINDOW = 4      # 标签页亚克力

def enable_acrylic_win11(hwnd):
    """
    在 Windows 11 上启用亚克力效果。
    要求窗口本身支持 DWM 合成，且不能是全屏/无边框的弹出窗口。
    """
    try:
        dwmapi = ctypes.windll.dwmapi
        # 设置窗口背景类型为亚克力
        value = ctypes.c_int(DWMSBT_TRANSIENTWINDOW)
        hr = dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            ctypes.c_uint(DWMWA_SYSTEMBACKDROP_TYPE),
            ctypes.byref(value),
            ctypes.sizeof(value),
        )
        if hr == 0:
            return True
        else:
            print(f"[DWM] SetWindowAttribute failed: 0x{hr & 0xFFFFFFFF:08X}")
            return False
    except Exception as e:
        print(f"[DWM] acrylic error: {e}")
        return False

WS_EX_NOREDIRECTIONBITMAP = 0x00200000
def createWindow(CLASS_NAME: str, WINDOW_TITLE: str, hinstance, width=900, height=600):
    hmonitor = win32api.MonitorFromPoint((0, 0),win32con.MONITOR_DEFAULTTONEAREST)
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

    hwnd = win32gui.CreateWindowEx(
        WS_EX_NOREDIRECTIONBITMAP,
        CLASS_NAME,
        WINDOW_TITLE,
        win32con.WS_OVERLAPPEDWINDOW,
        x, 
        y, 
        phys_w, 
        phys_h,
        0, 0,
        hinstance,
        None,
    )
    

    ico_path = get_resource_path(os.path.join("resources", "app.ico"))
    if os.path.isfile(ico_path):
        _load_window_icons(ico_path)
        user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, _hIconSmall)
        user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, _hIconBig)
    else:
        print(f"[App] 图标文件不存在：{ico_path}")
    set_window_prop(hwnd, "MinWidth", phys_w)
    set_window_prop(hwnd, "MinHeight", phys_h)
    return hwnd

def createWc(CLASS_NAME: str, wnd_proc, hinstance):
    ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)

    wc = win32gui.WNDCLASS()
    wc.hInstance = hinstance
    wc.lpszClassName = CLASS_NAME
    wc.lpfnWndProc = wnd_proc
    wc.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
    # wc.hbrBackground = win32con.COLOR_WINDOW + 1
    wc.hbrBackground = 0

    return win32gui.RegisterClass(wc)