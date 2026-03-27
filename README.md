# 抖音一站式运营 Skills

基于 Python CDP 浏览器自动化引擎 + AI 视频生成，支持 OpenClaw 及所有兼容 SKILL.md 格式的 AI Agent 平台。

## 🎯 核心能力

| 技能 | 说明 | 状态 |
|------|------|------|
| **dy-auth** | 认证管理：登录检查、扫码登录、多账号切换 | ✅ |
| **dy-publish** | 内容发布：视频发布、图文发布、定时发布 | ✅ |
| **dy-explore** | 内容发现：关键词搜索、视频详情、用户主页、推荐流 | ✅ |
| **dy-interact** | 社交互动：点赞、收藏、评论、关注 | ✅ |
| **dy-moviegen-v2** | **AI 短剧生成：剧本创作 + 图像生成 + 视频生成** ✨ | ✅ v10 |

---

## 🛠️ 环境要求

- Python >= 3.11
- uv 包管理器（推荐）或 pip
- Google Chrome 浏览器
- ffmpeg（视频生成需要）

---

## 📦 安装

```bash
cd ~/.openclaw/workspace/skills/douyin-skills

# 安装主依赖
uv sync

# 安装 dy-moviegen-v2 依赖（AI 视频生成）
cd skills/dy-moviegen-v2
pip install -r requirements.txt

# 安装 Playwright（剪映自动化模式需要）
playwright install chromium
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

**AI 短剧生成：**
- "帮我写一个古风重生权谋短剧，女主是将军之女"
- "生成角色三视图"
- "生成九宫格分镜"
- "用 Grok 生成一个仙侠战斗视频"

---

## 🎬 dy-moviegen-v2 - AI 短剧生成 Agent

增强版多 Agent 协作短剧自动生成工具，整合 **Grok Imagine API** + **Nano Banana 2 (Kie AI)** + **剪映自动化**。

### 核心能力

| 功能模块 | 说明 |
|---------|------|
| 🎬 导演统筹 | 自动规划整体节奏和分段 |
| ✍️ 编剧创作 | 根据剧情生成脚本和台词 |
| 🎥 分镜设计 | 专业分镜提示词，时间轴精确控制 |
| 📝 提示词编译 | 264 标签库，专业提示词生成 |
| 🤖 视频生成 | Grok Imagine API + 剪映自动化 |
| 🖼️ 图像生成 | Nano Banana 2 (Gemini 3.1 Flash) |
| 👤 角色三视图 | 上半身/正面全身/背面全身 |
| 📐 九宫格分镜 | 3×3 完整故事板 |
| 🏞️ 场景资产 | 鸟瞰图、全景图 |
| ✂️ 剪辑装配 | ffmpeg 拼接成片 |

### 平台支持

| 平台 | 功能 | 模式 |
|------|------|------|
| **Grok Imagine** | 视频生成 (T2V/I2V) | API 直连 |
| **Nano Banana 2** | 图像生成、三视图、九宫格 | API 直连 |
| **剪映** | 视频生成/编辑 | Playwright 自动化 |

### 快速开始

```bash
cd skills/dy-moviegen-v2

# 设置 API Key
export KIE_API_KEY="your-api-key"

# 图像生成
python3 scripts/nano_banana_api.py generate \
  --prompt "古风少女，仙气飘飘，手持玉笛" \
  --aspect-ratio 3:4 \
  --resolution 2K

# 角色三视图
python3 scripts/unified_workflow.py tri-view \
  --description "古风少女，身穿白色汉服，手持玉笛"

# 九宫格分镜
python3 scripts/unified_workflow.py 9grid \
  --content "九宫格分镜内容..." \
  --images 场景.png 角色1.png 角色2.png

# 视频生成 (Grok)
python3 scripts/grok_api.py \
  --prompt "A cyberpunk city with neon lights" \
  --duration 10 \
  --ratio 9:16
```

### 工作流文档

| 文档 | 说明 |
|------|------|
| `script-creation-workflow.md` | 短剧剧本创作提示词（状态机版） |
| `story-to-execution.md` | AI短视频故事生成模板 v2.0 |
| `image-prompt-generator.md` | 万能图像提示词生成器（264标签） |
| `character-design-template.md` | 角色设定提示词模板 |
| `asset-prompts.md` | 资产库提示词（鸟瞰图/全景图/三视图） |
| `platform-specs.md` | 平台规格（Grok + Nano Banana 2） |

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
│   └── dy-moviegen-v2/         # AI 短剧生成 ✨
│       ├── SKILL.md
│       ├── main.py
│       ├── scripts/            # API 客户端
│       │   ├── grok_api.py
│       │   ├── nano_banana_api.py
│       │   └── unified_workflow.py
│       └── references/         # 工作流文档
│           ├── script-creation-workflow.md
│           ├── story-to-execution.md
│           ├── image-prompt-generator.md
│           ├── character-design-template.md
│           └── ...
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

1. **API Key** - Grok 和 Nano Banana 2 需要 Kie AI API Key
2. **登录状态** - 部分功能需要登录后才能使用
3. **选择器更新** - 抖音页面结构可能变化，选择器需要定期更新
4. **九宫格生成** - 耗时较长，建议设置足够的 timeout

---

## 🔄 更新日志

### 2026-03-27 - v10.0
- 🔥 重构图像生成：使用 Nano Banana 2 (Kie AI API)
- ✨ 新增功能：角色三视图、九宫格分镜、场景鸟瞰图/全景图
- 📚 更新工作流文档：剧本创作、故事生成、角色设定、资产库提示词
- 🗑️ 移除 Seedance 2.0，统一使用 Grok + Nano Banana 2

### 2026-03-19 - v2.0
- ✨ 新增 dy-moviegen-v2 增强版短剧生成技能

### 2026-03-11 - v1.0
- ✨ 初始版本

---

## 🔗 相关资源

- **Kie AI**: https://kie.ai
- **抖音主站**: https://www.douyin.com
- **创作者中心**: https://creator.douyin.com
- **剪映**: https://xyq.jianying.com

---

## 📄 License

MIT