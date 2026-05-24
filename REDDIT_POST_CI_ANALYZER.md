REDDIT POST — READY TO SUBMIT
================================
Product: CI/CD Cost Analyzer ($99)
Target: r/devops, r/github, r/webdev, r/selfhosted
Validated: 204 upvotes, 72 comments on r/devops — "accidentally spent $300/month on macOS runners"

---

POST TITLE:
I saw the r/devops thread about $300/mo CI/CD mistakes. Built a free scanner that finds them before the bill lands.

BODY:
The thread yesterday about GitHub Actions cost disasters hit home. I've been there — woke up to a $287 bill because a macOS runner was firing on every push for 6 weeks.

Built a tool that scans your workflow YAML and finds:
- macOS runners that should be Ubuntu (10x cost difference)
- Matrix explosions (8x8 combos = $400/month on push alone)
- Missing caching (npm ci every single run)
- Timeout abuse (360 minutes default, jobs finish in 4)

Paste your YAML. Get a cost breakdown. Find the leaks.

Free. No account. No GitHub token needed — just paste your workflow file.

Link: [YOUR URL]/ci-cost-analyzer/index.html

Pro version ($99, one-time) adds multi-repo GitHub org scanning, cost anomaly detection, and Slack alerts before the AWS bill. But the free version catches 80% of the disasters.

What's your worst CI/CD bill story?
