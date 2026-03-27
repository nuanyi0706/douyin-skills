#!/usr/bin/env python3
"""
Chrome 浏览器启动器。

启动带有调试端口的 Chrome 浏览器，用于 CDP 自动化。
支持 X11 和 Wayland 显示环境。
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

# 默认配置
DEFAULT_PORT = 9222
DEFAULT_HOST = "127.0.0.1"
DEFAULT_USER_DATA_DIR = Path.home() / ".douyin-skills" / "chrome-profile"

# 启动超时配置
STARTUP_TIMEOUT = 15  # X11/默认环境
STARTUP_TIMEOUT_WAYLAND = 25  # Wayland环境需要更长时间


def detect_display_environment() -> dict:
    """
    检测显示环境并返回适当的环境变量。
    
    支持 X11、Wayland 和无头环境。
    """
    env = os.environ.copy()
    
    # 如果已经有显示环境，直接返回
    if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
        return env
    
    # 尝试检测 Wayland 会话
    xdg_runtime_dir = os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}"
    wayland_socket = os.path.join(xdg_runtime_dir, "wayland-0")
    
    if os.path.exists(wayland_socket):
        env["WAYLAND_DISPLAY"] = "wayland-0"
        env["XDG_RUNTIME_DIR"] = xdg_runtime_dir
        return env
    
    # 尝试检测 X11
    if os.path.exists("/tmp/.X11-unix"):
        for display_num in range(10):
            x_socket = f"/tmp/.X11-unix/X{display_num}"
            if os.path.exists(x_socket):
                env["DISPLAY"] = f":{display_num}"
                break
    
    return env


def get_chrome_flags_for_display(env: dict = None, headless: bool = False) -> list:
    """
    获取当前显示环境需要的 Chrome 参数。
    
    Args:
        env: 环境变量字典，如果为None则使用os.environ
        headless: 是否无头模式
    
    Returns:
        Chrome 命令行参数列表
    """
    flags = []
    
    check_env = env if env is not None else os.environ
    
    # 检查 Wayland 环境
    wayland_display = check_env.get("WAYLAND_DISPLAY")
    xdg_runtime = check_env.get("XDG_RUNTIME_DIR")
    
    if wayland_display and xdg_runtime:
        # Wayland 环境 - 需要 ozone platform
        flags.extend([
            "--ozone-platform=wayland",
            "--enable-features=UseOzonePlatform",
        ])
    
    if headless:
        flags.append("--headless=new")
        flags.append("--disable-gpu")
    
    return flags


def find_chrome_executable() -> str:
    """查找 Chrome 可执行文件"""
    # Linux
    candidates = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ]
    
    for path in candidates:
        if os.path.exists(path):
            return path
    
    raise FileNotFoundError("Chrome executable not found. Please install Google Chrome or Chromium.")


def is_chrome_running(port: int = DEFAULT_PORT) -> bool:
    """检查 Chrome 是否正在运行"""
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except Exception:
        return False


def start_chrome(
    port: int = DEFAULT_PORT,
    headless: bool = False,
    user_data_dir: str = None,
    account: str = "default"
) -> subprocess.Popen:
    """
    启动 Chrome 浏览器。
    
    Args:
        port: 调试端口
        headless: 是否无头模式
        user_data_dir: 用户数据目录
        account: 账号名称
    
    Returns:
        Chrome 进程
    """
    # 检查是否已在运行
    if is_chrome_running(port):
        print(f"[chrome_launcher] Chrome already running on port {port}")
        return None
    
    # 查找 Chrome 可执行文件
    chrome_exe = find_chrome_executable()
    
    # 设置用户数据目录
    if user_data_dir is None:
        user_data_dir = str(DEFAULT_USER_DATA_DIR / account)
    
    Path(user_data_dir).mkdir(parents=True, exist_ok=True)
    
    # 检测显示环境（先于构建参数）
    env = detect_display_environment()
    
    # 构建启动参数
    args = [
        chrome_exe,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={user_data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-networking",
        "--disable-client-side-phishing-detection",
        "--disable-default-apps",
        "--disable-extensions",
        "--disable-hang-monitor",
        "--disable-popup-blocking",
        "--disable-prompt-on-repost",
        "--disable-sync",
        "--disable-translate",
        "--metrics-recording-only",
        "--new-window",
        "https://www.douyin.com",
    ]
    
    # 添加显示环境相关的参数
    display_flags = get_chrome_flags_for_display(env=env, headless=headless)
    args.extend(display_flags)
    
    # 启动 Chrome
    mode_label = "headless" if headless else "headed"
    print(f"[chrome_launcher] Starting Chrome ({mode_label})...")
    print(f"[chrome_launcher] Port: {port}")
    print(f"[chrome_launcher] User data dir: {user_data_dir}")
    
    # 显示检测到的显示环境
    if env.get("WAYLAND_DISPLAY"):
        print(f"[chrome_launcher] Display: Wayland ({env.get('WAYLAND_DISPLAY')})")
    elif env.get("DISPLAY"):
        print(f"[chrome_launcher] Display: X11 ({env.get('DISPLAY')})")
    
    process = subprocess.Popen(
        args,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
    )
    
    # 等待 Chrome 启动（根据显示环境使用不同超时）
    print(f"[chrome_launcher] Waiting for Chrome to start...")
    timeout = STARTUP_TIMEOUT_WAYLAND if env.get("WAYLAND_DISPLAY") else STARTUP_TIMEOUT
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if is_chrome_running(port):
            print(f"[chrome_launcher] Chrome started successfully (PID: {process.pid})")
            return process
        time.sleep(0.5)
    
    print(f"[chrome_launcher] Warning: Chrome started but port {port} not responding after {timeout}s")
    return process


def kill_chrome(port: int = DEFAULT_PORT):
    """终止 Chrome 进程"""
    import signal
    
    # 通过调试端口获取进程信息
    import requests
    try:
        response = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=2)
        # 无法直接获取 PID，需要通过其他方式
    except Exception:
        pass
    
    # 使用 pkill 终止 Chrome
    subprocess.run(["pkill", "-f", f"remote-debugging-port={port}"], capture_output=True)
    print(f"[chrome_launcher] Chrome killed")


def main():
    parser = argparse.ArgumentParser(description="Chrome 浏览器启动器")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="调试端口")
    parser.add_argument("--headless", action="store_true", help="无头模式")
    parser.add_argument("--user-data-dir", help="用户数据目录")
    parser.add_argument("--account", default="default", help="账号名称")
    parser.add_argument("--kill", action="store_true", help="终止 Chrome")
    
    args = parser.parse_args()
    
    if args.kill:
        kill_chrome(args.port)
        return
    
    process = start_chrome(
        port=args.port,
        headless=args.headless,
        user_data_dir=args.user_data_dir,
        account=args.account
    )
    
    if process:
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n[chrome_launcher] Stopping Chrome...")
            process.terminate()


if __name__ == "__main__":
    main()