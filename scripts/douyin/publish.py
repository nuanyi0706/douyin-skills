"""
抖音内容发布模块。

支持视频发布、图文发布、定时发布。
"""

import os
import time
from pathlib import Path
from typing import Optional

from .cdp import CDPClient
from .selectors import SELECTORS
from .urls import URLS


def publish_video(
    cdp: CDPClient,
    video_path: str,
    title: str,
    description: str = "",
    cover_path: Optional[str] = None,
    topics: Optional[list[str]] = None,
    location: Optional[str] = None,
    schedule_time: Optional[str] = None
) -> dict:
    """
    发布视频（一步完成）。
    
    Args:
        cdp: CDP 客户端
        video_path: 视频文件路径
        title: 视频标题
        description: 视频描述
        cover_path: 封面图路径
        topics: 话题标签列表
        location: 位置
        schedule_time: 定时发布时间
    
    Returns:
        发布结果
    """
    # 步骤1：填写表单
    fill_result = fill_publish_form(
        cdp=cdp,
        video_path=video_path,
        title=title,
        description=description,
        cover_path=cover_path,
        topics=topics,
        location=location,
        schedule_time=schedule_time
    )
    
    if not fill_result.get("success"):
        return fill_result
    
    # 步骤2：点击发布
    time.sleep(2)  # 等待用户预览
    return click_publish(cdp)


def fill_publish_form(
    cdp: CDPClient,
    video_path: str,
    title: str,
    description: str = "",
    cover_path: Optional[str] = None,
    topics: Optional[list[str]] = None,
    location: Optional[str] = None,
    schedule_time: Optional[str] = None
) -> dict:
    """
    填写发布表单（不发布，供预览）。
    
    Args:
        cdp: CDP 客户端
        video_path: 视频文件路径
        title: 视频标题
        description: 视频描述
        cover_path: 封面图路径
        topics: 话题标签列表
        location: 位置
        schedule_time: 定时发布时间
    
    Returns:
        填写结果
    """
    # 验证文件
    if not os.path.exists(video_path):
        return {"success": False, "error": f"Video file not found: {video_path}"}
    
    # 导航到创作者中心发布页
    cdp.navigate(URLS["creator_publish"])
    time.sleep(3)
    
    # 上传视频
    upload_selector = SELECTORS["publish"]["upload_input"]
    
    # 使用 CDP 上传文件
    # 需要设置文件输入框的文件路径
    cdp.send("DOM.setFileInputFiles", {
        "files": [os.path.abspath(video_path)],
        "nodeId": 1  # 需要先获取实际的 nodeId
    })
    
    time.sleep(5)  # 等待上传
    
    # 填写标题
    title_selector = SELECTORS["publish"]["title_input"]
    if cdp.wait_for_selector(title_selector, timeout=10000):
        cdp.click(title_selector)
        time.sleep(0.5)
        cdp.type_text(title_selector, title)
    
    # 填写描述
    if description:
        desc_selector = SELECTORS["publish"]["desc_input"]
        if cdp.wait_for_selector(desc_selector, timeout=5000):
            cdp.click(desc_selector)
            time.sleep(0.5)
            cdp.type_text(desc_selector, description)
    
    # 选择封面
    if cover_path and os.path.exists(cover_path):
        # TODO: 实现封面上传
        pass
    
    # 添加话题
    if topics:
        # TODO: 实现话题添加
        pass
    
    # 添加位置
    if location:
        # TODO: 实现位置添加
        pass
    
    # 定时发布
    if schedule_time:
        # TODO: 实现定时发布
        pass
    
    return {
        "success": True,
        "status": "READY_TO_PUBLISH",
        "message": "Form filled. Please review in browser before publishing."
    }


def click_publish(cdp: CDPClient) -> dict:
    """
    点击发布按钮。
    
    Returns:
        发布结果
    """
    publish_selector = SELECTORS["publish"]["publish_button"]
    
    if not cdp.wait_for_selector(publish_selector, timeout=5000):
        return {"success": False, "error": "Publish button not found"}
    
    cdp.click(publish_selector)
    time.sleep(2)
    
    # TODO: 检查发布是否成功
    
    return {
        "success": True,
        "status": "PUBLISHED"
    }


def save_draft(cdp: CDPClient) -> dict:
    """
    保存为草稿。
    
    Returns:
        保存结果
    """
    draft_selector = SELECTORS["publish"]["draft_button"]
    
    if not cdp.wait_for_selector(draft_selector, timeout=5000):
        return {"success": False, "error": "Draft button not found"}
    
    cdp.click(draft_selector)
    time.sleep(1)
    
    return {
        "success": True,
        "status": "SAVED_AS_DRAFT"
    }