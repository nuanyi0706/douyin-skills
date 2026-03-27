"""
剪映自动化核心实现
来源：lanshu-waytovideo-main/jianying-video-gen/scripts/jianying_worker.py
"""
import asyncio
import json
import re
import os
import html
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright
from typing import Optional, Dict, Any

COOKIES_FILE = 'cookies.json'
DOWNLOAD_DIR = '.'
DEBUG_SCREENSHOTS = False


def load_and_clean_cookies(cookies_path: str):
    """加载并清理 cookies"""
    with open(cookies_path, 'r') as f:
        raw = json.load(f)
    cleaned = []
    allowed = ['name', 'value', 'domain', 'path', 'expires', 'httpOnly', 'secure']
    for c in raw:
        clean = {}
        for key in allowed:
            if key == 'expires':
                val = c.get('expirationDate') or c.get('expires')
                if val is not None:
                    clean['expires'] = val
                continue
            if key in c and c[key] is not None:
                clean[key] = c[key]
        cleaned.append(clean)
    return cleaned


async def screenshot(page, name: str):
    """截图调试"""
    if not DEBUG_SCREENSHOTS:
        return
    path = os.path.join(DOWNLOAD_DIR, f'step_{name}.png')
    await page.screenshot(path=path)
    print(f"  📸 Screenshot: {path}")


async def safe_click(page, locator_or_selector, label: str, timeout: int = 5000):
    """安全点击"""
    try:
        if isinstance(locator_or_selector, str):
            loc = page.locator(locator_or_selector).first
        else:
            loc = locator_or_selector
        await loc.click(timeout=timeout)
        print(f"  ✅ {label}: clicked")
        return True
    except Exception as e:
        print(f"  ❌ {label}: {e}")
        return False


async def run(
    prompt: str,
    duration: str = "10s",
    ratio: str = "横屏",
    model: str = "Seedance 2.0",
    dry_run: bool = False,
    ref_video: Optional[str] = None,
    ref_image: Optional[str] = None,
    cookies_path: str = "cookies.json",
    output_dir: str = "."
) -> Dict[str, Any]:
    """
    运行剪映自动化流程
    
    Returns:
        dict: {"status": "success"|"failed", "output_path": str, "thread_id": str}
    """
    global COOKIES_FILE, DOWNLOAD_DIR, DEBUG_SCREENSHOTS
    
    COOKIES_FILE = cookies_path
    DOWNLOAD_DIR = output_dir
    DEBUG_SCREENSHOTS = dry_run
    
    Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
    
    if ref_video and not os.path.exists(ref_video):
        return {"status": "failed", "error": f"参考视频不存在：{ref_video}"}
    if ref_image and not os.path.exists(ref_image):
        return {"status": "failed", "error": f"参考图片不存在：{ref_image}"}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        
        # Step 1: 注入 cookies
        print("🔑 [Step 1] Injecting cookies...")
        cookies = load_and_clean_cookies(cookies_path)
        await context.add_cookies(cookies)
        print(f"  ✅ {len(cookies)} cookies injected")
        
        page = await context.new_page()
        
        # Step 2: 导航
        print("🌐 [Step 2] Navigating to xyq.jianying.com...")
        await page.goto('https://xyq.jianying.com/home', wait_until='domcontentloaded')
        await page.wait_for_timeout(8000)
        
        # Step 3: 登录验证
        print("🔍 [Step 3] Checking login status...")
        content = await page.content()
        is_logged_in = '开始创作' in content or '登录' not in content
        if not is_logged_in:
            print("  ❌ LOGIN_FAILED")
            await browser.close()
            return {"status": "failed", "error": "登录失败，请重新导出 cookies"}
        print("  ✅ LOGIN_SUCCESS")
        
        # Step 4: 点击新建
        print("🆕 [Step 4] Clicking '+ 新建'...")
        await safe_click(page, page.locator('text=新建').first, '新建')
        await page.wait_for_timeout(3000)
        
        # Step 5: 选择模式 "沉浸式短片"
        print("🎬 [Step 5] Selecting mode: 沉浸式短片...")
        mode_selected = await page.evaluate('''() => {
            const items = Array.from(document.querySelectorAll('*'));
            const candidates = items.filter(el => {
                const text = el.innerText && el.innerText.trim();
                return text === '沉浸式短片' && el.offsetHeight < 50 && el.offsetHeight > 10;
            });
            candidates.sort((a, b) => {
                const ra = a.getBoundingClientRect();
                const rb = b.getBoundingClientRect();
                return rb.left - ra.left;
            });
            for (const el of candidates) {
                const rect = el.getBoundingClientRect();
                if (rect.left > 300) {
                    el.dispatchEvent(new MouseEvent('mousedown', {bubbles:true, cancelable:true}));
                    el.dispatchEvent(new MouseEvent('mouseup', {bubbles:true, cancelable:true}));
                    el.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true}));
                    return 'selected';
                }
            }
            return 'NOT_FOUND';
        }''')
        print(f"  沉浸式短片：{mode_selected}")
        await page.wait_for_timeout(3000)
        
        # Step 6: 选择模型
        print(f"🤖 [Step 6] Selecting model: {model}...")
        model_click = await page.evaluate('''() => {
            const items = Array.from(document.querySelectorAll('*'));
            const btn = items.find(el => {
                const text = el.innerText && el.innerText.trim();
                if (!text || !text.includes('2.0')) return false;
                if (text.length > 15) return false;
                const rect = el.getBoundingClientRect();
                return rect.top > 370 && rect.left > 600 && el.offsetHeight < 50 && el.offsetHeight > 15;
            });
            if (btn) {
                btn.dispatchEvent(new MouseEvent('mousedown', {bubbles:true, cancelable:true}));
                btn.dispatchEvent(new MouseEvent('mouseup', {bubbles:true, cancelable:true}));
                btn.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true}));
                return 'opened';
            }
            return 'NOT_FOUND';
        }''')
        print(f"  Model button: {model_click}")
        await page.wait_for_timeout(2000)
        
        if 'opened' in model_click:
            model_select = await page.evaluate('''([wantFast]) => {
                const items = Array.from(document.querySelectorAll('*'));
                const candidates = items.filter(el => {
                    const text = el.innerText && el.innerText.trim();
                    if (!text) return false;
                    if (!/^Seedance\s+\d/.test(text)) return false;
                    if (/[\u4e00-\u9fff]/.test(text)) return false;
                    if (el.offsetHeight > 40 || el.offsetHeight < 10) return false;
                    const rect = el.getBoundingClientRect();
                    return rect.left > 300 && rect.left < 1100 && rect.top > 400;
                });
                for (const el of candidates) {
                    const text = el.innerText.trim();
                    const isFast = text.includes('Fast');
                    if (wantFast === isFast) {
                        el.dispatchEvent(new MouseEvent('mousedown', {bubbles:true, cancelable:true}));
                        el.dispatchEvent(new MouseEvent('mouseup', {bubbles:true, cancelable:true}));
                        el.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true}));
                        return 'selected: ' + text;
                    }
                }
                return 'NOT_FOUND';
            }''', ["Fast" in model])
            print(f"  Model select: {model_select}")
            await page.wait_for_timeout(1500)
        
        # Step 7: 选择时长
        print(f"⏱️ [Step 7] Selecting duration: {duration}...")
        dur_btn = page.locator('text=/^\\d+s$/').first
        dur_opened = await safe_click(page, dur_btn, '时长按钮')
        await page.wait_for_timeout(1500)
        
        if dur_opened:
            try:
                dur_item = page.locator(f'text=/^{duration}$/').first
                await dur_item.click(timeout=3000)
                print(f"  ✅ 时长选择：{duration}")
            except Exception as e:
                print(f"  ⚠️ 时长选择：{e}")
            await page.wait_for_timeout(1000)
        
        # Step 8: 注入 Prompt
        print(f"📝 [Step 8] Injecting prompt...")
        inject_result = await page.evaluate('''([text]) => {
            const el = document.querySelector('div[contenteditable="true"]');
            if (el) {
                el.innerText = text;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                return 'OK';
            }
            return 'FAILED';
        }''', [prompt])
        print(f"  Inject: {inject_result}")
        await page.wait_for_timeout(1000)
        
        if dry_run:
            print("\n✅ DRY-RUN 完成！")
            await browser.close()
            return {"status": "dry_run", "message": "Dry run completed"}
        
        # Step 9: 提交
        thread_id = None
        
        async def sniff_thread(response):
            nonlocal thread_id
            if thread_id:
                return
            try:
                text = await response.text()
                if 'thread_id' in text:
                    import json as _json
                    data = _json.loads(text)
                    tid = data.get('thread_id') or data.get('data', {}).get('thread_id')
                    if not tid:
                        m = re.search(r'"thread_id"\s*:\s*"([^"]+)"', text)
                        if m:
                            tid = m.group(1)
                    if tid:
                        thread_id = tid
                        print(f"\n  🎯 Sniffed thread_id: {tid}")
            except Exception:
                pass
        
        page.on('response', sniff_thread)
        
        print("🖱️ [Step 9] Clicking '开始创作'...")
        submit_clicked = await safe_click(page, page.locator('text=开始创作').first, '开始创作')
        await page.wait_for_timeout(5000)
        
        if not submit_clicked:
            await browser.close()
            return {"status": "failed", "error": "提交失败"}
        
        # 等待 thread_id
        for _ in range(10):
            if thread_id:
                break
            await page.wait_for_timeout(2000)
        
        if not thread_id:
            print("  ⚠️ thread_id not captured")
            await browser.close()
            return {"status": "failed", "error": "未获取到 thread_id"}
        
        # Step 10: 导航到详情页 + 轮询视频
        detail_url = f"https://xyq.jianying.com/home?tab_name=integrated-agent&thread_id={thread_id}"
        print(f"🔗 [Step 10] Navigating to detail page...")
        await page.goto(detail_url, wait_until='domcontentloaded')
        await page.wait_for_timeout(8000)
        
        safe_name = ''.join(c for c in prompt[:15] if c.isalnum() or c in '_ ')
        filename = f"{safe_name}_{duration}.mp4"
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        
        print("⏳ Polling for video...")
        mp4_url = None
        for i in range(120):
            await page.wait_for_timeout(5000)
            
            mp4_url = await page.evaluate('''() => {
                const v = document.querySelector('video');
                if (v && v.src && v.src.includes('.mp4')) return v.src;
                const html = document.documentElement.innerHTML;
                const m = html.match(/https?:\/\/[^"'\\s\\\\]+\.mp4[^"'\\s\\\\]*/);
                return m ? m[0] : null;
            }''')
            
            if mp4_url:
                mp4_url = html.unescape(mp4_url)
                print(f"\n  🎉 Found MP4!")
                break
            
            if i % 12 == 0 and i > 0:
                print(f"  ⏳ Still generating... ({i*5}s)")
                await page.reload(wait_until='domcontentloaded')
                await page.wait_for_timeout(5000)
        
        if not mp4_url:
            print("  ❌ Timeout")
            await browser.close()
            return {"status": "failed", "error": "生成超时"}
        
        # Step 11: 下载视频
        print(f"📥 [Step 11] Downloading...")
        result = subprocess.run(
            ['curl', '-L', '-o', filepath, '-s', '-w', '%{http_code}', mp4_url],
            capture_output=True, text=True, timeout=120
        )
        http_code = result.stdout.strip()
        
        if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  ✅ Saved: {filepath} ({size_mb:.1f}MB)")
        else:
            print(f"  ❌ Download failed: HTTP {http_code}")
            await browser.close()
            return {"status": "failed", "error": f"下载失败：HTTP {http_code}"}
        
        await browser.close()
        
        return {
            "status": "success",
            "output_path": filepath,
            "thread_id": thread_id,
            "mp4_url": mp4_url
        }
