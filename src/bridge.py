import itertools
import win32con
import win32gui
from concurrent.futures import ThreadPoolExecutor
from src.net.request import send

WM_HTTP_RESULT = win32con.WM_APP + 1

class Bridge:
    def __init__(self):
        print("Bridge 实例化了")
        self.hwnd = None
        self.webview = None
        self._executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="http")
        self._counter = itertools.count(1)
        self._pending = {}

    def set_hwnd(self, hwnd):
        self.hwnd = hwnd

    def set_webview(self, webview):
        self.webview = webview

    # ---------- JS 消息入口 ----------

    def on_web_message(self, msg: dict):
        print("收到 JS 消息:", msg)
        if not isinstance(msg, dict):
            return
        if msg.get("type") == "http":
            self._handle_http(msg)

    def _handle_http(self, msg: dict):
        msg_id = msg.get("id")
        value = msg.get("value") or {}

        def work():
            print("[线程] 开始请求:", value.get("url"))
            result = send(value)
            payload = {"id": msg_id, "value": result}
            key = next(self._counter)
            self._pending[key] = payload

            if self.hwnd:
                win32gui.PostMessage(self.hwnd, WM_HTTP_RESULT, key, 0)

        self._executor.submit(work)
    
    # ---------- 主线程收到 WM_HTTP_RESULT 后回调这里 ----------

    def on_http_result(self, key):
        payload = self._pending.pop(key, None)
        if payload is not None and self.webview:
            try:
                self.webview.post_json(payload)
            except Exception:
                import traceback
                traceback.print_exc()
    def shutdown(self):
        self._executor.shutdown(wait=False)