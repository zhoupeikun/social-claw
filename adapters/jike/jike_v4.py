#!/usr/bin/env python3
"""
即刻一体化脚本 v4
流程: 登录 -> 保存token -> 直接发帖（不关闭浏览器）
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

TOKEN_FILE = "/Users/zhoupeikun/WorkBuddy/Claw/jike_tokens.json"
SHOT_DIR = "/Users/zhoupeikun/WorkBuddy/Claw"

# ===== 发帖内容 =====
POST_CONTENT = """用 Vibe Coding 方式开发了个小工具，让 AI 帮我把 14 年的微博数据变成数字分身 🤖

从 5000+ 条内容里蒸馏出一个「PrettyHugo」：
• 说话习惯、常用词、情绪模式
• 深夜的感性和白天的克制
• 对华为的偏执，对产品的较真

现在它能模仿我写即刻了 哈哈

#Vibe Coding# (｡･ω･ａ)ﾉ♡"""


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context(
            viewport={'width': 1400, 'height': 900},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        # 监听 API 请求
        api_log = []
        async def on_request(req):
            if 'ruguoapp.com' in req.url and req.method == 'POST':
                pd = None
                try: pd = req.post_data
                except: pass
                api_log.append({'url': req.url, 'body': pd})
                print(f"[API] POST {req.url.split('ruguoapp.com')[-1]}")
                if pd and 'content' in str(pd):
                    print(f"  !! 发帖请求体: {pd[:300]}")
        page.on('request', on_request)

        # === STEP 1: 登录 ===
        print("="*50)
        print("STEP 1: 打开即刻，等待扫码登录")
        print("="*50)
        await page.goto("https://web.okjike.com", timeout=30000)
        await asyncio.sleep(2)
        print(f"当前URL: {page.url}")

        # 等待离开登录页
        for i in range(100):
            await asyncio.sleep(3)
            url = page.url
            if 'login' not in url and 'okjike.com' in url:
                print(f"[{i*3}s] ✓ 登录成功! URL: {url}")
                break
            print(f"[{i*3}s] 等待登录... URL: {url}")
        else:
            print("登录超时")
            await browser.close()
            return

        # === STEP 2: 保存 token ===
        print("\n" + "="*50)
        print("STEP 2: 保存 Token")
        print("="*50)
        await asyncio.sleep(2)

        ls = await page.evaluate("() => ({ access: localStorage.getItem('JK_ACCESS_TOKEN'), refresh: localStorage.getItem('JK_REFRESH_TOKEN') })")
        print(f"access_token: {(ls.get('access') or '')[:50]}...")
        print(f"refresh_token: {(ls.get('refresh') or '')[:50]}...")

        token_save = {
            'localStorage': {
                'JK_ACCESS_TOKEN': ls.get('access', ''),
                'JK_REFRESH_TOKEN': ls.get('refresh', ''),
            }
        }
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_save, f, indent=2)
        print(f"✓ Token 已保存到 {TOKEN_FILE}")

        # === STEP 3: 发帖 ===
        print("\n" + "="*50)
        print("STEP 3: 发帖")
        print("="*50)
        await page.screenshot(path=f"{SHOT_DIR}/v4_logged_in.png")
        print(f"内容: {POST_CONTENT[:50]}...")

        # 找发帖输入框 - 即刻主页的发帖区域
        compose_selectors = [
            'textarea[placeholder]',
            '[contenteditable="true"]',
            '[placeholder*="分享"]',
            '[placeholder*="说"]',
            '[placeholder*="想法"]',
            '[placeholder*="动态"]',
            'textarea',
            '[role="textbox"]',
        ]

        found_compose = False
        for sel in compose_selectors:
            try:
                el = page.locator(sel).first
                if await el.is_visible(timeout=1500):
                    placeholder = await el.get_attribute('placeholder') or ''
                    print(f"✓ 找到输入框: {sel} placeholder='{placeholder}'")
                    await el.click()
                    await asyncio.sleep(1)
                    found_compose = True
                    break
            except:
                pass

        if not found_compose:
            print("没找到输入框，截图看看页面结构")
            await page.screenshot(path=f"{SHOT_DIR}/v4_no_compose.png")

            # 列出所有可见 input/textarea
            els = await page.query_selector_all('input, textarea, [contenteditable]')
            print(f"页面共 {len(els)} 个输入类元素:")
            for el in els[:15]:
                try:
                    tag = await el.evaluate("el => el.tagName")
                    ph = await el.get_attribute('placeholder') or ''
                    cls = await el.get_attribute('class') or ''
                    visible = await el.is_visible()
                    print(f"  <{tag}> placeholder='{ph}' class='{cls[:40]}' visible={visible}")
                except:
                    pass
        else:
            # 输入内容
            await page.keyboard.type(POST_CONTENT, delay=30)
            await asyncio.sleep(1)
            await page.screenshot(path=f"{SHOT_DIR}/v4_typed.png")
            print("内容已输入，截图: v4_typed.png")

            # 找发布按钮
            submit_selectors = [
                'button:has-text("发布")',
                'button:has-text("发送")',
                '[class*="submit"]',
                '[class*="publish"]',
                '[class*="Send"]',
                '[class*="Post"]',
                'button[type="submit"]',
            ]
            for sel in submit_selectors:
                try:
                    btn = page.locator(sel).first
                    if await btn.is_visible(timeout=1000):
                        print(f"✓ 找到发布按钮: {sel}")
                        await btn.click()
                        await asyncio.sleep(3)
                        await page.screenshot(path=f"{SHOT_DIR}/v4_posted.png")
                        print("✓ 已点击发布！截图: v4_posted.png")
                        break
                except:
                    pass

        # 保存所有 API 日志
        with open(f"{SHOT_DIR}/v4_api_log.json", 'w') as f:
            json.dump(api_log, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n共捕获 {len(api_log)} 个 API POST 请求")

        print("\n浏览器保持打开 60 秒...")
        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
