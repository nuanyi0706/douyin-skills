#!/usr/bin/env python3
"""
manjv - AI 短漫剧一站式生产平台

基于 LumenX Studio 架构设计，整合 Nano Banana 2 + Grok 实现完整创作链路
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))


class ManjvGenerator:
    """manjv 短漫剧生成器主类"""
    
    def __init__(
        self,
        output_dir: str = "./output",
        image_model: str = "nanobanana2",
        video_model: str = "grok",
        duration: str = "10",
        ratio: str = "9:16"
    ):
        self.output_dir = Path(output_dir)
        self.image_model = image_model
        self.video_model = video_model
        self.duration = duration
        self.ratio = ratio
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 环境变量检查
        self._check_env()
    
    def _check_env(self):
        """检查环境变量配置"""
        if not os.getenv("KIE_API_KEY"):
            print("ℹ️  未设置 KIE_API_KEY 环境变量")
    
    async def analyze_script(self, script_text: str) -> Dict[str, Any]:
        """
        剧本分析：深度分析小说文本
        
        Args:
            script_text: 小说/剧情文本
        
        Returns:
            分析结果字典
        """
        print("📝 开始剧本分析...\n")
        
        # Step 1: 识别角色
        print("🎭 Step 1: 提取角色")
        characters = await self._extract_characters(script_text)
        print(f"   发现角色：{len(characters)} 个\n")
        
        # Step 2: 识别场景
        print("🏞️  Step 2: 提取场景")
        scenes = await self._extract_scenes(script_text)
        print(f"   发现场景：{len(scenes)} 个\n")
        
        # Step 3: 识别道具
        print("🎬 Step 3: 提取道具")
        props = await self._extract_props(script_text)
        print(f"   发现道具：{len(props)} 个\n")
        
        # Step 4: 生成故事结构
        print("📖 Step 4: 分析故事结构")
        structure = await self._analyze_structure(script_text)
        print(f"   幕数：{structure.get('acts', 1)}")
        print(f"   场景数：{structure.get('scenes', 1)}\n")
        
        return {
            "characters": characters,
            "scenes": scenes,
            "props": props,
            "structure": structure,
            "script": script_text
        }
    
    async def _extract_characters(self, text: str) -> List[Dict[str, str]]:
        """提取角色"""
        # TODO: 调用 LLM 提取角色
        return []
    
    async def _extract_scenes(self, text: str) -> List[Dict[str, str]]:
        """提取场景"""
        # TODO: 调用 LLM 提取场景
        return []
    
    async def _extract_props(self, text: str) -> List[Dict[str, str]]:
        """提取道具"""
        # TODO: 调用 LLM 提取道具
        return []
    
    async def _analyze_structure(self, text: str) -> Dict[str, Any]:
        """分析故事结构"""
        # TODO: 调用 LLM 分析结构
        return {
            "acts": 1,
            "scenes": 1,
            "duration": self.duration
        }
    
    async def generate_assets(self, asset_type: str, description: str, reference_image: Optional[str] = None) -> Dict[str, Any]:
        """
        资产生成：角色、场景、道具
        
        Args:
            asset_type: 资产类型 (character-tri-view, scene-bird-view, etc.)
            description: 描述
            reference_image: 参考图
        
        Returns:
            生成结果
        """
        print(f"🎨 生成资产: {asset_type}...\n")
        
        if asset_type == "character-tri-view":
            from scripts.nanobanana_api import NanoBananaClient
            client = NanoBananaClient()
            
            prompt = f"""生成图中三视图，要求保持人物一致性，风格一致性，
左边是人物上半身，中间是人物正面全身，右边是人物背面全身。
{description}"""
            
            result = client.generate(
                prompt=prompt,
                aspect_ratio="16:9",
                resolution="2K",
                image_input=[reference_image] if reference_image else None
            )
            
            return {"status": result.status, "image_url": result.image_url}
        
        return {"status": "pending"}
    
    async def generate_storyboard(
        self,
        storyboard_type: str,
        content: str,
        style: str = "写实电影风格",
        reference_images: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        生成分镜
        
        Args:
            storyboard_type: 分镜类型 (9grid, 3grid)
            content: 分镜内容描述
            style: 风格基准
            reference_images: 参考图列表
        
        Returns:
            生成结果
        """
        print(f"📐 生成分镜: {storyboard_type}...\n")
        
        from scripts.nanobanana_api import NanoBananaClient
        client = NanoBananaClient()
        
        if storyboard_type == "9grid":
            prompt = f"""生成一张专业级超高清 3x3 九宫格横版故事板分镜图，
九个分镜色调统一，布局完美对称、干净专业，像官方动画分镜稿一样，
整体为横版构图，纯白色背景，9个面板之间用细黑色线条（宽度2px）和均匀白色间距清晰分割。

所有9个面板必须保持高度一致的风格。
每个面板严格为16:9横版比例。
每个面板右下角添加白色小圆角矩形角标标签（黑色清晰字体）：1-1、1-2、1-3、1-4、1-5、1-6、1-7、1-8、1-9

【风格基准】
{style}

【分镜内容】
{content}

每个面板独立成图且构图优秀，无任何文字、无字幕、无时间码、无水印、无风格漂移。
8k超高清，极其精细，masterpiece，cinematic质感。"""
            
            result = client.generate(
                prompt=prompt,
                aspect_ratio="16:9",
                resolution="4K",
                image_input=reference_images[:3] if reference_images else None
            )
            
            return {"status": result.status, "image_url": result.image_url}
        
        return {"status": "pending"}
    
    async def generate_video(
        self,
        mode: str,
        prompt: str,
        images: Optional[List[str]] = None,
        duration: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        视频生成
        
        Args:
            mode: 模式 (i2v, t2v)
            prompt: 提示词
            images: 图片列表 (I2V 模式)
            duration: 时长
        
        Returns:
            生成结果
        """
        print(f"🎥 生成视频: {mode}...\n")
        
        from scripts.grok_api import GrokClient
        client = GrokClient()
        
        duration = duration or self.duration
        
        if mode == "i2v" and images:
            result = await client.image_to_video(
                prompt=prompt,
                image_urls=images,
                duration=duration,
                resolution="720p",
                wait=True
            )
            return result
        elif mode == "t2v":
            result = await client.text_to_video(
                prompt=prompt,
                aspect_ratio=self.ratio,
                duration=duration,
                resolution="720p",
                wait=True
            )
            return result
        
        return {"status": "failed", "error": "Invalid mode"}
    
    async def assemble_video(self, video_clips: List[str], output_name: str = "final_drama.mp4") -> Path:
        """
        视频装配：ffmpeg 拼接
        
        Args:
            video_clips: 视频片段列表
            output_name: 输出文件名
        
        Returns:
            最终视频路径
        """
        print(f"✂️  装配视频: {len(video_clips)} 个片段...\n")
        
        from scripts.video_assembler import VideoAssembler
        
        assembler = VideoAssembler()
        output_path = self.output_dir / output_name
        
        await assembler.concat(video_clips, str(output_path))
        
        return output_path


async def main():
    parser = argparse.ArgumentParser(description="manjv - AI 短漫剧一站式生产平台")
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # analyze: 剧本分析
    analyze_parser = subparsers.add_parser("analyze", help="剧本分析")
    analyze_parser.add_argument("--script", "-s", required=True, help="剧本/小说文本")
    analyze_parser.add_argument("--output", "-o", default="./analysis.json", help="输出文件")
    
    # generate-asset: 资产生成
    asset_parser = subparsers.add_parser("generate-asset", help="资产生成")
    asset_parser.add_argument("--type", "-t", required=True, 
                             choices=["character-tri-view", "scene-bird-view", "scene-panoramic", "white-bg"],
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
    video_parser.add_argument("--images", "-i", nargs="*", help="图片列表(I2V模式)")
    video_parser.add_argument("--duration", "-d", default="10", help="时长(秒)")
    
    # assemble: 视频装配
    assemble_parser = subparsers.add_parser("assemble", help="视频装配")
    assemble_parser.add_argument("--clips", "-c", nargs="+", required=True, help="视频片段")
    assemble_parser.add_argument("--output", "-o", default="final_drama.mp4", help="输出文件")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    generator = ManjvGenerator()
    
    try:
        if args.command == "analyze":
            result = await generator.analyze_script(args.script)
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 分析完成: {args.output}")
        
        elif args.command == "generate-asset":
            result = await generator.generate_assets(
                asset_type=args.type,
                description=args.description,
                reference_image=args.image
            )
            print(f"\n✅ 资产生成完成: {result}")
        
        elif args.command == "generate-storyboard":
            result = await generator.generate_storyboard(
                storyboard_type=args.type,
                content=args.content,
                style=args.style,
                reference_images=args.images
            )
            print(f"\n✅ 分镜生成完成: {result}")
        
        elif args.command == "generate-video":
            result = await generator.generate_video(
                mode=args.mode,
                prompt=args.prompt,
                images=args.images,
                duration=args.duration
            )
            print(f"\n✅ 视频生成完成: {result}")
        
        elif args.command == "assemble":
            result = await generator.assemble_video(args.clips, args.output)
            print(f"\n✅ 视频装配完成: {result}")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
