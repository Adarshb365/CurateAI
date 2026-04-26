# Tool — `generate_checkout`

**When used:** Called by Gemini when the shopper is ready to pay — they've confirmed their look, seen the cart total, and signalled intent to check out ("let's buy this", "proceed", "go to checkout"). Triggers the GoKwik checkout bottom sheet in the UI with identity pre-filled.

**File location:**
- Declaration: `index.html` → `GEMINI_TOOLS[0].functionDeclarations[4]`
- Handler: `index.html` → `dispatchTool()` → `name === 'generate_checkout'` branch
- UI trigger: calls `setTimeout(() => openCheckout(sum), 200)` — the 200ms delay lets the agent's text reply render before the bottom sheet slides up

**What `openCheckout()` renders (based on identity state):**

| State | What the user sees |
|---|---|
| `S.shopper` set (returning) | Identity card with name + preferred payment pre-selected; address pre-filled if saved |
| `S.phone` set, no profile (new user) | Phone card shown; "Add delivery address" tap target |
| Neither (pure guest) | Collapsed "Add your details" box → tapping opens `showCheckoutAddressForm()` with phone + address fields |

---

## Tool Declaration (sent to Gemini)

```json
{
  "name": "generate_checkout",
  "description": "Open GoKwik checkout with identity and best price pre-applied.",
  "parameters": {
    "type": "OBJECT",
    "properties": {}
  }
}
```

## Example Tool Response

```json
{
  "total_payable": 1348,
  "total_savings": 350,
  "item_count": 2,
  "checkout_url": "https://checkout.gokwik.co/look"
}
```

## UI Side Effects (not Gemini-visible)

- `openCheckout()` is called client-side with the full cart summary
- Bottom sheet slides up over the chat with:
  - Item breakdown
  - Wallet savings (if any, per merchant)
  - Payment recommendation card
  - Identity section (returning / new / guest — conditionally rendered)
  - Sticky "Pay ₹{total}" CTA button
- Tapping "Pay" either proceeds (if address is on file) or triggers `showCheckoutAddressForm()` first
