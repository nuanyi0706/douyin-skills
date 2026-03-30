---
name: douyin-skills
description: |
  抖音一站式运营助手。基于 Python CDP 浏览器自动化引擎。
  
  核心能力：账号认证、内容发布、视频上传、搜索发现、评论互动、数据分析、AI短漫剧生成。
  
  触发场景：发布抖音、抖音视频、抖音运营、抖音搜索、回复评论、生成抖音内容、抖音账号管理、AI短漫剧生成、小说转视频。
  
  使用此技能当用户需要：运营抖音账号、发布视频到抖音、搜索抖音内容、回复抖音评论、分析抖音数据、做抖音账号定位、生成AI短漫剧。

metadata:
  trigger: 抖音运营、发布内容、视频上传、评论互动、搜索发现、AI短漫剧、小说转视频
  source: autoclaw-cc/xiaohongshu-skills (参考架构)
---

# 抖音一站式运营 Skills

基于 Python CDP 浏览器自动化引擎，支持 OpenClaw 及所有兼容 SKILL.md 格式的 AI Agent 平台。

## 核心能力

| 技能 | 说明 |
|------|------|
| dy-auth | 认证管理：登录检查、扫码登录、多账号切换 |
| dy-publish | 内容发布：视频发布、图文发布、定时发布 |
| dy-explore | 内容发现：关键词搜索、视频详情、用户主页、推荐流 |
| dy-interact | 社交互动：评论、回复、点赞、收藏、关注 |
| manjv | AI短漫剧：LumenX架构、剧本分析、资产生成、分镜绘制、视频合成 |

## 支持连贯操作

可以用自然语言下达复合指令，Agent 会自动串联多个技能完成任务。

**示例：**
- "搜索美食博主最近的热门视频，点赞并评论"
- "查看这个视频的详情，分析它的数据表现"
- "帮我发布一条视频，标题是…"
- "分析这个小说片段，生成一个AI短漫剧"

---

## 环境要求

- Python >= 3.11
- uv 包管理器
- Google Chrome 浏览器

## 安装

```bash
cd ~/.openclaw/workspace/skills/douyin-skills
uv sync
```

---

## 使用方式

### 自然语言调用

安装后直接用自然语言与 Agent 对话：

**认证登录：**
- "登录抖音" / "检查抖音登录状态"

**搜索浏览：**
- "搜索关于美食的视频" / "查看这个视频的详情"

**发布内容：**
- "帮我发布一条视频，标题是…，视频文件是…"

**社交互动：**
- "给这个视频点赞" / "收藏这个视频" / "评论：拍得太好了"

**AI短漫剧：**
- "分析这个小说片段"
- "生成角色三视图：古风少女"
- "生成9宫格分镜"
- "拼接所有视频片段"

---

## CLI 命令参考

```bash
cd ~/.openclaw/workspace/skills/douyin-skills

# ========== 抖音浏览器自动化 ==========

# 启动浏览器
python scripts/chrome_launcher.py

# 检查登录状态
python scripts/cli.py check-login

# 扫码登录
python scripts/cli.py login

# 搜索视频
python scripts/cli.py search-videos --keyword "关键词"

# 获取视频详情
python scripts/cli.py get-video-detail --video-id VIDEO_ID

# 发布视频
python scripts/cli.py publish-video \
  --title-file title.txt \
  --video /path/to/video.mp4

# 评论
python scripts/cli.py post-comment \
  --video-id VIDEO_ID \
  --content "评论内容"

# 点赞
python scripts/cli.py like-video --video-id VIDEO_ID

# ========== manjv AI短漫剧 ==========

cd skills/manjv

# 设置 API Key
export KIE_API_KEY="your-api-key"

# 剧本分析
python3 main.py analyze --script "小说文本..."

# 资产生成
python3 scripts/workflow.py generate-asset \
  --type character-tri-view \
  --description "古风少女" \
  --resolution 2K

# 分镜生成
python3 scripts/workflow.py generate-storyboard \
  --type 9grid \
  --content "分镜描述..." \
  --resolution 4K

# 视频生成
python3 scripts/workflow.py generate-video \
  --mode i2v \
  --images frame1.png frame2.png \
  --prompt "镜头推进"

# 视频装配
python3 scripts/workflow.py assemble \
  --clips video1.mp4 video2.mp4 \
  --output final_drama.mp4
```

---

## 子技能路由

根据用户意图自动路由到对应子技能：

1. **认证相关** → dy-auth
2. **发布相关** → dy-publish  
3. **搜索/发现** → dy-explore
4. **互动相关** → dy-interact
5. **AI短漫剧** → manjv

---

## 项目结构

```
douyin-skills/
├── SKILL.md                    # 技能入口
├── README.md                   # 项目说明
├── pyproject.toml              # Python 项目配置
├── uv.lock                     # 依赖锁定
├── scripts/                   # Python 自动化引擎
│   ├── douyin/                # 核心模块
│   │   ├── cdp.py             # CDP 客户端
│   │   ├── selectors.py       # CSS 选择器
│   │   ├── login.py           # 登录模块
│   │   ├── feeds.py           # Feed 流
│   │   ├── search.py          # 搜索模块
│   │   ├── publish.py         # 发布模块
│   │   └── interact.py         # 互动模块
│   ├── cli.py                 # CLI 入口
│   └── chrome_launcher.py     # 浏览器启动
└── skills/                    # 子技能目录
    ├── dy-auth/               # 认证管理
    ├── dy-publish/             # 内容发布
    ├── dy-explore/             # 内容发现
    ├── dy-interact/           # 社交互动
    └── manjv/                 # AI短漫剧生成
        ├── SKILL.md
        ├── main.py
        ├── requirements.txt
        ├── scripts/
        │   ├── nanobanana_api.py    # Nano Banana 2 API
        │   ├── grok_api.py          # Grok Imagine API
        │   ├── video_assembler.py   # ffmpeg 装配
        │   └── workflow.py          # 工作流
        └── references/
            ├── script-analysis-workflow.md   # 剧本分析
            ├── art-direction-workflow.md     # 风格定调
            ├── assets-generation-workflow.md # 资产生成
            ├── storyboard-workflow.md       # 分镜绘制
            ├── motion-workflow.md          # 视频合成
            └── assembly-workflow.md         # 成片装配
```

---

## 抖音网址

- 主站：https://www.douyin.com
- 创作者中心：https://creator.douyin.com
- 创作者中心发布页：https://creator.douyin.com/creator-micro/content/publish

---

## 更新日志

### v2.0.0
- 新增 **manjv** AI短漫剧生成模块
- 基于 LumenX Studio 架构设计
- 整合 Nano Banana 2 + Grok 实现完整创作链路
- 移除 dy-moviegen（已迁移到 manjv）

### v1.x
- 基础抖音运营功能
- 账号认证、内容发布、搜索发现、社交互动

---

#抖音 #运营 #发布 #视频 #互动 #AI短漫剧 #LumenX #manjv
