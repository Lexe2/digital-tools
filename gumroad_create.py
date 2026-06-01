#!/usr/bin/env python3
"""Create all Gumroad products — robust error handling, retry logic."""
from playwright.sync_api import sync_playwright
import json, os, time, re, subprocess, traceback

DIR = "/home/billonare2/digital-products"
PACKAGED = os.path.join(DIR, "packaged")
STORE = os.path.join(DIR, "store.html")
URLS_FILE = os.path.join(DIR, "gumroad_urls.json")
AUTH = os.path.join(DIR, ".gumroad_auth.json")

products = [
    ("SEO Blog Engine", "49", "seo-blog-engine-verified.zip", "Generate 30 SEO blog posts from a spreadsheet in 2 clicks. 6 content templates. Meta titles, FAQs, internal links. Markdown export. No API key. Works offline.", "seo,content marketing,ai writing,blog generator", "seo-blog-engine/app.html"),
    ("SimpleInvoice", "29", "simple-invoice-verified.zip", "Create professional invoices in 30 seconds. Save client details. One-click PDF download. Tax calculation. No subscription.", "invoicing,freelancer tools,invoice generator,small business", "simple-invoice/index.html"),
    ("PDF Invoice Extractor", "79", "pdf-invoice-extractor-verified.zip", "Extract vendor name, invoice number, dates, amounts from any PDF. 3 format recognizers. Batch processing. CSV/JSON. Works offline.", "pdf extraction,invoice ocr,data extraction,bookkeeping", "pdf-invoice-extractor/index.html"),
    ("Email Deliverability Kit", "67", "email-deliverability-kit-verified.zip", "Audit SPF/DKIM/DMARC. 0-100 score with fix recommendations. 30-day warmup. Pre-launch checklist.", "email deliverability,cold email,spf dkim dmarc,email audit", "email-deliverability-kit/index.html"),
    ("InvoiceChaser", "39", "invoice-chaser-verified.zip", "4-step follow-up sequence for unpaid invoices. Templates adapt by days overdue. Dashboard shows outstanding amounts.", "invoice follow-up,payment reminder,freelancer tools", "invoice-chaser/index.html"),
    ("BankMatch Reconciliation", "79", "bankmatch-reconciliation-verified.zip", "Upload bank CSV + invoice list. Fuzzy matching auto-matches payments. Categorizes transactions. Flags mismatches. Instant reconciliation.", "bank reconciliation,bookkeeping,accounting tools", "bankmatch-reconciliation/index.html"),
    ("WhatsApp Bot Kit", "79", "whatsapp-bot-kit.zip", "4 business templates: Pizza Shop, Hair Salon, Handyman, Medical Clinic. Quick-reply flows. Pro deployment code included.", "whatsapp bot,chatbot,small business tools", "whatsapp-bot-kit/index.html"),
    ("SOC2 Ready", "199", "soc2-ready.zip", "19 automated compliance checks across CC1-CC7. Auditor-ready report. See gaps before the real audit.", "soc2 compliance,security audit,saas security", "soc2-ready/index.html"),
    ("AI Visibility Audit", "149", "ai-visibility-audit.zip", "Check brand visibility across ChatGPT, Claude, Perplexity. 0-100 GEO Score. 6 ranked fixes.", "ai visibility,geo audit,chatgpt seo,brand visibility", "ai-visibility-audit/index.html"),
    ("CrawlShield", "49", "crawl-shield.zip", "Block AI crawlers. See bandwidth cost. Generate robots.txt, nginx, Cloudflare, .htaccess configs. One-click toggle.", "ai crawlers,bot blocking,web security", "crawl-shield/index.html"),
    ("AgencyAuditor", "149", "agency-auditor.zip", "Fire Risk Score. Red flag detection. KPI comparison. For businesses paying $10K-100K/month to agencies.", "agency audit,marketing roi,ppc audit", "agency-auditor/index.html"),
    ("DockSecure CVE Scanner", "29", "docksecure-cve-scanner.zip", "Scan Docker for CVEs. Prioritized criticals by CVSS score. Fix versions. Before your server becomes a miner.", "docker security,cve scanner,vulnerability scanner", "docksecure-cve-scanner/index.html"),
    ("DevPath Career Roadmap", "29", "devpath-career.zip", "Answer 8 questions. Personalized 90-day DevOps roadmap. 5 roles. Gap analysis. Salary benchmarks $130K-$160K+.", "devops career,learning path,career roadmap", "devpath-career/index.html"),
]

# Load existing URLs
urls = json.load(open(URLS_FILE)) if os.path.exists(URLS_FILE) else {}
remaining = [(n,p,z,d,t,demo) for n,p,z,d,t,demo in products if n not in urls]
print(f"Done: {len(urls)}/{len(products)}, Remaining: {len(remaining)}")

if not remaining:
    print("All products already created on Gumroad!")
else:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox','--disable-gpu','--disable-dev-shm-usage'])
        ctx = browser.new_context(storage_state=AUTH)
        page = ctx.new_page()
        
        for i, (name, price, zip_name, desc, tags, demo) in enumerate(remaining):
            print(f"\n[{i+1}/{len(remaining)}] {name} (${price})")
            
            try:
                # Go to new product page fresh each time
                page.goto("https://app.gumroad.com/products/new", wait_until="networkidle")
                time.sleep(4)
                
                # Fill name using native setter (React-controlled)
                js_set_value = f'''
                (() => {{
                    const inp = document.querySelector('input[id*="name"][id*="r1"]') || document.querySelector('input[aria-label="Name"]');
                    if (inp) {{
                        Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set.call(inp, {json.dumps(name)});
                        inp.dispatchEvent(new Event("input", {{bubbles: true}}));
                        inp.dispatchEvent(new Event("change", {{bubbles: true}}));
                    }}
                }})()
                '''
                page.evaluate(js_set_value)
                time.sleep(0.5)
                
                # Fill price
                page.evaluate(f'''
                (() => {{
                    const inp = document.querySelector('input[id*="price"][id*="r1"]') || document.querySelector('input[aria-label="Price"]');
                    if (inp) {{
                        Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set.call(inp, "{price}");
                        inp.dispatchEvent(new Event("input", {{bubbles: true}}));
                        inp.dispatchEvent(new Event("change", {{bubbles: true}}));
                    }}
                }})()
                ''')
                time.sleep(0.5)
                
                # Click "Digital product" (default) then "Next: Customize"
                page.evaluate('''
                (() => {
                    const btns = document.querySelectorAll('button');
                    for (const b of btns) {
                        const t = b.textContent;
                        if (t.includes('Next') || t.includes('Customize')) {
                            b.click();
                            return;
                        }
                    }
                    // Fallback: click submit
                    const submit = document.querySelector('button[type="submit"], input[type="submit"]');
                    if (submit) submit.click();
                })()
                ''')
                time.sleep(5)
                
                # Step 2: Fill description
                page.evaluate(f'''
                (() => {{
                    const divs = document.querySelectorAll('div[contenteditable="true"]');
                    for (const d of divs) {{
                        if (d.offsetParent !== null) {{
                            d.focus();
                            d.innerHTML = {json.dumps(desc)};
                            d.dispatchEvent(new Event("input", {{bubbles: true}}));
                            break;
                        }}
                    }}
                }})()
                ''')
                time.sleep(0.5)
                
                # Upload file — try all file inputs
                zip_path = os.path.join(PACKAGED, zip_name)
                file_inputs = page.query_selector_all('input[type="file"]')
                uploaded = False
                for fi in file_inputs:
                    try:
                        if not fi.is_visible():
                            # Make it visible via JS
                            page.evaluate('(el) => { el.style.display = "block"; el.style.visibility = "visible"; el.style.opacity = "1"; }', fi)
                        fi.set_input_files(zip_path)
                        uploaded = True
                        print(f"  ✓ Uploaded: {zip_name}")
                        break
                    except:
                        continue
                
                if not uploaded:
                    print(f"  ⚠ No file input accessible — uploading via JS")
                    # Try JS-based file upload
                    page.evaluate('''
                    (() => {
                        const fi = document.querySelector('input[type="file"]');
                        if (fi) {
                            fi.style.display = 'block';
                            fi.style.visibility = 'visible';
                        }
                    })()
                    ''')
                    time.sleep(1)
                    file_inputs = page.query_selector_all('input[type="file"]')
                    for fi in file_inputs:
                        try:
                            fi.set_input_files(zip_path)
                            uploaded = True
                            print(f"  ✓ Uploaded (retry): {zip_name}")
                            break
                        except:
                            pass
                
                time.sleep(2)
                
                # Click Save
                page.evaluate('''
                (() => {
                    const btns = document.querySelectorAll('button');
                    for (const b of btns) {
                        const t = b.textContent.trim();
                        if (t === 'Save' || t === 'Save and continue') {
                            b.click();
                            return;
                        }
                    }
                })()
                ''')
                time.sleep(5)
                
                # Extract slug
                cur = page.url
                m = re.search(r'/products/([a-zA-Z0-9_-]+)(?:/edit|/content|/|$)', cur)
                slug = m.group(1) if m else None
                
                if not slug or slug == 'new':
                    slug = page.evaluate('''
                    (() => {
                        const inp = document.querySelector('[id*=":r4:"]') || document.querySelector('input[placeholder*="slug" i]');
                        return inp ? inp.value : null;
                    })()
                    ''')
                
                if slug and slug != 'new':
                    gurl = f"https://gumroad.com/l/{slug}"
                    urls[name] = gurl
                    json.dump(urls, open(URLS_FILE, "w"), indent=2)
                    print(f"  ✓ Published: {gurl}")
                else:
                    print(f"  ⚠ Could not extract slug. URL: {cur[:80]}")
                
            except Exception as e:
                print(f"  ✗ ERROR: {e}")
                traceback.print_exc()
            
            time.sleep(1)
        
        ctx.close()
        browser.close()

# ============ UPDATE STORE + PUSH ============
print("\n===== UPDATING STORE =====")
html = open(STORE).read()
updated = 0

for name, price, _, _, _, demo in products:
    if name not in urls:
        continue
    gurl = urls[name]
    old = f'<a href="{demo}" class="btn btn-primary">Try Demo</a>'
    if old in html:
        new = f'<a href="{gurl}" target="_blank" class="btn btn-primary" style="margin-right:8px">Buy ${price}</a><a href="{demo}" class="btn btn-outline">Try Demo</a>'
        html = html.replace(old, new, 1)
        updated += 1
        print(f"  ✓ {name}")
    else:
        print(f"  ⚠ {name}: not found ({demo})")

open(STORE, "w").write(html)
print(f"{updated} buy buttons added")

os.chdir(DIR)
subprocess.run(["git", "add", "store.html", "gumroad_urls.json"], check=False)
subprocess.run(["git", "commit", "-m", f"Gumroad: {updated} products linked to buy buttons"], check=False)
subprocess.run(["git", "push", "origin", "main"], check=False)
print(f"\nDONE. https://lexe2.github.io/digital-tools/store.html")
for n, u in sorted(urls.items()):
    print(f"  {n}: {u}")
