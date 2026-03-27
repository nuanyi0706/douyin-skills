"""
抖音 CDP 自动化核心模块。

基于 Chrome DevTools Protocol 控制浏览器进行自动化操作。
"""

from .cdp import CDPClient, CDPError
from .selectors import SELECTORS
from .login import check_login, login_qrcode
from .search import search_videos, get_video_detail
from .feeds import get_feed_videos, get_user_profile, get_user_videos
from .interact import (
    get_current_video_info, like_current_video, collect_current_video,
    open_comments, post_comment, follow_current_author, next_video, previous_video
)
from .urls import URLS

__all__ = [
    "CDPClient",
    "CDPError",
    "SELECTORS",
    "URLS",
    "check_login",
    "login_qrcode",
    "search_videos",
    "get_video_detail",
    "get_feed_videos",
    "get_user_profile",
    "get_user_videos",
    "get_current_video_info",
    "like_current_video",
    "collect_current_video",
    "open_comments",
    "post_comment",
    "follow_current_author",
    "next_video",
    "previous_video",
]