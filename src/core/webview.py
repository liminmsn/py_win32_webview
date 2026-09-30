import ctypes
from ctypes import wintypes

import os
import sys

import comtypes
from comtypes import GUID, HRESULT, IUnknown, COMMETHOD, POINTER, COMObject
from lib.implDll import load_dll


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
        COMMETHOD([], HRESULT, "Invoke",
                  (["in"], HRESULT, "errorCode"),
                  (["in"], POINTER(IUnknown), "createdController")),
    ]


class ICoreWebView2EnvironmentCompletedHandler(IUnknown):
    _iid_ = GUID("{4E8A3389-C9D8-4BD2-B6B5-124FEE6CC14D}")
    _methods_ = [
        COMMETHOD([], HRESULT, "Invoke",
                  (["in"], HRESULT, "errorCode"),
                  (["in"], POINTER(IUnknown), "createdEnvironment")),
    ]


class ICoreWebView2Environment(IUnknown):
    _iid_ = GUID("{B96D755E-0319-4E92-A296-23436F46A1FC}")
    _methods_ = [
        COMMETHOD([], HRESULT, "CreateCoreWebView2Controller",
                  (["in"], wintypes.HWND, "parentWindow"),
                  (["in"], POINTER(ICoreWebView2ControllerCompletedHandler), "handler")),
    ]


class ICoreWebView2Controller(IUnknown):
    _iid_ = GUID("{4D00C0D1-9434-4EB6-8078-8697A560334F}")
    _methods_ = [
        COMMETHOD([], HRESULT, "get_IsVisible",
                  (["out"], POINTER(wintypes.BOOL), "value")),
        COMMETHOD([], HRESULT, "put_IsVisible",
                  (["in"], wintypes.BOOL, "value")),
        COMMETHOD([], HRESULT, "get_Bounds",
                  (["out"], POINTER(wintypes.RECT), "value")),
        COMMETHOD([], HRESULT, "put_Bounds",
                  (["in"], POINTER(wintypes.RECT), "value")),
        COMMETHOD([], HRESULT, "get_ZoomFactor",
                  (["out"], POINTER(ctypes.c_double), "value")),
        COMMETHOD([], HRESULT, "put_ZoomFactor",
                  (["in"], ctypes.c_double, "value")),
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
        COMMETHOD([], HRESULT, "get_ParentWindow",
                  (["out"], POINTER(wintypes.HWND), "value")),
        COMMETHOD([], HRESULT, "put_ParentWindow",
                  (["in"], wintypes.HWND, "value")),
        COMMETHOD([], HRESULT, "NotifyParentWindowPositionChanged"),
        COMMETHOD([], HRESULT, "Close"),
        COMMETHOD([], HRESULT, "get_CoreWebView2",
                  (["out"], POINTER(POINTER(IUnknown)), "value")),
    ]


# ---- 消息相关接口 ----

class ICoreWebView2WebMessageReceivedEventArgs(IUnknown):
    _iid_ = GUID("{0F99A40C-E962-4207-9E92-E3D542EFF849}")
    _methods_ = [
        COMMETHOD([], HRESULT, "get_Source",
                  (["out"], POINTER(ctypes.c_wchar_p), "value")),
        COMMETHOD([], HRESULT, "get_WebMessageAsJson",
                  (["out"], POINTER(ctypes.c_wchar_p), "value")),
        COMMETHOD([], HRESULT, "TryGetWebMessageAsString",
                  (["out"], POINTER(ctypes.c_wchar_p), "value")),
    ]


class ICoreWebView2WebMessageReceivedEventHandler(IUnknown):
    _iid_ = GUID("{57213F19-00E6-49FA-8E07-898EA01ECBD2}")
    _methods_ = [
        COMMETHOD([], HRESULT, "Invoke",
                  (["in"], POINTER(IUnknown), "sender"),
                  (["in"], POINTER(ICoreWebView2WebMessageReceivedEventArgs), "args")),
    ]


class ICoreWebView2ExecuteScriptCompletedHandler(IUnknown):
    _iid_ = GUID("{49511172-CC67-4BCA-99A1-4BCCE1F8B0D4}")
    _methods_ = [
        COMMETHOD([], HRESULT, "Invoke",
                  (["in"], HRESULT, "errorCode"),
                  (["in"], ctypes.c_wchar_p, "resultObjectAsJson")),
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

        # 7-26：vtable 占位（不用但必须保留，否则后面方法索引全错）
        COMMETHOD([], HRESULT, "add_NavigationStarting",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_NavigationStarting",
                  (["in"], ctypes.c_int64, "token")),
        COMMETHOD([], HRESULT, "add_ContentLoading",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_ContentLoading",
                  (["in"], ctypes.c_int64, "token")),
        COMMETHOD([], HRESULT, "add_SourceChanged",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_SourceChanged",
                  (["in"], ctypes.c_int64, "token")),
        COMMETHOD([], HRESULT, "add_HistoryChanged",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_HistoryChanged",
                  (["in"], ctypes.c_int64, "token")),
        COMMETHOD([], HRESULT, "add_NavigationCompleted",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_NavigationCompleted",
                  (["in"], ctypes.c_int64, "token")),
        COMMETHOD([], HRESULT, "add_FrameNavigationStarting",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_FrameNavigationStarting",
                  (["in"], ctypes.c_int64, "token")),
        COMMETHOD([], HRESULT, "add_FrameNavigationCompleted",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_FrameNavigationCompleted",
                  (["in"], ctypes.c_int64, "token")),
        COMMETHOD([], HRESULT, "add_ScriptDialogOpening",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_ScriptDialogOpening",
                  (["in"], ctypes.c_int64, "token")),
        COMMETHOD([], HRESULT, "add_PermissionRequested",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_PermissionRequested",
                  (["in"], ctypes.c_int64, "token")),
        COMMETHOD([], HRESULT, "add_ProcessFailed",
                  (["in"], POINTER(IUnknown), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        COMMETHOD([], HRESULT, "remove_ProcessFailed",
                  (["in"], ctypes.c_int64, "token")),

        # 27
        COMMETHOD([], HRESULT, "AddScriptToExecuteOnDocumentCreated",
                  (["in"], ctypes.c_wchar_p, "javascript"),
                  (["in"], POINTER(IUnknown), "handler")),
        # 28
        COMMETHOD([], HRESULT, "RemoveScriptToExecuteOnDocumentCreated",
                  (["in"], ctypes.c_wchar_p, "id")),
        # 29
        COMMETHOD([], HRESULT, "ExecuteScript",
                  (["in"], ctypes.c_wchar_p, "javascript"),
                  (["in"], POINTER(IUnknown), "handler")),
        # 30
        COMMETHOD([], HRESULT, "CapturePreview",
                  (["in"], ctypes.c_int, "imageFormat"),
                  (["in"], POINTER(IUnknown), "imageStream"),
                  (["in"], POINTER(IUnknown), "handler")),
        # 31
        COMMETHOD([], HRESULT, "Reload"),
        # 32
        COMMETHOD([], HRESULT, "PostWebMessageAsJson",
                  (["in"], ctypes.c_wchar_p, "webMessageAsJson")),
        # 33
        COMMETHOD([], HRESULT, "PostWebMessageAsString",
                  (["in"], ctypes.c_wchar_p, "webMessageAsString")),
        # 34
        COMMETHOD([], HRESULT, "add_WebMessageReceived",
                  (["in"], POINTER(ICoreWebView2WebMessageReceivedEventHandler), "handler"),
                  (["out"], POINTER(ctypes.c_int64), "token")),
        # 35
        COMMETHOD([], HRESULT, "remove_WebMessageReceived",
                  (["in"], ctypes.c_int64, "token")),
    ]

_loader = load_dll("WebView2Loader.dll")
CreateCoreWebView2EnvironmentWithOptions = (_loader.CreateCoreWebView2EnvironmentWithOptions)
CreateCoreWebView2EnvironmentWithOptions.restype = HRESULT
CreateCoreWebView2EnvironmentWithOptions.argtypes = [
    ctypes.c_wchar_p,
    ctypes.c_wchar_p,
    POINTER(IUnknown),
    POINTER(ICoreWebView2EnvironmentCompletedHandler),
]


# ============================================================
# Callbacks
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
            return 0
        except Exception:
            import traceback
            traceback.print_exc()
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
                return 0
            if not createdController:
                return 0

            controller = createdController.QueryInterface(ICoreWebView2Controller)
            self.webview._controller = controller

            core_ptr = controller.get_CoreWebView2()
            if not core_ptr:
                print("[WebView2] CoreWebView2 is None")
                return 0

            self.webview._webview = core_ptr.QueryInterface(ICoreWebView2)

            controller.put_IsVisible(True)
            self.webview._resize()

            self.webview._message_handler = WebMessageReceivedHandler(self.webview)
            self.webview._web_message_token = self.webview._webview.add_WebMessageReceived(
                self.webview._message_handler
            )

            if self.webview._pending_url:
                url = self.webview._pending_url
                self.webview._pending_url = None
                self.webview._navigate(url)

            self.webview._ready = True

            if self.webview._on_ready_cb:
                try:
                    self.webview._on_ready_cb()
                except Exception:
                    import traceback
                    traceback.print_exc()
            return 0
        except Exception:
            import traceback
            traceback.print_exc()
            return 0


class WebMessageReceivedHandler(COMObject):
    _com_interfaces_ = [ICoreWebView2WebMessageReceivedEventHandler]

    def __init__(self, webview):
        super().__init__()
        self.webview = webview

    def Invoke(self, sender, args):
        try:
            if args is None:
                return 0
            raw = args.get_WebMessageAsJson()
            self.webview._dispatch_message(raw)
        except Exception:
            import traceback
            traceback.print_exc()
        return 0


class ExecuteScriptCompletedHandler(COMObject):
    _com_interfaces_ = [ICoreWebView2ExecuteScriptCompletedHandler]

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def Invoke(self, errorCode, resultObjectAsJson):
        try:
            if self.callback is None:
                return 0
            if errorCode:
                self.callback(None, f"0x{errorCode & 0xFFFFFFFF:08X}")
            else:
                self.callback(resultObjectAsJson, None)
        except Exception:
            import traceback
            traceback.print_exc()
        return 0


# ============================================================
# WebView2 高层封装
# ============================================================

class WebView2:
    def __init__(self, hwnd, *, on_ready=None, on_error=None, on_message=None):
        """
        :param hwnd: 父窗口 HWND
        :param on_ready: 无参回调，WebView2 就绪时触发
        :param on_error: 单参回调，接收错误字符串
        :param on_message: 单参回调，接收 JS postMessage 发来的数据（已 JSON 解析）
        """
        self.hwnd = hwnd
        self._on_ready_cb = on_ready
        self._on_error_cb = on_error
        self._on_message_cb = on_message

        self._environment = None
        self._controller = None
        self._webview = None

        self._environment_handler = None
        self._controller_handler = None
        self._message_handler = None
        self._web_message_token = None
        self._script_handlers = []

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

        # WebView2 背景色：ARGB 格式，00000000 = 全透明
        os.environ["WEBVIEW2_DEFAULT_BACKGROUND_COLOR"] = "00000000"

        try:
            comtypes.CoInitialize()
            self._com_initialized = True
        except OSError:
            pass

        self._environment_handler = EnvironmentCompleted(self)

        hr = CreateCoreWebView2EnvironmentWithOptions(
            None, None, None, self._environment_handler,
        )
        if hr < 0:
            raise OSError(
                f"CreateCoreWebView2EnvironmentWithOptions failed: "
                f"0x{hr & 0xFFFFFFFF:08X}"
            )

        self._initialized = True
        return True

    def destroy(self):
        if self._destroyed:
            return

        self._destroyed = True
        self._ready = False
        self._pending_url = None

        if self._webview and self._web_message_token is not None:
            try:
                self._webview.remove_WebMessageReceived(self._web_message_token)
            except Exception:
                pass

        self._web_message_token = None
        self._message_handler = None
        self._script_handlers = []

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

    # ---------- 导航 ----------

    def navigate(self, url: str):
        if self._destroyed:
            return False
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
        if rect.right <= 0 or rect.bottom <= 0:
            return
        hr = self._controller.put_Bounds(ctypes.byref(rect))
        if hr < 0:
            print(f"[WebView2] put_Bounds failed: 0x{hr & 0xFFFFFFFF:08X}")

    # ---------- JS 通信 ----------

    def _dispatch_message(self, raw):
        if self._on_message_cb is None:
            return
        import json
        data = raw
        if raw is not None:
            try:
                data = json.loads(raw)
            except (ValueError, TypeError):
                data = raw
        try:
            self._on_message_cb(data)
        except Exception:
            import traceback
            traceback.print_exc()

    def post_json(self, obj):
        """发 JSON 消息给 JS。event.data 是对象。"""
        if self._webview is None:
            return False
        import json
        text = json.dumps(obj, ensure_ascii=False)
        return self._webview.PostWebMessageAsJson(text) >= 0

    def post_string(self, s: str):
        """发字符串消息给 JS。event.data 是字符串。"""
        if self._webview is None:
            return False
        return self._webview.PostWebMessageAsString(s) >= 0

    # 别名
    send_json = post_json
    send_string = post_string

    def execute_script(self, js: str, on_result=None):
        """
        执行 JS。
        :param js: JavaScript 代码
        :param on_result: (result_json, error) 回调
        """
        if self._webview is None:
            return False
        handler = ExecuteScriptCompletedHandler(on_result)
        self._script_handlers.append(handler)
        return self._webview.ExecuteScript(js, handler) >= 0

    # ---------- 属性 ----------

    @property
    def ready(self):
        return self._ready

    @property
    def core(self):
        return self._webview

    def _on_error(self, msg):
        if self._on_error_cb:
            try:
                self._on_error_cb(msg)
            except Exception:
                pass