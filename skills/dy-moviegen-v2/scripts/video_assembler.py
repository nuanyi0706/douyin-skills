"""
视频装配器 - 使用 ffmpeg 拼接视频片段
"""
import asyncio
import subprocess
from pathlib import Path
from typing import List


class VideoAssembler:
    """视频装配器"""
    
    def __init__(self, temp_dir: str = "./temp"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    async def concat(self, input_files: List[str], output_path: str) -> str:
        """
        拼接多个视频文件
        
        Args:
            input_files: 输入视频文件路径列表
            output_path: 输出文件路径
        
        Returns:
            输出文件路径
        """
        if len(input_files) == 1:
            return input_files[0]
        
        # 创建文件列表
        list_file = self.temp_dir / "concat_list.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for file_path in input_files:
                # ffmpeg 需要单引号包裹路径
                f.write(f"file '{file_path}'\n")
        
        # 执行 ffmpeg 拼接
        cmd = [
            "ffmpeg",
            "-y",  # 覆盖输出文件
            "-f", "concat",
            "-safe", "0",
            "-i", str(list_file),
            "-c", "copy",  # 直接复制流，不重新编码
            output_path
        ]
        
        print(f"  🔧 执行：{' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="ignore")
            raise Exception(f"ffmpeg 拼接失败：{error_msg}")
        
        print(f"  ✅ 拼接完成：{output_path}")
        return output_path
    
    async def add_audio(self, video_path: str, audio_path: str, output_path: str) -> str:
        """
        为视频添加音频
        
        Args:
            video_path: 视频文件路径
            audio_path: 音频文件路径
            output_path: 输出文件路径
        
        Returns:
            输出文件路径
        """
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            output_path
        ]
        
        print(f"  🔧 添加音频...")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="ignore")
            raise Exception(f"ffmpeg 添加音频失败：{error_msg}")
        
        print(f"  ✅ 音频已添加：{output_path}")
        return output_path
    
    async def trim(self, input_path: str, output_path: str, start: float, duration: float) -> str:
        """
        裁剪视频
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            start: 开始时间 (秒)
            duration: 持续时间 (秒)
        
        Returns:
            输出文件路径
        """
        cmd = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-ss", str(start),
            "-t", str(duration),
            "-c", "copy",
            output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="ignore")
            raise Exception(f"ffmpeg 裁剪失败：{error_msg}")
        
        print(f"  ✅ 裁剪完成：{output_path}")
        return output_path


async def main():
    """测试函数"""
    assembler = VideoAssembler()
    
    # 测试拼接
    test_files = ["test1.mp4", "test2.mp4"]
    output = await assembler.concat(test_files, "output.mp4")
    print(f"输出：{output}")


if __name__ == "__main__":
    asyncio.run(main())
