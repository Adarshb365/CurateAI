# Product Thinking Note — CurateAI

---

## (a) Which KPI do you move first and how?

Two KPIs, sequenced.

**Phase 1 — Shopper activation:** the number of unique shoppers who complete a discovery → cart cycle (at least one item added to cart via a CurateAI session) per week.

This is the "aha moment" metric. It proves the feature is being used and that the AI discovery experience is good enough to move someone from browsing to intent. It's squarely in GoKwik's control — they own the agent quality, the catalog matching, the UX — and it doesn't penalise GoKwik for a merchant's weak catalog or bad products. You can't optimise anything downstream until shoppers are actually adding things to cart.

**Phase 2 — Chat-to-checkout conversion rate:** of sessions where a shopper adds to cart via CurateAI, what % initiate a GoKwik checkout?

This is the metric that matters commercially — for GoKwik and for merchants. GoKwik's core value prop to merchants has always been "we improve your checkout conversion, here's the data." CurateAI lets them extend that same proof upstream into discovery. Once GoKwik can show a merchant "products surfaced in our agent convert at X%," they can charge for priority placement in the agent — sponsored ranking, category exclusivity, whatever the commercial model ends up being. That's a new revenue line on top of the checkout processing fee, and it's credible because GoKwik owns both ends of the funnel — the agent AND the checkout — so the attribution is clean. No third party claiming credit.

Move activation first to prove demand exists. Move conversion rate to prove the surface earns its place in the merchant's marketing stack.

---

## (b) What is the biggest technical or trust risk?

**Biggest technical risk: Platform dependency.**

The entire product lives inside Meta's DM API or WhatsApp Business API. One policy change, API deprecation, or pricing shift by Meta shuts the channel down. GoKwik's checkout SDK is embedded across thousands of merchant checkout pages — it is platform-agnostic by design. CurateAI as described is a single-platform bet. The deeper GoKwik invests in agent capabilities built on top of Meta's API contract, the more stranded those assets become if Meta changes the rules. This is an existential risk, not a feature risk. The V2 architecture needs to treat the channel as a pluggable layer — agent logic portable across Instagram, WhatsApp, and any future surface — not hardwired to one platform's API.

**Biggest trust risk: Multi-merchant post-purchase fragmentation.**

In a full-look session, a shopper buys a kurta from Global Desi, trousers from SNITCH, and a tote from Zouk — one chat, one payment, one experience in their head. But behind that is three separate merchant relationships, three fulfillment chains, and three return policies. When something goes wrong — wrong size, damaged item, delayed shipping — the shopper doesn't instinctively think "I need to contact SNITCH." They go back to where they bought it, which in their mental model is CurateAI. GoKwik processes the payment but owns none of the post-purchase experience. That gap is where trust breaks and churn happens.

Bringing order tracking, return initiation, and dispute resolution back into the chat thread is the V2 challenge that makes or breaks long-term retention. It requires deep merchant API integrations for each brand, unified order state management across merchants, and the ability to handle partial refunds in a single-payment multi-merchant flow — none of which are simple. Until this is solved, the more items a shopper buys in one session, the higher the risk of a post-purchase experience that feels abandoned.

---

## (c) What is your v2 vision?

CurateAI becomes GoKwik's checkout-in-context layer — deployable across any social surface where a brand talks to its shoppers, with a conversational experience sharp enough to replace a product page.

**Five V2 bets:**

**1. Cross-merchant attribute normalisation.** Size "L" at one brand is not "L" at another. "Off-white" and "cream" and "ivory" are the same colour named three different ways. Fabric specs, fit definitions, and size charts are inconsistent across merchants. Solving this is what lets the agent answer "is this true to size?" or "do you have this in a relaxed fit?" across a multi-merchant catalog — the questions that actually kill fashion conversions pre-checkout. This is the data infrastructure V2 is built on.

**2. Better vision and conversation quality.** A dedicated high-capability vision model for the item identification pass, separate from the conversational model. Shorter, tighter agent responses — every line of text above a product carousel is a scroll the shopper has to do on mobile. And a conversation design shift: ask 1–2 targeted clarifying questions ("casual or dressy?", "any budget?") before firing searches, rather than making assumptions and narrating them. The V1 agent is a search engine with a personality. The V2 agent is a tailor.

**3. Native social identity via Instagram auth.** The mid-chat phone nudge and OTP flow are V1 workarounds for the absence of platform identity. V2 integrates Instagram OAuth — the shopper is already logged in, GoKwik matches their handle to the identity graph, no phone number ask needed. This requires a Meta partnership, not just an engineering change. But it removes both the friction and the consent ambiguity in one move.

**4. Sponsored placement as a revenue line.** Once chat-to-checkout conversion is proven, merchants pay for their products to rank higher in agent responses — category exclusivity, first-surfaced deals, featured brand status. GoKwik owns the attribution (they see the full funnel), so the ROI story to merchants is clean. This is the business model that makes CurateAI a P&L line, not just a feature.

**5. Post-purchase in the same thread.** Order tracking, return initiation, re-order nudge — all in the DM thread that drove the original discovery. This directly addresses the fragmentation trust risk: instead of the shopper navigating three merchant portals after a multi-brand purchase, everything surfaces in one thread. GoKwik already owns the checkout data. Building the post-purchase layer closes the loop and gives shoppers a reason to come back to the thread — which is also where the next discovery session starts.

The V2 north star metric: how many GoKwik merchants have activated CurateAI as their default social commerce layer. That's the moat, not the AI.
