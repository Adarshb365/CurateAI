"""
Run once to populate image URLs from Unsplash into data/image_cache.json.

Usage:
    UNSPLASH_KEY=your_access_key python scripts/fetch_images.py

Get a free key at: https://unsplash.com/developers (App → Demo access, 50 req/hr)

What it does:
  - Reads data/products.json
  - For each unique image_keyword, searches Unsplash for 1 portrait fashion photo
  - Writes data/image_cache.json  →  { "keyword": "https://images.unsplash.com/..." }
  - The app reads image_cache.json at startup; falls back to picsum if key missing
"""

import json
import os
import time
import urllib.request
import urllib.parse

KEY = "2eczByC6ndXctn5B7yJtAaR4Xd34W-ZZKmXU5R4w7lQ"  # ← replace this string with your Unsplash Access Key
BASE = os.path.join(os.path.dirname(__file__), "..", "data")


def search_unsplash(keyword: str):
    query = urllib.parse.quote(keyword)
    url = (
        f"https://api.unsplash.com/search/photos"
        f"?query={query}&per_page=1&orientation=portrait"
        f"&content_filter=high&client_id={KEY}"
    )
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        results = data.get("results", [])
        if results:
            raw = results[0]["urls"]["regular"]
            # strip Unsplash tracking params, add our sizing
            photo_id = results[0]["id"]
            return f"https://images.unsplash.com/photo-{photo_id}?w=300&h=400&fit=crop&q=80"
    except Exception as e:
        print(f"  ERROR for '{keyword}': {e}")
    return None


def main():
    if not KEY:
        print("Set UNSPLASH_ACCESS_KEY env var first.\nGet one free at https://unsplash.com/developers")
        return

    with open(os.path.join(BASE, "products.json")) as f:
        products = json.load(f)

    keywords = sorted({p["image_keyword"] for p in products if p.get("image_keyword")})
    print(f"Fetching images for {len(keywords)} unique keywords…")

    cache_path = os.path.join(BASE, "image_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            cache = json.load(f)

    for kw in keywords:
        if kw in cache:
            print(f"  [cached] {kw}")
            continue
        print(f"  Searching: {kw}")
        url = search_unsplash(kw)
        if url:
            cache[kw] = url
            print(f"    → {url[:60]}…")
        else:
            print(f"    → no result, will use picsum fallback")
        time.sleep(0.5)  # stay well within 50 req/hr limit

    with open(cache_path, "w") as f:
        json.dump(cache, f, indent=2)

    print(f"\nDone. {len(cache)} keywords cached → data/image_cache.json")


if __name__ == "__main__":
    main()
