---
name: dy-auth
description: |
  抖音账号认证管理。支持登录检查、扫码登录、多账号切换。
  
  触发场景：登录抖音、检查抖音登录、切换抖音账号、抖音账号管理。
  
  使用此技能当用户需要：登录抖音账号、检查登录状态、切换账号、管理多个抖音账号。
---

# 抖音认证管理

## 功能

- 检查登录状态
- 扫码登录
- 多账号管理
- Cookie 持久化

## CLI 命令

```bash
# 检查登录状态
python scripts/cli.py check-login

# 扫码登录
python scripts/cli.py login

# 列出所有账号
python scripts/cli.py list-accounts

# 切换账号
python scripts/cli.py switch-account --account NAME

# 清除 cookies（退出登录）
python scripts/cli.py delete-cookies
```

## 返回格式

```json
{
  "logged_in": true,
  "user": {
    "nickname": "用户昵称",
    "user_id": "用户ID",
    "avatar": "头像URL"
  }
}
```

## 抖音登录流程

1. 启动 Chrome 浏览器（有窗口模式）
2. 导航到抖音首页
3. 检测登录状态
4. 未登录时显示二维码
5. 用户扫码确认
6. 保存 Cookie

## 相关文件

- `scripts/douyin/login.py` - 登录逻辑
- `scripts/douyin/cookies.py` - Cookie 管理
- `scripts/douyin/selectors.py` - 登录相关选择器