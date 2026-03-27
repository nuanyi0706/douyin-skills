"""
Sora2 API 客户端
支持：T2V 文生视频 / I2V 图生视频 / 水印移除
API 文档：https://kie.ai
"""

import asyncio
import aiohttp
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
import aiofiles
import json


class Sora2Client:
    """Sora2 API 客户端"""
    
    BASE_URL = "https://api.kie.ai"
    
    # 默认 API Key
    DEFAULT_API_KEY = "0ff057eed0630bbe5baae3a5e4c167db"
    
    def __init__(self, api_key: Optional[str] = None, callback_url: Optional[str] = None):
        """
        初始化 Sora2 客户端
        
        Args:
            api_key: Kie AI API Key，不传则使用默认值或环境变量 SORA2_API_KEY
            callback_url: 任务完成回调 URL，用于接收生成结果
        """
        self.api_key = api_key or os.getenv("SORA2_API_KEY") or self.DEFAULT_API_KEY
        self.callback_url = callback_url or os.getenv("SORA2_CALLBACK_URL")
        
        if not self.api_key:
            raise ValueError("缺少 API Key，请设置环境变量 SORA2_API_KEY 或传入 api_key 参数")
    
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
                
                # 状态映射
                status_map = {
                    "waiting": "processing",
                    "running": "processing",
                    "success": "completed",
                    "failed": "failed"
                }
                
                # 解析结果 URL
                result_url = data.get("resultJson", "")
                if result_url:
                    try:
                        result_data = json.loads(result_url)
                        result_url = result_data.get("video_url", result_url)
                    except:
                        pass
                
                return {
                    "status": "success",
                    "task_id": task_id,
                    "state": status_map.get(state, state),
                    "progress": data.get("progress", 0),
                    "model": data.get("model", ""),
                    "result_url": result_url,
                    "error": data.get("failMsg"),
                    "create_time": data.get("createTime"),
                    "complete_time": data.get("completeTime"),
                    "raw_data": data
                }
    
    async def create_task(
        self,
        model: str,
        input_data: dict,
        callback_url: Optional[str] = None,
        progress_callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建任务（通用方法）
        
        Args:
            model: 模型名称
            input_data: 输入数据
            callback_url: 任务完成回调 URL
            progress_callback_url: 进度回调 URL
        
        Returns:
            dict: {"status": "success", "task_id": str} 或 {"status": "failed", "error": str}
        """
        payload = {
            "model": model,
            "input": input_data
        }
        
        # 使用传入的回调 URL 或实例默认值
        cb_url = callback_url or self.callback_url
        if cb_url:
            payload["callBackUrl"] = cb_url
        if progress_callback_url:
            payload["progressCallBackUrl"] = progress_callback_url
        
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
                record_id = result.get("data", {}).get("recordId")
                
                if not task_id:
                    return {"status": "failed", "error": "未获取到 taskId"}
                
                return {
                    "status": "success",
                    "task_id": task_id,
                    "record_id": record_id,
                    "callback_url": cb_url
                }
    
    async def text_to_video(
        self,
        prompt: str,
        aspect_ratio: str = "landscape",
        n_frames: str = "10",
        remove_watermark: bool = False,
        character_id_list: Optional[List[str]] = None,
        callback_url: Optional[str] = None,
        progress_callback_url: Optional[str] = None,
        wait: bool = True,
        max_wait_seconds: int = 600
    ) -> Dict[str, Any]:
        """
        文生视频 (T2V)
        
        Args:
            prompt: 视频描述提示词（最大 10000 字符）
            aspect_ratio: 画面比例，"portrait" 或 "landscape"
            n_frames: 帧数，"10" 或 "15"
            remove_watermark: 是否移除水印
            character_id_list: 角色 ID 列表（最多 5 个）
            callback_url: 任务完成回调 URL
            progress_callback_url: 进度回调 URL
            wait: 是否等待完成
            max_wait_seconds: 最大等待秒数
        
        Returns:
            dict: {"status": "success", "task_id": str, ...}
        """
        input_data = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "n_frames": n_frames,
            "remove_watermark": remove_watermark
        }
        
        if character_id_list:
            input_data["character_id_list"] = character_id_list[:5]
        
        result = await self.create_task(
            model="sora-2-text-to-video",
            input_data=input_data,
            callback_url=callback_url,
            progress_callback_url=progress_callback_url
        )
        
        if result["status"] != "success":
            return result
        
        if wait:
            return await self._wait_for_completion(result["task_id"], max_wait_seconds)
        
        result["message"] = "任务创建成功，请登录 https://kie.ai 查看生成结果"
        return result
    
    async def image_to_video(
        self,
        prompt: str,
        image_urls: List[str],
        aspect_ratio: str = "landscape",
        n_frames: str = "10",
        remove_watermark: bool = False,
        character_id_list: Optional[List[str]] = None,
        callback_url: Optional[str] = None,
        progress_callback_url: Optional[str] = None,
        wait: bool = True,
        max_wait_seconds: int = 600
    ) -> Dict[str, Any]:
        """
        图生视频 (I2V)
        
        Args:
            prompt: 视频描述提示词（最大 10000 字符）
            image_urls: 图片 URL 列表（最多 1 个）
            aspect_ratio: 画面比例，"portrait" 或 "landscape"
            n_frames: 帧数，"10" 或 "15"
            remove_watermark: 是否移除水印
            character_id_list: 角色 ID 列表（最多 5 个）
            callback_url: 任务完成回调 URL
            progress_callback_url: 进度回调 URL
            wait: 是否等待完成
            max_wait_seconds: 最大等待秒数
        
        Returns:
            dict: {"status": "success", "task_id": str, ...}
        """
        input_data = {
            "prompt": prompt,
            "image_urls": image_urls[:1],  # 最多 1 个
            "aspect_ratio": aspect_ratio,
            "n_frames": n_frames,
            "remove_watermark": remove_watermark
        }
        
        if character_id_list:
            input_data["character_id_list"] = character_id_list[:5]
        
        result = await self.create_task(
            model="sora-2-image-to-video",
            input_data=input_data,
            callback_url=callback_url,
            progress_callback_url=progress_callback_url
        )
        
        if result["status"] != "success":
            return result
        
        if wait:
            return await self._wait_for_completion(result["task_id"], max_wait_seconds)
        
        result["message"] = "任务创建成功，请登录 https://kie.ai 查看生成结果"
        return result
    
    async def remove_watermark(
        self,
        video_url: str,
        callback_url: Optional[str] = None,
        wait: bool = True,
        max_wait_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        移除水印
        
        Args:
            video_url: Sora2 生成的视频 URL（必须以 sora.chatgpt.com 开头）
            callback_url: 任务完成回调 URL
            wait: 是否等待完成
            max_wait_seconds: 最大等待秒数
        
        Returns:
            dict: {"status": "success", "task_id": str, ...}
        """
        input_data = {
            "video_url": video_url
        }
        
        result = await self.create_task(
            model="sora-watermark-remover",
            input_data=input_data,
            callback_url=callback_url
        )
        
        if result["status"] != "success":
            return result
        
        if wait:
            return await self._wait_for_completion(result["task_id"], max_wait_seconds)
        
        result["message"] = "任务创建成功，请登录 https://kie.ai 查看生成结果"
        return result
    
    async def _wait_for_completion(
        self,
        task_id: str,
        max_wait_seconds: int = 600,
        poll_interval: int = 10
    ) -> Dict[str, Any]:
        """
        等待任务完成
        
        Args:
            task_id: 任务 ID
            max_wait_seconds: 最大等待秒数
            poll_interval: 轮询间隔秒数
        
        Returns:
            dict: 结果字典
        """
        print(f"⏳ 等待生成完成... (Task ID: {task_id})")
        
        max_attempts = max_wait_seconds // poll_interval
        
        for i in range(max_attempts):
            await asyncio.sleep(poll_interval)
            
            status = await self.get_task_status(task_id)
            
            if status.get("state") == "completed":
                print(f"  ✅ 生成完成!")
                result_url = status.get("result_url")
                
                if result_url:
                    # 下载视频
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
            
            elif status.get("state") == "failed":
                error = status.get("error", "Unknown error")
                print(f"  ❌ 生成失败：{error}")
                return {
                    "status": "failed",
                    "error": error,
                    "task_id": task_id
                }
            
            # 显示进度
            progress = status.get("progress", 0)
            if progress > 0:
                print(f"  ⏳ 进度：{progress}%")
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
            
            output_path = output_dir / f"sora2_{task_id}.mp4"
            
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
    
    async def generate(
        self,
        prompt: str,
        duration: str = "10s",
        ratio: str = "16:9",
        ref_image: Optional[str] = None,
        remove_watermark: bool = False,
        wait: bool = True
    ) -> Dict[str, Any]:
        """
        统一视频生成接口（兼容旧接口）
        
        Args:
            prompt: 视频描述提示词
            duration: 时长 ("10s" 或 "15s")
            ratio: 画面比例 ("16:9" 或 "9:16" 或 "1:1")
            ref_image: 参考图片 URL（I2V 模式）
            remove_watermark: 是否移除水印
            wait: 是否等待完成
        
        Returns:
            dict: {"status": "success"|"failed", "task_id": str, "output_path": str}
        """
        # 转换参数格式
        aspect_ratio = "landscape" if ratio == "16:9" else "portrait"
        n_frames = "15" if duration == "15s" else "10"
        
        if ref_image:
            return await self.image_to_video(
                prompt=prompt,
                image_urls=[ref_image],
                aspect_ratio=aspect_ratio,
                n_frames=n_frames,
                remove_watermark=remove_watermark,
                wait=wait
            )
        else:
            return await self.text_to_video(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                n_frames=n_frames,
                remove_watermark=remove_watermark,
                wait=wait
            )


# CLI 入口
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sora2 API 客户端")
    parser.add_argument("--prompt", "-p", type=str, default=None, help="视频描述提示词")
    parser.add_argument("--mode", "-m", type=str, choices=["t2v", "i2v"], default="t2v", help="生成模式")
    parser.add_argument("--image", "-i", type=str, default=None, help="参考图片 URL（I2V 模式）")
    parser.add_argument("--duration", "-d", type=str, choices=["10s", "15s"], default="10s", help="时长")
    parser.add_argument("--ratio", "-r", type=str, choices=["16:9", "9:16"], default="16:9", help="画面比例")
    parser.add_argument("--no-watermark", action="store_true", help="移除水印")
    parser.add_argument("--callback", "-c", type=str, default=None, help="回调 URL")
    parser.add_argument("--no-wait", action="store_true", help="不等待完成")
    parser.add_argument("--query", "-q", type=str, default=None, help="查询任务状态（传入 task_id）")
    
    args = parser.parse_args()
    
    client = Sora2Client(callback_url=args.callback)
    
    # 查询模式
    if args.query:
        result = await client.get_task_status(args.query)
        print("\n📊 任务状态：")
        print(f"  Task ID：{result.get('task_id')}")
        print(f"  状态：{result.get('state')}")
        print(f"  进度：{result.get('progress')}%")
        if result.get("result_url"):
            print(f"  结果：{result.get('result_url')}")
        if result.get("error"):
            print(f"  错误：{result.get('error')}")
        return
    
    # 生成模式需要 prompt
    if not args.prompt:
        parser.error("--prompt is required for video generation")
    
    # 生成模式
    if args.mode == "i2v" and args.image:
        result = await client.image_to_video(
            prompt=args.prompt,
            image_urls=[args.image],
            aspect_ratio="landscape" if args.ratio == "16:9" else "portrait",
            n_frames="15" if args.duration == "15s" else "10",
            remove_watermark=args.no_watermark,
            wait=not args.no_wait
        )
    else:
        result = await client.text_to_video(
            prompt=args.prompt,
            aspect_ratio="landscape" if args.ratio == "16:9" else "portrait",
            n_frames="15" if args.duration == "15s" else "10",
            remove_watermark=args.no_watermark,
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