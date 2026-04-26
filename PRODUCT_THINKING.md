# Product Thinking Note — CurateAI

---

## (a) Which KPI do you move first and how?

**First KPI: identity resolution rate in guest chat sessions.**

Specifically: the % of chat sessions that reach the cart stage where the shopper verifies their phone number before checkout.

This is the single highest-leverage metric because everything downstream — personalised pricing, wallet application, payment prefill, RTO-aware COD — is gated behind identity. A session with no identity resolves to a generic offer and an empty checkout form. A session with identity unlocks the entire GoKwik network intelligence.

GoKwik's own checkout data already shows that identified shoppers convert at significantly higher rates than anonymous ones. The same dynamic plays out in chat. Moving identity resolution rate is not a vanity metric — it directly predicts checkout conversion on this new surface.

**How to move it:**

The phone nudge must feel like the agent doing you a favour, not a form being served. The current implementation embeds the nudge into the product narration at a moment of value ("if you've shopped with these brands before, drop your number and I'll check for rewards") — not as a standalone ask. Two nudges max; if ignored both times, it's dropped. No "link your account" language.

The second lever is making the OTP moment frictionless — inline, 4-digit, no redirect. The faster OTP completes, the less the conversation breaks.

Instrument the funnel: chat start → first product add → phone nudge → phone entered → OTP verified → checkout start → checkout complete. Fix the biggest drop-off stage first.

---

## (b) What is the biggest technical or trust risk?

**Price trust gap between chat and checkout.**

If the agent says "pay ₹449 with your HDFC card" in the DM and the checkout page shows ₹499 — because an offer expired, the catalog had a lag, or a session timed out — the shopper doesn't just abandon. They feel misled inside what felt like a personal, high-trust channel (a DM with a brand they follow). That's a harder trust recovery than a normal checkout drop-off.

This risk is amplified because the agent speaks confidently and personally. "Your HDFC card gets you 10% back on this one" lands differently than a generic banner ad — which means the disappointment when it doesn't hold lands differently too.

**Mitigation:**
- Prices and offers are computed at tool call time, not at message render time. The `view_cart` tool re-runs the pricing calculation fresh each time it's called.
- The agent's language is deliberately soft on certainty: "gets you" and "saves you" rather than "I've applied" or "guaranteed savings". The prompt explicitly bans "applied".
- Checkout link generation should re-validate the offer against GoKwik's live network before surfacing the final price — the chat price is an estimate, the checkout price is the contract.

The secondary risk is LLM hallucination on product details. The current prompt enforces that every product name and price must come from a `search_products` tool result — not from model training data. This is enforced in both the system prompt and the tool description. But it needs to be monitored; a confident wrong answer about product availability erodes trust faster than a vague one.

---

## (c) What is your v2 vision?

**CurateAI becomes GoKwik's checkout-in-context API — deployable across any social surface where a brand talks to its shoppers.**

V1 proves the agent UX works in a simulated Instagram DM. V2 is about making this real and scalable: WhatsApp Business API (the highest-intent messaging surface in India), Instagram DMs via the official API, and eventually any chat thread where a brand-shopper conversation happens.

The product bet: GoKwik is uniquely positioned to win social commerce not because of better AI — any company can call GPT-4o — but because of the identity and loyalty graph it has already built across thousands of D2C merchants and millions of shoppers. A new entrant building a social commerce AI starts from zero on identity. GoKwik starts with a running head start.

**The V2 flywheel:**

More social checkouts → more transaction data per shopper across more channels → richer cross-merchant behavioural signal → better personalisation (product, price, and payment) → higher conversion → more merchants want to integrate → more shoppers in the graph.

**Three concrete V2 bets:**

1. **Real catalog integration** — instead of a mocked JSON, live product feeds from merchant PIM systems. The agent's search quality is currently limited by catalog depth. With real feeds, vision + search becomes genuinely useful at scale.

2. **Post-purchase loop in the same thread** — order status, return initiation, re-order nudge, review request. The same chat thread that drove discovery handles fulfilment. GoKwik already owns the checkout data; owning the post-purchase conversation is a natural extension.

3. **Agent handoff to merchant** — for edge cases (custom sizing, gifting queries, out-of-stock alternatives), the agent escalates to a human brand rep within the same thread, with full context already loaded. This is the "always-on junior assistant" positioning: the agent handles 80% of commerce queries autonomously; the brand's team handles the 20% that needs a human.

The V2 metric is not just social checkout conversion — it's **merchant adoption**: how many GoKwik merchants activate CurateAI as their default social commerce layer. That's the business moat, not the AI.
