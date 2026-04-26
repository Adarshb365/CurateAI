"""CurateAI — Kwik Assistant: AI fashion concierge inside an Instagram DM thread."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from dotenv import load_dotenv
from google.genai import types

from prompts import create_client, start_chat, dispatch_tool
from core.data_loader import get_shopper

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# ── Constants ──────────────────────────────────────────────────────────────────

BRAND = "StyleThread"
OTP_CODE = "1234"

# ── Page config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title=f"Kwik Assistant · {BRAND}",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        font-family: 'Be Vietnam Pro', sans-serif !important;
        background-color: #0e1416 !important;
        color: #dee3e6 !important;
    }

    /* Hide default chrome */
    #MainMenu, footer, header { visibility: hidden; }

    /* Center column */
    .main .block-container {
        max-width: 680px;
        padding: 0 12px 80px;
        margin: 0 auto;
    }

    /* Chat bubbles */
    [data-testid="stChatMessage"] {
        background: transparent !important;
    }
    [data-testid="chatAvatarIcon-user"] {
        background-color: #45445d !important;
    }
    [data-testid="chatAvatarIcon-assistant"] {
        background-color: #00b4d8 !important;
    }

    /* Text inputs */
    .stTextInput input {
        background-color: #171c1f !important;
        border: 1px solid #3d494d !important;
        border-radius: 24px !important;
        color: #dee3e6 !important;
        font-family: 'Be Vietnam Pro', sans-serif !important;
        font-size: 16px !important;
        padding: 10px 18px !important;
    }
    .stTextInput input::placeholder { color: #869398 !important; }

    /* Chat input */
    [data-testid="stChatInput"] textarea {
        background-color: #171c1f !important;
        border: 1px solid #3d494d !important;
        border-radius: 24px !important;
        color: #dee3e6 !important;
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 20px !important;
        font-family: 'Be Vietnam Pro', sans-serif !important;
        font-weight: 600 !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: #00b4d8 !important;
        color: #003642 !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #4cd6fb !important;
    }
    .stButton > button:disabled {
        background: #1b2023 !important;
        color: #4cd6fb !important;
        border: 1px solid #3d494d !important;
    }

    /* Link buttons */
    [data-testid="stLinkButton"] a {
        border-radius: 20px !important;
        font-family: 'Be Vietnam Pro', sans-serif !important;
        font-weight: 600 !important;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: #1b2023;
        border-radius: 12px;
        padding: 10px 12px;
        border: 1px solid #3d494d;
    }
    [data-testid="stMetricValue"] { color: #dee3e6 !important; font-size: 18px !important; }
    [data-testid="stMetricLabel"] { color: #869398 !important; }

    /* File uploader */
    [data-testid="stFileUploadDropzone"] {
        background-color: #171c1f !important;
        border: 1px dashed #3d494d !important;
        border-radius: 12px !important;
        color: #869398 !important;
    }

    /* Dividers */
    hr { border-color: #3d494d !important; margin: 12px 0 !important; }

    /* Expander */
    [data-testid="stExpander"] {
        background: #171c1f !important;
        border: 1px solid #3d494d !important;
        border-radius: 12px !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: #0e1416; }
    ::-webkit-scrollbar-thumb { background: #3d494d; border-radius: 2px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state ──────────────────────────────────────────────────────────────

def _init():
    defaults = {
        "phase": "phone",           # phone | otp | chat
        "pending_phone": "",
        "shopper": None,
        "cart": [],
        "messages": [],
        "chat": None,
        "client": None,
        "checkout_url": None,
        "checkout_summary": None,
        "show_checkout_modal": False,
        "pending_action": None,
        "img_upload_key": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Gemini client ──────────────────────────────────────────────────────────────

def _get_client():
    if not st.session_state.client:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            st.error(
                "**GEMINI_API_KEY missing.** "
                "Create `curateai/.env` with `GEMINI_API_KEY=your_key_here`."
            )
            st.stop()
        st.session_state.client = create_client(api_key)
    return st.session_state.client


def start_session(shopper=None):
    """Initialise Gemini chat session and get the opening greeting."""
    chat = start_chat(_get_client(), shopper)
    st.session_state.chat = chat
    st.session_state.shopper = shopper
    st.session_state.cart = []
    st.session_state.messages = []

    # Kickoff prompt — hidden from the user, only the reply is shown
    if shopper:
        first_name = shopper.get("name", "").split()[0]
        brands = ", ".join(shopper.get("top_brands", [])[:2])
        tier = shopper.get("loyalty_tier", "Bronze")
        kick = (
            f"Greet {first_name} naturally as Kwik Assistant for {BRAND}. "
            f"They are a {tier} member who loves {brands or 'fashion'}. "
            "Make them feel recognised without being robotic — like a knowledgeable friend at their favourite brand. "
            "Invite them to share a look photo or describe what they want. 2 sentences max."
        )
    else:
        kick = (
            f"Greet a new guest as Kwik Assistant for {BRAND}. "
            "Welcome them warmly, mention you can help find amazing looks and personalise their price "
            "if they share their mobile number — but keep it light and natural. 2 sentences max."
        )

    resp = chat.send_message(kick)
    st.session_state.messages.append({
        "role": "assistant",
        "text": resp.text or f"Hey! Welcome to {BRAND}. What look are we building today?",
        "tool_results": [],
    })


# ── Message dispatch ───────────────────────────────────────────────────────────

def send_message(text: str, image_bytes=None, display_text=None):
    """Send user message to Gemini, run tool call loop, update messages."""
    user_msg = {"role": "user", "text": display_text or text}
    if image_bytes:
        user_msg["image"] = image_bytes
    st.session_state.messages.append(user_msg)

    if image_bytes:
        content = [
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            types.Part.from_text(text=text or "Shop this look for me"),
        ]
    else:
        content = text

    chat = st.session_state.chat
    all_tool_calls = []

    try:
        response = chat.send_message(content)

        while True:
            fcs = []
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if (
                        hasattr(part, "function_call")
                        and part.function_call
                        and part.function_call.name
                    ):
                        fcs.append(part.function_call)

            if not fcs:
                break

            tool_parts = []
            for fc in fcs:
                args = dict(fc.args) if fc.args else {}
                result = dispatch_tool(fc.name, args, st.session_state)
                all_tool_calls.append({"name": fc.name, "args": args, "result": result})
                tool_parts.append(
                    types.Part.from_function_response(name=fc.name, response=result)
                )

            response = chat.send_message(tool_parts)

        try:
            final_text = response.text or ""
        except Exception:
            final_text = ""  # Tool calls succeeded; model returned no follow-up text

    except Exception as exc:
        if all_tool_calls:
            final_text = ""  # Tool calls ran fine; don't pollute with error text
        else:
            final_text = "Sorry, I hit a snag — please try again."
        if os.getenv("DEBUG"):
            final_text += f"\n\n_{exc}_"

    st.session_state.messages.append({
        "role": "assistant",
        "text": final_text,
        "tool_results": all_tool_calls,
    })


# ── Product cards ──────────────────────────────────────────────────────────────

def _product_card(prod: dict, key: str):
    cart_ids = {p["id"] for p in st.session_state.cart}

    # Image — rendered as HTML img tag (browser-side) so external URLs load correctly
    pid = prod.get("id", key)
    img_url = prod.get("image_url") or f"https://picsum.photos/seed/{pid}/300/400"
    fallback = f"https://picsum.photos/seed/{pid}/300/400"
    st.markdown(
        f'<img src="{img_url}" '
        f'onerror="this.onerror=null;this.src=\'{fallback}\'" '
        f'style="width:100%;border-radius:8px;display:block;margin-bottom:4px;">',
        unsafe_allow_html=True,
    )

    # Best deal badge
    if prod.get("is_best_deal"):
        st.markdown(
            '<span style="background:#00b4d8;color:#003642;font-size:10px;font-weight:700;'
            'padding:2px 8px;border-radius:4px;letter-spacing:.4px;">⚡ BEST DEAL</span>',
            unsafe_allow_html=True,
        )

    st.markdown(f"**{prod['name']}**")

    # Only show merchant if it differs from brand (D2C brands are usually the same)
    brand = prod.get("brand", "")
    merchant = prod.get("merchant", "")
    subtitle = brand if brand == merchant else f"{brand} · {merchant}"
    st.caption(subtitle)

    # Pricing
    final = prod.get("final_price", 0)
    mrp = prod.get("mrp", final)
    savings = prod.get("total_savings", 0)

    if savings > 0:
        st.markdown(
            f'<span style="font-size:17px;font-weight:700;">₹{final:,}</span>'
            f' <span style="font-size:12px;color:#869398;text-decoration:line-through;">'
            f'₹{mrp:,}</span>',
            unsafe_allow_html=True,
        )
        st.caption(f"Save ₹{savings:,}")
    else:
        st.markdown(
            f'<span style="font-size:17px;font-weight:700;">₹{final:,}</span>',
            unsafe_allow_html=True,
        )

    # Offer labels
    label = prod.get("network_offer_label") or prod.get("merchant_offer_label")
    if label:
        st.caption(f"🏷️ {label}")
    if prod.get("reward_applied", 0) > 0:
        st.caption(f"💰 ₹{prod['reward_applied']} wallet applied")

    # CTA
    if prod["id"] in cart_ids:
        st.button("✓ Added", key=key, disabled=True, use_container_width=True)
    else:
        if st.button("Add to Look", key=key, use_container_width=True):
            st.session_state.pending_action = {"type": "add_to_look", "product": prod}


def render_product_cards(products: list, key_prefix: str = "prod", search_args: dict = None):
    if not products:
        return

    # Search context header — shows what the vision model identified
    if search_args:
        category = search_args.get("category", "")
        tags = search_args.get("tags", [])
        tag_str = ", ".join(tags[:4]) if tags else ""
        label = category.capitalize() if category else "Items"
        if tag_str:
            st.markdown(
                f'<div style="color:#869398;font-size:11px;margin-bottom:6px;">'
                f'🔍 <strong style="color:#bcc9ce;">{label}</strong> — {tag_str}</div>',
                unsafe_allow_html=True,
            )

    # Always 3-column grid — 4th+ products get a 1/3 slot, never full-width
    COLS = 3
    for i in range(0, len(products), COLS):
        batch = products[i : i + COLS]
        cols = st.columns(COLS)
        for j in range(COLS):
            if j < len(batch):
                with cols[j]:
                    _product_card(batch[j], key=f"{key_prefix}_{i + j}")


# ── Cart summary ───────────────────────────────────────────────────────────────

def render_cart_summary(result: dict, key_suffix: str = ""):
    if result.get("message"):
        st.caption(result["message"])
        return

    items = result.get("items", [])
    if not items:
        return

    st.markdown("---")
    st.markdown("**Your Look**")

    for item in items:
        c1, c2 = st.columns([1, 2])
        with c1:
            img_url = item.get("image_url", "")
            if img_url:
                st.markdown(
                    f'<img src="{img_url}" style="width:90px;border-radius:8px;">',
                    unsafe_allow_html=True,
                )
        with c2:
            st.markdown(f"**{item.get('name', '')}**")
            brand = item.get('brand', '')
            merchant = item.get('merchant', '')
            st.caption(brand if brand == merchant else f"{brand} · {merchant}")
            final = item.get("final_price", 0)
            base = item.get("base_price", final)
            savings = item.get("total_savings", 0)
            if savings > 0:
                st.markdown(
                    f'<span style="font-weight:700;">₹{final:,}</span>'
                    f' <span style="color:#869398;font-size:12px;'
                    f'text-decoration:line-through;">₹{base:,}</span>'
                    f' <span style="color:#4cd6fb;font-size:12px;">−₹{savings:,}</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f"**₹{final:,}**")

    st.markdown("---")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total MRP", f"₹{result.get('subtotal', 0):,}")
    c2.metric("You Save", f"₹{result.get('total_savings', 0):,}")
    c3.metric("You Pay", f"₹{result.get('total_payable', 0):,}")

    total_payable = result.get("total_payable", 0)
    if st.button(
        f"Checkout — Pay ₹{total_payable:,}",
        type="primary",
        use_container_width=True,
        key=f"cart_cta{key_suffix}",
    ):
        st.session_state.pending_action = {"type": "checkout"}


# ── Checkout modal ─────────────────────────────────────────────────────────────

@st.dialog("GoKwik Checkout", width="large")
def checkout_dialog():
    summary = st.session_state.get("checkout_summary")
    url = st.session_state.get("checkout_url", "#")

    if not summary:
        st.write("No checkout session found.")
        if st.button("Close", key="dlg_close_empty"):
            st.session_state.show_checkout_modal = False
            st.rerun()
        return

    # Header
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">'
        '<div style="background:#14b8a6;color:#fff;font-weight:900;font-size:11px;'
        'padding:3px 8px;border-radius:4px;letter-spacing:.3px;">GK</div>'
        '<span style="font-weight:700;font-size:17px;">GoKwik Secure Checkout</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Identity card
    shopper = st.session_state.get("shopper")
    if shopper:
        st.markdown(
            f'<div style="background:#003642;border:1px solid #00b4d8;'
            f'border-radius:10px;padding:10px 14px;margin:10px 0 4px;">'
            f'<div style="color:#4cd6fb;font-size:11px;font-weight:700;'
            f'letter-spacing:.4px;">✓ GOKWIK IDENTITY VERIFIED</div>'
            f'<div style="margin-top:2px;">'
            f'<span style="font-weight:600;">{shopper.get("name","")}</span>'
            f' · <span style="color:#869398;">{shopper.get("phone","")}</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    # Items — checkout_summary uses nested {product, image_url, pricing}
    for item in summary.get("items", []):
        prod = item["product"]
        pricing = item["pricing"]
        img_url = item.get("image_url", "")

        c1, c2 = st.columns([1, 3])
        with c1:
            if img_url:
                st.markdown(
                    f'<img src="{img_url}" style="width:80px;border-radius:8px;">',
                    unsafe_allow_html=True,
                )
        with c2:
            st.markdown(f"**{prod['name']}**")
            st.caption(f"{prod['brand']} · {prod['merchant']}")

            final = pricing.get("final_price", 0)
            base = pricing.get("base_price", final)
            savings = pricing.get("total_savings", 0)

            if savings > 0:
                st.markdown(
                    f'₹{final:,}'
                    f' <span style="color:#869398;font-size:12px;'
                    f'text-decoration:line-through;">₹{base:,}</span>'
                    f' <span style="color:#4cd6fb;font-size:12px;">−₹{savings:,}</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.write(f"₹{final:,}")

            label = pricing.get("network_offer_label") or pricing.get("merchant_offer_label")
            if label:
                st.caption(f"🏷️ {label}")
            if pricing.get("reward_applied", 0) > 0:
                st.caption(f"💰 ₹{pricing['reward_applied']} {prod['merchant']} wallet applied")

        st.markdown("")

    st.divider()

    # Totals
    c1, c2, c3 = st.columns(3)
    c1.metric("Total MRP", f"₹{summary.get('subtotal', 0):,}")
    c2.metric("Total Saved", f"₹{summary.get('total_savings', 0):,}")
    c3.metric("You Pay", f"₹{summary.get('total_payable', 0):,}")

    st.markdown("")

    # Savings callout
    saved = summary.get("total_savings", 0)
    if saved > 0:
        st.markdown(
            f'<div style="background:#1b2023;border:1px solid #3d494d;border-radius:10px;'
            f'padding:10px 14px;text-align:center;color:#4cd6fb;font-weight:600;">'
            f'✨ You save ₹{saved:,} on this look — best price, personalised for you'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("")

    total = summary.get("total_payable", 0)
    c_pay, c_close = st.columns([3, 1])
    with c_pay:
        st.link_button(
            f"Pay ₹{total:,} →",
            url,
            type="primary",
            use_container_width=True,
        )
    with c_close:
        if st.button("Close", use_container_width=True, key="dlg_close"):
            st.session_state.show_checkout_modal = False
            st.rerun()


# ── Phone screen ───────────────────────────────────────────────────────────────

def phone_screen():
    st.markdown(
        f'<div style="text-align:center;padding:48px 0 20px;">'
        f'<div style="font-size:30px;font-weight:800;color:#4cd6fb;">{BRAND}</div>'
        f'<div style="color:#869398;font-size:13px;margin-top:4px;">'
        f'Powered by Kwik Assistant ⚡</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    with st.chat_message("assistant"):
        st.write(
            f"Hey! Welcome to {BRAND} 👋 I'm your Kwik Assistant — a personal shopping concierge "
            "built on the GoKwik identity network.\n\n"
            "Drop your mobile number and I'll unlock your personalised prices, wallet balances, "
            "and exclusive payment offers. Or just browse as a guest."
        )

    st.markdown("")

    _, col, _ = st.columns([1, 4, 1])
    with col:
        phone_val = st.text_input(
            "phone",
            placeholder="10-digit mobile number",
            label_visibility="collapsed",
            key="phone_input",
        )

        c_cont, c_guest = st.columns([2, 1])
        with c_cont:
            cont = st.button("Continue →", type="primary", use_container_width=True)
        with c_guest:
            guest_btn = st.button("Guest →", use_container_width=True)

        if cont:
            if not phone_val:
                st.caption("Please enter your mobile number.")
            else:
                phone_clean = phone_val.strip().replace(" ", "").replace("-", "")
                shopper = get_shopper(phone_clean)
                st.session_state.pending_phone = phone_clean
                st.session_state.shopper = shopper
                st.session_state.phase = "otp"
                st.rerun()

        if guest_btn:
            with st.spinner("Starting session..."):
                start_session(shopper=None)
            st.session_state.phase = "chat"
            st.rerun()


# ── OTP screen ─────────────────────────────────────────────────────────────────

def otp_screen():
    phone = st.session_state.pending_phone
    shopper = st.session_state.shopper

    st.markdown(
        f'<div style="text-align:center;padding:48px 0 20px;">'
        f'<div style="font-size:30px;font-weight:800;color:#4cd6fb;">{BRAND}</div>'
        f'<div style="color:#869398;font-size:13px;margin-top:4px;">'
        f'Powered by Kwik Assistant ⚡</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    with st.chat_message("assistant"):
        if shopper:
            masked = "•" * max(0, len(phone) - 4) + phone[-4:]
            st.write(
                f"Found your GoKwik profile! 🎉\n\n"
                f"We've sent an OTP to **{masked}**. "
                "Enter it below to unlock your personalised prices and wallet balance."
            )
        else:
            st.write(
                f"I couldn't find a GoKwik profile for **{phone}**.\n\n"
                "No worries — enter the OTP we sent to verify, or skip to continue browsing."
            )

    st.markdown("")

    _, col, _ = st.columns([1, 4, 1])
    with col:
        otp_val = st.text_input(
            "OTP",
            placeholder="Enter OTP",
            label_visibility="collapsed",
            max_chars=6,
            key="otp_input",
        )

        c_verify, c_skip = st.columns([2, 1])
        with c_verify:
            verify_btn = st.button("Verify OTP", type="primary", use_container_width=True)
        with c_skip:
            skip_btn = st.button("Skip →", use_container_width=True)

        if verify_btn:
            if not otp_val:
                st.caption("Enter the OTP to continue.")
            elif otp_val.strip() == OTP_CODE:
                with st.spinner("Verifying..."):
                    start_session(shopper=st.session_state.shopper)
                st.session_state.phase = "chat"
                st.rerun()
            else:
                st.error("Incorrect OTP. Please try again.")

        if skip_btn:
            with st.spinner("Starting session..."):
                start_session(shopper=None)
            st.session_state.phase = "chat"
            st.rerun()

        st.markdown("")
        if st.button("← Change number"):
            st.session_state.phase = "phone"
            st.session_state.shopper = None
            st.session_state.pending_phone = ""
            st.rerun()


# ── Chat screen ────────────────────────────────────────────────────────────────

def chat_screen():
    shopper = st.session_state.get("shopper")

    # Header bar
    if shopper:
        tier = shopper.get("loyalty_tier", "Bronze")
        tier_color = {"Gold": "#f59e0b", "Silver": "#94a3b8", "Bronze": "#b45309"}.get(
            tier, "#869398"
        )
        meta = (
            f'<span style="color:{tier_color};font-size:11px;font-weight:700;">{tier}</span>'
            f' · <span style="color:#4cd6fb;font-size:11px;">⚡ GoKwik</span>'
        )
    else:
        meta = '<span style="color:#869398;font-size:11px;">Guest Mode</span>'

    cart_count = len(st.session_state.cart)
    st.markdown(
        f'<div style="background:#090f11;border-bottom:1px solid #3d494d;'
        f'padding:10px 4px;margin-bottom:12px;">'
        f'<div style="display:flex;align-items:center;gap:10px;">'
        f'<div style="width:34px;height:34px;background:#00b4d8;border-radius:50%;'
        f'display:flex;align-items:center;justify-content:center;font-weight:800;'
        f'color:#003642;font-size:14px;flex-shrink:0;">K</div>'
        f'<div><div style="font-weight:700;font-size:15px;color:#dee3e6;">'
        f'Kwik Assistant</div><div>{meta}</div></div>'
        f'<div style="margin-left:auto;background:#1b2023;border:1px solid #3d494d;'
        f'border-radius:20px;padding:4px 12px;font-size:12px;color:#dee3e6;">'
        f'🛒 {cart_count}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── Pending action handling (runs before render) ───────────────────────────
    if st.session_state.pending_action:
        action = st.session_state.pending_action
        st.session_state.pending_action = None

        if action["type"] == "add_to_look":
            prod = action["product"]
            with st.spinner(f"Adding {prod['name']} to your look..."):
                send_message(
                    f"Add the {prod['name']} by {prod['brand']} "
                    f"(product id: {prod['id']}) to my look",
                    display_text=f"Add {prod['name']} to my look",
                )
        elif action["type"] == "checkout":
            with st.spinner("Generating your checkout..."):
                send_message("Generate the checkout for my current look")

    # ── Message history ────────────────────────────────────────────────────────
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            with st.chat_message("user"):
                if msg.get("image"):
                    st.image(msg["image"], width=240)
                if msg.get("text"):
                    st.write(msg["text"])
        else:
            with st.chat_message("assistant"):
                if msg.get("text"):
                    st.write(msg["text"])

                # Deduplicate product IDs across all carousels in this message
                shown_pids: set = set()

                for j, tc in enumerate(msg.get("tool_results", [])):
                    name = tc["name"]
                    result = tc["result"]
                    prefix = f"m{i}t{j}"

                    if name == "search_products":
                        all_prods = result.get("products", [])
                        # Filter out any product already shown in a prior carousel this message
                        products = [p for p in all_prods if p["id"] not in shown_pids]
                        shown_pids.update(p["id"] for p in all_prods)
                        if products:
                            render_product_cards(
                                products,
                                key_prefix=prefix,
                                search_args=tc.get("args", {}),
                            )

                    elif name == "view_cart":
                        render_cart_summary(result, key_suffix=f"_{prefix}")

                    elif name == "generate_checkout" and not result.get("error"):
                        total = result.get("total_payable", 0)
                        item_count = result.get("item_count", 0)
                        st.markdown(
                            f'<div style="background:#003642;border:1px solid #00b4d8;'
                            f'border-radius:12px;padding:12px 16px;margin:8px 0;">'
                            f'<div style="color:#4cd6fb;font-weight:700;font-size:13px;">'
                            f'✓ Checkout ready · {item_count} '
                            f'item{"s" if item_count != 1 else ""} · '
                            f'₹{total:,} payable</div></div>',
                            unsafe_allow_html=True,
                        )
                        if st.button(
                            "Open GoKwik Checkout →",
                            type="primary",
                            key=f"open_ckout_{prefix}",
                        ):
                            st.session_state.show_checkout_modal = True
                            st.rerun()

    # ── Checkout modal ─────────────────────────────────────────────────────────
    if st.session_state.show_checkout_modal:
        checkout_dialog()

    # ── Input area ─────────────────────────────────────────────────────────────
    st.markdown("")

    # Image upload
    with st.expander("📷 Share a look photo"):
        uploaded = st.file_uploader(
            "Upload an image",
            type=["jpg", "jpeg", "png", "webp"],
            label_visibility="collapsed",
            key=f"img_up_{st.session_state.img_upload_key}",
        )
        if uploaded:
            img_bytes = uploaded.read()
            c_img, c_btn = st.columns([3, 1])
            with c_img:
                from PIL import Image
                import io
                try:
                    pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                    st.image(pil_img, width=180)
                except Exception:
                    st.caption("📷 Image ready to send")
            with c_btn:
                if st.button("Shop this →", type="primary", key="shop_img"):
                    st.session_state.img_upload_key += 1
                    with st.spinner("Analysing your look..."):
                        send_message(
                            "Identify the items in this look and find similar products "
                            "from D2C fashion brands",
                            image_bytes=img_bytes,
                            display_text="📷 [Look photo] Shop this look for me",
                        )
                    st.rerun()

    # Text chat input
    user_input = st.chat_input("Describe a style, share a look, or ask anything...")
    if user_input:
        with st.spinner(""):
            send_message(user_input)
        st.rerun()


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    _init()
    phase = st.session_state.phase
    if phase == "phone":
        phone_screen()
    elif phase == "otp":
        otp_screen()
    else:
        chat_screen()


main()
