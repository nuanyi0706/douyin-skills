"""
抖音搜索模块。

支持关键词搜索视频、筛选排序。
"""

import time
import urllib.parse

from .cdp import CDPClient
from .selectors import SELECTORS


def search_videos(
    cdp: CDPClient,
    keyword: str,
    sort_by: str = "综合",
    publish_time: str = "不限",
    video_type: str = "不限",
    limit: int = 20
) -> dict:
    """
    搜索视频。
    
    Args:
        cdp: CDP 客户端
        keyword: 搜索关键词
        sort_by: 排序方式
        publish_time: 发布时间
        video_type: 视频类型
        limit: 返回数量
    
    Returns:
        {
            "keyword": str,
            "count": int,
            "videos": [...]
        }
    """
    # 构建搜索 URL
    encoded_keyword = urllib.parse.quote(keyword)
    search_url = f"https://www.douyin.com/search/{encoded_keyword}"
    
    # 导航到搜索页
    cdp.navigate(search_url)
    time.sleep(4)
    
    # 等待搜索结果加载
    search_selector = SELECTORS["search"]["search_card"]
    if not cdp.wait_for_selector(search_selector, timeout=10000):
        return {"keyword": keyword, "count": 0, "videos": []}
    
    # 从搜索卡片提取信息
    videos = cdp.evaluate(f'''
    (function() {{
        const videos = [];
        const cards = document.querySelectorAll('.search-result-card');
        
        cards.forEach((card, index) => {{
            if (index >= {limit}) return;
            
            // 获取封面图
            const img = card.querySelector('img');
            const cover = img ? img.src : '';
            
            // 获取文本内容
            const text = card.textContent || '';
            
            // 跳过非视频卡片（如"相关搜索"）
            if (text.includes('相关搜索') || !cover) return;
            
            // 解析格式: "02:0910.8万描述内容@作者 · 时间"
            
            // 1. 时长: 开头的 MM:SS 格式
            const durationMatch = text.match(/^(\\d{{1,2}}:\\d{{2}})/);
            const duration = durationMatch ? durationMatch[1] : '';
            
            // 2. 播放量: 时长后面到第一个非数字字符
            let plays = '';
            if (duration) {{
                const afterDuration = text.substring(duration.length);
                const playsMatch = afterDuration.match(/^(\\d+\\.?\\d*[万亿]?)/);
                if (playsMatch) plays = playsMatch[1];
            }}
            
            // 3. 作者: @后面的文字，到 · 为止
            const authorMatch = text.match(/@(.+?)\\s*·/);
            const author = authorMatch ? authorMatch[1].trim() : '';
            
            // 4. 发布时间: · 后面的文字
            const timeMatch = text.match(/·\\s*(.+?)\\s*$/);
            const publishTime = timeMatch ? timeMatch[1].trim() : '';
            
            // 5. 描述: 去掉时长、播放量、作者、时间后的文本
            let desc = text;
            if (duration) desc = desc.replace(duration, '');
            if (plays) {{
                // 转义特殊字符
                const escapedPlays = plays.replace(/\\./g, '\\\\.').replace(/万/g, '\\\\万').replace(/亿/g, '\\\\亿');
                desc = desc.replace(new RegExp('^' + escapedPlays), '');
            }}
            if (author) desc = desc.replace('@' + author, '');
            if (publishTime) desc = desc.replace('· ' + publishTime, '');
            desc = desc.replace(/^[\\s#]+/, '').trim();
            
            videos.push({{
                video_id: '', // 搜索页无直接视频ID
                author: author,
                plays: plays,
                duration: duration,
                publish_time: publishTime,
                title: desc.substring(0, 80),
                cover: cover
            }});
        }});
        
        return videos;
    }})()
    ''')
    
    return {
        "keyword": keyword,
        "count": len(videos) if videos else 0,
        "videos": videos or []
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
    video_url = f"https://www.douyin.com/video/{video_id}"
    cdp.navigate(video_url)
    time.sleep(3)
    
    try:
        detail = cdp.evaluate('''
        (function() {
            const result = {
                video_id: window.location.pathname.match(/video\\/(\\d+)/)?.[1] || '',
                url: window.location.href,
                title: '',
                description: '',
                author: {
                    nickname: '',
                    user_id: ''
                },
                stats: {
                    likes: 0,
                    comments: 0,
                    shares: 0,
                    collects: 0,
                    plays: 0
                }
            };
            
            // 从 __INITIAL_STATE__ 提取
            try {
                const state = window.__INITIAL_STATE__;
                if (state) {
                    const aweme = state.aweme?.detail || state.videoDetail || {};
                    result.title = aweme.desc || '';
                    result.description = aweme.desc || '';
                    result.author.nickname = aweme.author?.nickname || '';
                    result.author.user_id = aweme.author?.uid || '';
                    
                    const stats = aweme.statistics || {};
                    result.stats.likes = stats.digg_count || 0;
                    result.stats.comments = stats.comment_count || 0;
                    result.stats.shares = stats.share_count || 0;
                    result.stats.collects = stats.collect_count || 0;
                    result.stats.plays = stats.play_count || 0;
                }
            } catch(e) {}
            
            // 从 DOM 提取
            if (!result.title) {
                result.title = document.querySelector('[class*="desc"], [class*="title"]')?.textContent?.trim() || '';
            }
            if (!result.author.nickname) {
                const text = document.body.textContent;
                const match = text.match(/@(.+?)\\s/);
                if (match) result.author.nickname = match[1];
            }
            
            return result;
        })()
        ''')
        
        return detail or {"video_id": video_id, "error": "Failed to extract detail"}
        
    except Exception as e:
        return {"video_id": video_id, "error": str(e)}