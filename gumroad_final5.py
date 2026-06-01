#!/usr/bin/env python3
"""EXACT REPLICA of the pattern that created first 8 products. JS clicks, query_selector_all for files."""
from playwright.sync_api import sync_playwright
import json, os, time, re

DIR = "/home/billonare2/digital-products"
PACKAGED = os.path.join(DIR, "packaged")
URLS_FILE = os.path.join(DIR, "gumroad_urls.json")

remaining = [
    ("AI Visibility Audit", "149", "ai-visibility-audit.zip", "Check brand visibility across ChatGPT, Claude, Perplexity. 0-100 GEO Score with industry comparison. 6 specific ranked fixes for AI search optimization."),
    ("CrawlShield", "49", "crawl-shield.zip", "Block AI crawlers. See which bots hit your site and estimated bandwidth cost. Generate exact configs: robots.txt, nginx, Cloudflare WAF, .htaccess. One-click toggle per crawler."),
    ("AgencyAuditor", "149", "agency-auditor.zip", "Fire Risk Score (0-100). Red flag detection: cookie-cutter reports, cherry-picked metrics, no raw data. KPI comparison: promised vs actual leads. Industry benchmarks. Ranked action plan."),
    ("DockSecure CVE Scanner", "29", "docksecure-cve-scanner.zip", "Scan 8 containers against real CVE data. Prioritized critical/high CVEs by CVSS score. Fix version suggestions for each vulnerability. Container-by-container risk breakdown. Exportable security report."),
    ("DevPath Career Roadmap", "29", "devpath-career.zip", "5 target roles: DevOps Engineer, SRE, Cloud Engineer, Platform Engineer, DevSecOps. Role fit scoring. Skill gap analysis with visual bars. 12-week roadmap with specific weekly tasks. Salary benchmarks $130K-$160K+."),
]

urls = json.load(open(URLS_FILE))
print(f"Start: {len(urls)}/13")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
    ctx = browser.new_context(storage_state=".gumroad_auth.json")
    page = ctx.new_page()
    
    for i, (name, price, zip_name, desc) in enumerate(remaining):
        print(f"\n[{i+1}/5] {name} (${price})")
        
        page.goto("https://app.gumroad.com/products/new", wait_until="networkidle")
        time.sleep(4)
        
        # JS: name + price (EXACT pattern that worked)
        page.evaluate(f'''
            (() => {{
                const ni = document.querySelector('input[id*="name"]');
                if (ni) {{
                    Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set.call(ni, {json.dumps(name)});
                    ni.dispatchEvent(new Event("input", {{bubbles: true}}));
                    ni.dispatchEvent(new Event("change", {{bubbles: true}}));
                    ni.dispatchEvent(new Event("blur", {{bubbles: true}}));
                }}
                const pi = document.querySelector('input[id*="price"]');
                if (pi) {{
                    Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set.call(pi, "{price}");
                    pi.dispatchEvent(new Event("input", {{bubbles: true}}));
                    pi.dispatchEvent(new Event("change", {{bubbles: true}}));
                }}
            }})()
        ''')
        time.sleep(1)
        
        # JS: Click Digital product
        page.evaluate('''
            (() => {
                for (const b of document.querySelectorAll('button')) {
                    if (b.textContent.includes('Digital product')) {
                        b.click();
                        return;
                    }
                }
            })()
        ''')
        time.sleep(1)
        
        # JS: Click Next: Customize
        page.evaluate('''
            (() => {
                for (const b of document.querySelectorAll('button')) {
                    if (b.textContent.includes('Next')) {
                        b.click();
                        return;
                    }
                }
            })()
        ''')
        time.sleep(5)
        
        cur = page.url
        print(f"  Step2: {'YES' if 'new' not in cur.split('/')[-1] else 'STUCK'}")
        
        if 'new' in cur.split('/')[-1]:
            continue
        
        # JS: description
        page.evaluate(f'''
            (() => {{
                for (const d of document.querySelectorAll('div[contenteditable="true"]')) {{
                    if (d.offsetParent !== null) {{
                        d.innerHTML = {json.dumps(desc)};
                        d.dispatchEvent(new Event("input", {{bubbles: true}}));
                        break;
                    }}
                }}
            }})()
        ''')
        time.sleep(0.5)
        
        # File upload using query_selector_all (pattern that worked for first 8)
        zip_path = os.path.join(PACKAGED, zip_name)
        fis = page.query_selector_all('input[type="file"]')
        uploaded = False
        for fi in fis:
            try:
                fi.set_input_files(zip_path)
                uploaded = True
                print(f"  ✓ Upload: {zip_name}")
                break
            except:
                pass
        
        if not uploaded:
            print(f"  ✗ No upload — {len(fis)} file inputs found")
            continue
        
        time.sleep(2)
        
        # JS: Save
        page.evaluate('''
            (() => {
                for (const b of document.querySelectorAll('button')) {
                    const t = b.textContent.trim();
                    if (t === 'Save' || t === 'Save and continue') {
                        b.click();
                        return;
                    }
                }
            })()
        ''')
        time.sleep(5)
        
        cur = page.url
        m = re.search(r'/products/([a-zA-Z0-9_-]+)', cur)
        slug = m.group(1) if m else None
        
        if slug and slug != 'new':
            gurl = f"https://gumroad.com/l/{slug}"
            urls[name] = gurl
            json.dump(urls, open(URLS_FILE, "w"), indent=2)
            print(f"  ✓ DONE: {gurl}")
        else:
            print(f"  ⚠ No slug: {cur[:80]}")
        
        time.sleep(10)  # cooldown
    
    ctx.close()
    browser.close()

print(f"\n{len(urls)}/13 on Gumroad")
for n, u in sorted(urls.items()):
    print(f"  {n}: {u}")
