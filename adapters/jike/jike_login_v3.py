#!/usr/bin/env python3
"""
即刻登录 v3 - 抓取 localStorage token + 所有 Cookie
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

TOKEN_FILE = "/Users/zhoupeikun/WorkBuddy/Claw/jike_tokens.json"
COOKIE_FILE = "/Users/zhoupeikun/WorkBuddy/Claw/jike_cookies.json"
SHOT_DIR = "/Users/zhoupeikun/WorkBuddy/Claw"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        context = await browser.new_context(
            viewport={'width': 1400, 'height': 900},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
        )
        page = await context.new_page()

        # 监听网络请求，捕获 token
        captured_tokens = {}

        async def handle_request(request):
            headers = request.headers
            # 即刻 API 请求中会带 x-jike-access-token
            if 'x-jike-access-token' in headers:
                captured_tokens['access_token'] = headers['x-jike-access-token']
                print(f"🎯 捕获到 access_token: {headers['x-jike-access-token'][:30]}...")
            if 'x-jike-refresh-token' in headers:
                captured_tokens['refresh_token'] = headers['x-jike-refresh-token']
                print(f"🎯 捕获到 refresh_token: {headers['x-jike-refresh-token'][:30]}...")

        page.on('request', handle_request)

        print("打开即刻网页版...")
        await page.goto("https://web.okjike.com", timeout=30000)
        await asyncio.sleep(2)

        print(f"当前 URL: {page.url}")
        print("请在浏览器中扫码登录...")
        print("等待登录成功（最多5分钟）...\n")

        # 轮询等待登录
        for i in range(100):
            await asyncio.sleep(3)
            current_url = page.url
            print(f"[{i*3}s] URL: {current_url}")

            if 'login' not in current_url and 'okjike.com' in current_url and i > 0:
                print("\n✓ 已离开登录页！")
                await asyncio.sleep(3)  # 等网络请求触发

                # 1. 抓 localStorage
                print("\n=== 读取 localStorage ===")
                try:
                    local_storage = await page.evaluate("""
                        () => {
                            let result = {};
                            for (let i = 0; i < localStorage.length; i++) {
                                let key = localStorage.key(i);
                                result[key] = localStorage.getItem(key);
                            }
                            return result;
                        }
                    """)
                    print(f"localStorage keys: {list(local_storage.keys())}")

                    # 尝试找 token
                    for key, val in local_storage.items():
                        if any(k in key.lower() for k in ['token', 'auth', 'user', 'jike']):
                            print(f"  重要key: {key} = {str(val)[:80]}")

                    captured_tokens['localStorage'] = local_storage
                except Exception as e:
                    print(f"localStorage 读取失败: {e}")

                # 2. 抓 sessionStorage
                print("\n=== 读取 sessionStorage ===")
                try:
                    session_storage = await page.evaluate("""
                        () => {
                            let result = {};
                            for (let i = 0; i < sessionStorage.length; i++) {
                                let key = sessionStorage.key(i);
                                result[key] = sessionStorage.getItem(key);
                            }
                            return result;
                        }
                    """)
                    print(f"sessionStorage keys: {list(session_storage.keys())}")
                    for key, val in session_storage.items():
                        if any(k in key.lower() for k in ['token', 'auth', 'user', 'jike']):
                            print(f"  重要key: {key} = {str(val)[:80]}")

                    captured_tokens['sessionStorage'] = session_storage
                except Exception as e:
                    print(f"sessionStorage 读取失败: {e}")

                # 3. 抓所有 Cookie（包括 http-only）
                print("\n=== 读取 Cookie ===")
                try:
                    # 方法1: playwright context cookies
                    cookies = await context.cookies()
                    print(f"context.cookies(): {len(cookies)} 个")

                    # 方法2: 通过 CDP 获取所有 cookie（包括 httpOnly）
                    cdp = await context.new_cdp_session(page)
                    result = await cdp.send("Network.getAllCookies")
                    all_cookies = result.get('cookies', [])
                    print(f"CDP getAllCookies: {len(all_cookies)} 个")

                    for c in all_cookies:
                        print(f"  {c.get('name','?')} | {c.get('domain','?')} | httpOnly={c.get('httpOnly',False)}")

                    captured_tokens['cookies_cdp'] = all_cookies
                    captured_tokens['cookies_playwright'] = cookies

                    # 保存 Cookie
                    with open(COOKIE_FILE, 'w') as f:
                        json.dump(all_cookies, f, indent=2, ensure_ascii=False)
                    print(f"✓ Cookie 已保存: {COOKIE_FILE}")

                except Exception as e:
                    print(f"Cookie 读取失败: {e}")

                # 4. 保存所有 token 数据
                with open(TOKEN_FILE, 'w') as f:
                    json.dump(captured_tokens, f, indent=2, ensure_ascii=False)
                print(f"\n✓ 所有认证数据已保存: {TOKEN_FILE}")

                await page.screenshot(path=f"{SHOT_DIR}/v3_logged_in.png")
                print("截图: v3_logged_in.png")
                break
        else:
            print("超时")

        await asyncio.sleep(2)
        await browser.close()
        print("\n完成!")


if __name__ == "__main__":
    asyncio.run(main())
