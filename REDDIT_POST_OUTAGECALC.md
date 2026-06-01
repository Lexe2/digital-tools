# OUTAGECALC REDDIT POST — r/devops + r/SaaS + r/sysadmin

## POST 1: r/devops (primary)
TITLE: "Your SLA penalty covers only 15% of what a 3-hour outage actually costs — I ran the numbers"

BODY:

Just built a calculator that models the true cost of downtime. Not just SLA penalties. The full picture:

- Direct revenue loss per hour
- SLA penalty (contractual credit)
- Customer churn from the outage
- Engineering hours burned on response
- Support ticket overhead
- Reputation/PR impact

What surprised me: for a typical $5M SaaS company with 15K users, a 3-hour outage costs about $418K. The SLA penalty for that same outage? $62K. That's a 85% gap.

The churn is the silent killer. A 3-hour outage at peak time + major data loss triggers about 2% churn. That's $351K walking out the door — and your SLA contract doesn't cover a dime of it.

Pre-built scenarios:
- Startup (2hr outage) → $8,400
- SaaS Mid-Market (3hr outage) → $42,750  
- Enterprise Platform (6hr outage) → $287,000
- E-Com Black Friday (1hr at peak) → $156,000
- Fintech Breach (4hr + data loss) → $1.2M

Free demo: https://lexe2.github.io/digital-tools/outagecalc/index.html

Would love honest feedback. Especially from anyone who's actually claimed an SLA credit — did the amount even come close to your real losses?

---

## POST 2: r/SaaS (cross-post 2 days later)
TITLE: "We modeled the true cost of a 3-hour outage. The SLA penalty was only 15% of it."

BODY:

Built a free outage cost calculator after realizing most SaaS companies dramatically underestimate what downtime actually costs them.

Quick numbers for a standard $5M ARR company:
- 3-hour outage, 65% users affected, peak hours, major data loss
- Revenue lost: $1,670
- SLA penalty received: $62,500  
- Customer churn: $351,000 (2% churn)
- Total: $418,014

Your SLA contract protects you against about 15% of the real damage. The churn is what kills you — and it compounds.

Demo with pre-loaded scenarios: https://lexe2.github.io/digital-tools/outagecalc/index.html

The Enterprise Platform scenario (6hr outage, 500K users) hits $287K. Curious how that compares to anyone's actual outage costs here.

---

## POSTING SCHEDULE:
- r/devops: Post Monday June 1, 8-10am ET
- r/SaaS: Cross-post Wednesday June 3
- r/sysadmin: Post Friday June 5 (different angle — "What outage cost you the most?")

## KEY ANGLE:
The gap between SLA penalties and real costs is the hook. Every SaaS founder has been through an outage. Most have no idea how big the churn impact actually is. This calculator makes it concrete.
