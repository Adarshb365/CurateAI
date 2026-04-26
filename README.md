# CurateAI by GoKwik

An AI shopping concierge that lives inside a social DM thread — product discovery, personalised pricing, loyalty apply, and checkout without ever leaving the chat.

**Live:** https://curate-ai-eight.vercel.app · **Code:** https://github.com/Adarshb365/CurateAI

---

## Run it locally

```bash
git clone https://github.com/Adarshb365/CurateAI.git
cd CurateAI
python3 -m http.server 8080
```

Then open `http://localhost:8080`. It's a single HTML file — no build, no npm, no backend.

**API key:** Replace `GEMINI_KEY_PLACEHOLDER` in the `CFG` object at the top of `index.html` with a free key from [Google AI Studio](https://aistudio.google.com/app/apikey).

---

## How it works

The prototype simulates an Instagram feed → DM inbox → brand chat thread. Inside the chat:

1. **Identity** — shopper enters phone upfront or the agent nudges mid-chat. OTP verified inline. Profile loads silently; agent doesn't announce it.
2. **Shop the Look** — shopper drops a photo or describes what they want. Gemini vision identifies each item and calls `search_products` for each one.
3. **Best Price** — tool applies network offers and merchant wallet balances before returning prices. Agent narrates the best deal.
4. **Loyalty** — wallet credits (e.g. Caprese ₹450, Zouk ₹75) are pre-applied in the prices shown. Payment recommendation computed at cart level.
5. **Checkout** — `generate_checkout` opens a GoKwik-style bottom sheet. Identity pre-filled, wallet shown, preferred payment highlighted, one tap to pay.

---

## Architecture

Single-file browser app. All state in a JS object `S`. No server.

```
callGemini()  →  Gemini 3 Flash Preview (text + vision)
      ↓
dispatchTool()  →  search_products / add_to_look / remove_from_cart / view_cart / generate_checkout
      ↓
Local JSON data  →  products.json (95 products) · shoppers.json (10 profiles) · offers
```

The system prompt rebuilds on every API call so identity changes mid-conversation (guest → returning user after OTP) take effect immediately.

**Why not Streamlit?** I started there (`app.py` is still in the repo). Streamlit re-runs the whole script on every interaction — can't hold chat bubbles, bottom sheets, or carousels without a full custom frontend anyway. Switching to a single HTML file took 2 hours and the UX became 10x closer to a real DM.

---

## Shopper data model

```json
{
  "phone": "8800000001",
  "name": "Zara H",
  "loyalty_tier": "Gold",
  "preferred_payment": "credit_card",
  "preferred_card_bank": "HDFC",
  "merchant_rewards": { "Caprese": 450, "Giva": 200, "Zouk": 100 },
  "cod_eligible": true,
  "rto_risk_score": "low",
  "top_brands": ["Urbanic", "Twenty Dresses", "SNITCH"]
}
```

Six identity states are covered: new user, returning rich profile, returning sparse profile, mid-chat phone (registered), mid-chat phone (new), guest.

Test numbers and OTP (`1234`) are in [`DEMO_QUERIES.md`](./DEMO_QUERIES.md).

---

## LLM Prompts

All prompts are in [`/prompts`](./prompts/README.md) with full text and usage notes.

| Prompt | When |
|--------|------|
| Base system prompt | Every call — persona, tool rules, payment rules |
| Guest mode appendix | No phone verified — phone nudge logic |
| New user appendix | Verified, no GoKwik history |
| Returning user appendix | Known shopper — name, wallet, payment, COD injected dynamically |
| 5 tool declarations | `search_products`, `add_to_look`, `remove_from_cart`, `view_cart`, `generate_checkout` |

A few non-obvious decisions baked into the prompts: tool descriptions carry behavioural rules not just schema (Gemini internalises them into reasoning), COD eligibility is injected silently per-shopper so the agent never explains why COD is or isn't shown, and the agent is banned from saying "applied" — it recommends, the shopper applies at checkout.
