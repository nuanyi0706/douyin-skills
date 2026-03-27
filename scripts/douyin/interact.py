"""
抖音社交互动模块。

支持评论、回复、点赞、收藏、关注。
"""

import time
import random
from typing import Optional

from .cdp import CDPClient
from .selectors import SELECTORS


def get_current_video_info(cdp: CDPClient) -> dict:
    """
    获取当前播放视频的信息。
    
    Args:
        cdp: CDP 客户端
    
    Returns:
        视频信息
    """
    info = cdp.evaluate('''
    (function() {
        const result = {
            video_id: '',
            title: '',
            author: '',
            stats: {}
        };
        
        // 从 URL 提取视频 ID
        const urlMatch = window.location.href.match(/video\\/(\\d+)/);
        if (urlMatch) result.video_id = urlMatch[1];
        
        // 提取统计数据（从侧边栏按钮附近）
        const statElements = document.querySelectorAll('[class*="count"], [class*="num"]');
        const numbers = [];
        statElements.forEach(el => {
            const text = el.textContent?.trim();
            if (text && /^[\\d.]+[万亿]?$/.test(text)) {
                numbers.push(text);
            }
        });
        
        // 通常顺序：点赞、评论、收藏、分享
        if (numbers.length >= 3) {
            result.stats.likes = numbers[0];
            result.stats.comments = numbers[1];
            result.stats.collects = numbers[2];
        }
        
        // 提取作者名
        const authorMatch = document.body.textContent.match(/@(.+?)\\s/);
        if (authorMatch) result.author = authorMatch[1];
        
        return result;
    })()
    ''')
    
    return info or {}


def like_current_video(cdp: CDPClient) -> dict:
    """
    点赞当前视频。
    
    Args:
        cdp: CDP 客户端
    
    Returns:
        操作结果
    """
    # 查找点赞按钮（通常是第一个互动按钮）
    result = cdp.evaluate('''
    (function() {
        // 查找右侧工具栏的按钮
        const controlsRight = document.querySelector('.douyin-player-controls-right');
        if (!controlsRight) return { success: false, error: 'Controls not found' };
        
        // 查找所有按钮
        const buttons = controlsRight.querySelectorAll('button, [role="button"]');
        if (buttons.length === 0) return { success: false, error: 'No buttons found' };
        
        // 第一个按钮通常是点赞
        const likeButton = buttons[0];
        if (likeButton) {
            likeButton.click();
            return { success: true, action: 'liked' };
        }
        
        return { success: false, error: 'Like button not found' };
    })()
    ''')
    
    return result


def collect_current_video(cdp: CDPClient) -> dict:
    """
    收藏当前视频。
    
    Args:
        cdp: CDP 客户端
    
    Returns:
        操作结果
    """
    result = cdp.evaluate('''
    (function() {
        const controlsRight = document.querySelector('.douyin-player-controls-right');
        if (!controlsRight) return { success: false, error: 'Controls not found' };
        
        const buttons = controlsRight.querySelectorAll('button, [role="button"]');
        
        // 第三个按钮通常是收藏
        if (buttons.length >= 3) {
            const collectButton = buttons[2];
            if (collectButton) {
                collectButton.click();
                return { success: true, action: 'collected' };
            }
        }
        
        return { success: false, error: 'Collect button not found' };
    })()
    ''')
    
    return result


def share_current_video(cdp: CDPClient) -> dict:
    """
    分享当前视频。
    
    Args:
        cdp: CDP 客户端
    
    Returns:
        操作结果
    """
    result = cdp.evaluate('''
    (function() {
        const controlsRight = document.querySelector('.douyin-player-controls-right');
        if (!controlsRight) return { success: false, error: 'Controls not found' };
        
        const buttons = controlsRight.querySelectorAll('button, [role="button"]');
        
        // 第四个按钮通常是分享
        if (buttons.length >= 4) {
            const shareButton = buttons[3];
            if (shareButton) {
                shareButton.click();
                return { success: true, action: 'share_panel_opened' };
            }
        }
        
        return { success: false, error: 'Share button not found' };
    })()
    ''')
    
    return result


def open_comments(cdp: CDPClient) -> dict:
    """
    打开评论区。
    
    Args:
        cdp: CDP 客户端
    
    Returns:
        操作结果
    """
    result = cdp.evaluate('''
    (function() {
        const controlsRight = document.querySelector('.douyin-player-controls-right');
        if (!controlsRight) return { success: false, error: 'Controls not found' };
        
        const buttons = controlsRight.querySelectorAll('button, [role="button"]');
        
        // 第二个按钮通常是评论
        if (buttons.length >= 2) {
            const commentButton = buttons[1];
            if (commentButton) {
                commentButton.click();
                return { success: true, action: 'comments_opened' };
            }
        }
        
        return { success: false, error: 'Comment button not found' };
    })()
    ''')
    
    return result


def post_comment(cdp: CDPClient, content: str) -> dict:
    """
    发表评论。
    
    Args:
        cdp: CDP 客户端
        content: 评论内容
    
    Returns:
        操作结果
    """
    # 先打开评论区
    open_result = open_comments(cdp)
    if not open_result.get('success'):
        return open_result
    
    time.sleep(1)
    
    # 查找评论输入框
    result = cdp.evaluate(f'''
    (function() {{
        // 查找评论输入框
        const textarea = document.querySelector('textarea, [contenteditable="true"]');
        if (!textarea) return {{ success: false, error: 'Comment input not found' }};
        
        // 输入评论内容
        textarea.focus();
        textarea.value = '{content}';
        
        // 触发输入事件
        textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
        
        // 查找提交按钮
        const submitBtn = document.querySelector('button[type="submit"], [class*="submit"]');
        if (submitBtn) {{
            submitBtn.click();
            return {{ success: true, action: 'commented', content: '{content}' }};
        }}
        
        return {{ success: false, error: 'Submit button not found' }};
    }})()
    ''')
    
    return result


def follow_current_author(cdp: CDPClient) -> dict:
    """
    关注当前视频作者。
    
    Args:
        cdp: CDP 客户端
    
    Returns:
        操作结果
    """
    result = cdp.evaluate('''
    (function() {
        // 查找关注按钮
        const followBtn = document.querySelector('[class*="follow"], button[class*="follow"]');
        if (followBtn) {
            followBtn.click();
            return { success: true, action: 'followed' };
        }
        
        // 备用：查找作者区域的按钮
        const authorArea = document.querySelector('[class*="author"], [class*="user"]');
        if (authorArea) {
            const btn = authorArea.querySelector('button');
            if (btn && btn.textContent.includes('关注')) {
                btn.click();
                return { success: true, action: 'followed' };
            }
        }
        
        return { success: false, error: 'Follow button not found' };
    })()
    ''')
    
    return result


def next_video(cdp: CDPClient) -> dict:
    """
    切换到下一个视频。
    
    Args:
        cdp: CDP 客户端
    
    Returns:
        操作结果
    """
    # 模拟向下滚动或按向下键
    result = cdp.evaluate('''
    (function() {
        // 方法1：模拟按键
        const event = new KeyboardEvent('keydown', { key: 'ArrowDown', code: 'ArrowDown' });
        document.dispatchEvent(event);
        
        return { success: true, action: 'next_video' };
    })()
    ''')
    
    time.sleep(0.5)
    return result


def previous_video(cdp: CDPClient) -> dict:
    """
    切换到上一个视频。
    
    Args:
        cdp: CDP 客户端
    
    Returns:
        操作结果
    """
    result = cdp.evaluate('''
    (function() {
        const event = new KeyboardEvent('keydown', { key: 'ArrowUp', code: 'ArrowUp' });
        document.dispatchEvent(event);
        
        return { success: true, action: 'previous_video' };
    })()
    ''')
    
    time.sleep(0.5)
    return result