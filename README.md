# 抖音一站式运营 Skills

基于 Python CDP 浏览器自动化引擎 + AI 视频生成，支持 OpenClaw 及所有兼容 SKILL.md 格式的 AI Agent 平台。

## 🎯 核心能力

| 技能 | 说明 | 状态 |
|------|------|------|
| **dy-auth** | 认证管理：登录检查、扫码登录、多账号切换 | ✅ |
| **dy-publish** | 内容发布：视频发布、图文发布、定时发布 | ✅ |
| **dy-explore** | 内容发现：关键词搜索、视频详情、用户主页、推荐流 | ✅ |
| **dy-interact** | 社交互动：点赞、收藏、评论、关注 | ✅ |
| **dy-moviegen-v2** | **AI 视频生成：短剧制作、Seedance 2.0、剪映自动化** ✨ | ✅ v2 |

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
- "找一下这个作者的主页"

**社交互动：**
- "给这个视频点赞"
- "收藏这个视频"
- "评论：拍得太好了"
- "关注这个作者"

**内容发布：**
- "帮我发布一条视频，标题是…"
- "发布一个图文作品"

**AI 视频生成：**
- "帮我生成一个港风悬疑短剧，讲外卖员发现客户家的秘密"
- "用 Seedance 2.0 生成一个仙侠战斗视频"
- "把这张图片变成动画，镜头从左向右平移"
- "做一个 15 秒的赛博朋克风格产品广告"

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

# 清除 cookies（退出登录）
python scripts/cli.py delete-cookies
```

### 搜索与浏览

```bash
# 搜索视频
python scripts/cli.py search-videos --keyword "美食" --limit 10

# 获取首页推荐
python scripts/cli.py get-feed --limit 10

# 获取视频详情
python scripts/cli.py get-video-detail --video-id VIDEO_ID

# 获取用户信息
python scripts/cli.py get-user --user-id USER_ID
```

### 社交互动

```bash
# 点赞视频
python scripts/cli.py like-video --video-id VIDEO_ID

# 收藏视频
python scripts/cli.py collect-video --video-id VIDEO_ID

# 发表评论
python scripts/cli.py post-comment \
  --video-id VIDEO_ID \
  --content "太棒了！"

# 关注作者
python scripts/cli.py follow-user --user-id USER_ID
```

### 内容发布

```bash
# 发布视频
python scripts/cli.py publish-video \
  --title-file title.txt \
  --video /path/to/video.mp4

# 发布图文
python scripts/cli.py publish-image \
  --title "标题" \
  --images /path/to/img1.jpg /path/to/img2.jpg
```

---

## 🎬 dy-moviegen-v2 - AI 视频生成（增强版）

整合了 4 个开源项目的增强版短剧生成工具，支持 **Seedance 2.0 专业提示词工程** 和 **剪映自动化**。

### 核心能力

| 功能模块 | 说明 |
|---------|------|
| 🎬 导演统筹 | 多 Agent 协作规划整体节奏 |
| ✍️ 编剧创作 | 自动生成脚本和台词 |
| 🎥 分镜设计 | Seedance 2.0 专业分镜（精确到秒） |
| 📝 提示词编译 | 史诗级提示词架构 |
| 🤖 视频生成 | **剪映自动化** + **即梦 API** 双平台 |
| ✂️ 剪辑装配 | ffmpeg 拼接成片 |

### 安装配置

```bash
cd skills/dy-moviegen-v2

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright（剪映模式）
playwright install chromium
```

### 使用方式

**方式一：自然语言对话**
```
直接告诉 Agent：
- "生成一个赛博朋克风格的城市视频"
- "把这张图片变成动画"
- "用这首歌做个 MV"
```

**方式二：命令行调用**
```bash
cd ~/.openclaw/workspace/skills/douyin-skills/skills/dy-moviegen-v2

# 剪映自动化模式
python main.py \
  --input "风格：赛博朋克\n内容：未来城市的飞行汽车" \
  --platform jianying \
  --cookies cookies.json \
  --output-dir ./output

# 即梦 API 模式
python main.py \
  --input "风格：仙侠\n内容：修真者御剑飞行" \
  --platform seedance

# 指定时长和比例
python main.py \
  --input "风格：港风悬疑\n内容：外卖员发现秘密" \
  --platform jianying \
  --cookies cookies.json \
  --duration 15s \
  --ratio 9:16
```

**方式三：子技能调用**
```bash
# 文生视频 (T2V)
python scripts/jianying_worker.py \
  --cookies cookies.json \
  --output-dir ./output \
  --prompt "赛博朋克风格的长安城" \
  --duration 10s \
  --model "Seedance 2.0"

# 图生视频 (I2V)
python scripts/jianying_worker.py \
  --cookies cookies.json \
  --output-dir ./output \
  --ref-image ./reference.png \
  --prompt "将这张图片变成动画" \
  --duration 10s

# 参考视频生成 (V2V)
python scripts/jianying_worker.py \
  --cookies cookies.json \
  --output-dir ./output \
  --ref-video ./reference.mp4 \
  --prompt "画风改成宫崎骏风格" \
  --duration 10s

# Dry-run 调试
python scripts/jianying_worker.py \
  --cookies cookies.json \
  --prompt "测试" \
  --dry-run
```

### 环境配置

**剪映模式**（推荐个人使用）
- 从浏览器登录 https://xyq.jianying.com 导出 `cookies.json`

**即梦 API 模式**（推荐批量生成）
```bash
export ARK_API_KEY="your_api_key"
export ARK_SEEDANCE_CREATE_URL="..."
export ARK_SEEDANCE_QUERY_URL_TEMPLATE="...{task_id}..."
```

**LLM 配置**（Agent 协作需要）
```bash
export LLM_API_BASE="..."
export LLM_API_KEY="..."
export LLM_MODEL_PROVIDER="openai"
export LLM_MODEL_NAME="..."
```

### ⚠️ 注意事项

- ⚠️ 不支持写实真人脸部素材（平台会拦截）
- ⚠️ 混合输入总上限 12 个文件（图片 + 视频 + 音频）
- ⚠️ 单次生成上限 15 秒（超长需分段）
- ⚠️ 视频参考消耗更多积分/额度

📚 **详细文档**: [dy-moviegen-v2/SKILL.md](skills/dy-moviegen-v2/SKILL.md)

---

## 📁 项目结构

```
douyin-skills/
├── SKILL.md                    # 技能入口
├── README.md                   # 项目文档
├── pyproject.toml              # Python 依赖配置
├── uv.lock                     # uv 锁定文件
│
├── skills/                     # 子技能目录
│   ├── dy-auth/                # 认证管理
│   │   └── SKILL.md
│   ├── dy-publish/             # 内容发布
│   │   └── SKILL.md
│   ├── dy-explore/             # 内容发现
│   │   └── SKILL.md
│   ├── dy-interact/            # 社交互动
│   │   └── SKILL.md
│   └── dy-moviegen-v2/         # AI 视频生成（增强版）✨
│       ├── SKILL.md
│       ├── README.md
│       ├── main.py
│       ├── requirements.txt
│       ├── scripts/            # 子技能脚本
│       ├── templates/          # 分镜模板
│       ├── references/         # 参考资料
│       └── examples/           # 实战案例
│
└── scripts/                    # Python 自动化引擎
    ├── cli.py                  # CLI 入口
    ├── chrome_launcher.py      # 浏览器启动
    └── douyin/                 # 核心模块
        ├── cdp.py              # CDP 客户端
        ├── selectors.py        # CSS 选择器
        ├── login.py            # 登录模块
        ├── search.py           # 搜索模块
        ├── feeds.py            # Feed 流
        ├── interact.py         # 互动模块
        └── publish.py          # 发布模块
```

---

## 📊 API 返回格式

### 搜索结果
```json
{
  "keyword": "美食",
  "count": 10,
  "videos": [
    {
      "video_id": "",
      "author": "作者名",
      "plays": "10.8 万",
      "duration": "02:09",
      "publish_time": "1 天前",
      "title": "视频描述",
      "cover": "封面 URL"
    }
  ]
}
```

### 首页推荐
```json
{
  "success": true,
  "count": 10,
  "videos": [
    {
      "video_id": "7478923456789012345",
      "author": "作者名",
      "likes": "1.1 万",
      "cover": "封面 URL"
    }
  ]
}
```

### 视频详情
```json
{
  "video_id": "7478923456789012345",
  "title": "视频标题",
  "author": {
    "user_id": "MS4wLjAB...",
    "nickname": "作者名",
    "avatar": "头像 URL"
  },
  "statistics": {
    "plays": "10.8 万",
    "likes": "1.1 万",
    "comments": "523",
    "shares": "128"
  }
}
```

---

## ⚠️ 注意事项

1. **搜索页无视频 ID** - 抖音搜索结果页不直接提供视频 ID，只能获取描述信息
2. **登录状态** - 部分功能需要登录后才能使用
3. **选择器更新** - 抖音页面结构可能变化，选择器需要定期更新
4. **网络环境** - 需要稳定的网络连接访问抖音
5. **视频生成限制** - dy-moviegen-v2 不支持写实真人脸部素材

---

## 🔄 更新日志

### 2026-03-19 - v2.0
- ✨ 新增 **dy-moviegen-v2** 增强版短剧生成技能
- 🔥 整合 4 个开源项目（elementsix-skills、seedance2.0-prompt-skill、lanshu-waytovideo）
- 🎬 支持 Seedance 2.0 专业提示词工程
- 🤖 支持剪映自动化 + 即梦 API 双平台
- 📚 添加完整文档、模板、案例库

### 2026-03-11 - v1.0
- ✨ 新增 dy-moviegen 短剧生成技能
- 🐛 修复 Linux Wayland 环境下浏览器启动问题
- 📝 更新文档

---

## 🔗 相关资源

- **抖音主站**: https://www.douyin.com
- **创作者中心**: https://creator.douyin.com
- **剪映**: https://xyq.jianying.com
- **即梦 Seedance**: https://jimeng.jianying.com

---

## 📄 License

MIT
