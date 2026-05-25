import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import requests
import subprocess
import hashlib
import json


from load_graph import download_graph_if_needed
download_graph_if_needed()

st.set_page_config(
    page_title="드라마 Intelligence",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@300;400;700&family=DM+Sans:wght@300;400;500&display=swap');
:root {
    --cherry: #C41E3A;
    --deep: #1a0a0f;
    --gold: #D4AF37;
    --cream: #FDF6EC;
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--deep);
    color: var(--cream);
}
.stApp {
    background: linear-gradient(135deg, #1a0a0f 0%, #2d0f1a 50%, #1a0a0f 100%);
}
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
    border-bottom: 1px solid rgba(212, 175, 55, 0.3);
    margin-bottom: 2rem;
}
.hero-title {
    font-family: 'Noto Serif KR', serif;
    font-size: 3.5rem;
    font-weight: 700;
    color: var(--cream);
    letter-spacing: -1px;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}
.hero-korean {
    font-family: 'Noto Serif KR', serif;
    font-size: 1.1rem;
    color: var(--gold);
    letter-spacing: 4px;
    margin-bottom: 1rem;
}
.hero-sub {
    font-size: 1rem;
    color: rgba(253, 246, 236, 0.6);
    font-weight: 300;
}
.method-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 2px;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.global-badge {
    background: rgba(196, 30, 58, 0.2);
    border: 1px solid var(--cherry);
    color: var(--cherry);
}
.local-badge {
    background: rgba(212, 175, 55, 0.2);
    border: 1px solid var(--gold);
    color: var(--gold);
}
.answer-card {
    background: rgba(253, 246, 236, 0.04);
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-left: 3px solid var(--gold);
    border-radius: 4px;
    padding: 2rem;
    margin-top: 1.5rem;
    font-size: 0.95rem;
    line-height: 1.8;
    color: rgba(253, 246, 236, 0.9);
}
.question-display {
    font-family: 'Noto Serif KR', serif;
    font-size: 1.3rem;
    color: var(--cream);
    margin-bottom: 0.5rem;
    font-style: italic;
}
.divider {
    border: none;
    border-top: 1px solid rgba(212, 175, 55, 0.2);
    margin: 2rem 0;
}
.stTextInput > div > div > input {
    background: rgba(253, 246, 236, 0.05) !important;
    border: 1px solid rgba(212, 175, 55, 0.3) !important;
    border-radius: 2px !important;
    color: var(--cream) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
}
.stButton > button {
    background: var(--cherry) !important;
    color: var(--cream) !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    letter-spacing: 1px !important;
    padding: 0.6rem 2rem !important;
}
.stSelectbox > div > div {
    background: rgba(253, 246, 236, 0.05) !important;
    border: 1px solid rgba(212, 175, 55, 0.3) !important;
    color: var(--cream) !important;
    border-radius: 2px !important;
}
.stats-row {
    display: flex;
    gap: 2rem;
    justify-content: center;
    margin: 1.5rem 0;
}
.stat-item { text-align: center; }
.stat-num {
    font-family: 'Noto Serif KR', serif;
    font-size: 2rem;
    color: var(--gold);
    font-weight: 700;
}
.stat-label {
    font-size: 0.75rem;
    color: rgba(253, 246, 236, 0.5);
    letter-spacing: 2px;
    text-transform: uppercase;
}
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-korean">드라마 인텔리전스</div>
    <div class="hero-title">K-Drama Intelligence</div>
    <div class="hero-sub">GraphRAG-powered reasoning across 100 top Korean dramas</div>
    <div class="stats-row">
        <div class="stat-item">
            <div class="stat-num">100</div>
            <div class="stat-label">Dramas</div>
        </div>
        <div class="stat-item">
            <div class="stat-num">∞</div>
            <div class="stat-label">Connections</div>
        </div>
        <div class="stat-item">
            <div class="stat-num">2</div>
            <div class="stat-label">Query Modes</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    question = st.text_input(
        "",
        placeholder="Ask anything about K-dramas — actors, tropes, cultural impact...",
        label_visibility="collapsed"
    )
with col2:
    method = st.selectbox(
        "",
        ["global", "local"],
        label_visibility="collapsed",
        format_func=lambda x: "🌐 Global" if x == "global" else "🎯 Local"
    )

examples = [
    "Which dramas became global hits and why?",
    "Which actors have the most diverse roles?",
    "What makes Squid Game different from other survival dramas?",
    "Which dramas share the enemies-to-lovers trope?",
    "Why did Crash Landing on You resonate globally?",
]

st.markdown("**Try asking:**")
cols = st.columns(len(examples))
for i, ex in enumerate(examples):
    with cols[i]:
        if st.button(ex[:30] + "...", key=f"ex_{i}", use_container_width=True):
            question = ex

def run_graphrag_query(question, method):
    env = os.environ.copy()
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    root_path = os.path.join(project_root, "graphrag_input")
    
    result = subprocess.run(
        [
            "graphrag", "query",
            "--root", root_path,
            "--method", method,
            "--query", question
        ],
        capture_output=True,
        text=True,
        timeout=180,
        env=env
    )
    
    print("ROOT PATH:", root_path)
    print("STDOUT:", result.stdout[:500])
    print("STDERR:", result.stderr[:200])
    print("RETURN CODE:", result.returncode)
    
    output = result.stdout
    if "SUCCESS:" in output:
        answer = output.split("SUCCESS:", 1)[1].strip()
        if "Global Search Response:" in answer:
            answer = answer.split("Global Search Response:", 1)[1].strip()
        elif "Local Search Response:" in answer:
            answer = answer.split("Local Search Response:", 1)[1].strip()
        return answer
    return output.strip() or result.stderr or "No response generated"

@st.cache_data(ttl=3600)
def cached_query(question, method):
    return run_graphrag_query(question, method)


if st.button("Ask", use_container_width=False):
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        badge_class = "global-badge" if method == "global" else "local-badge"
        badge_text = "GLOBAL SEARCH" if method == "global" else "LOCAL SEARCH"

        with st.spinner("Traversing the knowledge graph..."):
            try:
                answer = cached_query(question, method)

                st.markdown(f'<div class="method-badge {badge_class}">{badge_text}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="question-display">"{question}"</div>', unsafe_allow_html=True)

                from tmdb_helper import extract_dramas_from_text, extract_actors_from_text, get_poster_url, get_actor_photo_url, KNOWN_ACTORS

                dramas = extract_dramas_from_text(answer)
                show_actors = any(actor in question.lower() for actor in KNOWN_ACTORS if len(actor) > 4)
                actors = extract_actors_from_text(answer) if show_actors else []

                left_col, right_col = st.columns([2, 1])

                with left_col:
                    st.markdown(f'<div class="answer-card">{answer}</div>', unsafe_allow_html=True)

                with right_col:
                    for drama in dramas[:3]:
                        poster_url, drama_name = get_poster_url(drama)
                        if poster_url:
                            st.image(poster_url, caption=drama_name, use_container_width=True)
                    for actor in actors[:2]:
                        photo_url, actor_name = get_actor_photo_url(actor)
                        if photo_url:
                            st.image(photo_url, caption=actor_name, use_container_width=True)

            except Exception as e:
                st.error(f"Error: {str(e)}")

st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color: rgba(253,246,236,0.3); font-size: 0.75rem; letter-spacing: 2px;">
    BUILT WITH MICROSOFT GRAPHRAG · OPENAI GPT-4O-MINI · PYTHON
</div>
""", unsafe_allow_html=True)