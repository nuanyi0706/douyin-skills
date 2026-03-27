---
name: dy-interact
description: |
  抖音社交互动。支持评论、回复、点赞、收藏、关注。
  
  触发场景：抖音评论、点赞抖音、收藏抖音视频、回复抖音评论、关注抖音用户。
  
  使用此技能当用户需要：发表评论、回复评论、点赞视频、收藏视频、关注用户、查看通知。
---

# 抖音社交互动

## 功能

- 发表评论
- 回复评论
- 点赞/取消点赞
- 收藏/取消收藏
- 关注/取消关注
- 查看通知

## CLI 命令

```bash
# 发表评论
python scripts/cli.py post-comment \
  --video-id VIDEO_ID \
  --content "评论内容"

# 回复评论
python scripts/cli.py reply-comment \
  --video-id VIDEO_ID \
  --comment-id COMMENT_ID \
  --content "回复内容"

# 点赞视频
python scripts/cli.py like-video --video-id VIDEO_ID

# 取消点赞
python scripts/cli.py unlike-video --video-id VIDEO_ID

# 收藏视频
python scripts/cli.py favorite-video --video-id VIDEO_ID

# 取消收藏
python scripts/cli.py unfavorite-video --video-id VIDEO_ID

# 关注用户
python scripts/cli.py follow-user --user-id USER_ID

# 取消关注
python scripts/cli.py unfollow-user --user-id USER_ID

# 查看通知
python scripts/cli.py get-notifications
```

## 评论规范

- 字数限制：150字以内
- 禁止敏感词
- 禁止广告链接
- 推荐使用互动性强的评论

## 返回格式

```json
{
  "success": true,
  "action": "comment",
  "video_id": "7xxxxxxxxxxxxxxx",
  "comment_id": "评论ID",
  "content": "评论内容",
  "create_time": "2024-01-01 12:00:00"
}
```

## 注意事项

- 评论频率限制：每小时最多 20 条
- 点赞频率限制：每小时最多 100 次
- 关注频率限制：每天最多 200 人
- 建议使用随机延迟模拟人类行为

## 相关文件

- `scripts/douyin/comment.py` - 评论逻辑
- `scripts/douyin/like_favorite.py` - 点赞收藏
- `scripts/douyin/follow.py` - 关注逻辑