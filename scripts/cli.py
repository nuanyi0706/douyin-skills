"""
抖音自动化 CLI 入口。

提供统一的命令行接口。
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from douyin import CDPClient
from douyin.login import check_login, login_qrcode, delete_cookies
from douyin.search import search_videos, get_video_detail
from douyin.feeds import get_feed_videos, get_user_profile, get_user_videos
from douyin.publish import fill_publish_form, click_publish, save_draft
from douyin.interact import (
    get_current_video_info, like_current_video, collect_current_video,
    open_comments, post_comment, follow_current_author, next_video, previous_video
)


def output_json(data: dict):
    """输出 JSON 格式结果"""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_check_login(args):
    """检查登录状态"""
    cdp = CDPClient(host=args.host, port=args.port)
    try:
        cdp.connect()
        result = check_login(cdp)
        output_json(result)
        sys.exit(0 if result.get("logged_in") else 1)
    finally:
        cdp.close()


def cmd_login(args):
    """扫码登录"""
    cdp = CDPClient(host=args.host, port=args.port)
    try:
        cdp.connect()
        result = login_qrcode(cdp, account=args.account, timeout=args.timeout)
        output_json(result)
        sys.exit(0 if result.get("success") else 2)
    finally:
        cdp.close()


def cmd_delete_cookies(args):
    """删除 Cookie"""
    result = delete_cookies(account=args.account)
    output_json({"success": result})
    sys.exit(0)


def cmd_search_videos(args):
    """搜索视频"""
    cdp = CDPClient(host=args.host, port=args.port)
    try:
        cdp.connect()
        result = search_videos(
            cdp=cdp,
            keyword=args.keyword,
            limit=args.limit
        )
        output_json(result)
        sys.exit(0)
    finally:
        cdp.close()


def cmd_get_feed(args):
    """获取首页视频"""
    cdp = CDPClient(host=args.host, port=args.port)
    try:
        cdp.connect()
        result = get_feed_videos(cdp=cdp, limit=args.limit)
        output_json(result)
        sys.exit(0)
    finally:
        cdp.close()


def cmd_get_user(args):
    """获取用户信息"""
    cdp = CDPClient(host=args.host, port=args.port)
    try:
        cdp.connect()
        result = get_user_profile(cdp=cdp, user_id=args.user_id)
        output_json(result)
        sys.exit(0)
    finally:
        cdp.close()


def cmd_like(args):
    """点赞当前视频"""
    cdp = CDPClient(host=args.host, port=args.port)
    try:
        cdp.connect()
        result = like_current_video(cdp)
        output_json(result)
        sys.exit(0 if result.get("success") else 2)
    finally:
        cdp.close()


def cmd_collect(args):
    """收藏当前视频"""
    cdp = CDPClient(host=args.host, port=args.port)
    try:
        cdp.connect()
        result = collect_current_video(cdp)
        output_json(result)
        sys.exit(0 if result.get("success") else 2)
    finally:
        cdp.close()


def cmd_comment(args):
    """发表评论"""
    cdp = CDPClient(host=args.host, port=args.port)
    try:
        cdp.connect()
        result = post_comment(cdp=cdp, content=args.content)
        output_json(result)
        sys.exit(0 if result.get("success") else 2)
    finally:
        cdp.close()


def cmd_follow(args):
    """关注当前作者"""
    cdp = CDPClient(host=args.host, port=args.port)
    try:
        cdp.connect()
        result = follow_current_author(cdp)
        output_json(result)
        sys.exit(0 if result.get("success") else 2)
    finally:
        cdp.close()


def cmd_video_info(args):
    """获取当前视频信息"""
    cdp = CDPClient(host=args.host, port=args.port)
    try:
        cdp.connect()
        result = get_current_video_info(cdp)
        output_json(result)
        sys.exit(0)
    finally:
        cdp.close()


def cmd_fill_publish(args):
    """填写发布表单"""
    cdp = CDPClient(host=args.host, port=args.port)
    try:
        cdp.connect()
        
        title = args.title
        if args.title_file:
            with open(args.title_file, "r", encoding="utf-8") as f:
                title = f.read().strip()
        
        result = fill_publish_form(
            cdp=cdp,
            video_path=args.video,
            title=title
        )
        output_json(result)
        sys.exit(0 if result.get("success") else 2)
    finally:
        cdp.close()


def main():
    """CLI 主入口"""
    parser = argparse.ArgumentParser(
        description="抖音自动化 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("--host", default="127.0.0.1", help="Chrome 调试主机")
    parser.add_argument("--port", type=int, default=9222, help="Chrome 调试端口")
    parser.add_argument("--account", default="default", help="账号名称")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # check-login
    p = subparsers.add_parser("check-login", help="检查登录状态")
    p.set_defaults(func=cmd_check_login)
    
    # login
    p = subparsers.add_parser("login", help="扫码登录")
    p.add_argument("--timeout", type=int, default=120)
    p.set_defaults(func=cmd_login)
    
    # delete-cookies
    p = subparsers.add_parser("delete-cookies", help="删除 Cookie")
    p.set_defaults(func=cmd_delete_cookies)
    
    # search-videos
    p = subparsers.add_parser("search-videos", help="搜索视频")
    p.add_argument("--keyword", required=True)
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_search_videos)
    
    # get-feed
    p = subparsers.add_parser("get-feed", help="获取首页视频")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_get_feed)
    
    # get-user
    p = subparsers.add_parser("get-user", help="获取用户信息")
    p.add_argument("--user-id", required=True)
    p.set_defaults(func=cmd_get_user)
    
    # like
    p = subparsers.add_parser("like", help="点赞当前视频")
    p.set_defaults(func=cmd_like)
    
    # collect
    p = subparsers.add_parser("collect", help="收藏当前视频")
    p.set_defaults(func=cmd_collect)
    
    # comment
    p = subparsers.add_parser("comment", help="发表评论")
    p.add_argument("--content", required=True)
    p.set_defaults(func=cmd_comment)
    
    # follow
    p = subparsers.add_parser("follow", help="关注当前作者")
    p.set_defaults(func=cmd_follow)
    
    # video-info
    p = subparsers.add_parser("video-info", help="获取当前视频信息")
    p.set_defaults(func=cmd_video_info)
    
    # fill-publish
    p = subparsers.add_parser("fill-publish", help="填写发布表单")
    p.add_argument("--video", required=True)
    p.add_argument("--title")
    p.add_argument("--title-file")
    p.set_defaults(func=cmd_fill_publish)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)


if __name__ == "__main__":
    main()