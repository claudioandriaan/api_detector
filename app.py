import streamlit as st
from core.browser import capture_api_calls
from core.analyzer import is_valid_api, classify, detect_pagination
from core.validator import test_endpoint
from core.db import init_db, log_usage, get_usage

import asyncio
import sys
import uuid

# =========================================================
# SYSTEM FIX (Windows only)
# =========================================================
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# =========================================================
# INIT DB + SESSION (SaaS layer)
# =========================================================
init_db()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# =========================================================
# SaaS LIMIT CONFIG
# =========================================================
MAX_REQUESTS = 10

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="API Detector SaaS", layout="wide")

# =========================================================
# SIDEBAR NAVIGATION
# =========================================================
menu = st.sidebar.selectbox(
    "Navigation",
    ["🔍 Detector", "📚 Docs", "📊 Stats"]
)

# =========================================================
# PAGE 1 — DETECTOR
# =========================================================
if menu == "🔍 Detector":

    st.title("🔍 API Detection Tool (SaaS Edition)")

    st.caption(f"Session ID: {st.session_state.session_id[:8]}")

    url = st.text_input("Enter website URL")

    # -------------------------
    # SaaS LIMIT CHECK
    # -------------------------
    usage = get_usage(st.session_state.session_id)

    st.sidebar.metric("Usage", f"{len(usage)} / {MAX_REQUESTS}")

    if len(usage) >= MAX_REQUESTS:
        st.error("🚫 Free plan limit reached. Please upgrade your plan.")
        st.stop()

    if st.button("Detect APIs"):

        if not url:
            st.warning("Please enter a URL")
        else:

            # log usage (SaaS tracking)
            log_usage(st.session_state.session_id, url)

            with st.spinner("Analyzing website..."):

                raw_results = capture_api_calls(url)

                results = []
                seen = set()

                for entry in raw_results:

                    if not is_valid_api(entry):
                        continue

                    if entry["url"] in seen:
                        continue

                    seen.add(entry["url"])

                    results.append({
                        "endpoint": entry["url"],
                        "type": classify(entry),
                        "method": entry["method"],
                        "reusable": test_endpoint(entry),
                        "pagination": detect_pagination(entry["url"])
                    })

            # -------------------------
            # RESULTS UI
            # -------------------------
            if results:
                st.success(f"{len(results)} API(s) detected")

                for api in results:
                    with st.expander(api["endpoint"]):
                        st.json(api)
            else:
                st.error("No API detected")

# =========================================================
# PAGE 2 — DOCS
# =========================================================
elif menu == "📚 Docs":

    st.title("📚 Documentation")

    st.markdown("""
## 🚀 API Detector SaaS

This tool automatically detects API endpoints from websites using Playwright.

---

## ⚙️ Features

- 🔍 Detect JSON API calls
- 📦 Extract endpoints
- 🧠 Classify API type
- 📄 Detect pagination patterns
- ✅ Validate endpoints

---

## 🧠 SaaS System

Each user gets:
- Unique session ID
- Usage tracking
- Free tier limit (10 requests)

---

## 💎 Future Plans

- Login system
- API keys
- Paid plans (Stripe)
- Proxy support
- Export results (CSV/JSON)
""")

# =========================================================
# PAGE 3 — STATS (SaaS DASHBOARD)
# =========================================================
elif menu == "📊 Stats":

    st.title("📊 Usage Dashboard")

    usage = get_usage(st.session_state.session_id)

    st.metric("Requests used", len(usage))
    st.metric("Remaining", MAX_REQUESTS - len(usage))

    st.markdown("### Recent activity")

    if usage:
        for u in usage[:20]:
            st.write(f"🌐 {u[0]}  |  🕒 {u[1]}")
    else:
        st.info("No activity yet")

    if len(usage) >= MAX_REQUESTS:
        st.error("🚫 You reached the free tier limit")

# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        bottom: 10px;
        right: 10px;
        font-size: 12px;
        color: #888;
    }
    </style>

    <div class="footer">
        SaaS API Detector • Built by Claudio Andriniaina
    </div>
    """,
    unsafe_allow_html=True
)