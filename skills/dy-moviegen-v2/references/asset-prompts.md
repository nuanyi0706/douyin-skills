# 资产库提示词模板

> 快速参考 - 场景/角色资产生成

---

## 场景设定提示词

### 鸟瞰图（21:9 比例）

```
参考图X，生成超远距离鸟瞰视角，看场景全貌，无缝拼接，无畸变，无拼接缝，无暗角，8K超高清分辨率，超精细细节，照片级真实感，真实光影，自然色彩，专业摄影，焦点清晰，要求透视不畸变，场景完整
```

**命令**：
```bash
python3 scripts/unified_workflow.py bird-view \
  --image "场景参考图.png" \
  --resolution 4K
```

---

### 210度全景视图

```
参考图X，210度全景视图，完整210度环绕视角，等距柱状投影，超广全环绕环境，人眼平视视角，无缝拼接，无畸变，无拼接缝，无暗角，8K超高清分辨率，超精细细节，照片级真实感，真实光影，自然色彩，专业摄影，焦点清晰，要求透视不畸变，场景完整
```

**命令**：
```bash
python3 scripts/unified_workflow.py panoramic \
  --image "场景参考图.png" \
  --resolution 4K
```

---

## 角色三视图设定提示词

```
生成图中人物三视图，要求白底图，保持人物一致性，风格一致性，左边是人物上半身，中间是人物正面全身，右边是人物背面全身
```

**命令**：
```bash
python3 scripts/unified_workflow.py tri-view \
  --description "角色描述" \
  --image "角色参考图.png" \
  --resolution 2K
```

---

## 资产生成提示词

```
提取中间的主体物件，生成平面白底图
```

**命令**：
```bash
python3 scripts/unified_workflow.py white-bg \
  --image "原图.png"
```

---

## 快速参考表

| 资产类型 | 提示词关键词 | 画幅 | 分辨率 |
|----------|--------------|------|--------|
| 鸟瞰图 | 超远距离鸟瞰视角 | 21:9 | 4K |
| 全景图 | 210度全景视图 | 21:9 | 4K |
| 三视图 | 人物三视图，白底图 | 16:9 | 2K |
| 白底图 | 提取主体，平面白底图 | auto | 1K |

---

## 使用示例

```bash
# 设置 API Key
export KIE_API_KEY="your-api-key"

# 场景鸟瞰图
python3 scripts/unified_workflow.py bird-view \
  --image "便利店场景.png" \
  --resolution 4K

# 场景全景图
python3 scripts/unified_workflow.py panoramic \
  --image "古风建筑.png" \
  --resolution 4K

# 角色三视图
python3 scripts/unified_workflow.py tri-view \
  --description "古风少女，身穿白色汉服，手持玉笛" \
  --image "角色参考.png" \
  --resolution 2K

# 白底资产图
python3 scripts/unified_workflow.py white-bg \
  --image "产品图.png"
```

---

#资产生成 #鸟瞰图 #全景图 #三视图 #白底图