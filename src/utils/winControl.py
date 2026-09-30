import win32gui
import win32con
import win32api
from ctypes import wintypes, Structure, sizeof, byref, windll

# 辅助结构体定义 (用于 GetWindowPlacement / SetWindowPlacement)
class POINT(Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]

class RECT(Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG)
    ]

class WINDOWPLACEMENT(Structure):
    _fields_ = [
        ("length", wintypes.UINT),
        ("flags", wintypes.UINT),
        ("showCmd", wintypes.UINT),
        ("ptMinPosition", POINT),
        ("ptMaxPosition", POINT),
        ("rcNormalPosition", RECT)
    ]


class WinControl:
    def __init__(self, hwnd=None):
        self.hwnd = hwnd
        self._is_fullscreen = False
        
        # 保存全屏前的样式与位置信息
        self._saved_style = 0
        self._saved_ex_style = 0
        self._saved_placement = WINDOWPLACEMENT()
        self._saved_placement.length = sizeof(WINDOWPLACEMENT)

    def ToggleFullscreen(self):
        if not self.hwnd or not win32gui.IsWindow(self.hwnd):
            return False

        if not self._is_fullscreen:
            # ================= 1. 进入全屏 =================
            # 获取当前窗口样式与扩展样式
            self._saved_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_STYLE)
            self._saved_ex_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
            
            # 保存窗口当前的位置与显示状态
            windll.user32.GetWindowPlacement(self.hwnd, byref(self._saved_placement))

            # 获取窗口所在显示器的物理分辨率
            monitor = win32api.MonitorFromWindow(self.hwnd, win32con.MONITOR_DEFAULTTONEAREST)
            monitor_info = win32api.GetMonitorInfo(monitor)
            monitor_rect = monitor_info["Monitor"]  # (left, top, right, bottom)
            
            x = monitor_rect[0]
            y = monitor_rect[1]
            width = monitor_rect[2] - monitor_rect[0]
            height = monitor_rect[3] - monitor_rect[1]

            # 去除标题栏和可拉伸边框样式
            new_style = self._saved_style & ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME)
            new_ex_style = self._saved_ex_style & ~(
                win32con.WS_EX_DLGMODALFRAME | 
                win32con.WS_EX_CLIENTEDGE | 
                win32con.WS_EX_STATICEDGE
            )

            # 更新样式
            win32gui.SetWindowLong(self.hwnd, win32con.GWL_STYLE, new_style)
            win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, new_ex_style)

            # 移动并覆盖整个屏幕 (SWP_FRAMECHANGED 会促使 Windows 重新计算非客户区)
            win32gui.SetWindowPos(
                self.hwnd,
                win32con.HWND_TOP,
                x, y, width, height,
                win32con.SWP_NOOWNERZORDER | win32con.SWP_FRAMECHANGED
            )

            self._is_fullscreen = True
        else:
            # ================= 2. 退出全屏 =================
            # 还原之前的样式
            win32gui.SetWindowLong(self.hwnd, win32con.GWL_STYLE, self._saved_style)
            win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, self._saved_ex_style)

            # 恢复全屏前的位置和大小
            windll.user32.SetWindowPlacement(self.hwnd, byref(self._saved_placement))

            # 刷新非客户区样式
            win32gui.SetWindowPos(
                self.hwnd,
                0,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | 
                win32con.SWP_NOSIZE | 
                win32con.SWP_NOZORDER | 
                win32con.SWP_NOACTIVATE | 
                win32con.SWP_FRAMECHANGED
            )

            self._is_fullscreen = False

        return self._is_fullscreen
    def EnterFullscreen(self):
        """显式进入全屏（如果当前不是全屏才触发）"""
        if not self._is_fullscreen:
            return self.ToggleFullscreen()
        return True
    
    def ExitFullscreen(self):
        """显式退出全屏（如果当前是全屏才触发）"""
        if self._is_fullscreen:
            return self.ToggleFullscreen()
        return False