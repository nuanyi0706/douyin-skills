"""
抖音登录模块。

支持登录检查、扫码登录、Cookie 持久化。
"""

import json
import os
import time
from pathlib import Path
from typing import Optional

from .cdp import CDPClient, CDPError
from .selectors import SELECTORS
from .urls import URLS


# Cookie 存储路径
COOKIE_DIR = Path.home() / ".douyin-skills" / "cookies"
COOKIE_DIR.mkdir(parents=True, exist_ok=True)


def get_cookie_path(account: str = "default") -> Path:
    """获取 Cookie 文件路径"""
    return COOKIE_DIR / f"{account}.json"


def check_login(cdp: CDPClient) -> dict:
    """
    检查登录状态。
    
    Returns:
        {
            "logged_in": bool,
            "user": {
                "nickname": str,
                "user_id": str,
                "avatar": str
            } | None
        }
    """
    # 导航到首页
    cdp.navigate(URLS["home"])
    time.sleep(2)
    
    # 检查是否有登录指示器
    avatar_selector = SELECTORS["login"]["logged_in_indicator"]
    if not cdp.wait_for_selector(avatar_selector, timeout=5000):
        return {"logged_in": False, "user": None}
    
    # 获取用户信息
    try:
        # 从页面数据提取用户信息
        page_data = cdp.get_page_data()
        user_info = page_data.get("user", {})
        
        if user_info:
            return {
                "logged_in": True,
                "user": {
                    "nickname": user_info.get("nickname", ""),
                    "user_id": user_info.get("userId", ""),
                    "avatar": user_info.get("avatarThumb", {}).get("urlList", [""])[0]
                }
            }
        
        # 尝试从 DOM 获取
        avatar = cdp.get_attribute(SELECTORS["login"]["user_avatar"], "src")
        name = cdp.get_text(SELECTORS["login"]["user_name"])
        
        if avatar or name:
            return {
                "logged_in": True,
                "user": {
                    "nickname": name or "未知用户",
                    "user_id": "",
                    "avatar": avatar or ""
                }
            }
    except Exception:
        pass
    
    return {"logged_in": False, "user": None}


def login_qrcode(cdp: CDPClient, account: str = "default", timeout: int = 120) -> dict:
    """
    扫码登录。
    
    Args:
        cdp: CDP 客户端
        account: 账号名称（用于保存 Cookie）
        timeout: 超时时间（秒）
    
    Returns:
        登录结果
    """
    # 导航到首页
    cdp.navigate(URLS["home"])
    time.sleep(2)
    
    # 检查是否已登录
    login_status = check_login(cdp)
    if login_status["logged_in"]:
        return {
            "success": True,
            "message": "Already logged in",
            "user": login_status["user"]
        }
    
    # 等待二维码出现
    qrcode_selector = SELECTORS["login"]["qrcode"]
    if not cdp.wait_for_selector(qrcode_selector, timeout=10000):
        # 可能需要点击登录按钮
        return {
            "success": False,
            "message": "QR code not found. Please open login dialog manually."
        }
    
    # 获取二维码图片
    qrcode_url = cdp.get_attribute(qrcode_selector, "src")
    print(f"[login] QR code URL: {qrcode_url}")
    print("[login] Please scan the QR code with Douyin app...")
    
    # 等待用户扫码
    start_time = time.time()
    while time.time() - start_time < timeout:
        login_status = check_login(cdp)
        if login_status["logged_in"]:
            # 保存 Cookie
            save_cookies(cdp, account)
            return {
                "success": True,
                "message": "Login successful",
                "user": login_status["user"]
            }
        time.sleep(2)
    
    return {
        "success": False,
        "message": f"Login timeout ({timeout}s)"
    }


def save_cookies(cdp: CDPClient, account: str = "default") -> bool:
    """保存 Cookie"""
    try:
        cookies = cdp.send("Network.getAllCookies").get("cookies", [])
        cookie_path = get_cookie_path(account)
        with open(cookie_path, "w") as f:
            json.dump(cookies, f)
        print(f"[login] Cookies saved to {cookie_path}")
        return True
    except Exception as e:
        print(f"[login] Failed to save cookies: {e}")
        return False


def load_cookies(cdp: CDPClient, account: str = "default") -> bool:
    """加载 Cookie"""
    cookie_path = get_cookie_path(account)
    if not cookie_path.exists():
        return False
    
    try:
        with open(cookie_path, "r") as f:
            cookies = json.load(f)
        
        for cookie in cookies:
            cdp.send("Network.setCookie", {
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie.get("domain", ".douyin.com"),
                "path": cookie.get("path", "/"),
                "secure": cookie.get("secure", False),
                "httpOnly": cookie.get("httpOnly", False),
            })
        print(f"[login] Cookies loaded from {cookie_path}")
        return True
    except Exception as e:
        print(f"[login] Failed to load cookies: {e}")
        return False


def delete_cookies(account: str = "default") -> bool:
    """删除 Cookie（退出登录）"""
    cookie_path = get_cookie_path(account)
    if cookie_path.exists():
        cookie_path.unlink()
        print(f"[login] Cookies deleted for account: {account}")
    return True