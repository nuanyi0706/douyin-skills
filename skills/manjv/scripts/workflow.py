#!/usr/bin/env python3
"""
manjv 工作流脚本

统一工作流入口，支持资产生成、分镜生成、视频生成、视频装配
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional, List

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from nanobanana_api import NanoBananaClient, GenerationResult
from grok_api import GrokClient
from video_assembler import VideoAssembler


# ============================================================
# 提示词模板
# ============================================================

# 角色三视图提示词
TRI_VIEW_PROMPT = """生成图中三视图，要求保持人物一致性，风格一致性，左边是人物上半身，中间是人物正面全身，右边是人物背面全身。
{character_description}"""

# 白底图提示词
WHITE_BG_PROMPT = """提取中间的主体物件，生成平面白底图。
{description}"""

# 鸟瞰图提示词
BIRD_VIEW_PROMPT = """参考图1，生成超远距离鸟瞰视角，看场景全貌，无缝拼接，无畸变，无拼接缝，无暗角，8K超高清分辨率，超精细细节，照片级真实感，真实光影，自然色彩，专业摄影，焦点清晰，要求透视不畸变，场景完整。
{additional_prompt}"""

# 全景图提示词
PANORAMIC_PROMPT = """参考图X，210度全景视图，完整210度环绕视角，等距柱状投影，超广全环绕环境，人眼平视视角，无缝拼接，无畸变，无拼接缝，无暗角，8K超高清分辨率，超精细细节，照片级真实感，真实光影，自然色彩，专业摄影，焦点清晰，要求透视不畸变，场景完整。
{additional_prompt}"""

# 九宫格分镜模板
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

# 三宫格分镜模板
THREE_GRID_TEMPLATE = """生成一张专业级超高清 三宫格横版故事板分镜图，三个分镜色调统一，布局完美对称、干净专业，像官方动画分镜稿一样，整体为竖版构图，纯白色背景。
所有面板必须保持高度一致的风格。
{style_base}
每个面板严格为16:9横版比例。
每个面板右下角添加白色小圆角矩形角标标签（黑色清晰字体）：1-1、1-2、1-3。

【分镜内容】
{shots_content}

每个面板独立成图且构图优秀，无任何文字、无字幕、无时间码、无水印、无风格漂移。
8k超高清，极其精细，masterpiece，cinematic质感。"""


# ============================================================
# 工作流类
# ============================================================

class ManjvWorkflow:
    """manjv 工作流"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.image_client = NanoBananaClient(api_key)
        self.video_client = GrokClient(api_key)
        self.assembler = VideoAssembler()
    
    # -------------------------------------------------------
    # 资产生成
    # -------------------------------------------------------
    
    def generate_character_tri_view(
        self,
        description: str,
        reference_image: Optional[str] = None,
        resolution: str = "2K"
    ) -> Optional[str]:
        """
        生成角色三视图
        
        Args:
            description: 角色描述
            reference_image: 角色参考图
            resolution: 分辨率
        
        Returns:
            图像 URL
        """
        print("🎨 生成角色三视图...")
        
        prompt = TRI_VIEW_PROMPT.format(character_description=description)
        images = [reference_image] if reference_image else None
        
        result = self.image_client.generate(
            prompt=prompt,
            aspect_ratio="16:9",
            resolution=resolution,
            image_input=images,
            timeout=600
        )
        
        if result.status == "completed":
            print(f"✅ 三视图生成完成: {result.image_url}")
            return result.image_url
        else:
            print(f"❌ 生成失败: {result.error}")
            return None
    
    def generate_white_background(
        self,
        image_url: str,
        description: str = "",
        resolution: str = "1K"
    ) -> Optional[str]:
        """生成白底图"""
        print("🎨 生成白底图...")
        
        prompt = WHITE_BG_PROMPT.format(description=description)
        
        result = self.image_client.generate(
            prompt=prompt,
            aspect_ratio="auto",
            resolution=resolution,
            image_input=[image_url]
        )
        
        if result.status == "completed":
            print(f"✅ 白底图生成完成: {result.image_url}")
            return result.image_url
        else:
            print(f"❌ 生成失败: {result.error}")
            return None
    
    def generate_bird_view(
        self,
        scene_image_url: str,
        additional_prompt: str = "",
        resolution: str = "4K"
    ) -> Optional[str]:
        """生成场景鸟瞰图"""
        print("🏞️ 生成场景鸟瞰图...")
        
        prompt = BIRD_VIEW_PROMPT.format(additional_prompt=additional_prompt)
        
        result = self.image_client.generate(
            prompt=prompt,
            aspect_ratio="21:9",
            resolution=resolution,
            image_input=[scene_image_url],
            timeout=600
        )
        
        if result.status == "completed":
            print(f"✅ 鸟瞰图生成完成: {result.image_url}")
            return result.image_url
        else:
            print(f"❌ 生成失败: {result.error}")
            return None
    
    def generate_panoramic(
        self,
        scene_image_url: str,
        additional_prompt: str = "",
        resolution: str = "4K"
    ) -> Optional[str]:
        """生成场景全景图"""
        print("🌐 生成场景全景图...")
        
        prompt = PANORAMIC_PROMPT.format(additional_prompt=additional_prompt)
        
        result = self.image_client.generate(
            prompt=prompt,
            aspect_ratio="21:9",
            resolution=resolution,
            image_input=[scene_image_url],
            timeout=600
        )
        
        if result.status == "completed":
            print(f"✅ 全景图生成完成: {result.image_url}")
            return result.image_url
        else:
            print(f"❌ 生成失败: {result.error}")
            return None
    
    # -------------------------------------------------------
    # 分镜生成
    # -------------------------------------------------------
    
    def generate_9grid_storyboard(
        self,
        shots_content: str,
        style_base: str = "写实电影风格，cinematic质感",
        reference_images: Optional[List[str]] = None,
        resolution: str = "4K"
    ) -> Optional[str]:
        """生成九宫格分镜"""
        print("📐 生成九宫格分镜...")
        
        prompt = NINE_GRID_TEMPLATE.format(
            style_base=style_base,
            shots_content=shots_content
        )
        
        images = reference_images[:3] if reference_images else None
        
        result = self.image_client.generate(
            prompt=prompt,
            aspect_ratio="16:9",
            resolution=resolution,
            image_input=images,
            timeout=900
        )
        
        if result.status == "completed":
            print(f"✅ 九宫格分镜生成完成: {result.image_url}")
            return result.image_url
        else:
            print(f"❌ 生成失败: {result.error}")
            return None
    
    def generate_3grid_storyboard(
        self,
        shots_content: str,
        style_base: str = "写实电影风格，cinematic质感",
        reference_images: Optional[List[str]] = None,
        resolution: str = "2K"
    ) -> Optional[str]:
        """生成三宫格分镜"""
        print("📐 生成三宫格分镜...")
        
        prompt = THREE_GRID_TEMPLATE.format(
            style_base=style_base,
            shots_content=shots_content
        )
        
        images = reference_images[:3] if reference_images else None
        
        result = self.image_client.generate(
            prompt=prompt,
            aspect_ratio="9:16",
            resolution=resolution,
            image_input=images,
            timeout=600
        )
        
        if result.status == "completed":
            print(f"✅ 三宫格分镜生成完成: {result.image_url}")
            return result.image_url
        else:
            print(f"❌ 生成失败: {result.error}")
            return None
    
    # -------------------------------------------------------
    # 视频生成
    # -------------------------------------------------------
    
    async def generate_video_i2v(
        self,
        image_urls: List[str],
        prompt: str,
        duration: str = "10",
        resolution: str = "720p"
    ) -> dict:
        """图生视频"""
        print(f"🎥 生成 I2V 视频 ({len(image_urls)} 张图)...")
        
        result = await self.video_client.image_to_video(
            prompt=prompt,
            image_urls=image_urls,
            duration=duration,
            resolution=resolution,
            wait=True
        )
        
        return result
    
    async def generate_video_t2v(
        self,
        prompt: str,
        duration: str = "10",
        ratio: str = "9:16",
        resolution: str = "720p"
    ) -> dict:
        """文生视频"""
        print("🎥 生成 T2V 视频...")
        
        result = await self.video_client.text_to_video(
            prompt=prompt,
            aspect_ratio=ratio,
            duration=duration,
            resolution=resolution,
            wait=True
        )
        
        return result
    
    # -------------------------------------------------------
    # 视频装配
    # -------------------------------------------------------
    
    async def assemble_video(
        self,
        video_clips: List[str],
        output_file: str
    ) -> bool:
        """视频拼接"""
        print(f"✂️ 拼接 {len(video_clips)} 个视频片段...")
        
        success = await self.assembler.concat(video_clips, output_file)
        
        if success:
            print(f"✅ 视频装配完成: {output_file}")
        else:
            print(f"❌ 视频装配失败")
        
        return success


# ============================================================
# CLI 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="manjv 工作流脚本")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # generate-asset: 资产生成
    asset_parser = subparsers.add_parser("generate-asset", help="资产生成")
    asset_parser.add_argument("--type", "-t", required=True,
                             choices=["character-tri-view", "white-bg", "scene-bird-view", "scene-panoramic"],
                             help="资产类型")
    asset_parser.add_argument("--description", "-d", default="", help="描述")
    asset_parser.add_argument("--image", "-i", default=None, help="参考图片")
    asset_parser.add_argument("--resolution", "-r", default="2K", help="分辨率")
    
    # generate-storyboard: 分镜生成
    storyboard_parser = subparsers.add_parser("generate-storyboard", help="分镜生成")
    storyboard_parser.add_argument("--type", "-t", required=True,
                                  choices=["9grid", "3grid"],
                                  help="分镜类型")
    storyboard_parser.add_argument("--content", "-c", required=True, help="分镜内容")
    storyboard_parser.add_argument("--style", "-s", default="写实电影风格", help="风格基准")
    storyboard_parser.add_argument("--images", "-i", nargs="*", help="参考图片")
    storyboard_parser.add_argument("--resolution", "-r", default="4K", help="分辨率")
    
    # generate-video: 视频生成
    video_parser = subparsers.add_parser("generate-video", help="视频生成")
    video_parser.add_argument("--mode", "-m", required=True, choices=["i2v", "t2v"], help="生成模式")
    video_parser.add_argument("--prompt", "-p", required=True, help="提示词")
    video_parser.add_argument("--images", "-i", nargs="*", help="图片列表(I2V)")
    video_parser.add_argument("--duration", "-d", default="10", help="时长")
    video_parser.add_argument("--ratio", "-r", default="9:16", help="画面比例(T2V)")
    
    # assemble: 视频装配
    assemble_parser = subparsers.add_parser("assemble", help="视频装配")
    assemble_parser.add_argument("--clips", "-c", nargs="+", required=True, help="视频片段")
    assemble_parser.add_argument("--output", "-o", default="output.mp4", help="输出文件")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        workflow = ManjvWorkflow()
        
        if args.command == "generate-asset":
            url = None
            
            if args.type == "character-tri-view":
                url = workflow.generate_character_tri_view(
                    description=args.description,
                    reference_image=args.image,
                    resolution=args.resolution
                )
            elif args.type == "white-bg":
                if not args.image:
                    print("❌ white-bg 需要 --image 参数")
                    return
                url = workflow.generate_white_background(
                    image_url=args.image,
                    description=args.description,
                    resolution=args.resolution
                )
            elif args.type == "scene-bird-view":
                if not args.image:
                    print("❌ scene-bird-view 需要 --image 参数")
                    return
                url = workflow.generate_bird_view(
                    scene_image_url=args.image,
                    additional_prompt=args.description,
                    resolution=args.resolution
                )
            elif args.type == "scene-panoramic":
                if not args.image:
                    print("❌ scene-panoramic 需要 --image 参数")
                    return
                url = workflow.generate_panoramic(
                    scene_image_url=args.image,
                    additional_prompt=args.description,
                    resolution=args.resolution
                )
            
            if url:
                print(f"\n✅ 完成: {url}")
        
        elif args.command == "generate-storyboard":
            url = None
            
            if args.type == "9grid":
                url = workflow.generate_9grid_storyboard(
                    shots_content=args.content,
                    style_base=args.style,
                    reference_images=args.images,
                    resolution=args.resolution
                )
            elif args.type == "3grid":
                url = workflow.generate_3grid_storyboard(
                    shots_content=args.content,
                    style_base=args.style,
                    reference_images=args.images,
                    resolution=args.resolution
                )
            
            if url:
                print(f"\n✅ 完成: {url}")
        
        elif args.command == "generate-video":
            if args.mode == "i2v":
                if not args.images:
                    print("❌ I2V 模式需要 --images 参数")
                    return
                result = asyncio.run(workflow.generate_video_i2v(
                    image_urls=args.images,
                    prompt=args.prompt,
                    duration=args.duration
                ))
            else:
                result = asyncio.run(workflow.generate_video_t2v(
                    prompt=args.prompt,
                    duration=args.duration,
                    ratio=args.ratio
                ))
            
            if result.get("status") == "success":
                print(f"\n✅ 视频生成完成")
                if result.get("output_url"):
                    print(f"   URL: {result.get('output_url')}")
                if result.get("output_path"):
                    print(f"   文件: {result.get('output_path')}")
            else:
                print(f"\n❌ 生成失败: {result.get('error')}")
        
        elif args.command == "assemble":
            success = asyncio.run(workflow.assemble_video(
                video_clips=args.clips,
                output_file=args.output
            ))
            
            if success:
                print(f"\n✅ 装配完成: {args.output}")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
