# Tool — `search_products`

**When used:** Called by Gemini whenever the agent needs to find products — triggered by a text query ("I want a white oversized tee") or by each distinct item identified in a look image. One call per item. The JS handler filters the local product catalog (`products.json`) and returns a ranked, personalised result set.

**File location:**
- Declaration: `index.html` → `GEMINI_TOOLS[0].functionDeclarations[0]`
- Handler: `index.html` → `dispatchTool()` → `case 'search_products'` / `find_products()` function

**What the handler does (not sent to Gemini, for reference):**
1. Filters `S.data.products` by `category`, `subcategory`, `gender`, `colors`, `style`, `tags`, `brand`, `max_price`, `min_price`
2. Applies `_subcat_match` and `_color_match` flags per product
3. Computes `is_closest_match` (highest subcategory + color score, first one only)
4. Applies personalised pricing: merchant wallet deductions if `S.shopper.merchant_rewards[brand] > 0`
5. Flags `is_best_deal` on the lowest effective price product
6. Returns `color_match_count`, `subcat_match_count` alongside the product array

---

## Tool Declaration (sent to Gemini)

```json
{
  "name": "search_products",
  "description": "Search D2C fashion catalog. Returns personalised pricing. Call once per distinct item visible in a look image or described by shopper. Map all attributes to catalog values — do not invent values outside the enums.",
  "parameters": {
    "type": "OBJECT",
    "required": ["category"],
    "properties": {
      "category": {
        "type": "STRING",
        "enum": ["topwear", "bottomwear", "footwear", "accessories", "ethnic", "dress"],
        "description": "Product category"
      },
      "subcategory": {
        "type": "STRING",
        "enum": [
          "t-shirt", "shirt", "jeans", "chinos", "trousers", "track-pants", "joggers",
          "polo", "sweatshirt", "sneakers", "loafers", "derby", "running-shoes", "sandals",
          "slides", "flats", "ethnic-sandals", "juttis", "kurta", "kurta-set", "anarkali",
          "churidar-set", "coord-set", "palazzo", "tunic", "blouse", "crop-top", "top",
          "midi-dress", "wrap-dress", "backpack", "duffel", "sling-bag", "tote",
          "sunglasses", "earrings", "cap", "hat", "belt", "watch", "wallet", "scarf",
          "jacket", "blazer", "shorts"
        ],
        "description": "Specific item type within category"
      },
      "gender": {
        "type": "STRING",
        "enum": ["men", "women", "unisex"],
        "description": "Target gender"
      },
      "colors": {
        "type": "ARRAY",
        "items": { "type": "STRING" },
        "description": "Colors visible — pick closest from: white, black, navy, blue, grey, brown, olive, green, red, orange, yellow, pink, purple, beige, cream, khaki, mustard, rust, teal, coral, maroon, mint, sage, peach, camel, charcoal, off-white, pastel-blue, sky-blue, forest-green, electric-blue, neon-yellow, multi"
      },
      "style": {
        "type": "STRING",
        "enum": [
          "casual", "streetwear", "formal", "smart-casual", "athleisure", "athletic",
          "ethnic", "festive", "minimal", "vintage", "vacation", "party", "classic",
          "casual-chic", "ethnic-boho", "ethnic-fusion", "modern", "versatile"
        ],
        "description": "Overall style of the item"
      },
      "tags": {
        "type": "ARRAY",
        "items": { "type": "STRING" },
        "description": "Construction/fit attributes e.g. [\"oversized\", \"graphic\", \"printed\", \"relaxed\", \"slim-fit\", \"v-neck\", \"cropped\"]"
      },
      "brand": {
        "type": "STRING",
        "enum": [
          "Adidas", "Assembly", "Aurelia", "Bewakoof", "Biba", "Campus Shoes", "Caprese",
          "Catwalk", "FabIndia", "Fastrack", "Giva", "Global Desi", "ID Shoes", "Inc.5",
          "Jaipur Kurti", "Lenskart", "Libas", "Mochi", "Mokobara", "Neemans", "Nike",
          "Puma India", "Rare Rabbit", "SNITCH", "Sassafras", "Solethreads",
          "The Bear House", "The Souled Store", "Titan Eye+", "Twenty Dresses", "Urbanic",
          "W for Woman", "Wrogn", "Zouk"
        ],
        "description": "Specific brand if mentioned by shopper"
      },
      "max_price": {
        "type": "INTEGER",
        "description": "Maximum price in INR — use when shopper mentions a budget"
      },
      "min_price": {
        "type": "INTEGER",
        "description": "Minimum price in INR — use when shopper wants premium options"
      },
      "limit": {
        "type": "INTEGER",
        "description": "Max products 1–6, default 4"
      }
    }
  }
}
```

## Example Tool Response

```json
{
  "products": [
    {
      "product_id": "p012",
      "name": "Oversized Drop-Shoulder Tee",
      "brand": "Bewakoof",
      "mrp": 699,
      "final_price": 449,
      "savings": 250,
      "image": "./data/images/p012.png",
      "is_closest_match": true,
      "is_best_deal": true
    },
    {
      "product_id": "p034",
      "name": "Classic Oversized Tee",
      "brand": "The Souled Store",
      "mrp": 799,
      "final_price": 599,
      "savings": 200,
      "image": "./data/images/p034.png",
      "is_closest_match": false,
      "is_best_deal": false
    }
  ],
  "color_match_count": 2,
  "subcat_match_count": 2
}
```
