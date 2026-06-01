#!/usr/bin/env python3
"""Gumroad automation — check session, prepare product list, launch login if needed."""
import subprocess, json, os, sys

PRODUCTS_DIR = "/home/billonare2/digital-products"
PACKAGED_DIR = os.path.join(PRODUCTS_DIR, "packaged")

products = [
    {"name": "SEO Blog Engine", "subtitle": "Generate 30 SEO blog posts from a spreadsheet in 2 clicks.", "price": "49", "zip": "seo-blog-engine-verified.zip", "description": "Stop paying $99/month for AI writing tools. SEO Blog Engine generates complete blog posts — with meta titles, FAQs, and internal links — from a simple keyword list. 6 content templates. Markdown export. Works offline. No API key needed.", "tags": "seo,content marketing,ai writing,blog generator,saas,content creation"},
    {"name": "SimpleInvoice", "subtitle": "The invoicing tool Reddit begged for. No subscription needed.", "price": "29", "zip": "simple-invoice-verified.zip", "description": "Create professional invoices in 30 seconds. Save client details. One-click PDF download. Tax calculation built in. No account. No subscription. Your data stays on your machine.", "tags": "invoicing,freelancer tools,invoice generator,small business,pdf invoice,contractor"},
    {"name": "PDF Invoice Extractor", "subtitle": "Extract data from any PDF invoice. CSV/JSON export.", "price": "79", "zip": "pdf-invoice-extractor-verified.zip", "description": "Extracts vendor name, invoice number, dates, amounts, and line items from any PDF invoice text. 3 built-in format recognizers. Batch processing for 100+ PDFs. Works offline. No cloud upload.", "tags": "pdf extraction,invoice ocr,data extraction,bookkeeping tools,automation,csv export"},
    {"name": "Email Deliverability Kit", "subtitle": "Audit your SPF/DKIM/DMARC and fix your cold email setup.", "price": "67", "zip": "email-deliverability-kit-verified.zip", "description": "DNS audit tool checks SPF/DKIM/DMARC. 0-100 deliverability score with specific fix recommendations. 30-day warmup schedule with exact daily email counts. Pre-launch checklist. Works in your browser.", "tags": "email deliverability,cold email,spf dkim dmarc,email audit,dns checker,sales tools"},
    {"name": "InvoiceChaser", "subtitle": "Automated payment follow-up. Stop losing thousands to unpaid invoices.", "price": "39", "zip": "invoice-chaser-verified.zip", "description": "4-step follow-up sequence: Gentle Reminder → Direct → Firm → Final Notice. Templates adapt based on how overdue the invoice is. Copy to clipboard, paste in Gmail. Visual dashboard with outstanding invoices.", "tags": "invoice follow-up,payment reminder,freelancer tools,accounts receivable,cash flow,invoicing"},
    {"name": "BankMatch Reconciliation", "subtitle": "Bookkeeping reconciliation. Upload CSV, auto-match, done in seconds.", "price": "79", "zip": "bankmatch-reconciliation-verified.zip", "description": "Upload bank CSV + invoice list CSV. Fuzzy name matching + amount matching auto-matches payments to invoices. Auto-categorizes transactions. Flags mismatches. Monthly net income instantly. Export to CSV.", "tags": "bank reconciliation,bookkeeping,accounting tools,transaction matching,small business,csv matching"},
    {"name": "WhatsApp Bot Kit", "subtitle": "Pre-built WhatsApp auto-reply flows for 4 business types.", "price": "79", "zip": "whatsapp-bot-kit.zip", "description": "4 business templates: Pizza Shop, Hair Salon, Handyman, Medical Clinic. Quick-reply button flows for ordering, booking, pricing, FAQs. Pro: Node.js code + WhatsApp Cloud API deployment guide.", "tags": "whatsapp bot,chatbot,small business tools,whatsapp business api,automation,customer service"},
    {"name": "SOC2 Ready", "subtitle": "19 automated compliance checks across all 7 trust criteria.", "price": "199", "zip": "soc2-ready.zip", "description": "Vanta and Drata don't catch everything. 19 evidence checks across CC1-CC7. Auditor-ready report with pass/fail/warning per check. Simulated provider connections. Pro: real API connections to your actual infrastructure.", "tags": "soc2 compliance,security audit,saas security,compliance tools,evidence collection,auditor prep"},
    {"name": "AI Visibility Audit", "subtitle": "See if ChatGPT and Claude recommend your brand. GEO score + 6 fixes.", "price": "149", "zip": "ai-visibility-audit.zip", "description": "Visibility check across ChatGPT, Claude, and Perplexity. 0-100 GEO Score with industry comparison. 6 specific, ranked fixes: Schema markup, backlinks, comparison content, NAP consistency, rich results, content depth.", "tags": "ai visibility,geo audit,chatgpt seo,ai search optimization,brand visibility,llm search"},
    {"name": "CrawlShield", "subtitle": "Block AI crawlers. Save bandwidth. One site got 11M hits in 30 days.", "price": "49", "zip": "crawl-shield.zip", "description": "AI crawler analysis shows which bots hit your site. Estimated bandwidth savings in dollars. Generates exact configs: robots.txt, nginx, Cloudflare WAF, .htaccess. One-click toggle per crawler.", "tags": "ai crawlers,bot blocking,web security,bandwidth saver,nginx config,cloudflare rules"},
    {"name": "AgencyAuditor", "subtitle": "Verify your marketing agency's ROI. Fire risk score + red flags.", "price": "149", "zip": "agency-auditor.zip", "description": "Fire Risk Score (0-100). Red flag detection: cookie-cutter reports, cherry-picked metrics. KPI comparison: promised vs actual leads. Industry benchmark comparison. Ranked action plan.", "tags": "agency audit,marketing roi,ppc audit,agency management,marketing spend,vendor audit"},
    {"name": "DockSecure CVE Scanner", "subtitle": "Docker vulnerability scanner. Before your server becomes a crypto miner.", "price": "29", "zip": "docksecure-cve-scanner.zip", "description": "Scan 8 containers against real CVE data. Prioritized critical/high CVEs by CVSS score. Fix version suggestions for each vulnerability. Container-by-container risk breakdown. Exportable security report.", "tags": "docker security,cve scanner,vulnerability scanner,self-hosted,container security,devops tools"},
    {"name": "DevPath Career Roadmap", "subtitle": "Personalized 90-day DevOps learning path. 8 questions → your roadmap.", "price": "29", "zip": "devpath-career.zip", "description": "5 target roles: DevOps Engineer, SRE, Cloud Engineer, Platform Engineer, DevSecOps. Role fit scoring. Skill gap analysis with visual bars. 12-week roadmap. Salary benchmarks ($130K-$160K+).", "tags": "devops career,learning path,career roadmap,devops engineer,sre,cloud career,tech career"},
]

# Verify zips
missing = [p["zip"] for p in products if not os.path.exists(os.path.join(PACKAGED_DIR, p["zip"]))]
if missing:
    print(f"MISSING ZIPS: {missing}")
    sys.exit(1)

print(f"✓ All {len(products)} zips verified")

# Save product data for automation script
with open(os.path.join(PRODUCTS_DIR, "gumroad_products.json"), "w") as f:
    json.dump(products, f, indent=2)
print("✓ Product data saved")

# Check Gumroad session
chrome_profile = "/home/billonare2/.config/chromium/Default"
if not os.path.exists(chrome_profile):
    print(f"✗ No Chrome profile at {chrome_profile}")
    print("  → Need to log into Gumroad manually first.")
    print("  → Open: https://app.gumroad.com/login")
    print("  → Log in, then re-run the automation.")
    sys.exit(1)

from playwright.sync_api import sync_playwright

try:
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            chrome_profile,
            headless=True,
            args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
        )
        page = context.new_page()
        page.goto("https://app.gumroad.com/dashboard", timeout=15000, wait_until="networkidle")
        page.wait_for_timeout(3000)
        url = page.url
        
        if "login" in url.lower() or "sign_in" in url.lower():
            print("✗ No active Gumroad session — need to login first")
            print("  → Launching browser for manual login...")
            context2 = p.chromium.launch_persistent_context(
                chrome_profile,
                headless=False,
                args=['--no-sandbox', '--disable-gpu']
            )
            login_page = context2.new_page()
            login_page.goto("https://app.gumroad.com/login")
            print("  → BROWSER OPEN: Log into Gumroad now. Close browser when done.")
            login_page.wait_for_timeout(300000)  # 5 min wait
            context2.close()
        else:
            print(f"✓ Active Gumroad session! URL: {url[:80]}")
            print(f"  Title: {page.title()[:80]}")
        
        context.close()
except Exception as e:
    print(f"Playwright error: {e}")
    print("  → Try: playwright install chromium")
