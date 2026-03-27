"""
抖音 CDP WebSocket 客户端。

通过 Chrome DevTools Protocol 控制浏览器进行自动化操作。
"""

import json
import random
import time
from typing import Any, Optional
from urllib.parse import urljoin

import requests
import websockets.sync.client as ws_client


class CDPError(Exception):
    """CDP 错误"""
    pass


class CDPClient:
    """CDP WebSocket 客户端"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9222):
        self.host = host
        self.port = port
        self.ws: Optional[ws_client.connect] = None
        self.message_id = 0
        self.page_url: Optional[str] = None
    
    def connect(self, page_url: Optional[str] = None) -> bool:
        """连接到 Chrome 调试端口"""
        # 获取可用页面
        pages = self._get_pages()
        if not pages:
            raise CDPError("No available Chrome pages. Make sure Chrome is running with --remote-debugging-port=9222")
        
        # 选择页面
        if page_url:
            target_page = next((p for p in pages if page_url in p.get("url", "")), None)
            if not target_page:
                # 创建新标签页
                target_page = self._new_page(page_url)
        else:
            # 使用第一个页面
            target_page = pages[0]
        
        ws_url = target_page.get("webSocketDebuggerUrl")
        if not ws_url:
            raise CDPEerror("No WebSocket URL found for page")
        
        self.ws = ws_client.connect(ws_url)
        self.page_url = target_page.get("url")
        return True
    
    def close(self):
        """关闭连接"""
        if self.ws:
            self.ws.close()
            self.ws = None
    
    def _get_pages(self) -> list[dict]:
        """获取所有可用页面"""
        try:
            response = requests.get(f"http://{self.host}:{self.port}/json", timeout=5)
            return response.json()
        except Exception:
            return []
    
    def _new_page(self, url: str) -> dict:
        """创建新标签页"""
        response = requests.get(f"http://{self.host}:{self.port}/json/new?{url}", timeout=5)
        return response.json()
    
    def send(self, method: str, params: Optional[dict] = None) -> dict:
        """发送 CDP 命令"""
        if not self.ws:
            raise CDPError("Not connected to Chrome")
        
        self.message_id += 1
        message = {
            "id": self.message_id,
            "method": method,
            "params": params or {}
        }
        
        self.ws.send(json.dumps(message))
        
        while True:
            response = self.ws.recv()
            data = json.loads(response)
            if data.get("id") == self.message_id:
                if "error" in data:
                    raise CDPError(data["error"].get("message", "Unknown CDP error"))
                return data.get("result", {})
    
    def navigate(self, url: str, wait_until: str = "load", timeout: int = 30000) -> dict:
        """导航到指定页面"""
        result = self.send("Page.navigate", {"url": url})
        self.page_url = url
        
        # 等待页面加载完成（使用轮询方式）
        import time
        start = time.time()
        while time.time() - start < timeout / 1000:
            ready_state = self.evaluate("document.readyState")
            if ready_state == "complete":
                break
            time.sleep(0.2)
        return result
    
    def evaluate(self, expression: str) -> Any:
        """执行 JavaScript 代码"""
        result = self.send("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": True
        })
        return result.get("result", {}).get("value")
    
    def query_selector(self, selector: str) -> Optional[str]:
        """查询选择器，返回元素 ID"""
        result = self.send("DOM.querySelector", {
            "nodeId": 1,  # 根节点
            "selector": selector
        })
        return result.get("nodeId")
    
    def click(self, selector: str, delay: float = 0.1) -> bool:
        """点击元素"""
        # 获取元素位置
        expression = f"""
        (function() {{
            const el = document.querySelector('{selector}');
            if (!el) return null;
            const rect = el.getBoundingClientRect();
            return {{
                x: rect.x + rect.width / 2,
                y: rect.y + rect.height / 2
            }};
        }})()
        """
        position = self.evaluate(expression)
        if not position:
            return False
        
        # 使用 CDP 模拟真实点击
        x, y = position["x"], position["y"]
        
        # 鼠标移动
        self.send("Input.dispatchMouseEvent", {
            "type": "mouseMoved",
            "x": x + random.uniform(-5, 5),
            "y": y + random.uniform(-5, 5)
        })
        
        time.sleep(delay)
        
        # 鼠标按下
        self.send("Input.dispatchMouseEvent", {
            "type": "mousePressed",
            "x": x,
            "y": y,
            "button": "left",
            "clickCount": 1
        })
        
        time.sleep(delay + random.uniform(0.05, 0.15))
        
        # 鼠标释放
        self.send("Input.dispatchMouseEvent", {
            "type": "mouseReleased",
            "x": x,
            "y": y,
            "button": "left",
            "clickCount": 1
        })
        
        return True
    
    def type_text(self, selector: str, text: str, delay: float = 0.05) -> bool:
        """输入文本"""
        # 先点击聚焦
        self.click(selector)
        time.sleep(0.1)
        
        # 逐字输入，模拟人类行为
        for char in text:
            self.send("Input.dispatchKeyEvent", {
                "type": "keyDown",
                "text": char
            })
            time.sleep(delay + random.uniform(0, 0.05))
            self.send("Input.dispatchKeyEvent", {
                "type": "keyUp",
                "text": char
            })
        
        return True
    
    def get_text(self, selector: str) -> Optional[str]:
        """获取元素文本"""
        expression = f"""
        document.querySelector('{selector}')?.textContent || null
        """
        return self.evaluate(expression)
    
    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """获取元素属性"""
        expression = f"""
        document.querySelector('{selector}')?.getAttribute('{attribute}') || null
        """
        return self.evaluate(expression)
    
    def wait_for_selector(self, selector: str, timeout: int = 10000) -> bool:
        """等待选择器出现"""
        start = time.time()
        while time.time() - start < timeout / 1000:
            result = self.evaluate(f"!!document.querySelector('{selector}')")
            if result:
                return True
            time.sleep(0.2)
        return False
    
    def screenshot(self, path: str) -> bool:
        """截图"""
        result = self.send("Page.captureScreenshot", {"format": "png"})
        if "data" in result:
            import base64
            with open(path, "wb") as f:
                f.write(base64.b64decode(result["data"]))
            return True
        return False
    
    def get_page_data(self) -> dict:
        """获取页面数据（从 __INITIAL_STATE__ 提取）"""
        expression = """
        (function() {
            try {
                return window.__INITIAL_STATE__ || window.__RENDER_DATA__ || null;
            } catch(e) {
                return null;
            }
        })()
        """
        return self.evaluate(expression) or {}