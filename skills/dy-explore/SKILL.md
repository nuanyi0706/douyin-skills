---
name: dy-explore
description: |
  抖音内容发现。支持关键词搜索、视频详情、用户主页、推荐流。
  
  触发场景：搜索抖音、抖音搜索、查看抖音视频、抖音推荐、发现抖音内容。
  
  使用此技能当用户需要：搜索抖音视频、查看视频详情、浏览用户主页、获取推荐内容。
---

# 抖音内容发现

## 功能

- 关键词搜索视频
- 获取视频详情
- 查看用户主页
- 获取推荐流
- 筛选排序

## CLI 命令

```bash
# 搜索视频
python scripts/cli.py search-videos --keyword "关键词"

# 带筛选条件搜索
python scripts/cli.py search-videos \
  --keyword "美食" \
  --sort-by "最多点赞" \
  --publish-time "一周内"

# 获取视频详情
python scripts/cli.py get-video-detail --video-id VIDEO_ID

# 获取用户主页
python scripts/cli.py user-profile --user-id USER_ID

# 获取推荐流
python scripts/cli.py list-feeds
```

## 搜索参数

| 参数 | 说明 | 可选值 |
|------|------|--------|
| --keyword | 搜索关键词 | - |
| --sort-by | 排序方式 | 综合、最新发布、最多点赞、最多评论 |
| --publish-time | 发布时间 | 不限、一天内、一周内、半年内 |
| --video-type | 视频类型 | 不限、视频、图文 |

## 返回格式

### 搜索结果

```json
{
  "keyword": "美食",
  "count": 20,
  "videos": [
    {
      "video_id": "7xxxxxxxxxxxxxxx",
      "title": "视频标题",
      "author": {
        "nickname": "作者昵称",
        "user_id": "用户ID"
      },
      "stats": {
        "likes": 10000,
        "comments": 500,
        "shares": 200,
        "plays": 500000
      },
      "cover": "封面URL",
      "publish_time": "2024-01-01"
    }
  ]
}
```

### 视频详情

```json
{
  "video_id": "7xxxxxxxxxxxxxxx",
  "title": "视频标题",
  "description": "视频描述",
  "author": {
    "nickname": "作者昵称",
    "user_id": "用户ID",
    "avatar": "头像URL",
    "followers": 100000
  },
  "stats": {
    "likes": 10000,
    "comments": 500,
    "shares": 200,
    "collects": 300,
    "plays": 500000
  },
  "video_url": "视频URL",
  "publish_time": "2024-01-01",
  "tags": ["美食", "教程"]
}
```

## 相关文件

- `scripts/douyin/search.py` - 搜索逻辑
- `scripts/douyin/feeds.py` - Feed 流
- `scripts/douyin/feed_detail.py` - 视频详情