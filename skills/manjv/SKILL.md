---
name: manjv
description: |
  AI 短漫剧一站式生产平台。基于 LumenX Studio 架构设计，复刻其从小说文本到动态视频的完整创作链路。
  
  核心能力：剧本分析、角色定制、场景生成、分镜绘制、视频合成。支持自然语言驱动多 Agent 协作。
  
  触发场景：生成短漫剧、AI短剧、AI漫画、小说转视频、剧本创作、分镜设计、角色三视图、场景图生成、视频合成。

metadata:
  trigger: AI短漫剧、生成短漫剧、AI漫画、小说转视频、剧本创作、分镜设计、角色定制、场景生成、视频合成、LumenX、manjv
  source: alibaba/lumenx
  version: 1.0.0
---

# manjv - AI 短漫剧一站式生产平台

基于 LumenX Studio 架构设计，整合 **Nano Banana 2** (图像生成) + **Grok** (视频生成)，实现从小说文本到动态视频的完整创作链路。

---

## 🎯 完整创作链路

```
故事素材 → 剧本分析 → 实体提取 → 风格定调 → 资产生成 → 分镜绘制 → 视频合成 → 成片装配
```

| 步骤 | 内容 | 工具 |
|------|------|------|
| 1 | 故事素材 | 用户输入 |
| 2 | 剧本分析 | LLM 分析剧情结构 |
| 3 | 实体提取 | 角色、场景、道具 |
| 4 | 风格定调 | 视觉风格标准 |
| 5 | 资产生成 | Nano Banana 2 |
| 6 | 分镜绘制 | 9宫格/3宫格 |
| 7 | 视频合成 | Grok I2V/T2V |
| 8 | 成片装配 | ffmpeg 拼接 |

---

## 📚 六大核心模块

| 模块 | 功能 | 触发词 |
|------|------|--------|
| 剧本分析 | 提取角色、场景、道具、冲突点 | 分析剧本、拆解剧情 |
| 风格定调 | 定义视觉风格、统一画面标准 | 风格设定、视觉风格 |
| 资产生成 | 角色三视图、场景图、道具图 | 生成角色图、三视图 |
| 分镜绘制 | 9宫格/3宫格分镜故事板 | 生成分镜、9宫格 |
| 视频合成 | I2V/T2V 动态视频生成 | 生成视频、I2V |
| 成片装配 | ffmpeg 拼接最终短剧 | 拼接视频、导出 |

---

## 🛠️ 技术能力

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

---

## 🚀 平台支持

| 平台 | 模式 | 用途 |
|------|------|------|
| **Nano Banana 2** | API | 图像生成 |
| **Grok Imagine** | API | 视频生成 |
| **ffmpeg** | 本地 | 视频拼接 |

### Nano Banana 2
- ✅ T2I / I2I（14张参考图）
- ✅ 角色三视图、九宫格、三宫格
- ✅ 鸟瞰图、全景图、白底图
- ✅ 1K / 2K / 4K 分辨率

### Grok Imagine
- ✅ I2V（7张图）/ T2V
- ✅ 6秒 / 10秒 时长
- ✅ 多种画面比例
- ✅ fun / normal / spicy 风格

---

## 💡 使用方式

### 自然语言调用

```
"分析这个小说片段"
"生成角色三视图：古风少女，白衣汉服"
"生成场景鸟瞰图"
"生成9宫格分镜"
"将分镜图转换为视频"
"拼接所有视频片段"
```

### 命令行调用

```bash
cd ~/.openclaw/workspace/skills/douyin-skills/skills/manjv
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

## ⚠️ 注意事项

### API 配置
```bash
export KIE_API_KEY="your-api-key"
```
获取地址：https://kie.ai/api-key

### 视频规则
- ✅ 环境音 + 人声
- ❌ BGM / 背景音乐（短剧除外）

---

## 📦 项目结构

```
manjv/
├── SKILL.md                    # 技能入口
├── main.py                     # 主入口
├── requirements.txt            # 依赖
├── scripts/
│   ├── nanobanana_api.py      # 图像生成
│   ├── grok_api.py            # 视频生成
│   ├── video_assembler.py     # ffmpeg装配
│   └── workflow.py            # 工作流
└── references/
    ├── script-analysis-workflow.md
    ├── art-direction-workflow.md
    ├── assets-generation-workflow.md
    ├── storyboard-workflow.md
    ├── motion-workflow.md
    └── assembly-workflow.md
```

---

## 🔗 相关技能

| 技能 | 说明 |
|------|------|
| dy-auth | 账号认证 |
| dy-publish | 内容发布 |
| dy-explore | 内容发现 |
| dy-interact | 社交互动 |

---

#AI短漫剧 #LumenX #manjv #NanoBanana #Grok #三视图 #九宫格 #分镜
