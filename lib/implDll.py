import ctypes
import os
import sys


# 当前文件所在目录（lib/）
_LIB_DIR = os.path.dirname(os.path.abspath(__file__))


# 已加载的 DLL 缓存：name -> WinDLL 实例
_loaded_cache = {}


def load_dll(name: str, use_cache: bool = True) -> ctypes.WinDLL:
    """
    加载 lib 目录下的指定 DLL。

    :param name: DLL 文件名，例如 "WebView2Loader.dll"（也可以写全路径）
    :param use_cache: 是否使用缓存，同一个 DLL 只加载一次
    :return: ctypes.WinDLL 实例
    :raises FileNotFoundError: DLL 不存在
    :raises OSError: DLL 加载失败（位数不匹配、缺依赖等）
    """
    # 允许传相对名或绝对路径
    if os.path.isabs(name):
        path = name
    else:
        path = os.path.join(_LIB_DIR, name)

    if not os.path.isfile(path):
        raise FileNotFoundError(f"DLL 不存在：{path}")

    # 缓存命中
    if use_cache and path in _loaded_cache:
        return _loaded_cache[path]

    # ★ 打包后（PyInstaller）优先从 _MEIPASS 找同目录 DLL
    search_dirs = [_LIB_DIR]
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        search_dirs.append(exe_dir)
        search_dirs.append(os.path.join(exe_dir, "_internal"))
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            search_dirs.append(meipass)

    # ★ 把 DLL 所在目录加入 DLL 搜索路径，
    #    让 DLL 自己的依赖（VC 运行时等）也能被找到
    for d in search_dirs:
        if os.path.isdir(d):
            try:
                os.add_dll_directory(d)
            except (AttributeError, OSError):
                pass

    # 尝试多种方式加载
    last_err = None
    for d in search_dirs:
        candidate = os.path.join(d, os.path.basename(path))
        if not os.path.isfile(candidate):
            continue
        try:
            dll = ctypes.WinDLL(candidate)
            if use_cache:
                _loaded_cache[path] = dll
            return dll
        except OSError as e:
            last_err = e

    raise OSError(
        f"无法加载 {name}。\n"
        f"已尝试目录：\n  " + "\n  ".join(search_dirs) + "\n"
        f"最后错误：{last_err}"
    )


def get_dll_path(name: str) -> str:
    """返回 lib 目录下指定 DLL 的绝对路径（不加载）。"""
    if os.path.isabs(name):
        return name
    return os.path.join(_LIB_DIR, name)


def list_dlls() -> list:
    """列出 lib 目录下所有 DLL。"""
    if not os.path.isdir(_LIB_DIR):
        return []
    return [
        f for f in os.listdir(_LIB_DIR)
        if f.lower().endswith(".dll")
        and os.path.isfile(os.path.join(_LIB_DIR, f))
    ]