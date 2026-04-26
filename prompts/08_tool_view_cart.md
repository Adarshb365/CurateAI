# Tool — `view_cart`

**When used:** Called by Gemini when the look is complete or the shopper asks to see their total / what they've saved / what's in their cart. Also called when the shopper asks about payment deals or rewards so the agent can give an accurate payment recommendation. The JS side renders a cart card bubble in the chat UI after this call.

**File location:**
- Declaration: `index.html` → `GEMINI_TOOLS[0].functionDeclarations[3]`
- Handler: `index.html` → `dispatchTool()` → `name === 'view_cart'` branch → calls `cartSummary()`
- UI render: `index.html` → `renderCartCard(result)` — renders after the agentic loop returns tool results

**What `cartSummary()` computes:**
1. Iterates `S.cart`, multiplies each product's `final_price` by `S.cartQty[pid]`
2. Applies wallet deductions if `S.shopper.merchant_rewards[brand] > 0`
3. Computes `payment_recommendation`: picks the single best payment method for the full cart total from the network offers configured in `CFG` / `S.data.offers`
4. Returns a structured summary with itemised breakdown and totals

---

## Tool Declaration (sent to Gemini)

```json
{
  "name": "view_cart",
  "description": "Show full cart summary with pricing. Call when look is complete or shopper asks for total.",
  "parameters": {
    "type": "OBJECT",
    "properties": {}
  }
}
```

## Example Tool Response

```json
{
  "items": [
    {
      "product_id": "p012",
      "name": "Oversized Drop-Shoulder Tee",
      "brand": "Bewakoof",
      "qty": 1,
      "unit_price": 449,
      "line_total": 449,
      "wallet_saving": 250
    },
    {
      "product_id": "p088",
      "name": "Slim Cargo Jogger",
      "brand": "SNITCH",
      "qty": 1,
      "unit_price": 899,
      "line_total": 899,
      "wallet_saving": 0
    }
  ],
  "subtotal": 1348,
  "total_savings": 250,
  "total_payable": 1348,
  "payment_recommendation": {
    "method": "Amazon Pay",
    "saving": 100,
    "label": "Pay with Amazon Pay — save ₹100"
  },
  "item_count": 2
}
```
