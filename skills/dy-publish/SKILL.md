---
name: dy-publish
description: |
  抖音内容发布。支持视频发布、图文发布、定时发布、分步预览。
  
  触发场景：发布抖音、发布视频、上传视频到抖音、抖音发布内容。
  
  使用此技能当用户需要：发布视频到抖音、发布图文内容、定时发布、预览发布内容。
---

# 抖音内容发布

## 功能

- 视频发布
- 图文发布
- 定时发布
- 分步预览（填写 → 预览 → 确认）

## CLI 命令

```bash
# 视频发布（一步完成）
python scripts/cli.py publish-video \
  --title "视频标题" \
  --video /path/to/video.mp4 \
  --content "视频描述"

# 分步发布（推荐）
# 步骤1：填写表单
python scripts/cli.py fill-publish \
  --title "标题" \
  --video /path/to/video.mp4 \
  --content "描述内容"

# 步骤2：用户预览后确认发布
python scripts/cli.py click-publish

# 或保存为草稿
python scripts/cli.py save-draft
```

## 发布参数

| 参数 | 说明 | 必需 |
|------|------|------|
| --title | 视频标题（最多55字） | 是 |
| --video | 视频文件路径 | 是 |
| --content | 视频描述 | 否 |
| --cover | 封面图路径 | 否 |
| --schedule | 定时发布时间 | 否 |
| --location | 添加位置 | 否 |
| --topics | 话题标签 | 否 |

## 发布流程

1. 检查登录状态
2. 导航到创作者中心发布页
3. 上传视频文件
4. 填写标题和描述
5. 选择封面
6. 添加话题/位置（可选）
7. 预览确认
8. 点击发布

## 标题规范

- 字数限制：55字以内
- 禁止敏感词
- 推荐使用疑问句、感叹句吸引注意

## 视频要求

- 格式：MP4、MOV
- 时长：15秒-10分钟
- 分辨率：建议 1080p
- 大小：最大 4GB

## 相关文件

- `scripts/douyin/publish.py` - 发布逻辑
- `scripts/douyin/selectors.py` - 发布页选择器