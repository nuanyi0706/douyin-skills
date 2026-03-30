# 抖音一站式运营 Skills

基于 Python CDP 浏览器自动化引擎 + AI 短漫剧生成，支持 OpenClaw 及所有兼容 SKILL.md 格式的 AI Agent 平台。

## 🎯 核心能力

| 技能 | 说明 | 状态 |
|------|------|------|
| **dy-auth** | 认证管理：登录检查、扫码登录、多账号切换 | ✅ |
| **dy-publish** | 内容发布：视频发布、图文发布、定时发布 | ✅ |
| **dy-explore** | 内容发现：关键词搜索、视频详情、用户主页、推荐流 | ✅ |
| **dy-interact** | 社交互动：点赞、收藏、评论、关注 | ✅ |
| **manjv** | **AI 短漫剧：LumenX架构、剧本分析、资产生成、分镜绘制、视频合成** ✨ | ✅ |

---

## 🛠️ 环境要求

- Python >= 3.11
- uv 包管理器（推荐）或 pip
- Google Chrome 浏览器
- ffmpeg（视频处理需要）

---

## 📦 安装

```bash
cd ~/.openclaw/workspace/skills/douyin-skills

# 安装主依赖
uv sync

# 安装 manjv 依赖（AI 短漫剧生成）
cd skills/manjv
pip install -r requirements.txt
```

---

## 💡 使用方式

### 自然语言调用（推荐）

直接与 Agent 对话即可：

**认证登录：**
- "登录抖音" / "检查抖音登录状态"

**搜索浏览：**
- "搜索关于美食的视频"
- "查看抖音首页推荐"

**社交互动：**
- "给这个视频点赞"
- "收藏这个视频"
- "评论：拍得太好了"

**内容发布：**
- "帮我发布一条视频，标题是…"

**AI 短漫剧生成：**
- "分析这个小说片段，提取角色和场景"
- "生成角色三视图：古风少女，白衣汉服"
- "生成场景鸟瞰图"
- "生成9宫格分镜"
- "将分镜图转换为视频"
- "拼接所有视频片段"

---

## 🎬 manjv - AI 短漫剧一站式生产平台

基于 LumenX Studio 架构设计，整合 **Nano Banana 2** (图像生成) + **Grok** (视频生成)，实现从小说文本到动态视频的完整创作链路。

### 完整创作链路

```
故事素材 → 剧本分析 → 实体提取 → 风格定调 → 资产生成 → 分镜绘制 → 视频合成 → 成片装配
```

### 六大核心模块

| 模块 | 功能 | 触发词 |
|------|------|--------|
| 剧本分析 | 提取角色、场景、道具、冲突点 | 分析剧本、拆解剧情 |
| 风格定调 | 定义视觉风格、统一画面标准 | 风格设定、视觉风格 |
| 资产生成 | 角色三视图、场景图、道具图 | 生成角色图、三视图 |
| 分镜绘制 | 9宫格/3宫格分镜故事板 | 生成分镜、9宫格 |
| 视频合成 | I2V/T2V 动态视频生成 | 生成视频、I2V |
| 成片装配 | ffmpeg 拼接最终短剧 | 拼接视频、导出 |

### 技术能力

| 功能 | 说明 |
|------|------|
| 👤 角色三视图 | 上半身/正面全身/背面全身 |
| 🏞️ 场景鸟瞰图 | 超远距离俯视视角 |
| 🌐 场景全景图 | 210度超广角 |
| 🎭 道具白底图 | 主体提取 |
| 📐 九宫格分镜 | 3x3 完整故事板 |
| 📊 三宫格分镜 | 3格精简版 |
| 🔍 图像放大 | 超高清 4K |
| 🎥 I2V 视频 | 图生视频 |
| 🎬 T2V 视频 | 文生视频 |
| ✂️ ffmpeg 装配 | 多段拼接 |

### 平台支持

| 平台 | 模式 | 用途 |
|------|------|------|
| **Nano Banana 2** | API 直连 | 图像生成（角色/场景/道具/分镜） |
| **Grok Imagine** | API 直连 | 视频生成（I2V/T2V） |
| **ffmpeg** | 本地 | 视频拼接与后期处理 |

### 快速开始

```bash
cd skills/manjv

# 设置 API Key
export KIE_API_KEY="your-api-key"

# 剧本分析
python3 main.py analyze --script "小说文本..."

# 资产生成 - 角色三视图
python3 scripts/workflow.py generate-asset \
  --type character-tri-view \
  --description "古风少女，身穿白色汉服" \
  --resolution 2K

# 资产生成 - 场景鸟瞰图
python3 scripts/workflow.py generate-asset \
  --type scene-bird-view \
  --image scene.png \
  --resolution 4K

# 分镜生成 - 9宫格
python3 scripts/workflow.py generate-storyboard \
  --type 9grid \
  --content "分镜内容描述..." \
  --resolution 4K

# 视频生成 - I2V
python3 scripts/workflow.py generate-video \
  --mode i2v \
  --images frame1.png frame2.png \
  --prompt "镜头推进，人物走向前方" \
  --duration 10

# 视频装配
python3 scripts/workflow.py assemble \
  --clips video1.mp4 video2.mp4 video3.mp4 \
  --output final_drama.mp4
```

### 工作流文档

| 文档 | 说明 |
|------|------|
| `script-analysis-workflow.md` | 剧本分析流程 |
| `art-direction-workflow.md` | 风格定调流程 |
| `assets-generation-workflow.md` | 资产生成流程 |
| `storyboard-workflow.md` | 分镜绘制流程 |
| `motion-workflow.md` | 视频合成流程 |
| `assembly-workflow.md` | 成片装配流程 |

---

## 📁 项目结构

```
douyin-skills/
├── SKILL.md                    # 技能入口
├── README.md                   # 项目文档
├── pyproject.toml              # Python 依赖配置
│
├── skills/                     # 子技能目录
│   ├── dy-auth/                # 认证管理
│   ├── dy-publish/             # 内容发布
│   ├── dy-explore/             # 内容发现
│   ├── dy-interact/            # 社交互动
│   └── manjv/                  # AI 短漫剧生成 ✨
│       ├── SKILL.md
│       ├── main.py
│       ├── requirements.txt
│       ├── scripts/
│       │   ├── nanobanana_api.py    # Nano Banana 2 API
│       │   ├── grok_api.py          # Grok Imagine API
│       │   ├── video_assembler.py   # ffmpeg 装配
│       │   └── workflow.py          # 工作流
│       └── references/              # 工作流文档
│           ├── script-analysis-workflow.md
│           ├── art-direction-workflow.md
│           ├── assets-generation-workflow.md
│           ├── storyboard-workflow.md
│           ├── motion-workflow.md
│           └── assembly-workflow.md
│
└── scripts/                    # Python 自动化引擎
    ├── cli.py
    ├── chrome_launcher.py
    └── douyin/
```

---

## 🔧 CLI 命令参考

### 基础命令

```bash
# 启动浏览器
python scripts/chrome_launcher.py

# 检查登录状态
python scripts/cli.py check-login

# 扫码登录
python scripts/cli.py login
```

### 搜索与浏览

```bash
# 搜索视频
python scripts/cli.py search-videos --keyword "美食" --limit 10

# 获取首页推荐
python scripts/cli.py get-feed --limit 10
```

### 社交互动

```bash
# 点赞视频
python scripts/cli.py like-video --video-id VIDEO_ID

# 发表评论
python scripts/cli.py post-comment --video-id VIDEO_ID --content "太棒了！"
```

### 内容发布

```bash
# 发布视频
python scripts/cli.py publish-video \
  --title-file title.txt \
  --video /path/to/video.mp4
```

---

## ⚠️ 注意事项

1. **API Key** - Nano Banana 2 和 Grok 需要 Kie AI API Key
   - 获取地址：https://kie.ai/api-key
2. **登录状态** - 部分功能需要登录后才能使用
3. **选择器更新** - 抖音页面结构可能变化，选择器需要定期更新

---

## 🔄 更新日志

### 2026-03-31 - v2.0.0
- 🔥 **重大更新**：新增 **manjv** AI 短漫剧生成模块
- ✨ 基于 LumenX Studio 架构设计
- ✨ 整合 Nano Banana 2 + Grok 实现完整创作链路
- 🗑️ 移除 dy-moviegen-v2（已迁移到 manjv）

### 2026-03-27 - v10.0
- 🔥 重构图像生成：使用 Nano Banana 2 (Kie AI API)
- ✨ 新增功能：角色三视图、九宫格分镜、场景鸟瞰图/全景图

### 2026-03-19 - v2.0
- ✨ 新增 dy-moviegen-v2 增强版短剧生成技能

### 2026-03-11 - v1.0
- ✨ 初始版本

---

## 🔗 相关资源

- **Kie AI**: https://kie.ai
- **LumenX Studio**: https://github.com/alibaba/lumenx
- **抖音主站**: https://www.douyin.com
- **创作者中心**: https://creator.douyin.com

---

## 📄 License

MIT
