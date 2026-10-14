from pathlib import Path
import sys
from src.application import Application

if getattr(sys, "frozen", False):
    # 打包环境：把 stdout/stderr 重定向到 exe 同目录的 run.log
    log_dir = Path(sys.executable).parent
    log_path = log_dir / "run.log"
    try:
        log_file = open(log_path, "a", encoding="utf-8", buffering=1)
        if sys.stdout is None:
            sys.stdout = log_file
        if sys.stderr is None:
            sys.stderr = log_file
    except Exception:
        pass

if __name__ == "__main__":
    Application().run()