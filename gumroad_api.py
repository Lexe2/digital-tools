#!/usr/bin/env python3
"""Create final 5 Gumroad products via backend API using extracted session cookies."""
import json, os, re, subprocess

DIR = "/home/billonare2/digital-products"
PACKAGED = os.path.join(DIR, "packaged")
URLS_FILE = os.path.join(DIR, "gumroad_urls.json")
AUTH_FILE = os.path.join(DIR, ".gumroad_auth.json")

# Extract cookies
auth = json.load(open(AUTH_FILE))
cookies = auth["cookies"]
cookie_header = "; ".join(f"{c['name']}={c['value']}" for c in cookies)

# Get XSRF token
xsrf = next((c["value"] for c in cookies if c["name"] == "XSRF-TOKEN"), "")

remaining = [
    ("AI Visibility Audit", "149", "ai-visibility-audit.zip", "Check brand visibility across ChatGPT, Claude, Perplexity. 0-100 GEO Score with industry comparison. 6 specific ranked fixes."),
    ("CrawlShield", "49", "crawl-shield.zip", "Block AI crawlers. See which bots hit your site and estimated bandwidth cost. Generate robots.txt, nginx, Cloudflare WAF, .htaccess."),
    ("AgencyAuditor", "149", "agency-auditor.zip", "Fire Risk Score (0-100). Red flag detection: cookie-cutter reports, cherry-picked metrics. KPI comparison. Industry benchmark comparison. Ranked action plan."),
    ("DockSecure CVE Scanner", "29", "docksecure-cve-scanner.zip", "Scan 8 Docker containers against real CVE data. Prioritized critical/high CVEs by CVSS score. Fix version suggestions. Exportable report."),
    ("DevPath Career Roadmap", "29", "devpath-career.zip", "5 target roles: DevOps Engineer, SRE, Cloud Engineer, Platform Engineer, DevSecOps. 12-week roadmap. Salary benchmarks $130K-$160K+."),
]

urls = json.load(open(URLS_FILE))

for name, price, zip_name, desc in remaining:
    print(f"\n{name} (${price})")
    
    # Build product data as form-encoded
    from urllib.parse import urlencode, quote
    from urllib.request import Request, urlopen
    
    # Gumroad API for creating products: POST to /products with multipart
    zip_path = os.path.join(PACKAGED, zip_name)
    
    import http.client
    import http.cookiejar
    from io import BytesIO
    
    # Use urllib for multipart upload
    boundary = '----FormBoundary' + os.urandom(8).hex()
    
    # Read zip file
    with open(zip_path, 'rb') as f:
        zip_data = f.read()
    
    body = BytesIO()
    # Name
    body.write(f'--{boundary}\r\n'.encode())
    body.write(f'Content-Disposition: form-data; name="product[name]"\r\n\r\n'.encode())
    body.write(f'{name}\r\n'.encode())
    # Price
    body.write(f'--{boundary}\r\n'.encode())
    body.write(f'Content-Disposition: form-data; name="product[price_cents]"\r\n\r\n'.encode())
    body.write(f'{int(price)*100}\r\n'.encode())
    # Description (as rich text)
    body.write(f'--{boundary}\r\n'.encode())
    body.write(f'Content-Disposition: form-data; name="product[description]"\r\n\r\n'.encode())
    body.write(f'{desc}\r\n'.encode())
    # File
    body.write(f'--{boundary}\r\n'.encode())
    body.write(f'Content-Disposition: form-data; name="product[file]"; filename="{zip_name}"\r\n'.encode())
    body.write(f'Content-Type: application/zip\r\n\r\n'.encode())
    body.write(zip_data)
    body.write(f'\r\n--{boundary}--\r\n'.encode())
    
    data = body.getvalue()
    
    req = Request(
        'https://app.gumroad.com/products',
        data=data,
        headers={
            'Cookie': cookie_header,
            'X-XSRF-TOKEN': xsrf,
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Accept': 'application/json, text/html',
            'Origin': 'https://app.gumroad.com',
            'Referer': 'https://app.gumroad.com/products/new',
        },
        method='POST'
    )
    
    try:
        resp = urlopen(req, timeout=30)
        body = resp.read().decode()
        print(f'  Status: {resp.status}')
        print(f'  Response: {body[:300]}')
        
        # Try to extract slug from redirect or JSON
        if resp.status in [200, 201, 302]:
            final_url = resp.geturl()
            m = re.search(r'/products/([a-zA-Z0-9_-]+)', final_url)
            slug = m.group(1) if m else None
            if not slug:
                # Try JSON response
                try:
                    data = json.loads(body)
                    slug = data.get('id') or data.get('unique_permalink') or data.get('slug')
                except:
                    pass
            
            if slug:
                gurl = f"https://gumroad.com/l/{slug}"
                urls[name] = gurl
                json.dump(urls, open(URLS_FILE, 'w'), indent=2)
                print(f'  ✓ {gurl}')
            else:
                print(f'  ⚠ No slug in response')
        else:
            print(f'  ✗ API error: {resp.status}')
    except Exception as e:
        print(f'  ✗ Request error: {e}')

print(f'\nTotal: {len(urls)}/13 on Gumroad')
for n, u in sorted(urls.items()):
    print(f'  {n}: {u}')
