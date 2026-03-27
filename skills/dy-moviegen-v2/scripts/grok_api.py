"""
Grok Imagine API 客户端
支持：T2V 文生视频 / I2V 图生视频 / 视频扩展
API 文档：https://kie.ai
"""

import asyncio
import aiohttp
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
import aiofiles
import json


class GrokClient:
    """Grok Imagine API 客户端"""
    
    BASE_URL = "https://api.kie.ai"
    
    # 默认 API Key
    DEFAULT_API_KEY = "0ff057eed0630bbe5baae3a5e4c167db"
    
    def __init__(self, api_key: Optional[str] = None, callback_url: Optional[str] = None):
        """
        初始化 Grok 客户端
        
        Args:
            api_key: Kie AI API Key，不传则使用默认值或环境变量 GROK_API_KEY
            callback_url: 任务完成回调 URL
        """
        self.api_key = api_key or os.getenv("GROK_API_KEY") or os.getenv("SORA2_API_KEY") or self.DEFAULT_API_KEY
        self.callback_url = callback_url or os.getenv("GROK_CALLBACK_URL")
        
        if not self.api_key:
            raise ValueError("缺少 API Key，请设置环境变量 GROK_API_KEY 或传入 api_key 参数")
    
    def _get_headers(self) -> dict:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态
        
        Args:
            task_id: 任务 ID
        
        Returns:
            dict: 任务状态详情
        """
        url = f"{self.BASE_URL}/api/v1/jobs/recordInfo?taskId={task_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self._get_headers()) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    return {
                        "status": "failed",
                        "error": f"查询失败：HTTP {resp.status} - {error_text}"
                    }
                
                result = await resp.json()
                
                if result.get("code") != 200:
                    return {
                        "status": "failed",
                        "error": result.get("msg", "Unknown error")
                    }
                
                data = result.get("data", {})
                state = data.get("state", "")
                
                # 状态映射（根据文档）
                # waiting: 已排队 | queuing: 队列中 | generating: 处理中
                # success: 成功 | fail: 失败
                status_map = {
                    "waiting": "processing",
                    "queuing": "processing",
                    "generating": "processing",
                    "success": "completed",
                    "fail": "failed"
                }
                
                # 解析结果 URL
                result_url = None
                result_urls = []
                result_json_str = data.get("resultJson", "")
                
                if result_json_str and state == "success":
                    try:
                        result_data = json.loads(result_json_str)
                        # 图像/媒体/视频格式: {resultUrls: []}
                        # 文本格式: {resultObject: {}}
                        result_urls = result_data.get("resultUrls", [])
                        if result_urls:
                            result_url = result_urls[0]
                        else:
                            # 尝试其他可能的字段
                            result_url = (
                                result_data.get("video_url") or
                                result_data.get("result_url") or
                                result_data.get("url")
                            )
                    except json.JSONDecodeError:
                        # URL encoded 情况
                        try:
                            from urllib.parse import unquote
                            decoded = unquote(result_json_str)
                            result_data = json.loads(decoded)
                            result_urls = result_data.get("resultUrls", [])
                            if result_urls:
                                result_url = result_urls[0]
                        except:
                            pass
                
                return {
                    "status": "success",
                    "task_id": task_id,
                    "state": status_map.get(state, state),
                    "raw_state": state,
                    "progress": data.get("progress", 0),
                    "model": data.get("model", ""),
                    "result_url": result_url,
                    "result_urls": result_urls,
                    "error": data.get("failMsg"),
                    "fail_code": data.get("failCode"),
                    "cost_time": data.get("costTime"),
                    "create_time": data.get("createTime"),
                    "complete_time": data.get("completeTime"),
                    "raw_data": data
                }
    
    async def text_to_video(
        self,
        prompt: str,
        aspect_ratio: str = "9:16",
        mode: str = "normal",
        duration: str = "10",
        resolution: str = "720p",
        callback_url: Optional[str] = None,
        wait: bool = True,
        max_wait_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        文生视频 (T2V)
        
        Args:
            prompt: 视频描述提示词（最大 5000 字符，支持英文）
            aspect_ratio: 画面比例 
                         - "2:3"(竖向), "3:2"(横向), "1:1"(正方形), "16:9"(宽屏), "9:16"(竖屏)
            mode: 生成模式 
                  - "fun": 更有创意和趣味的解读
                  - "normal": 平衡方法，具有良好的运动质量
                  - "spicy": 更有活力和强烈的运动效果
            duration: 时长 "6" 或 "10" 秒
            resolution: 分辨率 "480p" 或 "720p"
            callback_url: 任务完成回调 URL
            wait: 是否等待完成
            max_wait_seconds: 最大等待秒数
        
        Returns:
            dict: {"status": "success", "task_id": str, ...}
        """
        payload = {
            "model": "grok-imagine/text-to-video",
            "input": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "mode": mode,
                "duration": duration,
                "resolution": resolution
            }
        }
        
        cb_url = callback_url or self.callback_url
        if cb_url:
            payload["callBackUrl"] = cb_url
        
        result = await self._create_task(payload)
        
        if result["status"] != "success":
            return result
        
        if wait:
            return await self._wait_for_completion(result["task_id"], max_wait_seconds)
        
        result["message"] = "任务创建成功，请登录 https://kie.ai 查看生成结果"
        return result
    
    async def image_to_video(
        self,
        prompt: str = "",
        image_urls: Optional[List[str]] = None,
        task_id: Optional[str] = None,
        index: int = 0,
        mode: str = "normal",
        duration: str = "10",
        resolution: str = "720p",
        aspect_ratio: str = "9:16",
        callback_url: Optional[str] = None,
        wait: bool = True,
        max_wait_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        图生视频 (I2V)
        
        Args:
            prompt: 视频描述提示词（可选，最大5000字符，支持英文）
            image_urls: 图片 URL 列表（最多 7 张），不能与 task_id 同时使用
                        支持 JPEG、PNG、WEBP 格式，每张最大 10MB
            task_id: 之前生成的 Grok 图像任务 ID（不能与 image_urls 同时使用）
            index: 使用 task_id 时指定图像索引 (0-5)，默认 0
            mode: 生成模式 
                  - "fun": 更有创意和趣味的解读
                  - "normal": 平衡方法，具有良好的运动质量
                  - "spicy": 更有活力和强烈的运动效果（外部图片不可用）
            duration: 时长 "6" 或 "10" 秒，默认 "6"
            resolution: 分辨率 "480p" 或 "720p"，默认 "480p"
            aspect_ratio: 画面比例（仅多图模式适用）
                         - "2:3", "3:2", "1:1", "16:9", "9:16"
                         - 单图模式下视频宽高参考图片宽高
            callback_url: 任务完成回调 URL
            wait: 是否等待完成
            max_wait_seconds: 最大等待秒数
        
        Returns:
            dict: {"status": "success", "task_id": str, ...}
        """
        input_data = {
            "mode": mode,
            "duration": duration,
            "resolution": resolution
        }
        
        if prompt:
            input_data["prompt"] = prompt
        
        if image_urls:
            input_data["image_urls"] = image_urls[:7]  # 最多 7 张
            # 多图模式添加 aspect_ratio
            if len(image_urls) > 1:
                input_data["aspect_ratio"] = aspect_ratio
            # 外部图片不支持 spicy 模式
            if mode == "spicy":
                input_data["mode"] = "normal"
        elif task_id:
            input_data["task_id"] = task_id
            input_data["index"] = index
        else:
            return {"status": "failed", "error": "需要提供 image_urls 或 task_id"}
        
        payload = {
            "model": "grok-imagine/image-to-video",
            "input": input_data
        }
        
        cb_url = callback_url or self.callback_url
        if cb_url:
            payload["callBackUrl"] = cb_url
        
        result = await self._create_task(payload)
        
        if result["status"] != "success":
            return result
        
        if wait:
            return await self._wait_for_completion(result["task_id"], max_wait_seconds)
        
        result["message"] = "任务创建成功，请登录 https://kie.ai 查看生成结果"
        return result
    
    async def extend_video(
        self,
        task_id: str,
        prompt: str,
        extend_at: int = 0,
        extend_times: str = "10",
        callback_url: Optional[str] = None,
        wait: bool = True,
        max_wait_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        扩展视频
        
        基于之前生成的视频任务进行扩展延长。只能扩展由 Kie AI 模型生成的视频。
        
        Args:
            task_id: 之前成功的视频生成任务 ID（必须来自 Kie AI 视频生成模型）
                     支持 grok-imagine/text-to-video 或 grok-imagine/image-to-video 生成的任务
            prompt: 描述视频如何扩展的提示词（必填，支持中英文）
                    可指定镜头运动、场景变化、物体动作等
            extend_at: 扩展起点位置（默认 0，从视频开头扩展）
            extend_times: 扩展时长 "6" 或 "10" 秒（默认 "10"）
            callback_url: 任务完成回调 URL
            wait: 是否等待完成
            max_wait_seconds: 最大等待秒数
        
        Returns:
            dict: {"status": "success", "task_id": str, ...}
        
        注意:
            - 只能扩展由 Kie AI 生成的视频，不支持外部视频
            - 原始视频生成必须成功完成
            - 扩展时长越长，生成所需时间相应增加
        """
        # 参数验证
        if not task_id:
            return {"status": "failed", "error": "task_id 是必填字段"}
        if not prompt:
            return {"status": "failed", "error": "prompt 是必填字段"}
        if extend_times not in ["6", "10"]:
            return {"status": "failed", "error": "extend_times 必须是 '6' 或 '10'"}
        
        payload = {
            "model": "grok-imagine/extend",
            "input": {
                "task_id": task_id,
                "prompt": prompt,
                "extend_at": extend_at,
                "extend_times": extend_times
            }
        }
        
        cb_url = callback_url or self.callback_url
        if cb_url:
            payload["callBackUrl"] = cb_url
        
        result = await self._create_task(payload)
        
        if result["status"] != "success":
            return result
        
        if wait:
            return await self._wait_for_completion(result["task_id"], max_wait_seconds)
        
        result["message"] = "任务创建成功，请登录 https://kie.ai 查看生成结果"
        return result
    
    async def _create_task(self, payload: dict) -> Dict[str, Any]:
        """创建任务"""
        url = f"{self.BASE_URL}/api/v1/jobs/createTask"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self._get_headers(), json=payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    return {
                        "status": "failed",
                        "error": f"创建任务失败：HTTP {resp.status} - {error_text}"
                    }
                
                result = await resp.json()
                
                if result.get("code") != 200:
                    return {
                        "status": "failed",
                        "error": f"API 错误：{result.get('msg', 'Unknown error')}"
                    }
                
                task_id = result.get("data", {}).get("taskId")
                
                if not task_id:
                    return {"status": "failed", "error": "未获取到 taskId"}
                
                return {
                    "status": "success",
                    "task_id": task_id
                }
    
    async def _wait_for_completion(
        self,
        task_id: str,
        max_wait_seconds: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        等待任务完成
        
        轮询最佳实践：
        - 初始轮询（前30秒）: 每2-3秒
        - 30秒后: 每5-10秒
        - 2分钟后: 每15-30秒
        """
        print(f"⏳ 等待生成完成... (Task ID: {task_id})")
        
        max_attempts = max_wait_seconds // poll_interval
        
        for i in range(max_attempts):
            await asyncio.sleep(poll_interval)
            
            status = await self.get_task_status(task_id)
            
            raw_state = status.get("raw_state", "")
            
            if status.get("state") == "completed" or raw_state == "success":
                print(f"  ✅ 生成完成!")
                result_url = status.get("result_url")
                result_urls = status.get("result_urls", [])
                
                if result_urls and len(result_urls) > 0:
                    # 下载第一个视频
                    output_path = await self._download_video(result_urls[0], task_id)
                    return {
                        "status": "success",
                        "task_id": task_id,
                        "output_url": result_urls[0],
                        "output_urls": result_urls,
                        "output_path": str(output_path) if output_path else None
                    }
                elif result_url:
                    output_path = await self._download_video(result_url, task_id)
                    return {
                        "status": "success",
                        "task_id": task_id,
                        "output_url": result_url,
                        "output_path": str(output_path) if output_path else None
                    }
                else:
                    return {
                        "status": "success",
                        "task_id": task_id,
                        "output_url": None,
                        "message": "生成完成，请登录 https://kie.ai 下载"
                    }
            
            elif status.get("state") == "failed" or raw_state == "fail":
                error = status.get("error", "Unknown error")
                fail_code = status.get("fail_code", "")
                print(f"  ❌ 生成失败：{error} (code: {fail_code})")
                return {
                    "status": "failed",
                    "error": error,
                    "fail_code": fail_code,
                    "task_id": task_id
                }
            
            # 显示进度
            progress = status.get("progress", 0)
            if progress > 0:
                print(f"  ⏳ 进度：{progress}%")
            elif raw_state:
                state_desc = {
                    "waiting": "排队中",
                    "queuing": "队列中",
                    "generating": "生成中"
                }.get(raw_state, raw_state)
                print(f"  ⏳ 状态：{state_desc}")
            elif i > 0 and i % 6 == 0:
                print(f"  ⏳ 生成中... ({i * poll_interval}s)")
        
        print(f"  ⏰ 等待超时（{max_wait_seconds}s）")
        return {
            "status": "timeout",
            "task_id": task_id,
            "message": f"任务超时，请稍后登录 https://kie.ai 查看"
        }
    
    async def _download_video(self, url: str, task_id: str) -> Optional[Path]:
        """下载视频到本地"""
        try:
            output_dir = Path("./output")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_path = output_dir / f"grok_{task_id}.mp4"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        print(f"  ⚠️ 下载失败：HTTP {resp.status}")
                        return None
                    
                    async with aiofiles.open(output_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(8192):
                            await f.write(chunk)
            
            print(f"  📥 已保存：{output_path}")
            return output_path
        except Exception as e:
            print(f"  ⚠️ 下载出错：{e}")
            return None


# CLI 入口
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Grok Imagine API 客户端")
    parser.add_argument("--prompt", "-p", type=str, default=None, help="视频描述提示词")
    parser.add_argument("--mode", "-m", type=str, choices=["t2v", "i2v", "extend"], default="t2v", help="生成模式")
    parser.add_argument("--image", "-i", type=str, nargs="+", default=None, help="参考图片 URL（I2V 模式，最多 7 张）")
    parser.add_argument("--task-id", "-t", type=str, default=None, help="任务 ID（extend 模式或 I2V 使用 Grok 图像）")
    parser.add_argument("--duration", "-d", type=str, choices=["6", "10"], default="10", help="时长（秒）")
    parser.add_argument("--ratio", "-r", type=str, 
                       choices=["2:3", "3:2", "1:1", "16:9", "9:16"], 
                       default="9:16", help="画面比例")
    parser.add_argument("--style", "-s", type=str, 
                       choices=["fun", "normal", "spicy"], 
                       default="normal", help="生成风格")
    parser.add_argument("--resolution", type=str, choices=["480p", "720p"], default="720p", help="分辨率")
    parser.add_argument("--aspect-ratio", type=str,
                       choices=["2:3", "3:2", "1:1", "16:9", "9:16"],
                       default="9:16", help="画面比例（I2V多图模式）")
    parser.add_argument("--no-wait", action="store_true", help="不等待完成")
    parser.add_argument("--query", "-q", type=str, default=None, help="查询任务状态")
    
    args = parser.parse_args()
    
    client = GrokClient()
    
    # 查询模式
    if args.query:
        result = await client.get_task_status(args.query)
        print("\n📊 任务状态：")
        print(f"  Task ID：{result.get('task_id')}")
        print(f"  模型：{result.get('model')}")
        print(f"  状态：{result.get('raw_state', result.get('state'))}")
        if result.get("progress", 0) > 0:
            print(f"  进度：{result.get('progress')}%")
        if result.get("cost_time"):
            print(f"  耗时：{result.get('cost_time') / 1000:.1f}s")
        if result.get("result_urls"):
            print(f"  结果：")
            for i, url in enumerate(result.get("result_urls", []), 1):
                print(f"    {i}. {url}")
        elif result.get("result_url"):
            print(f"  结果：{result.get('result_url')}")
        if result.get("error"):
            print(f"  错误：{result.get('error')}")
        if result.get("fail_code"):
            print(f"  错误码：{result.get('fail_code')}")
        return
    
    # 生成模式
    if not args.prompt and args.mode != "i2v":
        parser.error("--prompt is required for video generation")
    
    prompt = args.prompt or ""
    
    if args.mode == "i2v":
        if not args.image and not args.task_id:
            parser.error("I2V 模式需要 --image 或 --task-id")
        result = await client.image_to_video(
            prompt=prompt,
            image_urls=args.image,
            task_id=args.task_id,
            mode=args.style,
            duration=args.duration,
            resolution=args.resolution,
            aspect_ratio=args.aspect_ratio,
            wait=not args.no_wait
        )
    elif args.mode == "extend":
        if not args.task_id:
            parser.error("extend 模式需要 --task-id")
        result = await client.extend_video(
            task_id=args.task_id,
            prompt=prompt,
            extend_times=args.duration,
            wait=not args.no_wait
        )
    else:
        result = await client.text_to_video(
            prompt=prompt,
            aspect_ratio=args.ratio,
            mode=args.style,
            duration=args.duration,
            resolution=args.resolution,
            wait=not args.no_wait
        )
    
    print("\n📊 生成结果：")
    print(f"  状态：{result.get('status')}")
    if result.get("task_id"):
        print(f"  Task ID：{result.get('task_id')}")
    if result.get("output_path"):
        print(f"  文件：{result.get('output_path')}")
    if result.get("output_url"):
        print(f"  URL：{result.get('output_url')}")
    if result.get("message"):
        print(f"  提示：{result.get('message')}")
    if result.get("error"):
        print(f"  错误：{result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())