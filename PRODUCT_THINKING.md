# Product Thinking Note — CurateAI

---

## (a) Which KPI do you move first and how?

Two KPIs, sequenced.

**Phase 1 — Shopper activation:** the number of unique shoppers who complete a discovery → cart cycle (at least one item added to cart via a CurateAI session) per week.

This is the "aha moment" metric. It proves the feature is being used and that the AI discovery experience is good enough to move someone from browsing to intent. It's squarely in GoKwik's control — they own the agent quality, the catalog matching, the UX — and it doesn't penalise GoKwik for a merchant's weak catalog or bad products. You can't optimise anything downstream until shoppers are actually adding things to cart.

**Phase 2 — Chat-to-checkout conversion rate:** of sessions where a shopper adds to cart via CurateAI, what % initiate a GoKwik checkout?

This is the metric that matters commercially — for GoKwik and for merchants. GoKwik's core value prop to merchants has always been "we improve your checkout conversion, here's the data." CurateAI lets them extend that same proof upstream into discovery. Once GoKwik can show a merchant "products surfaced in our agent convert at X%," they can charge for priority placement in the agent — sponsored ranking, category exclusivity, whatever the model ends up being. That's a new revenue line on top of the checkout processing fee, and it's credible because GoKwik owns both ends of the funnel — the agent AND the checkout — so the attribution is clean. No third party claiming credit.

Move activation first to prove demand exists. Move conversion rate to prove the surface earns its place in the merchant's marketing stack.

---

## (b) What is the biggest technical or trust risk?

Two risks that are specific to this surface — not generic e-commerce problems.

**1. Cross-merchant identity stitching without explicit consent in a social context.**

When a shopper DMs a brand on Instagram and shares their phone, they don't expect GoKwik to silently stitch their purchase history across Caprese, Zouk, and Giva. On a merchant's own app, data collection is expected — it's in the T&Cs they clicked through. In a DM thread with a brand they follow, it's not. The agent's value comes precisely from this cross-merchant intelligence — but if this surfaces publicly (a journalist, a viral tweet, a DPDP complaint), the damage hits GoKwik's network trust and the brand's social presence simultaneously. The intimacy of the social context makes the breach feel worse, not better.

Mitigation: explicit micro-consent at the phone verification moment ("sharing your number lets us check your rewards across brands in our network"), not buried. The current prototype asks for the phone to "check rewards" — that framing needs to be honest about what it actually does at scale.

**2. Platform dependency.**

The entire product lives inside Meta's DM API or WhatsApp Business API. One policy change, API deprecation, or pricing shift by Meta shuts the channel down. GoKwik's checkout SDK is embedded in thousands of merchant checkout pages and is not at any platform's mercy. CurateAI as described in V1 is. The deeper GoKwik invests in the social-commerce surface, the more this single point of failure compounds. V2 architecture needs a channel-agnostic design — the agent logic should be portable across surfaces, not hardwired to Instagram's API contract.

---

## (c) What is your v2 vision?

CurateAI becomes GoKwik's checkout-in-context API — deployable across any social surface where a brand talks to its shoppers.

V1 proves the agent UX works. V2 is about making it real at scale: WhatsApp Business (the highest-intent messaging surface in India), Instagram DMs via the official API, and any chat thread where a brand-shopper conversation is already happening. The product bet is not that GoKwik has better AI than anyone else — any company can call Gemini or GPT-4o. The bet is that GoKwik's cross-merchant identity and loyalty graph is a moat that takes years to replicate. A new entrant building social commerce AI starts from zero on shopper identity. GoKwik starts with millions of identified shoppers, their wallet balances, their payment preferences, and their RTO profiles already loaded.

Three concrete V2 bets:

**Real catalog integration.** Live product feeds from merchant PIM systems, not a mocked JSON. The agent's matching quality today is limited by catalog depth. With real feeds and structured attributes, vision + search becomes genuinely useful at the scale GoKwik operates.

**Sponsored placement as a revenue line.** Once chat-to-checkout conversion is proven, merchants pay for their products to rank higher in agent responses — category exclusivity, first-surfaced deals, "featured brand" status. GoKwik owns the attribution (they see the full funnel), so the ROI story to merchants is clean. This is the business model that makes CurateAI a P&L line, not just a feature.

**Post-purchase in the same thread.** Order status, return initiation, re-order nudge, review request — all in the same DM thread that drove the original discovery. GoKwik already owns the checkout data. Owning the post-purchase conversation is a natural extension that increases merchant stickiness and gives shoppers a reason to return to the thread.

The V2 north star metric: how many GoKwik merchants have activated CurateAI as their default social commerce layer. That's the moat, not the AI.
