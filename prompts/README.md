# CurateAI — Prompts Documentation

All LLM prompts used by CurateAI are documented here. The system uses **Google Gemini 2.0 Flash** via the `generateContent` API with a dynamic system prompt + 5 function/tool declarations.

---

## How prompts are assembled

Every Gemini call constructs the system prompt at runtime in `buildSystemPrompt()` (`index.html`):

```
[Base system prompt]  ←  always sent
      +
[One mode appendix]   ←  selected based on identity state:
    • Guest mode      (no phone verified)
    • New user mode   (phone verified, no GoKwik history)
    • Returning user  (phone verified, full profile found)
```

The 5 tool declarations are sent unchanged on every call.

---

## Files

| File | What it contains |
|------|-----------------|
| [01_system_prompt_base.md](01_system_prompt_base.md) | Core persona, search/cart/payment rules — always active |
| [02_system_prompt_guest_mode.md](02_system_prompt_guest_mode.md) | Phone nudge instructions for unverified sessions |
| [03_system_prompt_new_user_mode.md](03_system_prompt_new_user_mode.md) | First-visit framing (verified but no history) |
| [04_system_prompt_returning_user.md](04_system_prompt_returning_user.md) | Dynamic profile injection: name, wallet, payment, COD rules |
| [05_tool_search_products.md](05_tool_search_products.md) | Full schema for `search_products` — 11 parameters with enums |
| [06_tool_add_to_look.md](06_tool_add_to_look.md) | `add_to_look` — adds confirmed item to cart |
| [07_tool_remove_from_cart.md](07_tool_remove_from_cart.md) | `remove_from_cart` — removes item from cart |
| [08_tool_view_cart.md](08_tool_view_cart.md) | `view_cart` — full cart summary + payment recommendation |
| [09_tool_generate_checkout.md](09_tool_generate_checkout.md) | `generate_checkout` — triggers GoKwik checkout bottom sheet |

---

## Design decisions worth noting

- **No separate embedding / retrieval step.** Product search is pure JS filtering on a local JSON catalog. Gemini maps natural language → structured attributes → filtered results. Fast, deterministic, no RAG cost.
- **Prompt is stateful, not static.** The system prompt re-computes on every turn so mid-conversation identity changes (guest → returning user after OTP) take effect on the very next Gemini call.
- **Tools enforce actions, text enforces tone.** The base prompt's non-negotiable rules (never mention RTO, never announce profile loading) keep Gemini from leaking internal system details that would break the concierge illusion.
- **Closest Match is JS-side, not LLM-side.** Subcategory + color scoring happens in `dispatchTool()` before flags are passed to Gemini — reliable, consistent, no hallucination risk.
