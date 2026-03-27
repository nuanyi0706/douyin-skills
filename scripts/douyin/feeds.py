"""
抖音首页 Feed 流模块。

支持获取推荐视频、用户主页视频等。
"""

import time
from typing import Optional

from .cdp import CDPClient
from .selectors import SELECTORS, get_video_list_script


def get_feed_videos(cdp: CDPClient, limit: int = 20) -> dict:
    """
    获取首页推荐视频列表。
    
    Args:
        cdp: CDP 客户端
        limit: 返回数量
    
    Returns:
        {
            "success": bool,
            "count": int,
            "videos": [...]
        }
    """
    # 确保在首页
    cdp.navigate("https://www.douyin.com")
    time.sleep(3)
    
    # 等待视频卡片加载
    video_selector = SELECTORS["home"]["video_card"]
    if not cdp.wait_for_selector(video_selector, timeout=10000):
        return {"success": False, "videos": [], "error": "No videos found", "count": 0}
    
    # 滚动加载更多视频
    for _ in range(min(limit // 10, 3)):
        cdp.evaluate("window.scrollBy(0, 800)")
        time.sleep(0.5)
    
    # 使用优化的提取脚本
    script = get_video_list_script(limit)
    videos = cdp.evaluate(script)
    
    # 过滤无效项
    videos = [v for v in (videos or []) if v.get('video_id')]
    
    return {
        "success": True,
        "count": len(videos),
        "videos": videos
    }


def get_video_detail(cdp: CDPClient, video_id: str) -> dict:
    """
    获取视频详情。
    
    Args:
        cdp: CDP 客户端
        video_id: 视频 ID
    
    Returns:
        视频详情
    """
    # 导航到视频页面
    video_url = f"https://www.douyin.com/video/{video_id}"
    cdp.navigate(video_url)
    time.sleep(3)
    
    # 从页面提取视频详情
    detail = cdp.evaluate('''
    (function() {
        const result = {
            video_id: window.location.pathname.match(/video\\/(\\d+)/)?.[1] || '',
            url: window.location.href,
            title: '',
            author: {
                nickname: '',
                user_id: ''
            },
            stats: {
                likes: 0,
                comments: 0,
                shares: 0,
                collects: 0
            }
        };
        
        // 尝试从页面数据提取
        try {
            const initialState = window.__INITIAL_STATE__;
            if (initialState && initialState.aweme) {
                const aweme = initialState.aweme.detail || initialState.aweme;
                result.title = aweme.desc || '';
                result.author.nickname = aweme.author?.nickname || '';
                result.author.user_id = aweme.author?.uid || '';
                result.stats.likes = aweme.statistics?.digg_count || 0;
                result.stats.comments = aweme.statistics?.comment_count || 0;
                result.stats.shares = aweme.statistics?.share_count || 0;
                result.stats.collects = aweme.statistics?.collect_count || 0;
            }
        } catch(e) {}
        
        // 从 DOM 提取
        if (!result.title) {
            result.title = document.querySelector('[class*="desc"], [class*="title"]')?.textContent?.trim() || '';
        }
        if (!result.author.nickname) {
            result.author.nickname = document.querySelector('[class*="author"], [class*="name"]')?.textContent?.trim() || '';
        }
        
        return result;
    })()
    ''')
    
    return detail or {"video_id": video_id, "error": "Failed to get detail"}


def get_user_videos(cdp: CDPClient, user_id: str, limit: int = 20) -> dict:
    """
    获取用户主页视频列表。
    
    Args:
        cdp: CDP 客户端
        user_id: 用户 ID
        limit: 返回数量
    
    Returns:
        视频列表
    """
    # 导航到用户主页
    user_url = f"https://www.douyin.com/user/{user_id}"
    cdp.navigate(user_url)
    time.sleep(3)
    
    # 等待视频加载
    video_selector = SELECTORS["home"]["video_card"]
    if not cdp.wait_for_selector(video_selector, timeout=10000):
        return {"success": False, "videos": [], "error": "No videos found", "count": 0}
    
    # 滚动加载更多
    for _ in range(min(limit // 10, 3)):
        cdp.evaluate("window.scrollBy(0, 800)")
        time.sleep(0.8)
    
    # 提取视频数据
    script = get_video_list_script(limit)
    videos = cdp.evaluate(script)
    videos = [v for v in (videos or []) if v.get('video_id')]
    
    return {
        "success": True,
        "user_id": user_id,
        "count": len(videos),
        "videos": videos
    }


def get_user_profile(cdp: CDPClient, user_id: str) -> dict:
    """
    获取用户主页信息。
    
    Args:
        cdp: CDP 客户端
        user_id: 用户 ID
    
    Returns:
        用户信息
    """
    user_url = f"https://www.douyin.com/user/{user_id}"
    cdp.navigate(user_url)
    time.sleep(3)
    
    # 提取用户信息
    user_info = cdp.evaluate('''
    (function() {
        const info = {
            user_id: window.location.pathname.match(/user\\/(.+)/)?.[1] || '',
            nickname: '',
            signature: '',
            avatar: '',
            stats: {
                following: '0',
                followers: '0',
                likes: '0',
                videos: '0'
            }
        };
        
        // 尝试从页面数据提取
        try {
            const initialState = window.__INITIAL_STATE__;
            if (initialState && initialState.user) {
                const user = initialState.user;
                info.nickname = user.nickname || '';
                info.signature = user.signature || '';
                info.avatar = user.avatarThumb?.urlList?.[0] || '';
            }
        } catch(e) {}
        
        // 从 DOM 提取
        if (!info.nickname) {
            info.nickname = document.querySelector('[class*="nickname"], [class*="name"]')?.textContent?.trim() || '';
        }
        if (!info.signature) {
            info.signature = document.querySelector('[class*="signature"], [class*="desc"]')?.textContent?.trim() || '';
        }
        if (!info.avatar) {
            info.avatar = document.querySelector('img[class*="avatar"]')?.src || '';
        }
        
        // 提取统计数据
        const statsEls = document.querySelectorAll('[class*="count"], [class*="num"]');
        statsEls.forEach(el => {
            const text = el.textContent?.trim();
            const label = el.parentElement?.textContent || '';
            if (label.includes('关注')) info.stats.following = text;
            if (label.includes('粉丝')) info.stats.followers = text;
            if (label.includes('获赞')) info.stats.likes = text;
        });
        
        return info;
    })()
    ''')
    
    return user_info or {"user_id": user_id, "error": "Failed to get user info"}


def scroll_feed(cdp: CDPClient, distance: int = 500) -> dict:
    """
    滚动 Feed 流。
    
    Args:
        cdp: CDP 客户端
        distance: 滚动距离
    
    Returns:
        操作结果
    """
    cdp.evaluate(f"window.scrollBy(0, {distance})")
    time.sleep(0.5)
    
    return {"success": True, "action": "scrolled"}