# 图像生成示例库

> Grok Imagine + Nano Banana 2 (Kie AI) 使用示例

---

## 1. Nano Banana 2 图像生成示例

### 通用图像生成

```bash
# 写实人像
python3 scripts/unified_workflow.py generate \
  --prompt "少女，清冷气质，黑色长发，穿着白色连衣裙，黄昏海边，逆光" \
  --style realistic \
  --aspect-ratio 3:4 \
  --resolution 2K

# 古风人像
python3 scripts/unified_workflow.py generate \
  --prompt "古风侠女，手持长剑，竹林深处，水墨风格" \
  --style gufeng \
  --aspect-ratio 2:3 \
  --resolution 2K

# CG 角色
python3 scripts/unified_workflow.py generate \
  --prompt "赛博朋克女战士，霓虹城市，机甲风格" \
  --style cg \
  --aspect-ratio 16:9 \
  --resolution 4K
```

### 角色三视图

```bash
python3 scripts/unified_workflow.py tri-view \
  --description "古风少女，身穿白色汉服，手持玉笛，长发飘逸，仙气飘飘" \
  --resolution 2K
```

**输出**：一张包含上半身、正面全身、背面全身的并排三视图。

### 白底图生成

```bash
python3 scripts/unified_workflow.py white-bg \
  --image "https://example.com/product.png" \
  --description "提取主体物件"
```

### 场景鸟瞰图

```bash
python3 scripts/unified_workflow.py bird-view \
  --image "场景参考图.png" \
  --prompt "古代城池，俯瞰全貌" \
  --resolution 4K
```

### 场景全景图

```bash
python3 scripts/unified_workflow.py panoramic \
  --image "场景参考图.png" \
  --prompt "山间古寺，云雾缭绕" \
  --resolution 4K
```

### 九宫格分镜

```bash
python3 scripts/unified_workflow.py 9grid \
  --content "
【分镜 1-1】中景 - 开场建立
古风少女站在竹林入口，微风吹动她的发丝，镜头缓缓推进

【分镜 1-2】特写 - 面部
少女的眼眸清澈如水，目光坚定望向前方

【分镜 1-3】中景 - 动作
少女从腰间抽出玉笛，横在唇边

【分镜 1-4】特写 - 手部
纤细的手指按在玉笛的音孔上

【分镜 1-5】全景 - 环境变化
笛声响起，周围的竹叶开始随风飘动

【分镜 1-6】中景 - 情绪
少女闭眼吹奏，表情沉醉

【分镜 1-7】远景 - 意境
笛声传出，鸟儿从竹林深处飞起

【分镜 1-8】中景 - 收尾
少女放下玉笛，睁开眼睛

【分镜 1-9】远景 - 结束
少女转身走向竹林深处，背影渐行渐远
" \
  --style "写实古风，电影级cinematic质感，冷色调低饱和" \
  --images "场景图.png" "角色图.png" \
  --resolution 4K
```

### 三宫格分镜

```bash
python3 scripts/unified_workflow.py 3grid \
  --content "
【分镜 1-1】中景 - 起势
角色立于画面中央，蓄势待发

【分镜 1-2】特写 - 爆发
瞬间的动作爆发，动态模糊

【分镜 1-3】远景 - 收尾
角色站在废墟中，背对镜头
" \
  --resolution 2K
```

### 图像放大

```bash
python3 scripts/unified_workflow.py upscale \
  --image "原图.png" \
  --aspect-ratio 16:9 \
  --resolution 4K
```

---

## 2. Grok Imagine 视频生成示例

### 文生视频 (T2V)

```bash
python3 scripts/grok_api.py \
  --prompt "A cyberpunk city with neon lights, flying cars, and rain. Camera slowly moves forward through the streets." \
  --duration 10 \
  --ratio 9:16 \
  --mode normal
```

### 图生视频 (I2V)

```bash
python3 scripts/grok_api.py \
  --mode i2v \
  --image "https://example.com/character.png" \
  --prompt "The character turns around and walks away, hair flowing in the wind" \
  --duration 6 \
  --ratio 9:16
```

### 多图视频

```bash
python3 scripts/grok_api.py \
  --mode i2v \
  --image "img1.png" "img2.png" "img3.png" \
  --prompt "Scene transitions between the three locations, smooth camera movement" \
  --duration 10 \
  --ratio 16:9
```

### 视频扩展

```bash
python3 scripts/grok_api.py \
  --mode extend \
  --task-id "previous_task_id" \
  --prompt "Continue the scene, camera pans to the right showing more of the environment" \
  --extend-times 10
```

---

## 3. 提示词模板

### 写实人像模板

```
超高清写实摄影，杰作，最佳质量，8K UHD，raw photo，超高细节，锐利焦点

主体：[年龄] [性别]，[人种]，[气质]，[外貌特征]
服装：身着 [服装]，[材质] 面料，[细节]
场景：位于 [场景]，[环境描述]
光影：[光线类型]，[时间]，[氛围]
技术：[镜头]，[角度]，[构图]，[特效]
```

### 古风人像模板

```
古风人像，杰作，最佳质量，超高清，国风美学，东方韵味，精致细节

主体：[朝代] 时期 [性别]，[面容]，[发型]，[妆容]，[神态]
服装：身着 [汉服类型]，[面料]，[纹样]，[配饰]
场景：[场景]，[建筑]，[景致]
光影：[光线]，[时分]，[意境]
技术：[画风]，[画质]，[效果]
```

### CG 角色模板

```
杰作，最佳质量，超高清，3D渲染，CG艺术，虚幻引擎5，Octane渲染，精致细节

主体：[性别] 角色，[风格] 特征，[身份] 形象
服装：穿着 [服装]，[质感]，[装饰]
场景：[场景] 背景，[氛围]
光影：[光照]，[色调]，[情绪]
技术：[渲染]，[特效]，[品质]
```

---

## 4. 分镜提示词技巧

### 镜头术语

| 中文 | 英文 | 说明 |
|------|------|------|
| 特写 | Close-up / CU | 面部或细节 |
| 近景 | Medium Close-up / MCU | 胸部以上 |
| 中景 | Medium Shot / MS | 腰部以上 |
| 全景 | Full Shot / FS | 全身 |
| 远景 | Long Shot / LS | 环境为主 |

### 运镜术语

| 中文 | 英文 | 说明 |
|------|------|------|
| 推镜头 | Dolly In / Push In | 镜头向前推进 |
| 拉镜头 | Dolly Out / Pull Out | 镜头向后拉远 |
| 摇镜头 | Pan | 水平方向转动 |
| 移镜头 | Tracking / Dolly | 跟随移动 |
| 环绕 | Orbit | 围绕主体旋转 |
| 升降 | Crane Up/Down | 垂直方向移动 |

### 时间节奏

| 时长 | 用途 |
|------|------|
| 0-3秒 | 建立镜头、开场 |
| 3-5秒 | 动作展示 |
| 5-8秒 | 情绪渲染 |
| 8-10秒 | 复杂动作、场景切换 |
| 10-15秒 | 完整叙事段落 |

---

## 5. 常见问题

### Q: 如何保持角色一致性？

A: 使用图生图 (I2I) 模式，传入角色参考图：

```bash
python3 scripts/unified_workflow.py generate \
  --prompt "同样的角色，不同的场景" \
  --images "角色参考图.png"
```

### Q: 九宫格生成失败怎么办？

A: 九宫格生成耗时较长，确保：
1. 设置足够的 timeout (默认 900 秒)
2. 提示词不要过长
3. 参考图片不超过 3 张

### Q: 如何获取更好的生成质量？

A: 
1. 使用 4K 分辨率
2. 提示词要具体、详细
3. 使用风格模板
4. 提供高质量参考图

---

#图像生成 #视频生成 #Grok #NanoBanana #提示词 #分镜 #示例