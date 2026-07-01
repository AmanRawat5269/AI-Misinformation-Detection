import streamlit as st
import requests
import threading
import time

st.set_page_config(page_title="Misinformation Detector", page_icon="🔍", layout="centered")

st.markdown("""
<style>
.main { padding-top: 2rem; }
.stTextInput input {
    border-radius: 10px;
    padding: 12px;
    font-size: 16px;
}
.stButton button {
    border-radius: 10px;
    padding: 10px 24px;
    font-weight: 600;
    width: 100%;
}
.verdict-box {
    padding: 20px;
    border-radius: 12px;
    margin: 16px 0;
    font-size: 20px;
    font-weight: 700;
}
.true-box { background-color: rgba(34,197,94,0.12); border: 1px solid rgba(34,197,94,0.4); color: #22c55e; }
.false-box { background-color: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.4); color: #ef4444; }
.misleading-box { background-color: rgba(234,179,8,0.12); border: 1px solid rgba(234,179,8,0.4); color: #eab308; }
.section-title { font-size: 18px; font-weight: 600; margin-top: 24px; margin-bottom: 8px; }
.source-link { font-size: 14px; opacity: 0.85; }
</style>
""", unsafe_allow_html=True)

st.title("🔍 Misinformation Detector")
st.caption("Powered by LangChain + Ollama + Groq")
st.divider()

claim = st.text_input("Enter your claim", placeholder="e.g. Drinking bleach cures COVID-19", label_visibility="collapsed")

if st.button("Check Claim", type="primary"):
    if claim:
        progress_bar = st.progress(0)
        progress_text = st.empty()
        result_holder = {}

        def call_api():
            result_holder["response"] = requests.post(
                "http://127.0.0.1:8000/predict",
                json={"claim": claim}
            )

        thread = threading.Thread(target=call_api)
        thread.start()

        steps = [
            ("🔍 Searching the web...", 15),
            ("📄 Scraping sources...", 40),
            ("🧠 Analyzing evidence...", 70),
            ("✅ Generating verdict...", 90),
        ]

        i = 0
        while thread.is_alive():
            text, pct = steps[i % len(steps)]
            progress_text.markdown(f"**{text}**")
            progress_bar.progress(pct)
            time.sleep(3)
            i += 1

        thread.join()
        progress_bar.progress(100)
        time.sleep(0.3)
        progress_bar.empty()
        progress_text.empty()

        response = result_holder["response"]
        data = response.json()
        
        # st.write(data)

        verdict = data["verdict"]
        confidence = data["confidence"]
        explanation = data["explanation"]
        sources = data["sources"]

        st.divider()

        # Verdict badge
        css_class = {"True": "true-box", "False": "false-box"}.get(verdict, "misleading-box")
        icon = {"True": "✅", "False": "❌"}.get(verdict, "⚠️")
        st.markdown(f'<div class="verdict-box {css_class}">{icon} VERDICT: {verdict}</div>', unsafe_allow_html=True)

        # Confidence bar
        try:
            conf_value = float(confidence)
            st.metric(label="Confidence Score", value=f"{conf_value:.0%}")
            st.progress(conf_value)
        except:
            st.write(f"Confidence: {confidence}")

        # Explanation
        st.markdown('<div class="section-title">📋 Explanation</div>', unsafe_allow_html=True)
        st.write(explanation)

        # Sources
        st.markdown('<div class="section-title">🔗 Sources</div>', unsafe_allow_html=True)
        if sources and sources != "No sources available":
            if isinstance(sources, str):
                sources = sources.split(',')
            for url in sources:
                url = url.strip()
                if url.startswith("http"):
                    st.markdown(f'<div class="source-link">• <a href="{url}" target="_blank">{url}</a></div>', unsafe_allow_html=True)
        else:
            st.write("No sources available")

    else:
        st.warning("Please enter a claim first!")