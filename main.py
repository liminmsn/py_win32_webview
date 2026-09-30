import win32api
import win32con
import win32gui

from src.core.window import createWc, createWindow,enable_dpi_awareness
from src.core.webview import WebView2
webview = None

CLASS_NAME = "hkhj5"
WINDOW_TITLE = "好看韩剧5"
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

    
    win32gui.ShowWindow(hwnd,win32con.SW_SHOW)
    win32gui.UpdateWindow(hwnd)
    webview = WebView2(hwnd,on_message=on_web_message)
    webview.init()
    webview.navigate("http://127.0.0.1:5173/")

    win32gui.PumpMessages()

def on_web_message(msg: dict):
    print("收到 JS 消息:", msg)
    if msg.get("type") == "ready":
        webview.post_json({"type": "hello", "data": "world"})

if __name__ == "__main__":
    main()