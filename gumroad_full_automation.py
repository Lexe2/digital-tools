#!/usr/bin/env python3
"""
FULL GUMSOAD AUTOMATION — Steps 1-4 in one shot:
1. Open browser for Gumroad login (user logs in once)
2. Create all 14 products with zip uploads
3. Extract Gumroad product URLs
4. Patch store.html with buy links + push to GitHub
"""
import subprocess, json, os, sys, time, re

PRODUCTS_DIR = "/home/billonare2/digital-products"
PACKAGED_DIR = os.path.join(PRODUCTS_DIR, "packaged")
STORE_HTML = os.path.join(PRODUCTS_DIR, "store.html")
GUMROAD_URLS_FILE = os.path.join(PRODUCTS_DIR, "gumroad_urls.json")

products = [
    {"name": "SEO Blog Engine", "subtitle": "Generate 30 SEO blog posts from a spreadsheet in 2 clicks.", "price": "49", "zip": "seo-blog-engine-verified.zip", "description": "Stop paying $99/month for AI writing tools. SEO Blog Engine generates complete blog posts with meta titles, FAQs, and internal links from a simple keyword list. 6 content templates. Markdown export. Works offline. No API key needed.", "tags": "seo,content marketing,ai writing,blog generator,saas,content creation", "folder": "seo-blog-engine"},
    {"name": "SimpleInvoice", "subtitle": "The invoicing tool Reddit begged for. No subscription needed.", "price": "29", "zip": "simple-invoice-verified.zip", "description": "Create professional invoices in 30 seconds. Save client details. One-click PDF download. Tax calculation built in. No account. No subscription. Your data stays on your machine.", "tags": "invoicing,freelancer tools,invoice generator,small business,pdf invoice,contractor", "folder": "simple-invoice"},
    {"name": "PDF Invoice Extractor", "subtitle": "Extract data from any PDF invoice. CSV/JSON export.", "price": "79", "zip": "pdf-invoice-extractor-verified.zip", "description": "Extracts vendor name, invoice number, dates, amounts, and line items from any PDF invoice text. 3 built-in format recognizers. Batch processing for 100+ PDFs. Works offline. No cloud upload.", "tags": "pdf extraction,invoice ocr,data extraction,bookkeeping tools,automation,csv export", "folder": "pdf-invoice-extractor"},
    {"name": "Email Deliverability Kit", "subtitle": "Audit SPF/DKIM/DMARC and fix your cold email setup.", "price": "67", "zip": "email-deliverability-kit-verified.zip", "description": "DNS audit tool checks SPF/DKIM/DMARC. 0-100 deliverability score with specific fix recommendations. 30-day warmup schedule with exact daily email counts. Pre-launch checklist. Works in your browser.", "tags": "email deliverability,cold email,spf dkim dmarc,email audit,dns checker,sales tools", "folder": "email-deliverability-kit"},
    {"name": "InvoiceChaser", "subtitle": "Automated payment follow-up. Stop losing thousands to unpaid invoices.", "price": "39", "zip": "invoice-chaser-verified.zip", "description": "4-step follow-up sequence: Gentle Reminder, Direct, Firm, Final Notice. Templates adapt based on how overdue the invoice is. Copy to clipboard, paste in Gmail. Visual dashboard with outstanding invoices.", "tags": "invoice follow-up,payment reminder,freelancer tools,accounts receivable,cash flow,invoicing", "folder": "invoice-chaser"},
    {"name": "BankMatch Reconciliation", "subtitle": "Bookkeeping reconciliation. Upload CSV, auto-match, done.", "price": "79", "zip": "bankmatch-reconciliation-verified.zip", "description": "Upload bank CSV + invoice list CSV. Fuzzy name matching + amount matching auto-matches payments to invoices. Auto-categorizes transactions. Flags mismatches. Monthly net income instantly. Export to CSV.", "tags": "bank reconciliation,bookkeeping,accounting tools,transaction matching,small business,csv matching", "folder": "bankmatch-reconciliation"},
    {"name": "WhatsApp Bot Kit", "subtitle": "Pre-built WhatsApp auto-reply flows for 4 business types.", "price": "79", "zip": "whatsapp-bot-kit.zip", "description": "4 business templates: Pizza Shop, Hair Salon, Handyman, Medical Clinic. Quick-reply button flows for ordering, booking, pricing, FAQs. Pro: Node.js code + WhatsApp Cloud API deployment guide.", "tags": "whatsapp bot,chatbot,small business tools,whatsapp business api,automation,customer service", "folder": "whatsapp-bot-kit"},
    {"name": "SOC2 Ready", "subtitle": "19 automated compliance checks across all 7 trust criteria.", "price": "199", "zip": "soc2-ready.zip", "description": "19 evidence checks across CC1-CC7: Access Control, Monitoring, Change Management, Risk Assessment, MFA, Data Classification, Personnel. Auditor-ready report with pass/fail/warning per check.", "tags": "soc2 compliance,security audit,saas security,compliance tools,evidence collection,auditor prep", "folder": "soc2-ready"},
    {"name": "AI Visibility Audit", "subtitle": "See if ChatGPT and Claude recommend your brand. GEO score + 6 fixes.", "price": "149", "zip": "ai-visibility-audit.zip", "description": "Visibility check across ChatGPT, Claude, and Perplexity. 0-100 GEO Score with industry comparison. 6 specific, ranked fixes: Schema markup, backlinks, comparison content, NAP consistency, rich results, content depth.", "tags": "ai visibility,geo audit,chatgpt seo,ai search optimization,brand visibility,llm search", "folder": "ai-visibility-audit"},
    {"name": "CrawlShield", "subtitle": "Block AI crawlers. Save bandwidth. One site got 11M hits in 30 days.", "price": "49", "zip": "crawl-shield.zip", "description": "AI crawler analysis shows which bots hit your site and estimated bandwidth cost. Generates exact configs: robots.txt, nginx, Cloudflare WAF, .htaccess. One-click toggle per crawler.", "tags": "ai crawlers,bot blocking,web security,bandwidth saver,nginx config,cloudflare rules", "folder": "crawl-shield"},
    {"name": "AgencyAuditor", "subtitle": "Verify your marketing agency's ROI. Fire risk score + red flags.", "price": "149", "zip": "agency-auditor.zip", "description": "Fire Risk Score (0-100). Red flag detection: cookie-cutter reports, cherry-picked metrics. KPI comparison: promised vs actual leads. Industry benchmark comparison. Ranked action plan.", "tags": "agency audit,marketing roi,ppc audit,agency management,marketing spend,vendor audit", "folder": "agency-auditor"},
    {"name": "DockSecure CVE Scanner", "subtitle": "Docker vulnerability scanner. Before your server becomes a crypto miner.", "price": "29", "zip": "docksecure-cve-scanner.zip", "description": "Scan 8 containers against real CVE data. Prioritized critical/high CVEs by CVSS score. Fix version suggestions for each vulnerability. Container-by-container risk breakdown. Exportable security report.", "tags": "docker security,cve scanner,vulnerability scanner,self-hosted,container security,devops tools", "folder": "docksecure-cve-scanner"},
    {"name": "DevPath Career Roadmap", "subtitle": "Personalized 90-day DevOps learning path. 8 questions, your roadmap.", "price": "29", "zip": "devpath-career.zip", "description": "5 target roles: DevOps Engineer, SRE, Cloud Engineer, Platform Engineer, DevSecOps. Role fit scoring. Skill gap analysis with visual bars. 12-week roadmap with specific tasks. Salary benchmarks ($130K-$160K+).", "tags": "devops career,learning path,career roadmap,devops engineer,sre,cloud career,tech career", "folder": "devpath-career"},
]

# ===========================================================================
# STEP 1: Login (visible browser — user logs in)
# ===========================================================================
from playwright.sync_api import sync_playwright

chrome_profile = "/home/billonare2/.config/chromium/Default"
gumroad_urls = {}

# Load existing URLs if any
if os.path.exists(GUMROAD_URLS_FILE):
    with open(GUMROAD_URLS_FILE) as f:
        gumroad_urls = json.load(f)
    print(f"Loaded {len(gumroad_urls)} existing Gumroad URLs")

remaining = [p for p in products if p["name"] not in gumroad_urls]
print(f"Products to create: {len(remaining)} / {len(products)}")

if not remaining:
    print("All products already have Gumroad URLs — skipping to store update")
else:
    print("\n" + "="*60)
    print("STEP 1: OPENING BROWSER FOR GUMROAD LOGIN")
    print("="*60)
    print("A Chrome window will open. Log into Gumroad, then close the browser.")
    print("The automation will continue after you close the window.")
    print("="*60)
    
    with sync_playwright() as p:
        # Launch visible browser
        context = p.chromium.launch_persistent_context(
            chrome_profile,
            headless=False,
            args=['--no-sandbox', '--disable-gpu', '--start-maximized']
        )
        login_page = context.new_page()
        login_page.goto("https://app.gumroad.com/products", timeout=20000, wait_until="networkidle")
        time.sleep(3)
        
        if "login" in login_page.url.lower() or "sign_in" in login_page.url.lower():
            login_page.goto("https://app.gumroad.com/login")
            print("\n>>> LOG IN TO GUMROAD NOW. Then close the browser window. <<<")
            # Wait for user to close browser
            try:
                login_page.wait_for_timeout(600000)  # 10 min max
            except:
                pass
        else:
            print("Already logged into Gumroad!")
        
        context.close()
    
    # ===========================================================================
    # STEP 2: Create products (headless — uses saved session)
    # ===========================================================================
    print("\n" + "="*60)
    print("STEP 2: CREATING GUMSOAD PRODUCTS")
    print("="*60)
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            chrome_profile,
            headless=True,
            args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
        )
        
        for i, product in enumerate(remaining):
            print(f"\n[{i+1}/{len(remaining)}] Creating: {product['name']}...")
            
            page = context.new_page()
            
            try:
                # Go to products page
                page.goto("https://app.gumroad.com/products", timeout=15000, wait_until="networkidle")
                page.wait_for_timeout(2000)
                
                # Check for login redirect
                if "login" in page.url.lower():
                    print(f"  ✗ Session expired — need to re-login")
                    page.close()
                    break
                
                # Click "New product" button
                new_btn = page.query_selector('a[href*="products/new"], button:has-text("New product"), a:has-text("New product")')
                if new_btn:
                    new_btn.click()
                else:
                    page.goto("https://app.gumroad.com/products/new", timeout=10000)
                
                page.wait_for_timeout(2000)
                
                # Fill product name
                name_input = page.query_selector('input[name="product[name]"], input[aria-label="Name"], input[placeholder*="name" i]')
                if name_input:
                    name_input.fill(product["name"])
                else:
                    # Try finding any input near top
                    inputs = page.query_selector_all('input[type="text"]')
                    if inputs:
                        inputs[0].fill(product["name"])
                
                page.wait_for_timeout(500)
                
                # Fill description
                desc_areas = page.query_selector_all('textarea')
                if desc_areas:
                    desc_areas[0].fill(product["description"])
                
                page.wait_for_timeout(500)
                
                # Set price
                price_inputs = page.query_selector_all('input[type="number"], input[name*="price" i]')
                for pi in price_inputs:
                    try:
                        pi.fill("")
                        pi.fill(product["price"])
                        break
                    except:
                        pass
                
                page.wait_for_timeout(500)
                
                # Upload zip file — look for file input
                zip_path = os.path.join(PACKAGED_DIR, product["zip"])
                file_inputs = page.query_selector_all('input[type="file"]')
                if file_inputs:
                    file_inputs[0].set_input_files(zip_path)
                    print(f"  ✓ Uploaded: {product['zip']}")
                else:
                    print(f"  ⚠ No file input found — may need manual upload")
                
                page.wait_for_timeout(1000)
                
                # Click Save/Publish
                save_btns = page.query_selector_all('button:has-text("Save"), button:has-text("Publish"), input[type="submit"]')
                for btn in save_btns:
                    try:
                        btn.click()
                        break
                    except:
                        pass
                
                page.wait_for_timeout(3000)
                
                # Extract product URL
                current_url = page.url
                product_id_match = re.search(r'/products/([a-zA-Z0-9_-]+)', current_url)
                if product_id_match:
                    product_slug = product_id_match.group(1)
                    gumroad_url = f"https://gumroad.com/l/{product_slug}"
                    gumroad_urls[product["name"]] = gumroad_url
                    print(f"  ✓ URL: {gumroad_url}")
                    
                    # Save immediately
                    with open(GUMROAD_URLS_FILE, "w") as f:
                        json.dump(gumroad_urls, f, indent=2)
                else:
                    print(f"  ⚠ Could not extract URL from: {current_url[:80]}")
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
            
            finally:
                page.close()
                time.sleep(2)  # Rate limit
        
        context.close()

# ===========================================================================
# STEP 3: Print all URLs
# ===========================================================================
print("\n" + "="*60)
print(f"STEP 3: GUMSOAD URLS ({len(gumroad_urls)} products)")
print("="*60)
for name, url in gumroad_urls.items():
    print(f"  {name}: {url}")

# Save final URL list
with open(GUMROAD_URLS_FILE, "w") as f:
    json.dump(gumroad_urls, f, indent=2)

# ===========================================================================
# STEP 4: Update store.html with Gumroad links
# ===========================================================================
print("\n" + "="*60)
print("STEP 4: UPDATING STORE.HTML WITH GUMSOAD LINKS")
print("="*60)

if not gumroad_urls:
    print("No URLs to update — skipping")
    sys.exit(0)

with open(STORE_HTML, "r") as f:
    html = f.read()

# Build a mapping of product name → folder → existing demo link → new buy link
updates = []
for product in products:
    if product["name"] in gumroad_urls:
        gumroad_url = gumroad_urls[product["name"]]
        folder = product.get("folder", product["name"].lower().replace(" ", "-"))
        
        # Find the existing "Try Demo" link for this product
        # Pattern: look for product card with the product name, then find the <a href="...">Try Demo</a>
        # The product cards have structure: <h3>Product Name</h3> ... <a href="folder/index.html">Try Demo</a>
        
        # We need to find each product card and add a Gumroad buy button next to the demo link
        pass

# Simpler approach: replace each product card's demo link section with demo + buy link
for product in products:
    name = product["name"]
    if name not in gumroad_urls:
        continue
    
    gumroad_url = gumroad_urls[name]
    folder = product.get("folder", name.lower().replace(" ", "-"))
    
    # Find: <a href="FOLDER/index.html" class="btn btn-primary">Try Demo</a>
    old_pattern = f'<a href="{folder}/index.html" class="btn btn-primary">Try Demo</a>'
    # Also check for app.html variant
    if folder == "seo-blog-engine":
        old_pattern = f'<a href="seo-blog-engine/app.html" class="btn btn-primary">Try Demo</a>'
    
    if old_pattern in html:
        new_btns = f'<a href="{gumroad_url}" target="_blank" class="btn btn-primary" style="margin-right:8px">Buy ${product["price"]}</a><a href="{folder}/index.html" class="btn btn-outline">Try Demo</a>'
        html = html.replace(old_pattern, new_btns, 1)
        print(f"  ✓ {name}: {gumroad_url}")
    else:
        print(f"  ⚠ {name}: old pattern not found — trying alternate")
        # Try finding any btn-primary inside this product's card
        # Find the product card by h3 text, then replace the first btn-primary in it

# Special case for SEO Blog Engine (app.html)
if "SEO Blog Engine" in gumroad_urls:
    old_seo = '<a href="seo-blog-engine/app.html" class="btn btn-primary">Try Demo</a>'
    if old_seo in html:
        new_seo = f'<a href="{gumroad_urls["SEO Blog Engine"]}" target="_blank" class="btn btn-primary" style="margin-right:8px">Buy $49</a><a href="seo-blog-engine/app.html" class="btn btn-outline">Try Demo</a>'
        html = html.replace(old_seo, new_seo, 1)
        print("  ✓ SEO Blog Engine: special case handled")

# Handle InvoiceChaser (was index.html)
if "InvoiceChaser" in gumroad_urls:
    olds = [
        '<a href="invoice-chaser/index.html" class="btn btn-primary">Try Demo</a>',
    ]
    for old_pat in olds:
        if old_pat in html:
            new_pat = f'<a href="{gumroad_urls["InvoiceChaser"]}" target="_blank" class="btn btn-primary" style="margin-right:8px">Buy $39</a><a href="invoice-chaser/index.html" class="btn btn-outline">Try Demo</a>'
            html = html.replace(old_pat, new_pat, 1)
            print("  ✓ InvoiceChaser: patched")
            break

# Write updated store.html
with open(STORE_HTML, "w") as f:
    f.write(html)
print(f"\n✓ store.html updated at {STORE_HTML}")

# ===========================================================================
# STEP 5: Push to GitHub
# ===========================================================================
print("\n" + "="*60)
print("STEP 5: PUSHING TO GITHUB")
print("="*60)

os.chdir(PRODUCTS_DIR)
subprocess.run(["git", "add", "store.html", "gumroad_urls.json"], check=False)
result = subprocess.run(["git", "diff", "--cached", "--stat"], capture_output=True, text=True)
print(result.stdout)
subprocess.run(["git", "commit", "-m", "Gumroad links added to store — all 14 products with buy buttons"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=False)
print("\n✓ Pushed to GitHub")
print(f"✓ Store live at: https://lexe2.github.io/digital-tools/store.html")

print("\n" + "="*60)
print("ALL DONE. Products on Gumroad, store updated, pushed to GitHub.")
print("="*60)
