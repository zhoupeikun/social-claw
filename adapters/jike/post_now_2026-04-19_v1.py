#!/usr/bin/env python3
"""
即刻发帖脚本 - 单次发帖用
内容：《古拉格群岛》思辨帖
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

TOKEN_FILE = "/Users/zhoupeikun/WorkBuddy/Claw/jike_tokens.json"
SHOT_DIR = "/Users/zhoupeikun/WorkBuddy/Claw"

POST_CONTENT = """读《古拉格群岛》时那种系统如何悄然异化个体的寒意。如今某些推荐算法，是否也在用温柔的效率，塑造着思想的"群岛"。我们享受着个性化的牢笼，却失去了迷路的权利。既要又要还要。(｡･ω･ａ)ﾉ♡"""


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

        page.on('request', on_request)

        # === STEP 1: 登录 ===
        print("="*50)
        print("STEP 1: 打开即刻，请扫码登录")
        print("="*50)
        await page.goto("https://web.okjike.com", timeout=30000)
        await asyncio.sleep(2)
        print(f"当前URL: {page.url}")

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
        await asyncio.sleep(2)
        ls = await page.evaluate("() => ({ access: localStorage.getItem('JK_ACCESS_TOKEN'), refresh: localStorage.getItem('JK_REFRESH_TOKEN') })")
        token_save = {
            'localStorage': {
                'JK_ACCESS_TOKEN': ls.get('access', ''),
                'JK_REFRESH_TOKEN': ls.get('refresh', ''),
            }
        }
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token_save, f, indent=2)
        print(f"✓ Token 已更新保存")

        # === STEP 3: 发帖 ===
        print("\n" + "="*50)
        print("STEP 3: 发帖")
        print("="*50)
        print(f"内容预览: {POST_CONTENT[:40]}...")

        compose_selectors = [
            '[contenteditable="true"]',
            'textarea[placeholder]',
            '[placeholder*="分享"]',
            '[placeholder*="说"]',
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
            print("❌ 没找到输入框，截图查看")
            await page.screenshot(path=f"{SHOT_DIR}/post_now_no_compose.png")
        else:
            await page.keyboard.type(POST_CONTENT, delay=30)
            await asyncio.sleep(1)
            await page.screenshot(path=f"{SHOT_DIR}/post_now_typed.png")
            print("✓ 内容已输入")

            # 找发布按钮
            for sel in ['button:has-text("发送")', 'button:has-text("发布")', 'button[type="submit"]']:
                try:
                    btn = page.locator(sel).first
                    if await btn.is_visible(timeout=1000):
                        print(f"✓ 找到发布按钮: {sel}")
                        await btn.click()
                        await asyncio.sleep(3)
                        await page.screenshot(path=f"{SHOT_DIR}/post_now_done.png")
                        print("✅ 发帖完成！截图: post_now_done.png")
                        break
                except:
                    pass

        print("\n浏览器保持打开 30 秒...")
        await asyncio.sleep(30)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
