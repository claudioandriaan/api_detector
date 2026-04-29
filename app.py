import streamlit as st
from core.browser import capture_api_calls
from core.analyzer import is_valid_api, classify, detect_pagination
from core.validator import test_endpoint
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
st.set_page_config(page_title="API Detector", layout="wide")

st.title("🔍 API Detection Tool (for Scrapers)")

url = st.text_input("Enter website URL")

if st.button("Detect APIs"):
    if not url:
        st.warning("Please enter a URL")
    else:
        with st.spinner("Analyzing..."):
            raw_results = capture_api_calls(url)

            results = []
            seen = set()

            for entry in raw_results:
                if not is_valid_api(entry):
                    continue

                if entry["url"] in seen:
                    continue

                seen.add(entry["url"])

                api_type = classify(entry)
                reusable = test_endpoint(entry)
                pagination = detect_pagination(entry["url"])

                results.append({
                    "endpoint": entry["url"],
                    "type": api_type,
                    "method": entry["method"],
                    "reusable": reusable,
                    "pagination": pagination
                })

        if results:
            st.success(f"{len(results)} API(s) detected")

            for api in results:
                with st.expander(api["endpoint"]):
                    st.json(api)
        else:
            st.error("No API detected")

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
        Developed by <a href="https://github.com/claudioandriaan" target="_blank">Claudio Andriniaina</a>
    </div>
    """,
    unsafe_allow_html=True
)