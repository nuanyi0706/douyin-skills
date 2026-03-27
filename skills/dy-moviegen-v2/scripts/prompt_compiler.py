"""
提示词编译器 - 专业视频生成提示词生成

整合好莱坞大师级导演/编剧/摄影经验
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


# 好莱坞大师角色设定
DIRECTOR_SYSTEM_PROMPT = """你是一个拥有120年的好莱坞电影制作经验的全能导演和编剧和摄影大师，拥有专业和丰富的编剧经验和丰富的制作经验和丰富的运镜技巧经验。

你的职责是将用户的简单描述转化为专业、精准、有电影质感的视频生成提示词。

你的核心能力：
- 120年好莱坞电影制作经验，深谙叙事结构与节奏把控
- 精通编剧技巧：三幕结构、英雄之旅、非线性叙事等
- 精通运镜技巧：推拉摇移、环绕、升降、跟拍、希区柯克变焦等
- 精通光影设计：伦勃朗光、逆光、体积光、丁达尔效应等
- 精通画面构图：三分法、黄金比例、对称构图、框架构图等
- 精通色调控制：电影级调色、情绪渲染、氛围营造

生成提示词时，请遵循以下原则：
1. 镜头语言要专业准确（使用标准电影术语）
2. 画面描述要具体细腻（光线、质感、情绪）
3. 动作节奏要张弛有度（起承转合）
4. 整体风格要统一协调（色调、氛围、音乐）
"""


@dataclass
class ShotInfo:
    """镜头信息"""
    id: int
    time_range: str
    camera: str
    movement: str
    action: str
    audio: str
    style: str = ""
    lighting: str = ""
    mood: str = ""


class PromptCompiler:
    """提示词编译器"""
    
    def __init__(self, system_prompt: str = DIRECTOR_SYSTEM_PROMPT):
        self.system_prompt = system_prompt
    
    def compile(
        self,
        user_input: str,
        style: str = "",
        duration: str = "10s",
        ratio: str = "16:9",
        shots: Optional[List[ShotInfo]] = None
    ) -> str:
        """
        编译生成专业视频提示词
        
        Args:
            user_input: 用户原始输入
            style: 风格描述
            duration: 时长
            ratio: 画面比例
            shots: 分镜信息列表
        
        Returns:
            专业视频生成提示词
        """
        # 如果有分镜信息，按分镜编译
        if shots:
            return self._compile_from_shots(shots, style, duration, ratio)
        
        # 否则从用户输入直接编译
        return self._compile_from_input(user_input, style, duration, ratio)
    
    def _compile_from_input(
        self,
        user_input: str,
        style: str,
        duration: str,
        ratio: str
    ) -> str:
        """从用户输入编译提示词"""
        
        # 画面比例转换
        aspect_map = {
            "16:9": "landscape, widescreen cinematic",
            "9:16": "portrait, vertical format",
            "1:1": "square format"
        }
        aspect_desc = aspect_map.get(ratio, "landscape")
        
        # 时长帧数转换
        duration_map = {
            "5s": "5 seconds",
            "10s": "10 seconds",
            "15s": "15 seconds"
        }
        duration_desc = duration_map.get(duration, "10 seconds")
        
        # 构建专业提示词
        prompt = self._build_professional_prompt(
            user_input=user_input,
            style=style,
            duration=duration_desc,
            aspect=aspect_desc
        )
        
        return prompt
    
    def _compile_from_shots(
        self,
        shots: List[ShotInfo],
        style: str,
        duration: str,
        ratio: str
    ) -> str:
        """从分镜信息编译提示词"""
        
        parts = []
        
        # 风格总纲
        if style:
            parts.append(f"【风格】{style}")
        
        # 画幅
        aspect_map = {
            "16:9": "电影宽屏 16:9",
            "9:16": "竖屏 9:16",
            "1:1": "方形 1:1"
        }
        parts.append(f"【画幅】{aspect_map.get(ratio, '16:9')}")
        
        parts.append("")  # 空行
        
        # 分镜描述
        for shot in shots:
            shot_desc = self._format_shot(shot)
            parts.append(shot_desc)
        
        return "\n".join(parts)
    
    def _format_shot(self, shot: ShotInfo) -> str:
        """格式化单个镜头"""
        parts = [f"{shot.time_range}："]
        
        # 镜头语言
        camera_parts = []
        if shot.camera:
            camera_parts.append(shot.camera)
        if shot.movement:
            camera_parts.append(shot.movement)
        if camera_parts:
            parts.append(" ".join(camera_parts) + "，")
        
        # 动作描述
        if shot.action:
            parts.append(shot.action)
        
        # 光影
        if shot.lighting:
            parts.append(f"，光线：{shot.lighting}")
        
        # 情绪氛围
        if shot.mood:
            parts.append(f"，氛围：{shot.mood}")
        
        # 音效
        if shot.audio:
            parts.append(f"，音效：{shot.audio}")
        
        return "".join(parts)
    
    def _build_professional_prompt(
        self,
        user_input: str,
        style: str,
        duration: str,
        aspect: str
    ) -> str:
        """构建专业级提示词"""
        
        # 基于好莱坞经验的提示词结构
        prompt = f"""Cinematic video, {duration}, {aspect}.

{user_input}

Technical specifications:
- Camera: Professional cinema camera, shallow depth of field
- Lighting: Cinematic three-point lighting, natural rim light
- Color: Film-grade color grading, rich contrast
- Motion: Smooth camera movement, professional gimbal work
- Quality: 4K resolution, high detail, professional production value
"""
        
        if style:
            prompt = f"""Cinematic {style} style video, {duration}, {aspect}.

{user_input}

Style: {style}
Technical: Professional {style.lower()} cinematography, atmospheric lighting, cinematic color palette.
"""
        
        return prompt.strip()
    
    def compile_from_shot(
        self,
        shot: ShotInfo,
        style: str = "",
        duration: str = "10s",
        ratio: str = "16:9"
    ) -> str:
        """从单个镜头信息编译提示词"""
        return self._format_shot(shot)
    
    def enhance_prompt(self, base_prompt: str, enhancement_type: str = "cinematic") -> str:
        """
        增强基础提示词
        
        Args:
            base_prompt: 基础提示词
            enhancement_type: 增强类型 (cinematic/dramatic/ethereal/action)
        
        Returns:
            增强后的提示词
        """
        enhancements = {
            "cinematic": """
Cinematic quality: Film-grade production, professional color grading, atmospheric lighting, 
smooth camera movement, shallow depth of field, 4K detail.""",
            
            "dramatic": """
Dramatic intensity: High contrast lighting, emotional close-ups, dynamic camera angles,
tension-building composition, powerful visual storytelling.""",
            
            "ethereal": """
Ethereal atmosphere: Soft diffused lighting, dreamy color palette, floating camera movement,
magical particles, otherworldly ambiance.""",
            
            "action": """
Action sequence: Dynamic camera work, fast cuts rhythm, explosive energy, 
impactful motion blur, adrenaline-pumping pace."""
        }
        
        enhancement = enhancements.get(enhancement_type, enhancements["cinematic"])
        return f"{base_prompt}\n{enhancement}"


def compile_video_prompt(
    user_input: str,
    style: str = "",
    duration: str = "10s",
    ratio: str = "16:9"
) -> str:
    """
    便捷函数：编译视频提示词
    
    Args:
        user_input: 用户输入描述
        style: 风格
        duration: 时长
        ratio: 画面比例
    
    Returns:
        专业视频生成提示词
    """
    compiler = PromptCompiler()
    return compiler.compile(user_input, style, duration, ratio)


# CLI 测试
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python prompt_compiler.py '用户描述' [风格] [时长] [比例]")
        print("示例: python prompt_compiler.py '一只猫咪在阳光下打盹' '治愈系' '10s' '16:9'")
        sys.exit(1)
    
    user_input = sys.argv[1]
    style = sys.argv[2] if len(sys.argv) > 2 else ""
    duration = sys.argv[3] if len(sys.argv) > 3 else "10s"
    ratio = sys.argv[4] if len(sys.argv) > 4 else "16:9"
    
    print("=" * 60)
    print("🎬 好莱坞大师级提示词编译器")
    print("=" * 60)
    print(f"\n📝 用户输入：{user_input}")
    print(f"🎨 风格：{style or '自动'}")
    print(f"⏱️  时长：{duration}")
    print(f"📐 比例：{ratio}")
    print("\n" + "=" * 60)
    print("📋 生成提示词：")
    print("=" * 60 + "\n")
    
    prompt = compile_video_prompt(user_input, style, duration, ratio)
    print(prompt)
    print("\n" + "=" * 60)