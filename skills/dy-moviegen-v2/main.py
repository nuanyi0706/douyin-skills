#!/usr/bin/env python3
"""
短剧生成 Agent v2 - 主入口

整合 Grok Imagine API + 剪映自动化 + 多 Agent 协作
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))


class ShortDramaGenerator:
    """短剧生成器主类"""
    
    def __init__(
        self,
        platform: str = "grok",
        cookies_path: Optional[str] = None,
        output_dir: str = "./output",
        duration: str = "6",
        ratio: str = "9:16",
        model: str = "Grok Imagine"
    ):
        self.platform = platform
        self.cookies_path = cookies_path
        self.output_dir = Path(output_dir)
        self.duration = duration
        self.ratio = ratio
        self.model = model
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 环境变量检查
        self._check_env()
    
    def _check_env(self):
        """检查环境变量配置"""
        if self.platform == "grok":
            if not os.getenv("GROK_API_KEY") and not os.getenv("SORA2_API_KEY"):
                print("ℹ️  使用默认 API Key")
        elif self.platform == "jianying":
            if self.cookies_path and not Path(self.cookies_path).exists():
                print(f"⚠️  Cookies 文件不存在：{self.cookies_path}")
                print("请从浏览器导出剪映 cookies.json")
    
    async def generate(self, input_text: str) -> dict:
        """
        生成短剧的完整流程
        
        Args:
            input_text: 用户输入，格式如 "风格：港风悬疑\n内容：外卖员发现..."
        
        Returns:
            生成结果字典
        """
        print("🎬 开始短剧生成流程...\n")
        
        # Step 1: 解析用户输入
        print("📝 Step 1: 解析用户输入")
        parsed = self._parse_input(input_text)
        print(f"   风格：{parsed.get('style', '未指定')}")
        print(f"   内容：{parsed.get('content', '未指定')[:50]}...\n")
        
        # Step 2: 导演 Agent - 整体规划
        print("🎭 Step 2: 导演统筹 - 规划整体节奏")
        director_plan = await self._director_agent(parsed)
        print(f"   分段数：{director_plan.get('segments', 1)}")
        print(f"   总时长：{director_plan.get('total_duration', self.duration)}\n")
        
        # Step 3: 编剧 Agent - 脚本创作
        print("✍️  Step 3: 编剧创作 - 生成脚本和台词")
        script = await self._writer_agent(parsed, director_plan)
        print(f"   场景数：{len(script.get('scenes', []))}")
        print(f"   台词数：{len(script.get('dialogues', []))}\n")
        
        # Step 4: 分镜 Agent - 镜头设计
        print("🎥 Step 4: 分镜设计 - 拆解镜头")
        storyboard = await self._storyboard_agent(script, director_plan)
        print(f"   镜头数：{len(storyboard.get('shots', []))}\n")
        
        # Step 5: 提示词编译 - 专业提示词生成
        print("📝 Step 5: 提示词编译 - 好莱坞大师级提示词生成")
        prompts = await self._compile_prompts(storyboard, parsed.get("style", ""))
        print(f"   提示词数：{len(prompts)}\n")
        
        # Step 6: 视频生成
        print(f"🤖 Step 6: 视频生成 - 使用 {self.platform} 平台")
        video_results = await self._generate_videos(prompts)
        print(f"   生成视频数：{len(video_results)}\n")
        
        # Step 7: 剪辑装配
        print("✂️  Step 7: 剪辑装配 - ffmpeg 拼接")
        final_video = await self._assemble_video(video_results)
        print(f"   最终视频：{final_video}\n")
        
        return {
            "status": "success",
            "final_video": str(final_video),
            "storyboard": storyboard,
            "prompts": prompts,
            "video_segments": video_results
        }
    
    def _parse_input(self, input_text: str) -> dict:
        """解析用户输入"""
        result = {"raw": input_text}
        
        for line in input_text.strip().split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
            elif "：" in line:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
        
        return result
    
    async def _director_agent(self, parsed: dict) -> dict:
        """导演 Agent：整体规划"""
        # TODO: 调用 LLM 进行整体规划
        return {
            "segments": 1,
            "total_duration": self.duration,
            "structure": "single_shot",
            "pacing": "normal"
        }
    
    async def _writer_agent(self, parsed: dict, plan: dict) -> dict:
        """编剧 Agent：脚本创作"""
        # TODO: 调用 LLM 生成脚本
        return {
            "scenes": [
                {
                    "id": 1,
                    "description": parsed.get("content", ""),
                    "duration": "10s"
                }
            ],
            "dialogues": [],
            "narration": ""
        }
    
    async def _storyboard_agent(self, script: dict, plan: dict) -> dict:
        """分镜 Agent：镜头设计"""
        # TODO: 生成分镜设计
        return {
            "shots": [
                {
                    "id": 1,
                    "time_range": "0-10s",
                    "camera": "Medium Shot",
                    "movement": "Slow Dolly In",
                    "action": script["scenes"][0]["description"],
                    "audio": "Background music"
                }
            ]
        }
    
    async def _compile_prompts(self, storyboard: dict, style: str = "") -> list:
        """提示词编译：生成专业视频提示词"""
        from scripts.prompt_compiler import PromptCompiler, ShotInfo
        
        compiler = PromptCompiler()
        prompts = []
        
        for shot in storyboard.get("shots", []):
            # 构建 ShotInfo 对象
            shot_info = ShotInfo(
                id=shot.get("id", 1),
                time_range=shot.get("time_range", "0-10s"),
                camera=shot.get("camera", ""),
                movement=shot.get("movement", ""),
                action=shot.get("action", ""),
                audio=shot.get("audio", ""),
                style=style,
                lighting=shot.get("lighting", ""),
                mood=shot.get("mood", "")
            )
            
            # 编译提示词
            prompt = compiler.compile_from_shot(shot_info, style, self.duration, self.ratio)
            prompts.append(prompt)
        
        return prompts
    
    async def _generate_videos(self, prompts: list) -> list:
        """视频生成"""
        results = []
        
        if self.platform == "jianying":
            # 使用剪映自动化
            from scripts.jianying_worker import JianyingWorker
            
            worker = JianyingWorker(
                cookies_path=self.cookies_path,
                output_dir=str(self.output_dir),
                duration=self.duration,
                model=self.model
            )
            
            for i, prompt in enumerate(prompts):
                print(f"   生成视频 {i+1}/{len(prompts)}...")
                result = await worker.generate(prompt)
                results.append(result)
        
        elif self.platform == "grok":
            # 使用 Grok Imagine API
            from scripts.grok_api import GrokClient
            
            client = GrokClient()
            
            # Grok 时长格式转换
            duration = "6" if self.duration == "6" or self.duration == "6s" else "10"
            
            for i, prompt in enumerate(prompts):
                print(f"   生成视频 {i+1}/{len(prompts)}...")
                result = await client.text_to_video(
                    prompt=prompt,
                    aspect_ratio=self.ratio,
                    mode="normal",
                    duration=duration,
                    resolution="720p"
                )
                results.append(result)
        
        return results
    
    async def _assemble_video(self, video_results: list) -> Path:
        """剪辑装配：ffmpeg 拼接"""
        if len(video_results) == 1:
            return Path(video_results[0].get("output_path", ""))
        
        # 使用 ffmpeg 拼接多个视频
        from scripts.video_assembler import VideoAssembler
        
        assembler = VideoAssembler()
        input_files = [r["output_path"] for r in video_results]
        output_file = self.output_dir / "final_video.mp4"
        
        await assembler.concat(input_files, str(output_file))
        
        return output_file


async def main():
    parser = argparse.ArgumentParser(description="短剧生成 Agent v2")
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="输入描述，格式：'风格：xxx\\n内容：xxx'"
    )
    parser.add_argument(
        "--platform", "-p",
        type=str,
        choices=["grok", "jianying"],
        default="grok",
        help="生成平台（默认：grok）"
    )
    parser.add_argument(
        "--cookies", "-c",
        type=str,
        default=None,
        help="剪映 cookies.json 路径（jianying 模式需要）"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="./output",
        help="输出目录（默认：./output）"
    )
    parser.add_argument(
        "--duration", "-d",
        type=str,
        choices=["6", "10", "6s", "10s"],
        default="10",
        help="视频时长（默认：10秒）"
    )
    parser.add_argument(
        "--ratio", "-r",
        type=str,
        choices=["2:3", "3:2", "1:1", "16:9", "9:16"],
        default="9:16",
        help="画面比例（默认：9:16竖屏）"
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="Grok Imagine",
        help="模型选择（默认：Grok Imagine）"
    )
    
    args = parser.parse_args()
    
    generator = ShortDramaGenerator(
        platform=args.platform,
        cookies_path=args.cookies,
        output_dir=args.output_dir,
        duration=args.duration,
        ratio=args.ratio,
        model=args.model
    )
    
    result = await generator.generate(args.input)
    
    print("\n✅ 生成完成！")
    print(f"📹 最终视频：{result['final_video']}")
    
    # 保存生成报告
    report_path = Path(args.output_dir) / "generation_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"📄 生成报告：{report_path}")


if __name__ == "__main__":
    asyncio.run(main())
