#!/usr/bin/env python3
"""
统一工作流脚本 - 整合所有图像生成工作流

基于两个工作流 JSON 文件：
1. 万能图像生成器.json - 通用图像生成
2. SD专用资产生成.json - 角色资产、场景资产、九宫格分镜

使用 Nano Banana 2 API (Kie AI)

Author: Work-Fisher
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass

from nano_banana_api import NanoBananaClient, GenerationResult


# ============================================================
# 提示词模板
# ============================================================

# 通用图像生成模板
IMAGE_TEMPLATES = {
    "realistic": {
        "prefix": "超高清写实摄影，杰作，最佳质量，8K UHD，raw photo，超高细节，锐利焦点，",
        "suffix": "电影级光影，专业摄影"
    },
    "cg": {
        "prefix": "杰作，最佳质量，超高清，3D渲染，CG艺术，虚幻引擎5，Octane渲染，精致细节，",
        "suffix": "UE5渲染，动态模糊，粒子特效，16K分辨率"
    },
    "gufeng": {
        "prefix": "古风人像，杰作，最佳质量，超高清，国风美学，东方韵味，精致细节，",
        "suffix": "古风画意，电影级质感"
    },
    "anime": {
        "prefix": "动漫风格，杰作，最佳质量，精致画面，",
        "suffix": "日系动漫风格，高质量渲染"
    },
    "cinematic": {
        "prefix": "电影级画面，杰作，最佳质量，8K，cinematic，电影质感，",
        "suffix": "专业摄影，电影级光影"
    }
}

# 三视图提示词模板（来自 SD专用资产生成.json）
TRI_VIEW_PROMPT = """生成图中三视图，要求保持人物一致性，风格一致性，左边是人物上半身，中间是人物正面全身，右边是人物背面全身。
{character_description}"""

# 白底图提示词模板
WHITE_BG_PROMPT = """提取中间的主体物件，生成平面白底图。
{description}"""

# 鸟瞰图提示词模板（来自 SD专用资产生成.json）
BIRD_VIEW_PROMPT = """参考图1，生成超远距离鸟瞰视角，看场景全貌，无缝拼接，无畸变，无拼接缝，无暗角，8K超高清分辨率，超精细细节，照片级真实感，真实光影，自然色彩，专业摄影，焦点清晰，要求透视不畸变，场景完整。
{additional_prompt}"""

# 全景图提示词模板（来自 SD专用资产生成.json）
PANORAMIC_PROMPT = """参考图X，210度全景视图，完整210度环绕视角，等距柱状投影，超广全环绕环境，人眼平视视角，无缝拼接，无畸变，无拼接缝，无暗角，8K超高清分辨率，超精细细节，照片级真实感，真实光影，自然色彩，专业摄影，焦点清晰，要求透视不畸变，场景完整。
{additional_prompt}"""

# 九宫格分镜模板（来自 SD专用资产生成.json）
NINE_GRID_TEMPLATE = """生成一张专业级超高清 3x3 九宫格横版故事板分镜图，九个分镜色调统一，布局完美对称、干净专业，像官方动画分镜稿一样，整体为横版构图，纯白色背景，9个面板之间用细黑色线条（宽度2px）和均匀白色间距清晰分割。
所有9个面板必须保持高度一致的风格。
每个面板严格为16:9横版比例。
每个面板右下角添加白色小圆角矩形角标标签（黑色清晰字体）：1-1、1-2、1-3、1-4、1-5、1-6、1-7、1-8、1-9

【风格基准】
{style_base}

【分镜内容】
{shots_content}

每个面板独立成图且构图优秀，无任何文字、无字幕、无时间码、无水印、无风格漂移。
8k超高清，极其精细，masterpiece，cinematic质感。"""

# 三宫格分镜模板（来自 SD专用资产生成.json）
THREE_GRID_TEMPLATE = """生成一张专业级超高清 三宫格横版故事板分镜图，三个分镜色调统一，布局完美对称、干净专业，像官方动画分镜稿一样，整体为竖版构图，纯白色背景。
所有面板必须保持高度一致的风格。
{style_base}
每个面板严格为16:9横版比例。
每个面板右下角添加白色小圆角矩形角标标签（黑色清晰字体）：1-1、1-2、1-3。

【分镜内容】
{shots_content}

每个面板独立成图且构图优秀，无任何文字、无字幕、无时间码、无水印、无风格漂移。
8k超高清，极其精细，masterpiece，cinematic质感。"""

# 超高清放大模板
UPSCALE_PROMPT = """将这张图片，超分为4K超清画质，保留的所有细腻纹理、虹彩光泽，色彩还原准确，无噪点、无模糊，边缘锐利，画面干净。
{additional_prompt}"""


# ============================================================
# 工作流类
# ============================================================

@dataclass
class StoryboardShot:
    """分镜镜头"""
    shot_number: int
    shot_type: str
    description: str
    prompt: str
    image_url: Optional[str] = None


class UnifiedWorkflow:
    """统一工作流 - 基于 SD专用资产生成 + 万能图像生成器"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = NanoBananaClient(api_key)
    
    # -------------------------------------------------------
    # 1. 通用图像生成
    # -------------------------------------------------------
    
    def generate_image(
        self,
        prompt: str,
        style: str = "realistic",
        aspect_ratio: str = "auto",
        resolution: str = "1K",
        reference_images: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        通用图像生成
        
        Args:
            prompt: 提示词
            style: 风格模板
            aspect_ratio: 画幅比例
            resolution: 分辨率
            reference_images: 参考图片列表
        
        Returns:
            图像 URL
        """
        template = IMAGE_TEMPLATES.get(style, IMAGE_TEMPLATES["realistic"])
        full_prompt = f"{template['prefix']}{prompt}，{template['suffix']}"
        
        result = self.client.generate(
            prompt=full_prompt,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            image_input=reference_images
        )
        
        return result.image_url
    
    # -------------------------------------------------------
    # 2. 角色三视图生成
    # -------------------------------------------------------
    
    def generate_tri_view(
        self,
        character_description: str,
        reference_image: Optional[str] = None,
        resolution: str = "2K"
    ) -> Optional[str]:
        """
        生成角色三视图
        
        来自 SD专用资产生成.json 的三视图工作流
        
        Args:
            character_description: 角色描述
            reference_image: 角色参考图片 URL
            resolution: 分辨率
        
        Returns:
            图像 URL
        """
        print("生成角色三视图...")
        
        prompt = TRI_VIEW_PROMPT.format(character_description=character_description)
        
        images = [reference_image] if reference_image else None
        
        result = self.client.generate(
            prompt=prompt,
            aspect_ratio="16:9",  # 三视图并排
            resolution=resolution,
            image_input=images,
            timeout=600
        )
        
        if result.status == "completed":
            print(f"✓ 三视图生成完成: {result.image_url}")
            return result.image_url
        else:
            print(f"✗ 生成失败: {result.error}")
            return None
    
    # -------------------------------------------------------
    # 3. 白底图生成
    # -------------------------------------------------------
    
    def generate_white_background(
        self,
        image_url: str,
        description: str = "",
        resolution: str = "1K"
    ) -> Optional[str]:
        """
        生成白底图
        
        来自 SD专用资产生成.json 的白底图工作流
        
        Args:
            image_url: 原图 URL
            description: 补充描述
            resolution: 分辨率
        
        Returns:
            图像 URL
        """
        print("生成白底图...")
        
        prompt = WHITE_BG_PROMPT.format(description=description)
        
        result = self.client.generate(
            prompt=prompt,
            aspect_ratio="auto",
            resolution=resolution,
            image_input=[image_url]
        )
        
        if result.status == "completed":
            print(f"✓ 白底图生成完成: {result.image_url}")
            return result.image_url
        else:
            print(f"✗ 生成失败: {result.error}")
            return None
    
    # -------------------------------------------------------
    # 4. 场景鸟瞰图生成
    # -------------------------------------------------------
    
    def generate_bird_view(
        self,
        scene_image_url: str,
        additional_prompt: str = "",
        resolution: str = "4K"
    ) -> Optional[str]:
        """
        生成场景鸟瞰图
        
        来自 SD专用资产生成.json 的鸟瞰图工作流
        
        Args:
            scene_image_url: 场景图片 URL
            additional_prompt: 补充提示词
            resolution: 分辨率
        
        Returns:
            图像 URL
        """
        print("生成场景鸟瞰图...")
        
        prompt = BIRD_VIEW_PROMPT.format(additional_prompt=additional_prompt)
        
        result = self.client.generate(
            prompt=prompt,
            aspect_ratio="21:9",  # 宽画幅
            resolution=resolution,
            image_input=[scene_image_url],
            timeout=600
        )
        
        if result.status == "completed":
            print(f"✓ 鸟瞰图生成完成: {result.image_url}")
            return result.image_url
        else:
            print(f"✗ 生成失败: {result.error}")
            return None
    
    # -------------------------------------------------------
    # 5. 场景全景图生成
    # -------------------------------------------------------
    
    def generate_panoramic(
        self,
        scene_image_url: str,
        additional_prompt: str = "",
        resolution: str = "4K"
    ) -> Optional[str]:
        """
        生成场景全景图
        
        来自 SD专用资产生成.json 的全景图工作流
        
        Args:
            scene_image_url: 场景图片 URL
            additional_prompt: 补充提示词
            resolution: 分辨率
        
        Returns:
            图像 URL
        """
        print("生成场景全景图...")
        
        prompt = PANORAMIC_PROMPT.format(additional_prompt=additional_prompt)
        
        result = self.client.generate(
            prompt=prompt,
            aspect_ratio="21:9",  # 宽画幅
            resolution=resolution,
            image_input=[scene_image_url],
            timeout=600
        )
        
        if result.status == "completed":
            print(f"✓ 全景图生成完成: {result.image_url}")
            return result.image_url
        else:
            print(f"✗ 生成失败: {result.error}")
            return None
    
    # -------------------------------------------------------
    # 6. 九宫格分镜生成
    # -------------------------------------------------------
    
    def generate_9_grid_storyboard(
        self,
        shots_content: str,
        style_base: str = "写实暗黑国风，电影级cinematic质感，冷色调低饱和，高对比光影，8k超高清，16:9横版，无时间码，无字幕，无水印",
        reference_images: Optional[List[str]] = None,
        resolution: str = "4K"
    ) -> Optional[str]:
        """
        生成 3x3 九宫格分镜
        
        来自 SD专用资产生成.json 的九宫格工作流
        
        Args:
            shots_content: 分镜内容（完整描述）
            style_base: 风格基准
            reference_images: 参考图片列表（最多3张：场景、角色1、角色2）
            resolution: 分辨率
        
        Returns:
            图像 URL
        """
        print("生成九宫格分镜...")
        if reference_images:
            print(f"参考图片: {len(reference_images)} 张")
        
        prompt = NINE_GRID_TEMPLATE.format(
            style_base=style_base,
            shots_content=shots_content
        )
        
        # 最多使用前3张参考图
        images = reference_images[:3] if reference_images else None
        
        result = self.client.generate(
            prompt=prompt,
            aspect_ratio="16:9",
            resolution=resolution,
            image_input=images,
            timeout=900  # 九宫格生成较慢
        )
        
        if result.status == "completed":
            print(f"✓ 九宫格分镜生成完成: {result.image_url}")
            return result.image_url
        else:
            print(f"✗ 生成失败: {result.error}")
            return None
    
    # -------------------------------------------------------
    # 7. 三宫格分镜生成
    # -------------------------------------------------------
    
    def generate_3_grid_storyboard(
        self,
        shots_content: str,
        style_base: str = "写实暗黑国风，电影级cinematic质感，冷色调低饱和，高对比光影，8k超高清，16:9横版",
        reference_images: Optional[List[str]] = None,
        resolution: str = "2K"
    ) -> Optional[str]:
        """
        生成三宫格分镜
        
        来自 SD专用资产生成.json 的三宫格工作流
        
        Args:
            shots_content: 分镜内容
            style_base: 风格基准
            reference_images: 参考图片列表
            resolution: 分辨率
        
        Returns:
            图像 URL
        """
        print("生成三宫格分镜...")
        
        prompt = THREE_GRID_TEMPLATE.format(
            style_base=style_base,
            shots_content=shots_content
        )
        
        # 最多使用前3张参考图
        images = reference_images[:3] if reference_images else None
        
        result = self.client.generate(
            prompt=prompt,
            aspect_ratio="9:16",  # 竖版三宫格
            resolution=resolution,
            image_input=images,
            timeout=600
        )
        
        if result.status == "completed":
            print(f"✓ 三宫格分镜生成完成: {result.image_url}")
            return result.image_url
        else:
            print(f"✗ 生成失败: {result.error}")
            return None
    
    # -------------------------------------------------------
    # 8. 图像超高清放大
    # -------------------------------------------------------
    
    def upscale_image(
        self,
        image_url: str,
        aspect_ratio: str = "16:9",
        resolution: str = "4K",
        additional_prompt: str = ""
    ) -> Optional[str]:
        """
        图像超高清放大
        
        来自 SD专用资产生成.json 的放大工作流
        
        Args:
            image_url: 原图 URL
            aspect_ratio: 目标画幅
            resolution: 目标分辨率
            additional_prompt: 补充提示词
        
        Returns:
            图像 URL
        """
        print(f"图像超高清放大 ({resolution})...")
        
        prompt = UPSCALE_PROMPT.format(additional_prompt=additional_prompt)
        
        result = self.client.generate(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            image_input=[image_url],
            timeout=600
        )
        
        if result.status == "completed":
            print(f"✓ 放大完成: {result.image_url}")
            return result.image_url
        else:
            print(f"✗ 生成失败: {result.error}")
            return None
    
    # -------------------------------------------------------
    # 9. 批量生成
    # -------------------------------------------------------
    
    def batch_generate(
        self,
        prompts: List[str],
        aspect_ratio: str = "auto",
        resolution: str = "1K"
    ) -> List[GenerationResult]:
        """
        批量生成图像
        
        Args:
            prompts: 提示词列表
            aspect_ratio: 画幅比例
            resolution: 分辨率
        
        Returns:
            生成结果列表
        """
        return self.client.batch_generate(
            prompts=prompts,
            aspect_ratio=aspect_ratio,
            resolution=resolution
        )


# ============================================================
# CLI 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="统一图像生成工作流 - Nano Banana 2 (Kie AI)")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # generate: 通用图像生成
    gen_parser = subparsers.add_parser("generate", help="通用图像生成")
    gen_parser.add_argument("--prompt", "-p", required=True, help="提示词")
    gen_parser.add_argument("--style", "-s", default="realistic", 
                           choices=["realistic", "cg", "gufeng", "anime", "cinematic"],
                           help="风格模板")
    gen_parser.add_argument("--aspect-ratio", "-a", default="auto", help="画幅比例")
    gen_parser.add_argument("--resolution", "-r", default="1K", help="分辨率")
    gen_parser.add_argument("--images", "-i", nargs="+", help="参考图片URL列表")
    gen_parser.add_argument("--output", "-o", help="输出文件路径")
    
    # tri-view: 三视图
    tv_parser = subparsers.add_parser("tri-view", help="生成角色三视图")
    tv_parser.add_argument("--description", "-d", required=True, help="角色描述")
    tv_parser.add_argument("--image", "-i", help="角色参考图片URL")
    tv_parser.add_argument("--resolution", "-r", default="2K", help="分辨率")
    tv_parser.add_argument("--output", "-o", help="输出文件路径")
    
    # white-bg: 白底图
    wb_parser = subparsers.add_parser("white-bg", help="生成白底图")
    wb_parser.add_argument("--image", "-i", required=True, help="原图URL")
    wb_parser.add_argument("--description", "-d", default="", help="补充描述")
    wb_parser.add_argument("--output", "-o", help="输出文件路径")
    
    # bird-view: 鸟瞰图
    bv_parser = subparsers.add_parser("bird-view", help="生成场景鸟瞰图")
    bv_parser.add_argument("--image", "-i", required=True, help="场景图片URL")
    bv_parser.add_argument("--prompt", "-p", default="", help="补充提示词")
    bv_parser.add_argument("--resolution", "-r", default="4K", help="分辨率")
    bv_parser.add_argument("--output", "-o", help="输出文件路径")
    
    # panoramic: 全景图
    pn_parser = subparsers.add_parser("panoramic", help="生成场景全景图")
    pn_parser.add_argument("--image", "-i", required=True, help="场景图片URL")
    pn_parser.add_argument("--prompt", "-p", default="", help="补充提示词")
    pn_parser.add_argument("--resolution", "-r", default="4K", help="分辨率")
    pn_parser.add_argument("--output", "-o", help="输出文件路径")
    
    # 9grid: 九宫格分镜
    g9_parser = subparsers.add_parser("9grid", help="生成九宫格分镜")
    g9_parser.add_argument("--content", "-c", required=True, help="分镜内容")
    g9_parser.add_argument("--style", "-s", default="写实暗黑国风，电影级cinematic质感", help="风格基准")
    g9_parser.add_argument("--images", "-i", nargs="+", help="参考图片列表（场景、角色1、角色2）")
    g9_parser.add_argument("--resolution", "-r", default="4K", help="分辨率")
    g9_parser.add_argument("--output", "-o", help="输出文件路径")
    
    # 3grid: 三宫格分镜
    g3_parser = subparsers.add_parser("3grid", help="生成三宫格分镜")
    g3_parser.add_argument("--content", "-c", required=True, help="分镜内容")
    g3_parser.add_argument("--style", "-s", default="写实暗黑国风，电影级cinematic质感", help="风格基准")
    g3_parser.add_argument("--images", "-i", nargs="+", help="参考图片列表")
    g3_parser.add_argument("--resolution", "-r", default="2K", help="分辨率")
    g3_parser.add_argument("--output", "-o", help="输出文件路径")
    
    # upscale: 超高清放大
    up_parser = subparsers.add_parser("upscale", help="图像超高清放大")
    up_parser.add_argument("--image", "-i", required=True, help="原图URL")
    up_parser.add_argument("--aspect-ratio", "-a", default="16:9", help="目标画幅")
    up_parser.add_argument("--resolution", "-r", default="4K", help="目标分辨率")
    up_parser.add_argument("--prompt", "-p", default="", help="补充提示词")
    up_parser.add_argument("--output", "-o", help="输出文件路径")
    
    # batch: 批量生成
    batch_parser = subparsers.add_parser("batch", help="批量生成")
    batch_parser.add_argument("--file", "-f", required=True, help="提示词文件")
    batch_parser.add_argument("--aspect-ratio", "-a", default="auto", help="画幅比例")
    batch_parser.add_argument("--resolution", "-r", default="1K", help="分辨率")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        workflow = UnifiedWorkflow()
        url = None
        
        if args.command == "generate":
            url = workflow.generate_image(
                prompt=args.prompt,
                style=args.style,
                aspect_ratio=args.aspect_ratio,
                resolution=args.resolution,
                reference_images=args.images
            )
        
        elif args.command == "tri-view":
            url = workflow.generate_tri_view(
                character_description=args.description,
                reference_image=args.image,
                resolution=args.resolution
            )
        
        elif args.command == "white-bg":
            url = workflow.generate_white_background(
                image_url=args.image,
                description=args.description
            )
        
        elif args.command == "bird-view":
            url = workflow.generate_bird_view(
                scene_image_url=args.image,
                additional_prompt=args.prompt,
                resolution=args.resolution
            )
        
        elif args.command == "panoramic":
            url = workflow.generate_panoramic(
                scene_image_url=args.image,
                additional_prompt=args.prompt,
                resolution=args.resolution
            )
        
        elif args.command == "9grid":
            url = workflow.generate_9_grid_storyboard(
                shots_content=args.content,
                style_base=args.style,
                reference_images=args.images,
                resolution=args.resolution
            )
        
        elif args.command == "3grid":
            url = workflow.generate_3_grid_storyboard(
                shots_content=args.content,
                style_base=args.style,
                reference_images=args.images,
                resolution=args.resolution
            )
        
        elif args.command == "upscale":
            url = workflow.upscale_image(
                image_url=args.image,
                aspect_ratio=args.aspect_ratio,
                resolution=args.resolution,
                additional_prompt=args.prompt
            )
        
        elif args.command == "batch":
            with open(args.file, "r", encoding="utf-8") as f:
                prompts = [line.strip() for line in f if line.strip()]
            
            results = workflow.batch_generate(
                prompts=prompts,
                aspect_ratio=args.aspect_ratio,
                resolution=args.resolution
            )
            
            success = sum(1 for r in results if r.status == "completed")
            print(f"\n完成: {success}/{len(results)}")
            return
        
        # 输出结果
        if url:
            print(f"\n✓ 结果: {url}")
            
            if hasattr(args, 'output') and args.output:
                if workflow.client.download_image(url, args.output):
                    print(f"已保存到: {args.output}")
        else:
            print("\n✗ 生成失败")
    
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()