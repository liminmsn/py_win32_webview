import os
import sys
import ctypes

from ctypes import wintypes

import comtypes
from comtypes import GUID, HRESULT, IUnknown, COMMETHOD, POINTER, COMObject


# ============================================================
# Win32
# ============================================================

user32 = ctypes.windll.user32

user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.GetClientRect.restype = wintypes.BOOL


# ============================================================
# WebView2 COM Interfaces
# ============================================================

class ICoreWebView2ControllerCompletedHandler(IUnknown):
    _iid_ = GUID("{6C4819F3-C9B7-4260-8127-C9F5BDE7F68C}")
    _methods_ = [
        COMMETHOD(
            [], HRESULT, "Invoke",
            (["in"], HRESULT, "errorCode"),
            (["in"], POINTER(IUnknown), "createdController"),
        ),
    ]


class ICoreWebView2EnvironmentCompletedHandler(IUnknown):
    _iid_ = GUID("{4E8A3389-C9D8-4BD2-B6B5-124FEE6CC14D}")
    _methods_ = [
        COMMETHOD(
            [], HRESULT, "Invoke",
            (["in"], HRESULT, "errorCode"),
            (["in"], POINTER(IUnknown), "createdEnvironment"),
        ),
    ]


class ICoreWebView2Environment(IUnknown):
    _iid_ = GUID("{B96D755E-0319-4E92-A296-23436F46A1FC}")
    _methods_ = [
        # 3
        COMMETHOD(
            [], HRESULT, "CreateCoreWebView2Controller",
            (["in"], wintypes.HWND, "parentWindow"),
            (["in"], POINTER(ICoreWebView2ControllerCompletedHandler), "handler"),
        ),
    ]


class ICoreWebView2Controller(IUnknown):
    _iid_ = GUID("{4D00C0D1-9434-4EB6-8078-8697A560334F}")
    _methods_ = [
        # 3
        COMMETHOD([], HRESULT, "get_IsVisible",
                  (["out"], POINTER(wintypes.BOOL), "value")),
        # 4
        COMMETHOD([], HRESULT, "put_IsVisible",
                  (["in"], wintypes.BOOL, "value")),
        # 5
        COMMETHOD([], HRESULT, "get_Bounds",
                  (["out"], POINTER(wintypes.RECT), "value")),
        # 6
        COMMETHOD([], HRESULT, "put_Bounds",
                  (["in"], POINTER(wintypes.RECT), "value")),
        # 7
        COMMETHOD([], HRESULT, "get_ZoomFactor",
                  (["out"], POINTER(ctypes.c_double), "value")),
        # 8
        COMMETHOD([], HRESULT, "put_ZoomFactor",
                  (["in"], ctypes.c_double, "value")),
        # 9-24 之间的方法按官方 vtable 顺序补齐
        COMMETHOD([], HRESULT, "add_ZoomFactorChanged",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_ZoomFactorChanged",
                  (["in"], ctypes.c_int64, "token")),
        COMMETHOD([], HRESULT, "SetBoundsAndZoomFactor",
                  (["in"], POINTER(wintypes.RECT), "bounds"),
                  (["in"], ctypes.c_double, "zoomFactor")),
        COMMETHOD([], HRESULT, "MoveFocus",
                  (["in"], ctypes.c_int, "reason")),
        COMMETHOD([], HRESULT, "add_MoveFocusRequested",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_MoveFocusRequested",
                  (["in"], ctypes.c_int64, "token")),
        COMMETHOD([], HRESULT, "add_GotFocus",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_GotFocus",
                  (["in"], ctypes.c_int64, "token")),
        COMMETHOD([], HRESULT, "add_LostFocus",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_LostFocus",
                  (["in"], ctypes.c_int64, "token")),
        COMMETHOD([], HRESULT, "add_AcceleratorKeyPressed",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_AcceleratorKeyPressed",
                  (["in"], ctypes.c_int64, "token")),
        # 21
        COMMETHOD([], HRESULT, "get_ParentWindow",
                  (["out"], POINTER(wintypes.HWND), "value")),
        # 22
        COMMETHOD([], HRESULT, "put_ParentWindow",
                  (["in"], wintypes.HWND, "value")),
        # 23
        COMMETHOD([], HRESULT, "NotifyParentWindowPositionChanged"),
        # 24
        COMMETHOD([], HRESULT, "Close"),
        # 25
        COMMETHOD([], HRESULT, "get_CoreWebView2",
                  (["out"], POINTER(POINTER(IUnknown)), "value")),
    ]


class ICoreWebView2(IUnknown):
    _iid_ = GUID("{76ECEACB-0462-4D94-AC83-423A6793775E}")
    _methods_ = [
        # 3
        COMMETHOD([], HRESULT, "get_Settings",
                  (["out"], POINTER(POINTER(IUnknown)), "value")),
        # 4
        COMMETHOD([], HRESULT, "get_Source",
                  (["out"], POINTER(ctypes.c_wchar_p), "value")),
        # 5
        COMMETHOD([], HRESULT, "Navigate",
                  (["in"], ctypes.c_wchar_p, "uri")),
        # 6
        COMMETHOD([], HRESULT, "NavigateToString",
                  (["in"], ctypes.c_wchar_p, "htmlContent")),
    ]


# ============================================================
# WebView2Loader
# ============================================================
def _get_search_dirs():
    """返回应该搜索 WebView2Loader.dll 的目录列表（按优先级）。"""
    dirs = []

    # 1. 环境变量指定的具体文件
    env = os.environ.get("WEBVIEW2_LOADER_PATH")
    if env:
        dirs.append(("file", env))

    if getattr(sys, "frozen", False):
        # ★ onedir：exe 所在目录
        exe_dir = os.path.dirname(sys.executable)
        dirs.append(("dir", exe_dir))

        # 单文件兜底：_MEIPASS
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            dirs.append(("dir", meipass))
    else:
        # 开发环境：脚本目录
        dirs.append(("dir", os.path.dirname(os.path.abspath(__file__))))

    return dirs


def _load_loader():
    search = _get_search_dirs()

    # 1) 先尝试环境变量指定的完整路径
    for kind, p in search:
        if kind != "file":
            continue
        try:
            return ctypes.WinDLL(p)
        except OSError as e:
            last_err = e

    # 2) 再按目录查找
    last_err = None
    tried = []
    for kind, d in search:
        if kind != "dir":
            continue
        dll_path = os.path.join(d, "WebView2Loader.dll")
        tried.append(dll_path)

        if not os.path.isfile(dll_path):
            continue

        # ★ 关键：把 DLL 所在目录加入 DLL 搜索路径，
        #    这样 WebView2Loader 自己的依赖（VC 运行时等）也能被找到
        try:
            os.add_dll_directory(d)
        except (AttributeError, OSError):
            pass

        try:
            return ctypes.WinDLL(dll_path)
        except OSError as e:
            last_err = e

    # 3) 最后让系统 PATH 兜底
    try:
        return ctypes.WinDLL("WebView2Loader.dll")
    except OSError as e:
        last_err = e

    raise OSError(
        "无法加载 WebView2Loader.dll。\n"
        "已尝试的路径：\n  " + "\n  ".join(tried) + "\n"
        "请确认：\n"
        "  1) WebView2Loader.dll 与 exe 在同一目录\n"
        "  2) DLL 位数与 Python/exe 一致（x64 vs x86）\n"
        "  3) 系统已安装 WebView2 Runtime\n"
        f"最后错误：{last_err}"
    )


_loader = _load_loader()

CreateCoreWebView2EnvironmentWithOptions = (
    _loader.CreateCoreWebView2EnvironmentWithOptions
)
CreateCoreWebView2EnvironmentWithOptions.restype = HRESULT
CreateCoreWebView2EnvironmentWithOptions.argtypes = [
    ctypes.c_wchar_p,
    ctypes.c_wchar_p,
    POINTER(IUnknown),
    POINTER(ICoreWebView2EnvironmentCompletedHandler),
]


# ============================================================
# Callback
# ============================================================

class EnvironmentCompleted(COMObject):
    _com_interfaces_ = [ICoreWebView2EnvironmentCompletedHandler]

    def __init__(self, webview):
        super().__init__()
        self.webview = webview

    def Invoke(self, errorCode, createdEnvironment):
        try:
            if self.webview._destroyed:
                return 0

            if errorCode:
                print(f"[WebView2] Environment failed: 0x{errorCode & 0xFFFFFFFF:08X}")
                self.webview._on_error(f"Environment failed: 0x{errorCode & 0xFFFFFFFF:08X}")
                return 0

            if not createdEnvironment:
                print("[WebView2] Environment is None")
                return 0

            environment = createdEnvironment.QueryInterface(ICoreWebView2Environment)
            self.webview._environment = environment

            self.webview._controller_handler = ControllerCompleted(self.webview)

            hr = environment.CreateCoreWebView2Controller(
                self.webview.hwnd,
                self.webview._controller_handler,
            )
            if hr < 0:
                print(f"[WebView2] CreateCoreWebView2Controller failed: 0x{hr & 0xFFFFFFFF:08X}")
                self.webview._on_error(f"CreateController failed: 0x{hr & 0xFFFFFFFF:08X}")
            return 0
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.webview._on_error(str(e))
            return 0


class ControllerCompleted(COMObject):
    _com_interfaces_ = [ICoreWebView2ControllerCompletedHandler]

    def __init__(self, webview):
        super().__init__()
        self.webview = webview

    def Invoke(self, errorCode, createdController):
        try:
            if self.webview._destroyed:
                return 0

            if errorCode:
                print(f"[WebView2] Controller failed: 0x{errorCode & 0xFFFFFFFF:08X}")
                self.webview._on_error(f"Controller failed: 0x{errorCode & 0xFFFFFFFF:08X}")
                return 0

            if not createdController:
                print("[WebView2] Controller is None")
                return 0

            controller = createdController.QueryInterface(ICoreWebView2Controller)
            self.webview._controller = controller

            # ★★★ 修复点：get_CoreWebView2 是 ["out"] 参数的方法，
            #     comtypes 会把 out 参数作为返回值返回，
            #     所以不能传 byref，直接接收返回值即可。
            core_ptr = controller.get_CoreWebView2()

            if not core_ptr:
                print("[WebView2] CoreWebView2 is None")
                self.webview._on_error("CoreWebView2 is None")
                return 0

            self.webview._webview = core_ptr.QueryInterface(ICoreWebView2)

            # 显示 + 设置 bounds
            hr = controller.put_IsVisible(True)
            if hr < 0:
                print(f"[WebView2] put_IsVisible failed: 0x{hr & 0xFFFFFFFF:08X}")

            self.webview._resize()

            # 处理提前调用的 navigate
            if self.webview._pending_url:
                url = self.webview._pending_url
                self.webview._pending_url = None
                self.webview._navigate(url)

            self.webview._ready = True

            # 触发 ready 回调
            if self.webview._on_ready_cb:
                try:
                    self.webview._on_ready_cb()
                except Exception:
                    import traceback
                    traceback.print_exc()

            return 0
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.webview._on_error(str(e))
            return 0


# ============================================================
# WebView2 高层封装
# ============================================================

class WebView2:
    def __init__(self, hwnd, on_ready=None, on_error=None):
        """
        :param hwnd: 父窗口 HWND
        :param on_ready: WebView2 准备就绪后的回调（在主线程消息循环中被调用）
        :param on_error: 出错回调，接收错误信息字符串
        """
        self.hwnd = hwnd
        self._on_ready_cb = on_ready
        self._on_error_cb = on_error

        self._environment = None
        self._controller = None
        self._webview = None

        self._environment_handler = None
        self._controller_handler = None

        self._initialized = False
        self._ready = False
        self._destroyed = False
        self._pending_url = None

        self._com_initialized = False

    # ---------- 生命周期 ----------

    def init(self):
        if self._initialized:
            return True

        self._destroyed = False
        self._ready = False

        # 确保 COM 已初始化（STA，配合 Win32 消息循环）
        try:
            comtypes.CoInitialize()
            self._com_initialized = True
        except OSError:
            # 已经初始化过（RPC_E_CHANGED_MODE 等），忽略
            pass

        self._environment_handler = EnvironmentCompleted(self)

        hr = CreateCoreWebView2EnvironmentWithOptions(
            None, None, None,
            self._environment_handler,
        )
        if hr < 0:
            raise OSError(
                f"CreateCoreWebView2EnvironmentWithOptions failed: "
                f"0x{hr & 0xFFFFFFFF:08X}\n"
                f"请检查 WebView2 Runtime 是否已安装。"
            )

        self._initialized = True
        return True

    def destroy(self):
        if self._destroyed:
            return

        self._destroyed = True
        self._ready = False
        self._pending_url = None

        if self._controller:
            try:
                self._controller.Close()
            except Exception:
                pass

        self._webview = None
        self._controller = None
        self._environment = None
        self._controller_handler = None
        self._environment_handler = None

        # 注意：不要在 destroy 里 CoUninitialize，
        # 因为 Win32 消息循环可能还在跑。

    # ---------- 导航 ----------

    def navigate(self, url: str):
        if self._destroyed:
            return False

        # WebView2 创建是异步的，如果还没就绪先缓存
        if self._webview is None:
            self._pending_url = url
            return True

        return self._navigate(url)

    def _navigate(self, url: str):
        if self._webview is None:
            self._pending_url = url
            return True

        hr = self._webview.Navigate(url)
        if hr < 0:
            raise OSError(f"Navigate failed: 0x{hr & 0xFFFFFFFF:08X}")
        return True

    def navigate_to_string(self, html: str):
        if self._webview is None:
            return False
        hr = self._webview.NavigateToString(html)
        if hr < 0:
            raise OSError(f"NavigateToString failed: 0x{hr & 0xFFFFFFFF:08X}")
        return True

    # ---------- 尺寸 ----------

    def resize(self):
        self._resize()

    def _resize(self):
        if self._controller is None:
            return

        rect = wintypes.RECT()
        user32.GetClientRect(self.hwnd, ctypes.byref(rect))

        # 忽略 0 尺寸（窗口尚未布局时）
        if rect.right <= 0 or rect.bottom <= 0:
            return

        hr = self._controller.put_Bounds(ctypes.byref(rect))
        if hr < 0:
            print(f"[WebView2] put_Bounds failed: 0x{hr & 0xFFFFFFFF:08X}")

    # ---------- 属性 ----------

    @property
    def ready(self):
        return self._ready

    @property
    def core(self):
        """返回 ICoreWebView2，未就绪时为 None。"""
        return self._webview

    def _on_error(self, msg):
        if self._on_error_cb:
            try:
                self._on_error_cb(msg)
            except Exception:
                pass