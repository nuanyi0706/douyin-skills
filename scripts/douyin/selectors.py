"""
抖音页面 CSS 选择器。

基于抖音网页版实际结构更新（2026-03-08 测试）。
抖音使用混淆类名，优先使用数据属性和语义选择器。
"""

SELECTORS = {
    # =====================
    # 首页 - 视频卡片
    # =====================
    "home": {
        # 视频卡片容器
        "video_card": "[data-aweme-id], [class*='discover-video-card']",
        "video_card_item": ".discover-video-card-item",
        
        # 视频ID（数据属性）
        "video_id": "[data-aweme-id]",
        
        # 封面图
        "cover_image": "img",
        
        # 视频标题/描述（从文本中提取）
        "video_desc": "[class*='video-title'], [class*='desc']",
        
        # 作者信息（格式: @用户名 · 日期）
        "author_section": "[class*='author'], [class*='userInfo']",
        
        # 点赞数（从文本提取）
        "likes_text": "[class*='like'], [class*='digg']",
        
        # 视频链接
        "video_link": "a[href*='/video/']",
    },
    
    # =====================
    # 搜索页
    # =====================
    "search": {
        # 搜索结果卡片
        "search_card": ".search-result-card",
        "search_card_item": "[class*='search-result-card']",
        
        # 视频信息
        "video_cover": "[class*='videoImage'] img",
        "video_duration": "[class*='videoImage']",
    },
    
    # =====================
    # 登录相关
    # =====================
    "login": {
        # 登录按钮/区域
        "login_button": "[class*='login'], .douyin_login_new_class",
        
        # 已登录：用户头像区域
        "user_avatar": "[class*='tab-user'], [class*='avatar']",
        "user_avatar_img": "img[class*='Avatar']",
        
        # 二维码登录
        "qrcode": "[class*='qrcode'] img",
        "qrcode_container": "[class*='qrcode-container']",
    },
    
    # =====================
    # 视频详情页
    # =====================
    "video": {
        # 视频播放器
        "video_player": "video",
        
        # 视频信息
        "video_info": "[class*='video-info']",
        "video_desc": "[class*='desc'], [class*='title']",
        
        # 作者
        "author_name": "[class*='author'], [class*='name']",
        "author_avatar": "img[class*='avatar']",
        
        # 互动按钮
        "like_button": "[class*='like'], button[aria-label*='赞']",
        "comment_button": "[class*='comment'], button[aria-label*='评论']",
        "collect_button": "[class*='collect'], button[aria-label*='收藏']",
        "share_button": "[class*='share'], button[aria-label*='分享']",
    },
    
    # =====================
    # 评论
    # =====================
    "comment": {
        "comment_panel": "[class*='comment-panel']",
        "comment_input": "textarea",
        "comment_submit": "button[type='submit'], [class*='submit']",
        "comment_list": "[class*='comment-list']",
        "comment_item": "[class*='comment-item']",
    },
    
    # =====================
    # 创作者中心 - 发布
    # =====================
    "publish": {
        "upload_area": "[class*='upload'], input[type='file']",
        "upload_input": "input[type='file']",
        "title_input": "textarea[class*='title']",
        "desc_input": "textarea[class*='desc']",
        "publish_button": "[class*='publish'], [class*='submit']",
    },
    
    # =====================
    # 用户主页
    # =====================
    "user": {
        "user_info": "[class*='user-info'], [class*='profile']",
        "user_name": "[class*='nickname'], [class*='name']",
        "user_stats": "[class*='stats'], [class*='count']",
        "video_list": "[data-aweme-id]",
    },
}


def get_video_list_script(limit: int = 20) -> str:
    """获取首页视频列表的 JavaScript 脚本"""
    return f'''
    (function() {{
        const videos = [];
        const cards = document.querySelectorAll('[data-aweme-id]');
        
        cards.forEach((card, index) => {{
            if (index >= {limit}) return;
            
            const videoId = card.getAttribute('data-aweme-id');
            const imgEl = card.querySelector('img');
            const cover = imgEl ? imgEl.src : '';
            
            // 从文本提取作者名
            let author = '';
            const text = card.textContent;
            const match = text.match(/@(.+?)\\s*·/);
            if (match) author = match[1].trim();
            
            // 提取点赞数
            let likes = '0';
            const numbers = text.match(/(\\d+\\.?\\d*[万]?)\\s*$/g);
            if (numbers && numbers.length > 0) {{
                likes = numbers[0].trim();
            }}
            
            videos.push({{
                video_id: videoId,
                author: author,
                likes: likes,
                cover: cover
            }});
        }});
        
        return videos;
    }})()
    '''


def get_search_results_script(limit: int = 20) -> str:
    """获取搜索结果视频列表的 JavaScript 脚本"""
    return f'''
    (function() {{
        const videos = [];
        const cards = document.querySelectorAll('.search-result-card');
        
        cards.forEach((card, index) => {{
            if (index >= {limit}) return;
            
            // 提取视频链接和ID
            const linkEl = card.querySelector('a[href*="/video/"]');
            const videoUrl = linkEl ? linkEl.href : '';
            const videoIdMatch = videoUrl.match(/video\\/(\\d+)/);
            const videoId = videoIdMatch ? videoIdMatch[1] : '';
            
            // 提取封面图
            const imgEl = card.querySelector('img');
            const cover = imgEl ? imgEl.src : '';
            
            // 提取文本内容
            const text = card.textContent || '';
            
            // 提取时长和播放量
            const statsMatch = text.match(/(\\d+:\\d+)(\\d+\\.?\\d*[万]?)/);
            let duration = '';
            let plays = '0';
            if (statsMatch) {{
                duration = statsMatch[1];
                plays = statsMatch[2];
            }}
            
            // 提取描述
            const desc = text.replace(/\\d+:\\d+/g, '').replace(/\\d+\\.?\\d*[万]?/g, '').trim().substring(0, 100);
            
            // 提取作者名
            const authorMatch = text.match(/@(.+?)\\s/);
            const author = authorMatch ? authorMatch[1].trim() : '';
            
            videos.push({{
                video_id: videoId,
                video_url: videoUrl,
                author: author,
                plays: plays,
                duration: duration,
                title: desc,
                cover: cover
            }});
        }});
        
        return videos;
    }})()
    '''