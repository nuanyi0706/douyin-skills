---
name: dy-moviegen-v2
description: |
  增强版短剧生成 Agent —— 整合 Grok Imagine API + Nano Banana 2 (Kie AI) + 剪映自动化 + 多 Agent 协作。
  
  核心能力：专业剧本创作、图像提示词生成、15秒分段执行稿、角色三视图、场景鸟瞰图/全景图、九宫格/三宫格分镜、图像超高清放大、Grok/剪映双平台视频生成、ffmpeg 一键装配。
  
  触发场景：生成短剧、AI 短剧、视频生成、短剧制作、剧情视频、Grok 视频创作、剧本创作、分镜设计、图像生成、三视图、九宫格分镜、场景资产、随拍带货、带货视频、种草视频。

metadata:
  trigger: 生成短剧、AI 短剧、视频生成、短剧制作、Grok、Grok Imagine、剪映、剧本创作、分镜、提示词、分镜生成、Nano Banana、图像生成、三视图、九宫格、鸟瞰图、全景图、资产生成、随拍带货、带货视频、种草视频
  source: 整合 douyin-skills/dy-moviegen + 万能图像生成器.json + SD专用资产生成.json + Grok Imagine API
  version: 10.0.0

---

# 短剧生成 Agent v2 (dy-moviegen-v2)

增强版多 Agent 协作短剧自动生成工具，整合 **Grok Imagine API**、**Nano Banana 2 (Kie AI)**、**剪映自动化** 和 **ffmpeg 后期装配**。

---

## 🎯 完整创作链路

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  故事素材   │ ──► │  剧本创作   │ ──► │  执行稿拆解 │
│             │     │  (工作流1)  │     │  (工作流3)  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                   │
                           ▼                   │
                    ┌─────────────┐            │
                    │  资产生成   │            │
                    │ Nano Banana │            │
                    │ (角色/场景) │            │
                    └─────────────┘            │
                           │                   │
                           ▼                   ▼
                    ┌─────────────┐     ┌─────────────┐
                    │ 图像提示词  │ ──► │  视频生成   │
                    │  (工作流2)  │     │ Grok/剪映   │
                    └─────────────┘     └─────────────┘
```

**正确链路说明：**
1. 故事素材 → 剧本创作（工作流1）
2. 剧本创作 → 资产生成（角色三视图、场景图等）
3. 剧本创作 → 图像提示词生成（工作流2）
4. 执行稿拆解（工作流3）→ 输出分镜和提示词
5. 综合以上资产 → 视频生成（Grok/剪映）

---

## 📚 四大创作工作流

### 工作流 1：剧本创作（状态机驱动）

**文件**：`references/script-creation-workflow.md`

**功能**：将故事设定/素材 → 2分钟分场剧本

**状态机**：
```
INIT → WAITING_MATERIAL → ANALYZING → WRITING_SCRIPT → SCRIPT_DONE
```

**核心规则**：
- 开篇3秒抓眼冲突
- 每15秒一个小节点
- 每30秒一个反转
- 结尾留钩子/悬念

**触发词**：写剧本、创作短剧、古风权谋

---

### 工作流 2：图像提示词生成器

**文件**：`references/image-prompt-generator.md`

**功能**：标签组合 → 多样化图像提示词

**六大标签库**（共264个标签）：
- 主体类型（46个）
- 画面风格（38个）
- 光影氛围（38个）
- 构图视角（31个）
- 服装造型（46个）
- 场景背景（37个）
- 技术画质（28个）

**触发词**：生成图像提示词、出角色图、画场景

---

### 工作流 3：短视频故事执行稿

**文件**：`references/story-to-execution.md`

**功能**：完整剧本 → 15秒段图像+视频提示词

**输出结构**：
```
故事总览 → 角色统一设定 → 场景统一设定 → 15秒分段总表 → 逐段执行稿
```

**触发词**：拆剧本、执行稿、15秒分段

---

### 工作流 4：随拍带货短视频

**文件**：`references/spontaneous-shopping-video-workflow.md`

**功能**：产品卖点 → 随拍风格带货视频脚本

**触发词**：随拍带货、带货视频、种草视频

---

## 🛠️ 技术能力

| 功能模块 | 说明 |
|---------|------|
| 🎬 导演统筹 | 自动规划整体节奏和分段 |
| ✍️ 编剧创作 | 根据剧情生成脚本和台词 |
| 🎥 分镜设计 | 专业分镜提示词，时间轴精确控制 |
| 📝 提示词编译 | 专业提示词生成，支持标签组合 |
| 🤖 视频生成 | Grok Imagine API + 剪映自动化双模式 |
| 🖼️ 图像生成 | Nano Banana 2 (Kie AI)，支持 T2I/I2I |
| 👤 角色三视图 | 上半身/正面全身/背面全身并排 |
| 📐 九宫格分镜 | 3x3 完整九宫格故事板 |
| 📊 三宫格分镜 | 3格分镜故事板 |
| 🎭 白底图生成 | 提取主体生成白底图 |
| 🏞️ 场景鸟瞰图 | 超远距离鸟瞰视角 |
| 🌐 场景全景图 | 210度全景视图 |
| 🔍 图像放大 | 超高清放大至 4K |
| ✂️ 剪辑装配 | 使用 ffmpeg 拼接成片 |
| 🎵 音效设计 | 环境音 + 人声（禁止BGM） |

---

## 🚀 平台支持

| 平台 | 模式 | 说明 |
|------|------|------|
| **Grok Imagine (Kie AI)** | API 直连 | 视频生成，需要 API Key |
| **Nano Banana 2 (Kie AI)** | API 直连 | 图像生成，需要 API Key |
| **剪映 (Jianying)** | Playwright 自动化 | 视频生成/编辑，需要 cookies |

### Grok Imagine 平台特性

- ✅ 文生视频 (T2V) - 纯文本生成视频
- ✅ 图生视频 (I2V) - 图片转视频（最多 7 张图）
- ✅ 视频扩展 - 延长已有视频
- ✅ 多种画面比例 - 2:3, 3:2, 1:1, 16:9, 9:16
- ✅ 多种时长 - 6秒 / 10秒
- ✅ 三种风格模式：fun / normal / spicy

### Nano Banana 2 平台特性

- ✅ 文生图 (T2I) - 纯文本生成图像
- ✅ 图生图 (I2I) - 最多 14 张参考图
- ✅ 角色三视图 - 上半身/正面/背面并排
- ✅ 九宫格分镜 - 3x3 完整故事板
- ✅ 三宫格分镜 - 3格分镜故事板
- ✅ 白底图生成 - 提取主体
- ✅ 场景鸟瞰图 - 超远距离鸟瞰视角
- ✅ 场景全景图 - 210度全景视图
- ✅ 图像放大 - 超高清 4K
- ✅ 批量生成 - 支持批量处理
- ✅ 多分辨率 - 1K / 2K / 4K
- ✅ 多画幅 - auto/1:1/16:9/9:16/4:3/3:4/21:9 等

---

## 📦 项目结构

```
dy-moviegen-v2/
├── SKILL.md                              # 技能入口
├── main.py                               # 主入口脚本
├── requirements.txt                      # Python 依赖
├── scripts/
│   ├── grok_api.py                       # Grok Imagine API 客户端
│   ├── jianying_worker.py                # 剪映自动化
│   ├── prompt_compiler.py                # 提示词编译
│   ├── video_assembler.py                # 视频装配：ffmpeg 拼接
│   ├── nano_banana_api.py                # Nano Banana 2 API 客户端 (Kie AI)
│   └── unified_workflow.py               # 统一工作流脚本
└── references/
    ├── script-creation-workflow.md       # 工作流1：剧本创作
    ├── image-prompt-generator.md         # 工作流2：图像提示词
    ├── story-to-execution.md             # 工作流3：执行稿拆解
    ├── spontaneous-shopping-video-workflow.md  # 工作流4：随拍带货
    ├── vocabulary.md                     # 专业词汇库
    ├── platform-specs.md                 # 平台规格说明
    └── examples.md                       # 示例参考
```

---

## 💡 使用方式

### 方式一：自然语言对话（推荐）

直接与 Agent 对话，根据意图自动路由：

**剧本创作**：
- "帮我写一个古风重生权谋短剧，女主是将军之女"
- "创作一个2分钟的悬疑短剧剧本"

**图像生成**：
- "生成一张古风少女图"
- "生成角色三视图"
- "生成九宫格分镜"

**资产生成**：
- "生成场景鸟瞰图"
- "生成全景图"
- "生成白底图"
- "把这张图放大到4K"

**视频生成**：
- "用 Grok 生成一个仙侠战斗视频"
- "把这张图片变成动画"

### 方式二：命令行调用

```bash
cd ~/.openclaw/workspace/skills/douyin-skills/skills/dy-moviegen-v2

# 设置 API Key
export KIE_API_KEY="your-api-key"

# ========== Nano Banana 2 图像生成 ==========

# 通用图像生成
python3 scripts/unified_workflow.py generate \
  --prompt "古风少女，仙气飘飘，手持玉笛" \
  --style gufeng \
  --aspect-ratio 3:4 \
  --resolution 2K

# 角色三视图
python3 scripts/unified_workflow.py tri-view \
  --description "古风少女，身穿白色汉服，手持玉笛，长发飘逸" \
  --image "角色参考图.png" \
  --resolution 2K

# 白底图
python3 scripts/unified_workflow.py white-bg \
  --image "原图.png"

# 场景鸟瞰图
python3 scripts/unified_workflow.py bird-view \
  --image "场景图.png" \
  --resolution 4K

# 场景全景图
python3 scripts/unified_workflow.py panoramic \
  --image "场景图.png" \
  --resolution 4K

# 九宫格分镜
python3 scripts/unified_workflow.py 9grid \
  --content "完整的九宫格分镜描述..." \
  --images "场景.png" "角色1.png" "角色2.png" \
  --resolution 4K

# 三宫格分镜
python3 scripts/unified_workflow.py 3grid \
  --content "三格分镜描述..." \
  --resolution 2K

# 图像放大
python3 scripts/unified_workflow.py upscale \
  --image "原图.png" \
  --resolution 4K

# 批量生成
python3 scripts/unified_workflow.py batch \
  --file prompts.txt \
  --aspect-ratio 16:9 \
  --resolution 2K

# ========== Grok 视频生成 ==========

# 文生视频
python3 scripts/grok_api.py \
  --prompt "A cyberpunk city with neon lights" \
  --duration 10 \
  --ratio 9:16

# 图生视频
python3 scripts/grok_api.py \
  --mode i2v \
  --image "https://example.com/image.png" \
  --prompt "镜头推进，人物走向前方" \
  --duration 6
```

---

## 📊 API 参数

### Nano Banana 2 参数

| 参数 | 选项 | 默认值 |
|------|------|--------|
| aspect_ratio | auto/1:1/16:9/9:16/4:3/3:4/21:9/2:3/3:2/1:4/4:1/1:8/8:1/4:5/5:4 | auto |
| resolution | 1K / 2K / 4K | 1K |
| output_format | jpg / png | jpg |
| image_input | 最多 14 张图片 URL | - |
| prompt | 最大 20000 字符 | - |

### Grok Imagine 参数

| 参数 | 选项 | 默认值 |
|------|------|--------|
| duration | 6s / 10s | 6s |
| ratio | 2:3/3:2/1:1/16:9/9:16 | 16:9 |
| resolution | 480p / 720p | 720p |
| style | fun / normal / spicy | normal |
| image_input | 最多 7 张图片 | - |

---

## ⚠️ 注意事项

### API 配置

```bash
# Kie AI API Key（Grok + Nano Banana 2）
export KIE_API_KEY="your-api-key"
```

### 获取 API Key

访问 [Kie AI API Key 管理](https://kie.ai/api-key) 获取

### 声音设计规则

- ✅ 只保留：环境音 + 人声
- ❌ 禁止：BGM / 背景音乐 / 配乐

### 物理逻辑要求

- 动作要有重心、惯性、反作用力
- 布料、头发、烟尘、雨水要随动作变化

---

## 🔗 相关技能

- **dy-auth** - 抖音账号认证管理
- **dy-publish** - 抖音视频发布
- **dy-explore** - 抖音内容搜索发现
- **dy-interact** - 抖音社交互动

---

#短剧生成 #AI视频 #Grok #GrokImagine #NanoBanana #图像生成 #三视图 #九宫格 #鸟瞰图 #全景图 #资产生成 #剪映 #视频自动化 #剧本创作 #分镜