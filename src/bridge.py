import itertools
import win32con
import win32gui
from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from src.net.request import send
from src.utils.winControl import WinControl

WM_HTTP_RESULT = win32con.WM_APP + 1

class BridgeMessage(Enum):
    HTTP="http"
    CLIENT="client"
class Bridge:
    def __init__(self):
        print("Bridge 实例化了")
        self.hwnd = None
        self.webview = None
        self._executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="http")
        self._counter = itertools.count(1)
        self._pending = {}
        self.winc = None

    def set_hwnd(self, hwnd):
        self.hwnd = hwnd
        self.winc =WinControl(self.hwnd)

    def set_webview(self, webview):
        self.webview = webview

    def shutdown(self):
        self._executor.shutdown(wait=False)

    # ---------- 主线程收到 WM_HTTP_RESULT 后回调这里 ----------
    def on_http_result(self, key):
        payload = self._pending.pop(key, None)
        if payload is not None and self.webview:
            try:
                self.webview.post_json(payload)
            except Exception:
                import traceback
                traceback.print_exc()

    # ---------- JS 消息入口 ----------
    def on_web_message(self, msg: dict):
        print("收到 JS 消息:", msg)
        if not isinstance(msg, dict):
            return
        
        msg_type = msg.get("type")
        msg_id = msg.get("id")
        msg_value = msg.get("value")
        if msg_type == BridgeMessage.HTTP.value:
            def work():
                print("[线程] 开始请求:", msg_value.get("url"))
                result = send(msg_value)
                payload = {"id": msg_id, "value": result}
                key = next(self._counter)
                self._pending[key] = payload
                if self.hwnd:
                    win32gui.PostMessage(self.hwnd, WM_HTTP_RESULT, key, 0)
            self._executor.submit(work)
        elif msg_type == BridgeMessage.CLIENT.value:
            action_name = msg_value.get("type")
            if action_name:
                getattr(self.winc, action_name)()
            pass