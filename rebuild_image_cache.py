"""
Rebuild image_cache.json keyed by product ID.
Each product gets its own Unsplash search: "{brand} {product name} fashion".
Guarantees unique images across the entire carousel.
"""
import json, time, urllib.request, urllib.parse, os

API_KEY  = "2eczByC6ndXctn5B7yJtAaR4Xd34W-ZZKmXU5R4w7lQ"
PRODUCTS = os.path.join(os.path.dirname(__file__), "data", "products.json")
CACHE    = os.path.join(os.path.dirname(__file__), "data", "image_cache.json")

with open(PRODUCTS) as f:
    products = json.load(f)

# Load existing cache so we can skip already-fetched product IDs on reruns
try:
    with open(CACHE) as f:
        cache = json.load(f)
except Exception:
    cache = {}

def fetch(query: str) -> str:
    qs = urllib.parse.urlencode({"query": query, "per_page": 1, "orientation": "portrait"})
    url = f"https://api.unsplash.com/search/photos?{qs}&client_id={API_KEY}"
    req = urllib.request.Request(url, headers={"Accept-Version": "v1"})
    with urllib.request.urlopen(req, timeout=12) as r:
        data = json.loads(r.read())
    results = data.get("results", [])
    return results[0]["urls"]["regular"] if results else ""

total = len(products)
for i, p in enumerate(products, 1):
    pid   = p["id"]
    name  = p["name"]
    brand = p["brand"]
    gender_word = {"men": "men", "women": "women"}.get(p.get("gender", ""), "")
    query = f"{brand} {name} fashion"

    if cache.get(pid):  # only skip if there's an actual URL, not empty string
        print(f"[{i}/{total}] {pid} — skip (cached)")
        continue

    print(f"[{i}/{total}] {pid} {brand} — {name[:40]}", end=" ... ", flush=True)
    try:
        url = fetch(query)
        if url:
            cache[pid] = url
            print("OK")
        else:
            # fallback: gender + top style tags for relevance
            style_tags = " ".join(p.get("tags", [])[:3])
            fallback_q = f"{gender_word} {style_tags} fashion photography".strip()
            url = fetch(fallback_q)
            cache[pid] = url or ""
            print("tag-fallback" if url else "NO RESULT")
    except Exception as e:
        print(f"ERROR: {e}")
        cache[pid] = ""

    time.sleep(0.4)  # ~2.5 req/s

with open(CACHE, "w") as f:
    json.dump(cache, f, indent=2)

filled = sum(1 for v in cache.values() if v)
print(f"\nDone — {filled}/{len(cache)} products have images → {CACHE}")
