"""
剪映 (Jianying) 自动化视频生成
引擎：Playwright + Chromium
支持：文生视频 (T2V) + 图生视频 (I2V) + 参考视频生成 (V2V)

来源：lanshu-waytovideo/jianying-video-gen
"""
import asyncio
import json
import re
import os
import html
import argparse
from pathlib import Path
from playwright.async_api import async_playwright
from typing import Optional, Dict, Any


class JianyingWorker:
    """剪映视频生成工作器"""
    
    def __init__(
        self,
        cookies_path: str = "cookies.json",
        output_dir: str = "./output",
        duration: str = "10s",
        ratio: str = "横屏",
        model: str = "Seedance 2.0"
    ):
        self.cookies_path = cookies_path
        self.output_dir = Path(output_dir)
        self.duration = duration
        self.ratio = ratio
        self.model = model
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.debug_screenshots = False
    
    async def generate(
        self,
        prompt: str,
        ref_image: Optional[str] = None,
        ref_video: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """生成视频"""
        if ref_image:
            mode_label = "I2V (图生视频)"
        elif ref_video:
            mode_label = "V2V (参考视频)"
        else:
            mode_label = "T2V (文生视频)"
        
        print(f"🚀 启动剪映自动化 [{mode_label}]")
        
        # 验证文件存在
        if ref_image and not Path(ref_image).exists():
            raise FileNotFoundError(f"参考图片不存在：{ref_image}")
        if ref_video and not Path(ref_video).exists():
            raise FileNotFoundError(f"参考视频不存在：{ref_video}")
        
        # 导入外部 run 函数
        from scripts.jianying_worker_impl import run
        
        result = await run(
            prompt=prompt,
            duration=self.duration,
            ratio=self.ratio,
            model=self.model,
            dry_run=dry_run,
            ref_video=ref_video,
            ref_image=ref_image,
            cookies_path=self.cookies_path,
            output_dir=str(self.output_dir)
        )
        
        return result


async def main():
    parser = argparse.ArgumentParser(description="剪映 AI 视频生成器")
    parser.add_argument("--prompt", type=str, default="一个美女在跳舞", help="视频描述")
    parser.add_argument("--duration", type=str, default="10s", choices=["5s", "10s", "15s"])
    parser.add_argument("--ratio", type=str, default="横屏", choices=["横屏", "竖屏", "方屏"])
    parser.add_argument("--model", type=str, default="Seedance 2.0",
                        choices=["Seedance 2.0", "Seedance 2.0 Fast"])
    parser.add_argument("--ref-video", type=str, default=None, help="参考视频文件路径 (V2V 模式)")
    parser.add_argument("--ref-image", type=str, default=None, help="参考图片文件路径 (I2V 模式)")
    parser.add_argument("--cookies", type=str, default="cookies.json", help="cookies.json 路径")
    parser.add_argument("--output-dir", type=str, default="./output", help="输出目录")
    parser.add_argument("--dry-run", action="store_true", help="仅填写表单，不提交")
    
    args = parser.parse_args()
    
    worker = JianyingWorker(
        cookies_path=args.cookies,
        output_dir=args.output_dir,
        duration=args.duration,
        ratio=args.ratio,
        model=args.model
    )
    
    result = await worker.generate(
        prompt=args.prompt,
        ref_image=args.ref_image,
        ref_video=args.ref_video,
        dry_run=args.dry_run
    )
    
    print(f"\n✅ 生成完成：{result.get('output_path', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(main())
