#!/usr/bin/env python3
"""Finish last 5 Gumroad products using CloakBrowser stealth mode."""
from cloakbrowser import launch
import json, os, time, re

DIR = "/home/billonare2/digital-products"
PACKAGED = os.path.join(DIR, "packaged")
URLS_FILE = os.path.join(DIR, "gumroad_urls.json")
AUTH = json.load(open(os.path.join(DIR, ".gumroad_auth.json")))

remaining = [
    ("AI Visibility Audit", "149", "ai-visibility-audit.zip", "Check brand visibility across ChatGPT, Claude, Perplexity. 0-100 GEO Score. 6 ranked fixes."),
    ("CrawlShield", "49", "crawl-shield.zip", "Block AI crawlers. See bandwidth cost. Generate robots.txt, nginx, Cloudflare, .htaccess configs."),
    ("AgencyAuditor", "149", "agency-auditor.zip", "Fire Risk Score. Red flag detection. KPI comparison. For businesses paying $10K-100K/month to agencies."),
    ("DockSecure CVE Scanner", "29", "docksecure-cve-scanner.zip", "Scan Docker for CVEs. Prioritized criticals. Fix versions. Exportable report."),
    ("DevPath Career Roadmap", "29", "devpath-career.zip", "5 target roles. Personalized 90-day roadmap. 12 weekly tasks. Salary benchmarks."),
]

urls = json.load(open(URLS_FILE))

browser = launch(headless=True, humanize=True)
ctx = browser.new_context()
ctx.add_cookies(AUTH["cookies"])
page = ctx.new_page()

for name, price, zip_name, desc in remaining:
    print(f"\n{name} (${price})")
    
    page.goto("https://app.gumroad.com/products/new", wait_until="networkidle")
    time.sleep(5)
    
    # Fill name
    page.fill('input[id*="name"]:visible', name)
    time.sleep(0.5)
    # Fill price
    page.fill('input[id*="price"]:visible', price)
    time.sleep(0.5)
    # Click Digital product
    page.click('button:has-text("Digital product")')
    time.sleep(1)
    # Click Next
    page.click('button[type="submit"]')
    time.sleep(5)
    
    url_now = page.url
    step2 = "/new" not in url_now.split("/")[-1]
    print(f"  Step2: {'YES' if step2 else 'STUCK'}")
    
    if not step2:
        print(f"  URL: {url_now[:80]}")
        continue
    
    # Description
    desc_div = page.locator('div[contenteditable="true"]:visible').first
    if desc_div.count() > 0:
        desc_div.fill(desc)
    
    # Upload
    zip_path = os.path.join(PACKAGED, zip_name)
    fi = page.locator('input[type="file"]').first
    if fi.count() > 0:
        fi.set_input_files(zip_path)
        print(f"  Uploaded: {zip_name}")
        time.sleep(3)
        
        page.locator('button:has-text("Save")').first.click()
        time.sleep(5)
        
        cur = page.url
        m = re.search(r'/products/([a-zA-Z0-9_-]+)', cur)
        slug = m.group(1) if m else None
        if slug and slug != "new":
            gurl = f"https://gumroad.com/l/{slug}"
            urls[name] = gurl
            json.dump(urls, open(URLS_FILE, "w"), indent=2)
            print(f"  DONE: {gurl}")
    else:
        # Count all file inputs on page
        fis = page.query_selector_all('input[type="file"]')
        print(f"  File inputs found: {len(fis)}")
        for fi2 in fis:
            try:
                fi2.set_input_files(zip_path)
                print(f"  Uploaded (alt): {zip_name}")
                time.sleep(3)
                page.locator('button:has-text("Save")').first.click()
                time.sleep(5)
                cur = page.url
                m = re.search(r'/products/([a-zA-Z0-9_-]+)', cur)
                slug = m.group(1) if m else None
                if slug and slug != "new":
                    gurl = f"https://gumroad.com/l/{slug}"
                    urls[name] = gurl
                    json.dump(urls, open(URLS_FILE, "w"), indent=2)
                    print(f"  DONE: {gurl}")
                break
            except:
                pass
    
    time.sleep(10)

browser.close()
print(f"\n{len(urls)}/13 on Gumroad")
for n, u in sorted(urls.items()):
    print(f"  {n}: {u}")
