"""Run once: adds image_keyword to every product in products.json."""
import json, os

BASE = os.path.join(os.path.dirname(__file__), "..", "data")

KEYWORD_MAP = {
    "t-shirt":          "oversized graphic t-shirt men streetwear fashion",
    "polo":             "men polo shirt smart casual fashion",
    "sweatshirt":       "men sweatshirt casual athleisure fashion",
    "shirt":            "men casual linen shirt fashion",
    "top":              "women casual fashion top summer",
    "tunic":            "women ethnic fusion top indian fashion",
    "crop-top":         "women crop top street style fashion",
    "blouse":           "women smart casual blouse office fashion",
    "joggers":          "men jogger pants athleisure streetwear",
    "track-pants":      "men track pants athletic sport fashion",
    "chinos":           "men slim chinos smart casual fashion",
    "trousers":         "women straight trousers smart casual fashion",
    "palazzo":          "women palazzo pants indian ethnic fashion",
    "jeans":            "women high waist jeans street style fashion",
    "midi-dress":       "women midi wrap dress casual fashion",
    "wrap-dress":       "women wrap dress casual summer fashion",
    "coord-set":        "women co-ord set fashion outfit",
    "anarkali":         "women anarkali indian ethnic festive wear",
    "kurta-set":        "women kurta set indian ethnic fashion",
    "kurta":            "women kurta indian ethnic casual fashion",
    "churidar-set":     "women churidar kurta set indian fashion",
    "sneakers":         "white sneakers fashion street style",
    "running-shoes":    "athletic running shoes sport fashion",
    "slides":           "casual slides sandals minimalist fashion",
    "sandals":          "women block heel sandals party fashion",
    "derby":            "men derby dress shoes formal fashion",
    "flats":            "women embellished flats party fashion",
    "loafers":          "men loafer smart casual shoes fashion",
    "ethnic-sandals":   "women kolhapuri ethnic sandals indian",
    "juttis":           "women embroidered juttis indian ethnic festive",
    "backpack":         "minimal premium backpack travel fashion",
    "tote":             "women tote bag everyday fashion",
    "sling-bag":        "women crossbody sling bag fashion",
    "duffel":           "canvas weekender duffel travel bag",
    "sunglasses":       "sunglasses fashion street style",
    "earrings":         "women earrings jewelry fashion minimal",
}

with open(os.path.join(BASE, "products.json")) as f:
    products = json.load(f)

for p in products:
    sub = p.get("subcategory", "")
    kw = KEYWORD_MAP.get(sub)
    if not kw:
        # fallback: use subcategory + gender + fashion
        kw = f"{sub} {p.get('gender','unisex')} fashion"
    p["image_keyword"] = kw

with open(os.path.join(BASE, "products.json"), "w") as f:
    json.dump(products, f, indent=2)

print(f"Added image_keyword to {len(products)} products.")
