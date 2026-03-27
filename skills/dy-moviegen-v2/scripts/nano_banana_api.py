#!/usr/bin/env python3
"""
Nano Banana 2 API Client - Kie AI Image Generation

使用 Kie AI API 进行图像生成，支持：
- 文生图 (T2I)
- 图生图 (I2I) - 最多 14 张参考图
- 多种画幅比例和分辨率

API 文档: https://api.kie.ai/api/v1/jobs/createTask

Author: Work-Fisher
"""

import argparse
import json
import os
import sys
import time
import requests
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class Resolution(Enum):
    """分辨率选项"""
    ONE_K = "1K"
    TWO_K = "2K"
    FOUR_K = "4K"


class AspectRatio(Enum):
    """画幅比例"""
    AUTO = "auto"
    SQUARE = "1:1"
    LANDSCAPE = "16:9"
    PORTRAIT = "9:16"
    CLASSIC = "4:3"
    CLASSIC_PORTRAIT = "3:4"
    CINEMATIC = "21:9"
    WIDE = "2:3"
    TALL = "3:2"
    ULTRA_WIDE_1_4 = "1:4"
    ULTRA_WIDE_4_1 = "4:1"
    ULTRA_WIDE_1_8 = "1:8"
    ULTRA_WIDE_8_1 = "8:1"
    CLASSIC_WIDE = "4:5"
    CLASSIC_TALL = "5:4"


class OutputFormat(Enum):
    """输出格式"""
    JPG = "jpg"
    PNG = "png"


@dataclass
class GenerationResult:
    """生成结果"""
    task_id: str
    status: str
    image_url: Optional[str] = None
    error: Optional[str] = None


class NanoBananaClient:
    """Nano Banana 2 API 客户端"""
    
    BASE_URL = "https://api.kie.ai/api/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端
        
        Args:
            api_key: API 密钥，如果不提供则从环境变量 KIE_API_KEY 读取
        """
        self.api_key = api_key or os.environ.get("KIE_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set KIE_API_KEY environment variable or pass api_key parameter.")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_task(
        self,
        prompt: str,
        aspect_ratio: str = "auto",
        resolution: str = "1K",
        output_format: str = "jpg",
        image_input: Optional[List[str]] = None,
        callback_url: Optional[str] = None
    ) -> str:
        """
        创建图像生成任务
        
        Args:
            prompt: 提示词（最大 20000 字符）
            aspect_ratio: 画幅比例 (auto/1:1/16:9/9:16/4:3/3:4/21:9/2:3/3:2/1:4/4:1/1:8/8:1/4:5/5:4)
            resolution: 分辨率 (1K/2K/4K)
            output_format: 输出格式 (jpg/png)
            image_input: 图生图的输入图片URL列表（最多 14 张）
            callback_url: 回调URL
        
        Returns:
            task_id: 任务ID
        """
        payload = {
            "model": "nano-banana-2",
            "input": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "output_format": output_format,
                "image_input": image_input or []
            }
        }
        
        if callback_url:
            payload["callBackUrl"] = callback_url
        
        response = requests.post(
            f"{self.BASE_URL}/jobs/createTask",
            headers=self.headers,
            json=payload
        )
        
        response.raise_for_status()
        result = response.json()
        
        if result.get("code") != 200:
            raise Exception(f"API Error [{result.get('code')}]: {result.get('msg', 'Unknown error')}")
        
        return result["data"]["taskId"]
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态
        
        Args:
            task_id: 任务ID
        
        Returns:
            任务状态信息
        """
        response = requests.get(
            f"{self.BASE_URL}/jobs/recordInfo?taskId={task_id}",
            headers=self.headers
        )
        
        response.raise_for_status()
        result = response.json()
        
        if result.get("code") != 200:
            raise Exception(f"API Error [{result.get('code')}]: {result.get('msg', 'Unknown error')}")
        
        return result["data"]
    
    def wait_for_completion(
        self,
        task_id: str,
        timeout: int = 600,
        poll_interval: int = 5
    ) -> GenerationResult:
        """
        等待任务完成
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）
            poll_interval: 轮询间隔（秒）
        
        Returns:
            GenerationResult: 生成结果
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                status_info = self.get_task_status(task_id)
                status = status_info.get("status")
                
                if status == "completed":
                    output = status_info.get("output", {})
                    image_url = output.get("image_url") or output.get("imageUrl")
                    
                    return GenerationResult(
                        task_id=task_id,
                        status="completed",
                        image_url=image_url
                    )
                elif status == "failed":
                    return GenerationResult(
                        task_id=task_id,
                        status="failed",
                        error=status_info.get("error", "Generation failed")
                    )
                
                print(f"  状态: {status}, 等待中...")
            
            except Exception as e:
                print(f"  查询出错: {e}")
            
            time.sleep(poll_interval)
        
        return GenerationResult(
            task_id=task_id,
            status="timeout",
            error=f"Task timed out after {timeout} seconds"
        )
    
    def generate(
        self,
        prompt: str,
        aspect_ratio: str = "auto",
        resolution: str = "1K",
        output_format: str = "jpg",
        image_input: Optional[List[str]] = None,
        wait: bool = True,
        timeout: int = 600
    ) -> GenerationResult:
        """
        生成图像（一站式调用）
        
        Args:
            prompt: 提示词
            aspect_ratio: 画幅比例
            resolution: 分辨率
            output_format: 输出格式
            image_input: 图生图输入（最多 14 张）
            wait: 是否等待完成
            timeout: 超时时间
        
        Returns:
            GenerationResult: 生成结果
        """
        print(f"创建任务...")
        print(f"  提示词: {prompt[:100]}...")
        print(f"  画幅: {aspect_ratio}, 分辨率: {resolution}")
        if image_input:
            print(f"  参考图: {len(image_input)} 张")
        
        task_id = self.create_task(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            output_format=output_format,
            image_input=image_input
        )
        
        print(f"  任务ID: {task_id}")
        
        if not wait:
            return GenerationResult(task_id=task_id, status="pending")
        
        return self.wait_for_completion(task_id, timeout=timeout)
    
    def batch_generate(
        self,
        prompts: List[str],
        aspect_ratio: str = "auto",
        resolution: str = "1K",
        output_format: str = "jpg"
    ) -> List[GenerationResult]:
        """
        批量生成图像
        
        Args:
            prompts: 提示词列表
            aspect_ratio: 画幅比例
            resolution: 分辨率
            output_format: 输出格式
        
        Returns:
            生成结果列表
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            print(f"\n[{i+1}/{len(prompts)}] 生成: {prompt[:50]}...")
            
            result = self.generate(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                output_format=output_format
            )
            results.append(result)
            
            if result.status == "completed":
                print(f"  ✓ 完成: {result.image_url}")
            else:
                print(f"  ✗ 失败: {result.error}")
        
        return results
    
    def download_image(self, image_url: str, output_path: str) -> bool:
        """
        下载生成的图像
        
        Args:
            image_url: 图像 URL
            output_path: 输出路径
        
        Returns:
            是否成功
        """
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            print(f"下载失败: {e}")
            return False


# ============================================================
# 便捷函数
# ============================================================

def generate_image(
    prompt: str,
    aspect_ratio: str = "auto",
    resolution: str = "1K",
    image_input: Optional[List[str]] = None,
    api_key: Optional[str] = None
) -> Optional[str]:
    """
    快速生成单张图像
    
    Args:
        prompt: 提示词
        aspect_ratio: 画幅比例
        resolution: 分辨率
        image_input: 参考图片列表
        api_key: API密钥
    
    Returns:
        图像URL或None
    """
    client = NanoBananaClient(api_key)
    result = client.generate(
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        image_input=image_input
    )
    return result.image_url


# ============================================================
# CLI 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Nano Banana 2 图像生成 API 客户端 (Kie AI)")
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成单张图像")
    gen_parser.add_argument("--prompt", "-p", required=True, help="图像提示词")
    gen_parser.add_argument("--aspect-ratio", "-a", default="auto", 
                           choices=["auto", "1:1", "16:9", "9:16", "4:3", "3:4", 
                                   "21:9", "2:3", "3:2", "1:4", "4:1", "1:8", "8:1", "4:5", "5:4"],
                           help="画幅比例")
    gen_parser.add_argument("--resolution", "-r", default="1K", 
                           choices=["1K", "2K", "4K"],
                           help="分辨率")
    gen_parser.add_argument("--format", "-f", default="jpg", 
                           choices=["jpg", "png"],
                           help="输出格式")
    gen_parser.add_argument("--images", "-i", nargs="+", help="参考图片URL列表（最多14张）")
    gen_parser.add_argument("--output", "-o", help="输出文件路径")
    
    # batch 命令
    batch_parser = subparsers.add_parser("batch", help="批量生成")
    batch_parser.add_argument("--file", "-f", required=True, help="提示词文件（每行一个）")
    batch_parser.add_argument("--aspect-ratio", "-a", default="auto", help="画幅比例")
    batch_parser.add_argument("--resolution", "-r", default="1K", help="分辨率")
    
    # status 命令
    status_parser = subparsers.add_parser("status", help="查询任务状态")
    status_parser.add_argument("--task-id", "-t", required=True, help="任务 ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        client = NanoBananaClient()
        
        if args.command == "generate":
            result = client.generate(
                prompt=args.prompt,
                aspect_ratio=args.aspect_ratio,
                resolution=args.resolution,
                output_format=args.format,
                image_input=args.images
            )
            
            if result.status == "completed":
                print(f"\n✓ 图像生成成功: {result.image_url}")
                
                if args.output:
                    if client.download_image(result.image_url, args.output):
                        print(f"  已保存到: {args.output}")
            else:
                print(f"\n✗ 生成失败: {result.error}")
        
        elif args.command == "batch":
            with open(args.file, "r", encoding="utf-8") as f:
                prompts = [line.strip() for line in f if line.strip()]
            
            results = client.batch_generate(
                prompts=prompts,
                aspect_ratio=args.aspect_ratio,
                resolution=args.resolution
            )
            
            print("\n=== 批量生成完成 ===")
            success = sum(1 for r in results if r.status == "completed")
            print(f"成功: {success}/{len(results)}")
        
        elif args.command == "status":
            status = client.get_task_status(args.task_id)
            print(json.dumps(status, indent=2, ensure_ascii=False))
    
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()