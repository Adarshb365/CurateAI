"""
CurateAI — Gemini agent prompts and tool definitions.

Architecture: 4 tools, one chat session per shopper, one system prompt.
Gemini decides when to call tools. Python only dispatches and renders.
Uses google-genai SDK (v1+).
"""

from google import genai
from google.genai import types


# ── Tool definitions ──────────────────────────────────────────────────────────

TOOLS = [
    types.Tool(
        function_declarations=[

            types.FunctionDeclaration(
                name="search_products",
                description=(
                    "Search the D2C fashion catalog for products matching a look or style. "
                    "Returns products with fully personalised pricing — merchant discounts, "
                    "GoKwik network payment offers, and wallet balances already computed. "
                    "The best deal is flagged. "
                    "Call this whenever the shopper shares an image, describes a style, or asks to see options. "
                    "For a full look with multiple item types, call once per category "
                    "(e.g. topwear, bottomwear, footwear, accessories). "
                    "Use the returned pricing breakdown to narrate deals naturally — never calculate yourself."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "tags": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.STRING),
                            description=(
                                "Style tags describing the item. "
                                "e.g. ['oversized','graphic','streetwear'] for an oversized tee "
                                "or ['white','low-top','leather','sneakers'] for white sneakers."
                            )
                        ),
                        "colors": types.Schema(
                            type=types.Type.ARRAY,
                            items=types.Schema(type=types.Type.STRING),
                            description=(
                                "Colors visible on the item. Use simple color words. "
                                "e.g. ['mustard', 'yellow'] for a mustard yellow top, "
                                "['navy', 'blue'] for a navy piece, ['white'] for white. "
                                "Always populate this when color is visible — it improves matching."
                            )
                        ),
                        "category": types.Schema(
                            type=types.Type.STRING,
                            description="One of: topwear, bottomwear, footwear, accessories, ethnic, dress"
                        ),
                        "gender": types.Schema(
                            type=types.Type.STRING,
                            description="One of: men, women, unisex"
                        ),
                        "limit": types.Schema(
                            type=types.Type.INTEGER,
                            description="Max products to return. Default 5, max 6."
                        ),
                    },
                    required=["tags"]
                ),
            ),

            types.FunctionDeclaration(
                name="add_to_look",
                description=(
                    "Add a product to the shopper's current look. "
                    "Call this as soon as the shopper confirms they want a specific product — "
                    "they say yes, pick it, or tap add. "
                    "Returns the updated cart and which look categories still need filling."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "product_id": types.Schema(
                            type=types.Type.STRING,
                            description="Product id from search results e.g. 'p001'"
                        ),
                    },
                    required=["product_id"]
                ),
            ),

            types.FunctionDeclaration(
                name="view_cart",
                description=(
                    "Get the complete look summary — all added products with per-item pricing, "
                    "total savings, and total payable. "
                    "Call this when the shopper asks to see their full look or total, "
                    "or when all look categories are filled and it's time to show the Look Summary."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={},
                ),
            ),

            types.FunctionDeclaration(
                name="generate_checkout",
                description=(
                    "Generate the pre-filled GoKwik checkout for the shopper's current look. "
                    "Call this when the shopper confirms they want to pay — "
                    "they say checkout, proceed, pay, or similar. "
                    "Triggers the in-chat checkout modal with identity, best price, "
                    "and rewards all pre-applied. Shopper just confirms payment."
                ),
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={},
                ),
            ),

        ]
    )
]


# ── System prompt ─────────────────────────────────────────────────────────────

def build_system_prompt(shopper: dict = None) -> str:
    base = """\
You are Kwik Assistant — a personal shopping concierge living inside a brand's chat thread.
Your job: help shoppers find looks they love, get the best personalised price, and check out — without leaving this chat.

Personality:
- Warm, confident, direct. Like a knowledgeable friend who works in fashion.
- Short messages. One idea at a time. No walls of text.
- Natural conversation — handle questions, digressions, small talk, then steer back to shopping.
- Never sound like a bot reading a script.

How to work:
- When the shopper shares a look image: first reply with a single natural sentence naming every distinct item you see (e.g. "I can see a graphic tee, an overshirt, black trousers, and white sneakers — finding similar pieces now"). Then call search_products for each item.
- Treat each visible layer as a distinct item — an inner tee and an outer overshirt are both topwear but must be searched separately with their own tags.
- Make one search_products call per distinct visible item, NOT one per category. Five items in a look = five calls.
- search_products returns personalised prices — use the breakdown to narrate deals naturally. Never do math yourself.
- When the shopper picks a product, immediately call add_to_look.
- Once the look is complete or the shopper asks for a total, call view_cart.
- When they are ready to pay, call generate_checkout.

Non-negotiable rules:
- Never mention RTO, return rate, risk score, fraud, or anything implying you are assessing the shopper.
- Never announce that you are loading data, checking a profile, or calling any system.
- Never break character. You are a concierge, not a chatbot.
- If the shopper asks something off-topic, answer briefly and naturally steer back.
- Best price is always personalised — different shoppers see different deals on the same product.\
"""

    if not shopper:
        return base + """

Mode: Guest — no GoKwik identity found for this number.
- Show standard pricing with merchant sale offers only. No payment-specific deals.
- Do not show wallet balances.
- Once, naturally suggest linking their account: "If you have shopped at any D2C brand before, linking your account unlocks your card offers and any loyalty wallet you have built up."
- Keep it warm — guest mode is not a lesser experience, just less personalised.\
"""

    rewards = {k: v for k, v in shopper.get("merchant_rewards", {}).items() if v > 0}
    reward_lines = "\n".join(f"  - {m}: ₹{a} wallet" for m, a in rewards.items()) \
                   or "  - No active wallet balances"

    payment = shopper.get("preferred_payment", "")
    if payment == "credit_card":
        payment_label = f"credit card — {shopper.get('preferred_card_bank', '')} bank"
    elif payment == "upi":
        payment_label = f"UPI — {shopper.get('preferred_upi_app', '')}"
    else:
        payment_label = payment

    cod_rule = ""
    risk = shopper.get("rto_risk_score", "low")
    if not shopper.get("cod_eligible", True) or risk == "high":
        cod_rule = "\n- Do NOT offer or mention Cash on Delivery. Only show prepaid options. Never explain why."
    elif risk == "medium":
        cod_rule = "\n- Show prepaid options first and prominently. If COD appears, list it last with no offer or highlight."

    first_name = shopper.get("name", "").split()[0]

    return base + f"""

Shopper profile — loaded silently, behave as if you simply know this:
- Name: {shopper.get("name")} (use first name "{first_name}" occasionally — not every message)
- Loyalty tier: {shopper.get("loyalty_tier", "Bronze")}
- Preferred payment: {payment_label}
- Favourite categories: {shopper.get("top_category", "")}
- Favourite brands: {", ".join(shopper.get("top_brands", [])[:3])}
- Merchant wallet balances:
{reward_lines}

Personalisation behaviour:
- Narrate their specific payment deal naturally e.g. "your PhonePe gets you ₹75 back on this one".
- Surface wallet balances as a benefit e.g. "you have got ₹200 sitting in your Bewakoof wallet — that takes it down to ₹249".
- The best deal flag in search results is already computed for this shopper — trust it.{cod_rule}\
"""


# ── Gemini client factory ─────────────────────────────────────────────────────

def create_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def start_chat(client: genai.Client, shopper: dict = None):
    """
    Returns a configured chat session with system prompt and tools loaded.
    """
    config = types.GenerateContentConfig(
        system_instruction=build_system_prompt(shopper),
        tools=TOOLS,
        temperature=0.7,
    )
    return client.chats.create(model="gemini-3-flash-preview", config=config)


# ── Tool dispatcher ───────────────────────────────────────────────────────────

def dispatch_tool(tool_name: str, tool_args: dict, session_state) -> dict:
    from core.data_loader import (
        match_products, effective_price, cart_summary,
        build_checkout_url, get_image_url, PRODUCTS
    )

    shopper = session_state.get("shopper") or {}
    cart: list = session_state.get("cart", [])

    if tool_name == "search_products":
        tags = tool_args.get("tags", [])
        colors = tool_args.get("colors", [])
        category = tool_args.get("category")
        gender = tool_args.get("gender")
        limit = min(int(tool_args.get("limit", 5)), 6)

        results = match_products(tags, colors=colors, gender=gender, limit=limit * 2)
        if category:
            filtered = [p for p in results if p.get("category") == category]
            results = filtered if filtered else results
        results = results[:limit]

        products_out = []
        for p in results:
            if shopper:
                ep = effective_price(p, shopper)
            else:
                ep = {
                    "base_price": p["price"], "merchant_discount": 0,
                    "merchant_offer_label": None, "network_discount": 0,
                    "network_offer_label": None, "reward_applied": 0,
                    "total_savings": 0, "final_price": p["price"],
                }
            products_out.append({
                "id": p["id"],
                "name": p["name"],
                "brand": p["brand"],
                "merchant": p["merchant"],
                "mrp": p["mrp"],
                "base_price": ep["base_price"],
                "merchant_discount": ep["merchant_discount"],
                "merchant_offer_label": ep["merchant_offer_label"],
                "network_discount": ep["network_discount"],
                "network_offer_label": ep["network_offer_label"],
                "reward_applied": ep["reward_applied"],
                "total_savings": ep["total_savings"],
                "final_price": ep["final_price"],
                "image_url": get_image_url(p),
                "subcategory": p.get("subcategory", ""),
                "colors": p.get("colors", []),
            })

        if products_out:
            min_price = min(p["final_price"] for p in products_out)
            for p in products_out:
                p["is_best_deal"] = (p["final_price"] == min_price)

        return {"products": products_out, "count": len(products_out)}

    elif tool_name == "add_to_look":
        pid = tool_args.get("product_id")
        product = next((p for p in PRODUCTS if p["id"] == pid), None)
        if not product:
            return {"error": f"Product {pid} not found"}
        if pid not in [p["id"] for p in cart]:
            cart.append(product)
            session_state["cart"] = cart
        return {
            "added": product["name"],
            "brand": product["brand"],
            "cart_count": len(cart),
            "cart_items": [{"id": p["id"], "name": p["name"], "brand": p["brand"]} for p in cart],
        }

    elif tool_name == "view_cart":
        if not cart:
            return {"message": "Cart is empty — no items added yet"}
        summary = cart_summary(cart, shopper)
        return {
            "item_count": len(summary["items"]),
            "items": [
                {
                    "product_id": item["product"]["id"],
                    "name": item["product"]["name"],
                    "brand": item["product"]["brand"],
                    "merchant": item["product"]["merchant"],
                    "image_url": item["image_url"],
                    **item["pricing"],
                }
                for item in summary["items"]
            ],
            "subtotal": summary["subtotal"],
            "total_savings": summary["total_savings"],
            "total_payable": summary["total_payable"],
        }

    elif tool_name == "generate_checkout":
        if not cart:
            return {"error": "No items in look — add something first"}
        summary = cart_summary(cart, shopper)
        url = build_checkout_url(cart, shopper, summary)
        session_state["checkout_url"] = url
        session_state["checkout_summary"] = summary
        session_state["show_checkout_modal"] = True
        return {
            "checkout_url": url,
            "total_payable": summary["total_payable"],
            "total_savings": summary["total_savings"],
            "item_count": len(cart),
        }

    return {"error": f"Unknown tool: {tool_name}"}
