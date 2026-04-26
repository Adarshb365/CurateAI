# Tool — `add_to_look`

**When used:** Called by Gemini immediately when the shopper confirms they want a product — either by saying "yes", "add it", or by confirming a full look ("add all"). One call per product. Never called speculatively — only on explicit shopper confirmation.

**File location:**
- Declaration: `index.html` → `GEMINI_TOOLS[0].functionDeclarations[1]`
- Handler: `index.html` → `dispatchTool()` → `name === 'add_to_look'` branch

**What the handler does:**
1. Looks up `product_id` in `S.data.products`
2. If not already in `S.cart`, pushes it and initialises `S.cartQty[product_id] = 1`
3. Returns confirmation object with product name, brand, and current cart size

---

## Tool Declaration (sent to Gemini)

```json
{
  "name": "add_to_look",
  "description": "Add product to cart. Call immediately when shopper confirms a product.",
  "parameters": {
    "type": "OBJECT",
    "required": ["product_id"],
    "properties": {
      "product_id": {
        "type": "STRING",
        "description": "e.g. 'p001'"
      }
    }
  }
}
```

## Example Tool Response

```json
{
  "added": true,
  "product_id": "p012",
  "name": "Oversized Drop-Shoulder Tee",
  "brand": "Bewakoof",
  "cart_size": 1
}
```
