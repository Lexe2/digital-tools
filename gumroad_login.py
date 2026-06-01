#!/usr/bin/env python3
"""Login to Gumroad using JavaScript injection — no selectors, no clicking inputs."""
from playwright.sync_api import sync_playwright
import time

EMAIL = "helpteks@gmail.com"
PW = "Sathome4455$$"

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        '/home/billonare2/.config/chromium/Default',
        headless=False,
        args=['--no-sandbox','--disable-gpu','--start-maximized']
    )
    page = ctx.new_page()
    page.goto('https://gumroad.com/login', wait_until='networkidle')
    time.sleep(3)
    
    # JavaScript injection — directly set values and click
    result = page.evaluate(f'''
        (() => {{
            const inputs = document.querySelectorAll('input:not([type="hidden"])');
            inputs[0].value = "{EMAIL}";
            inputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
            inputs[1].value = "{PW}";
            inputs[1].dispatchEvent(new Event('input', {{ bubbles: true }}));
            const btn = document.querySelector('button[type="submit"]');
            if (!btn) {{
                const buttons = document.querySelectorAll('button');
                for (const b of buttons) {{
                    if (b.textContent.trim() === 'Login' || b.textContent.trim() === 'Log in') {{
                        b.click();
                        return 'clicked:' + b.textContent;
                    }}
                }}
                return 'no_button';
            }}
            btn.click();
            return 'clicked';
        }})()
    ''')
    print(f"JS result: {result}")
    time.sleep(4)
    
    title = page.title()
    print(f"Page: {title}")
    
    if 'Authentication' in title:
        code = input("Enter 2FA code: ").strip()
        if code:
            page.evaluate(f'''
                document.querySelector('input[type="text"]').value = "{code}";
                document.querySelector('input[type="text"]').dispatchEvent(new Event('input', {{ bubbles: true }}));
                document.querySelector('button[type="submit"]').click();
            ''')
            print(f"2FA submitted: {code}")
            time.sleep(5)
            u = page.url
            print(f"After 2FA: {u[:80]}")
            if 'login' not in u.lower() and 'Authentication' not in u:
                print("LOGGED IN!")
                ctx.storage_state(path='/home/billonare2/digital-products/.gumroad_auth.json')
                print("Session saved!")
    elif 'login' not in page.url.lower():
        print("Logged in (no 2FA)")
        ctx.storage_state(path='/home/billonare2/digital-products/.gumroad_auth.json')
    
    ctx.close()
