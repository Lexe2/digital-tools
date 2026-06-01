#!/usr/bin/env python3
"""
Phase 1: Visible login + 2FA → save session.
Phase 2: Headless product creation using saved session.
Phase 3: Update store.html + push to GitHub.
"""
import subprocess, json, os, sys, time, re
from playwright.sync_api import sync_playwright

PRODUCTS_DIR = "/home/billonare2/digital-products"
PACKAGED_DIR = os.path.join(PRODUCTS_DIR, "packaged")
STORE_HTML = os.path.join(PRODUCTS_DIR, "store.html")
URLS_FILE = os.path.join(PRODUCTS_DIR, "gumroad_urls.json")
AUTH_FILE = os.path.join(PRODUCTS_DIR, ".gumroad_auth.json")

products = [
    ("SEO Blog Engine", "49", "seo-blog-engine-verified.zip", "Stop paying $99/month for AI writing tools. Generate complete blog posts with meta titles, FAQs, and internal links from a keyword list.", "seo,content marketing,ai writing,blog generator", "seo-blog-engine/app.html"),
    ("SimpleInvoice", "29", "simple-invoice-verified.zip", "Create professional invoices in 30 seconds. Save client details. One-click PDF download. Tax calculation built in. No subscription.", "invoicing,freelancer tools,invoice generator,small business", "simple-invoice/index.html"),
    ("PDF Invoice Extractor", "79", "pdf-invoice-extractor-verified.zip", "Extracts vendor name, invoice number, dates, amounts from any PDF invoice. Batch processing. CSV/JSON export. Works offline.", "pdf extraction,invoice ocr,data extraction,bookkeeping", "pdf-invoice-extractor/index.html"),
    ("Email Deliverability Kit", "67", "email-deliverability-kit-verified.zip", "Audit SPF/DKIM/DMARC. 0-100 deliverability score with fix recommendations. 30-day warmup schedule. Pre-launch checklist.", "email deliverability,cold email,spf dkim dmarc,email audit", "email-deliverability-kit/index.html"),
    ("InvoiceChaser", "39", "invoice-chaser-verified.zip", "4-step follow-up sequence for unpaid invoices. Templates adapt by how overdue. Dashboard with outstanding invoices.", "invoice follow-up,payment reminder,freelancer tools", "invoice-chaser/index.html"),
    ("BankMatch Reconciliation", "79", "bankmatch-reconciliation-verified.zip", "Upload bank CSV + invoice list. Auto-matches payments, categorizes transactions, flags mismatches. Monthly net income in seconds.", "bank reconciliation,bookkeeping,accounting tools", "bankmatch-reconciliation/index.html"),
    ("WhatsApp Bot Kit", "79", "whatsapp-bot-kit.zip", "4 business templates: Pizza Shop, Hair Salon, Handyman, Medical Clinic. Quick-reply flows + Pro deployment code.", "whatsapp bot,chatbot,small business tools", "whatsapp-bot-kit/index.html"),
    ("SOC2 Ready", "199", "soc2-ready.zip", "19 evidence checks across all 7 trust criteria. Auditor-ready report. See what an auditor would flag before they do.", "soc2 compliance,security audit,saas security", "soc2-ready/index.html"),
    ("AI Visibility Audit", "149", "ai-visibility-audit.zip", "Check brand visibility across ChatGPT, Claude, and Perplexity. GEO Score + 6 ranked fixes.", "ai visibility,geo audit,chatgpt seo,brand visibility", "ai-visibility-audit/index.html"),
    ("CrawlShield", "49", "crawl-shield.zip", "Block AI crawlers. See bandwidth cost, generate robots.txt/nginx/Cloudflare/.htaccess configs.", "ai crawlers,bot blocking,web security", "crawl-shield/index.html"),
    ("AgencyAuditor", "149", "agency-auditor.zip", "Fire Risk Score. Red flag detection. KPI comparison. For businesses paying $10K-100K/month to agencies.", "agency audit,marketing roi,ppc audit", "agency-auditor/index.html"),
    ("DockSecure CVE Scanner", "29", "docksecure-cve-scanner.zip", "Scan Docker containers for CVEs. Prioritized criticals with fix versions. Before your server becomes a crypto miner.", "docker security,cve scanner,vulnerability scanner", "docksecure-cve-scanner/index.html"),
    ("DevPath Career Roadmap", "29", "devpath-career.zip", "Answer 8 questions → personalized 90-day DevOps roadmap. 5 target roles. Skill gap analysis.", "devops career,learning path,career roadmap", "devpath-career/index.html"),
]

# Verify zips
missing = [z for _, _, z, _, _, _ in products if not os.path.exists(os.path.join(PACKAGED_DIR, z))]
if missing:
    print(f"MISSING: {missing}")
    sys.exit(1)
print(f"✓ {len(products)} zips verified")

# ===================================================================
# PHASE 1: LOGIN WITH VISIBLE BROWSER (2FA handled interactively)
# ===================================================================
print("\n" + "="*60)
print("PHASE 1: LOGIN → HANDLE 2FA → SAVE SESSION")
print("="*60)

session_ok = False
if os.path.exists(AUTH_FILE):
    print("Existing auth file found. Testing...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
            ctx = browser.new_context(storage_state=AUTH_FILE)
            page = ctx.new_page()
            page.goto("https://app.gumroad.com/products", timeout=15000, wait_until="networkidle")
            time.sleep(2)
            if "login" not in page.url.lower():
                print(f"✓ Session valid — logged in as {page.url[:60]}")
                session_ok = True
            else:
                print("✗ Session expired — re-authenticating")
            ctx.close()
            browser.close()
    except Exception as e:
        print(f"✗ Auth check failed: {e}")

if not session_ok:
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            "/home/billonare2/.config/chromium/Default",
            headless=False,
            args=['--no-sandbox','--disable-gpu','--start-maximized']
        )
        page = ctx.new_page()
        
        # Login
        page.goto("https://app.gumroad.com/login", wait_until="networkidle")
        time.sleep(2)
        
        page.fill('input[type="email"], input[name="email"], input[placeholder*="Email" i]', "helpteks@gmail.com")
        page.fill('input[type="password"], input[name="password"], input[placeholder*="Password" i]', "Sathome4455$$")
        page.click('button:has-text("Login"), input[type="submit"]')
        time.sleep(3)
        
        # Handle 2FA
        url_now = page.url
        if "two-factor" in url_now.lower() or "2fa" in url_now.lower() or "authenticat" in url_now.lower():
            print("\n*** 2FA REQUIRED ***")
            print("Check email helpteks@gmail.com for the code.")
            print("A browser window is open — TYPE THE CODE DIRECTLY INTO THE BROWSER.")
            print("Then press ENTER. I'll wait 3 minutes for you.")
            print("***")
            time.sleep(180)
        
        # Wait for login to complete
        for _ in range(60):
            time.sleep(1)
            u = page.url
            if "login" not in u.lower() and "two-factor" not in u.lower() and "2fa" not in u.lower():
                break
        
        u = page.url
        if "login" in u.lower() or "two-factor" in u.lower():
            print("Login still incomplete. Waiting another 60s...")
            time.sleep(60)
        
        u = page.url
        if "login" in u.lower():
            print("ERROR: Still on login page. Aborting.")
            ctx.close()
            sys.exit(1)
        
        print(f"✓ Logged in! URL: {u[:80]}")
        
        # Save session
        ctx.storage_state(path=AUTH_FILE)
        print(f"✓ Session saved to {AUTH_FILE}")
        ctx.close()

# ===================================================================
# PHASE 2: CREATE PRODUCTS (headless, fast)
# ===================================================================
print("\n" + "="*60)
print("PHASE 2: CREATING PRODUCTS (headless)")
print("="*60)

# Reload existing URLs
urls = {}
if os.path.exists(URLS_FILE):
    urls = json.load(open(URLS_FILE))
remaining = [(n,p,z,d,t,demo) for n,p,z,d,t,demo in products if n not in urls]
print(f"Already done: {len(urls)}/{len(products)}, Remaining: {len(remaining)}")

if remaining:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage']
        )
        ctx = browser.new_context(storage_state=AUTH_FILE)
        page = ctx.new_page()
        
        for i, (name, price, zip_name, desc, tags, demo) in enumerate(remaining):
            print(f"\n[{i+1}/{len(remaining)}] {name} (${price})")
            
            # Go to new product form
            page.goto("https://app.gumroad.com/products/new", wait_until="networkidle")
            time.sleep(2)
            
            if "login" in page.url.lower():
                print("  ✗ Session expired mid-run!")
                break
            
            # Fill name
            try:
                page.fill('input:not([type="hidden"]):not([type="file"])', name)
                page.wait_for_timeout(300)
            except:
                # Try clicking first input
                inputs = page.query_selector_all('input')
                for inp in inputs:
                    if inp.is_visible() and inp.get_attribute('type') not in ['hidden','file','submit','checkbox','radio']:
                        inp.click()
                        inp.fill(name)
                        break
            
            # Fill description (contenteditable div)
            ce = page.query_selector('div[contenteditable="true"]')
            if ce:
                ce.click()
                ce.fill(desc)
            
            # Upload zip
            zip_path = os.path.join(PACKAGED_DIR, zip_name)
            page.set_input_files('input[type="file"]', zip_path)
            print(f"  ✓ Uploaded: {zip_name}")
            time.sleep(1)
            
            # Click save
            buttons = page.query_selector_all('button')
            clicked = False
            for btn in buttons:
                txt = (btn.inner_text() or "").strip()
                if txt in ["Save", "Publish", "Save and continue", "Save changes"]:
                    btn.click()
                    clicked = True
                    break
            if not clicked and buttons:
                buttons[-1].click()  # Last button is usually save
            
            time.sleep(3)
            
            # Extract URL
            cur = page.url
            # Look for product ID in URL: /products/UUID/edit or /edit/UUID
            m = re.search(r'/products/([a-zA-Z0-9_-]+)(?:/edit)?', cur)
            if m:
                slug = m.group(1)
            else:
                m = re.search(r'/edit/([a-zA-Z0-9_-]+)', cur)
                slug = m.group(1) if m else None
            
            if slug:
                gurl = f"https://app.gumroad.com/l/{slug}"
                urls[name] = gurl
                json.dump(urls, open(URLS_FILE, "w"), indent=2)
                print(f"  ✓ URL: {gurl}")
            else:
                # Try a different page to find the slug
                page.goto("https://app.gumroad.com/products", wait_until="networkidle")
                time.sleep(2)
                # Look for the product we just created
                links = page.query_selector_all('a')
                for l in links:
                    href = l.get_attribute('href') or ''
                    if '/l/' in href:
                        linked_name = l.inner_text().strip()
                        if linked_name == name or name.lower() in linked_name.lower():
                            gurl = href if href.startswith('http') else f"https://app.gumroad.com{href}"
                            urls[name] = gurl
                            json.dump(urls, open(URLS_FILE, "w"), indent=2)
                            print(f"  ✓ URL (from list): {gurl}")
                            slug = True  # flag
                            break
                if not slug:
                    print(f"  ⚠ Could not extract URL: {cur[:80]}")
            
            time.sleep(1)
        
        ctx.close()
        browser.close()
        print(f"\n✓ Total products with URLs: {len(urls)}")

# ===================================================================
# PHASE 3: UPDATE STORE + PUSH
# ===================================================================
print("\n" + "="*60)
print("PHASE 3: UPDATING STORE.HTML + PUSH")
print("="*60)

html = open(STORE_HTML).read()
updated = 0

for name, price, _, _, _, demo in products:
    if name not in urls:
        print(f"  ✗ {name}: no URL — skipping")
        continue
    
    gurl = urls[name]
    old = f'<a href="{demo}" class="btn btn-primary">Try Demo</a>'
    
    if old in html:
        new_btns = f'<a href="{gurl}" target="_blank" class="btn btn-primary" style="margin-right:8px">Buy ${price}</a><a href="{demo}" class="btn btn-outline">Try Demo</a>'
        html = html.replace(old, new_btns, 1)
        updated += 1
        print(f"  ✓ {name}")
    else:
        print(f"  ⚠ {name}: demo link not found ({demo})")

open(STORE_HTML, "w").write(html)
print(f"\n✓ {updated} Buy buttons added to store.html")

os.chdir(PRODUCTS_DIR)
subprocess.run(["git", "add", "store.html", "gumroad_urls.json"], check=False)
subprocess.run(["git", "commit", "-m", f"Gumroad buy buttons: {updated} products linked"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=False)

print("\n" + "="*60)
print("DONE. https://lexe2.github.io/digital-tools/store.html")
print(f"Gumroad products: {len(urls)}/{len(products)}")
for name, url in sorted(urls.items()):
    print(f"  {name}: {url}")
print("="*60)
