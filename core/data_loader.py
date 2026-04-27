import json
import os

_BASE = os.path.join(os.path.dirname(__file__), "..", "data")


def _load(filename):
    with open(os.path.join(_BASE, filename), "r") as f:
        return json.load(f)


# All data loaded once at import — stays in memory
PRODUCTS = _load("products.json")
SHOPPERS = {s["phone"]: s for s in _load("shoppers.json")}
MERCHANT_OFFERS = _load("merchant_offers.json")
NETWORK_OFFERS = _load("gokwik_network_offers.json")

_image_cache_path = os.path.join(_BASE, "image_cache.json")
IMAGE_CACHE = _load("image_cache.json") if os.path.exists(_image_cache_path) else {}


# ── Identity ──────────────────────────────────────────────────────────────────

def get_shopper(phone: str):
    return SHOPPERS.get(phone.strip())


# ── Images ────────────────────────────────────────────────────────────────────

def get_image_url(product: dict) -> str:
    keyword = product.get("image_keyword", "")
    if keyword and keyword in IMAGE_CACHE:
        return IMAGE_CACHE[keyword]
    return product.get("image_url", f"https://picsum.photos/seed/{product['id']}/300/400")


# ── Product matching ──────────────────────────────────────────────────────────

def match_products(tags: list, colors: list = None, gender: str = None, limit: int = 5) -> list:
    """Return up to `limit` products ranked by tag + color overlap with the query."""
    tag_set = set(t.lower() for t in tags)
    color_set = set(c.lower() for c in (colors or []))
    scored = []
    for p in PRODUCTS:
        if gender and p.get("gender") not in (gender, "unisex"):
            continue
        tag_overlap = len(set(t.lower() for t in p["tags"]) & tag_set)
        # Expand hyphenated colors so "mustard-yellow" matches "mustard" or "yellow"
        p_colors = set()
        for c in p.get("colors", []):
            p_colors.add(c.lower())
            p_colors.update(c.lower().replace("-", " ").split())
        color_overlap = len(p_colors & color_set)
        score = tag_overlap + color_overlap
        if score > 0:
            scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:limit]]


# ── Offer helpers ─────────────────────────────────────────────────────────────

def _calc_discount(offer: dict, price: float) -> float:
    if offer["discount_type"] == "percent":
        raw = price * offer["discount_value"] / 100
        return min(raw, offer.get("max_discount", raw))
    return float(offer["discount_value"])


def best_merchant_offer(merchant: str, price: float):
    offers = MERCHANT_OFFERS.get(merchant, {}).get("offers", [])
    applicable = [o for o in offers if price >= o.get("min_order_value", 0)]
    if not applicable:
        return None
    return max(applicable, key=lambda o: _calc_discount(o, price))


def best_network_offer(shopper: dict, price: float):
    """Return the best GoKwik network offer for this shopper's payment method."""
    payment = shopper.get("preferred_payment", "")
    bank = shopper.get("preferred_card_bank", "")
    upi = shopper.get("preferred_upi_app", "")

    candidates = []

    # Bank offers
    for o in NETWORK_OFFERS.get("bank_offers", []):
        if price < o.get("min_order_value", 0):
            continue
        if payment == "credit_card" and o.get("card_bank") == bank:
            candidates.append(o)

    # UPI offers
    for o in NETWORK_OFFERS.get("upi_offers", []):
        if price < o.get("min_order_value", 0):
            continue
        if payment == "upi" and o.get("upi_app") == upi:
            candidates.append(o)

    # Partner offers (CRED)
    for o in NETWORK_OFFERS.get("partner_offers", []):
        if price < o.get("min_order_value", 0):
            continue
        if payment == o.get("payment_method"):
            candidates.append(o)

    # Prepaid offer — applies to any non-COD payment
    prepaid = NETWORK_OFFERS.get("prepaid_offer")
    if prepaid and payment != "cod" and price >= prepaid.get("min_order_value", 0):
        candidates.append(prepaid)

    if not candidates:
        return None
    return max(candidates, key=lambda o: _calc_discount(o, price))


# ── Effective price ───────────────────────────────────────────────────────────

def effective_price(product: dict, shopper: dict) -> dict:
    """
    Returns a breakdown dict:
      base_price, merchant_discount, merchant_offer_label,
      network_discount, network_offer_label,
      reward_applied, final_price
    """
    base = float(product["price"])
    merchant = product["merchant"]

    m_offer = best_merchant_offer(merchant, base)
    m_discount = _calc_discount(m_offer, base) if m_offer else 0.0
    m_label = m_offer["display_label"] if m_offer else None

    n_offer = best_network_offer(shopper, base)
    n_discount = _calc_discount(n_offer, base) if n_offer else 0.0
    n_label = n_offer["display_label"] if n_offer else None

    reward = float(shopper.get("merchant_rewards", {}).get(merchant, 0))

    final = max(0.0, base - m_discount - n_discount - reward)

    return {
        "base_price": round(base),
        "merchant_discount": round(m_discount),
        "merchant_offer_label": m_label,
        "network_discount": round(n_discount),
        "network_offer_label": n_label,
        "reward_applied": round(reward),
        "total_savings": round(m_discount + n_discount + reward),
        "final_price": round(final),
    }


# ── RTO / COD guard ───────────────────────────────────────────────────────────

def cod_allowed(shopper: dict) -> bool:
    return shopper.get("cod_eligible", True)


# ── Cart helpers ──────────────────────────────────────────────────────────────

def cart_summary(cart_items: list, shopper: dict) -> dict:
    """
    cart_items: list of product dicts (one per look category, already selected)
    Returns subtotal, total_savings, total_payable, per-item breakdowns.
    """
    items = []
    subtotal = 0
    total_savings = 0

    for product in cart_items:
        ep = effective_price(product, shopper)
        subtotal += ep["base_price"]
        total_savings += ep["total_savings"]
        items.append({
            "product": product,
            "image_url": get_image_url(product),
            "pricing": ep,
        })

    # Network offer re-applied on full cart for display — already factored per-item above
    total_payable = subtotal - total_savings

    return {
        "items": items,
        "subtotal": subtotal,
        "total_savings": total_savings,
        "total_payable": max(0, total_payable),
    }


def build_checkout_url(cart_items: list, shopper: dict, summary: dict) -> str:
    """Mock GoKwik checkout URL with all params pre-filled."""
    import urllib.parse
    item_ids = ",".join(p["id"] for p in cart_items)
    rewards = ";".join(
        f"{p['merchant']}:{shopper.get('merchant_rewards',{}).get(p['merchant'],0)}"
        for p in cart_items
        if shopper.get("merchant_rewards", {}).get(p["merchant"], 0) > 0
    )
    params = {
        "phone": shopper["phone"],
        "items": item_ids,
        "total": summary["total_payable"],
        "savings": summary["total_savings"],
    }
    if rewards:
        params["rewards"] = rewards
    return "https://checkout.gokwik.co/look?" + urllib.parse.urlencode(params)
