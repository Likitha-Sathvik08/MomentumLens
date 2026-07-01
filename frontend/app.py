import streamlit as st

st.set_page_config(
    page_title="MomentumLens",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚽ MomentumLens")
st.markdown("**AI-powered tactical shift explainer for soccer matches**")

st.sidebar.header("Navigation")
st.sidebar.info("Use the pages on the left to load a match, view the momentum dashboard, or chat with the AI analyst.")

st.markdown("""
## Welcome to MomentumLens

MomentumLens helps you understand **why momentum changes** during a soccer match — not just what happened, but the tactical story behind each shift.

### How it works
1. **Load a match** — provide match details and events
2. **Analyze** — detect turning points automatically
3. **Explain** — IBM Granite generates human-friendly tactical explanations
4. **Chat** — ask follow-up questions about the match

Navigate to the **Dashboard** page to get started.
""")
