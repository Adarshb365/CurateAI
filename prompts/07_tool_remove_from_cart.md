# Tool — `remove_from_cart`

**When used:** Called by Gemini when the shopper explicitly asks to remove an item from their cart — "actually remove the tee", "undo that", "take out the sneakers". The agent must call this before confirming removal to the user — saying "I've removed it" in text alone has no effect on state.

**File location:**
- Declaration: `index.html` → `GEMINI_TOOLS[0].functionDeclarations[2]`
- Handler: `index.html` → `dispatchTool()` → `name === 'remove_from_cart'` branch

**What the handler does:**
1. Filters `S.cart` to exclude the given `product_id`
2. Deletes `S.cartQty[product_id]`
3. Returns confirmation with product name and updated cart size

---

## Tool Declaration (sent to Gemini)

```json
{
  "name": "remove_from_cart",
  "description": "Remove a product fully from the cart. Call when shopper asks to remove or undo an item. Never confirm removal without calling this first.",
  "parameters": {
    "type": "OBJECT",
    "required": ["product_id"],
    "properties": {
      "product_id": {
        "type": "STRING",
        "description": "Product ID to remove e.g. 'p001'"
      }
    }
  }
}
```

## Example Tool Response

```json
{
  "removed": true,
  "product_id": "p012",
  "name": "Oversized Drop-Shoulder Tee",
  "cart_size": 0
}
```
