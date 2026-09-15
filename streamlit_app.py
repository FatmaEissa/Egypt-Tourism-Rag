"""
streamlit_app.py

UI for the Egypt Tourism RAG assistant.

This file contains NO RAG logic. It only sends the user's question to the
FastAPI backend (`POST /ask`) and renders the returned answer + sources.
"""

import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Egypt Tourism AI",
    page_icon="🏺",
    layout="centered",
    initial_sidebar_state="collapsed",
)

UI_TEXT = {
    "English": {
        "hero_title": "Explore Egypt with AI",
        "subtitle": "Ask about places, activities, and landmarks across Egypt.",
        "placeholder": "e.g. What can I visit in Luxor?",
        "button": "Ask",
        "spinner": "Searching sources and generating an answer...",
        "sources": "Sources",
        "empty": "Please type a question first.",
        "error": "Could not reach the assistant backend",
        "explore": "Explore Egypt",
        "ask_about": "Ask about",
        "try_asking": "Try asking",
        "can_ask": "What can I ask about?",
    },
    "العربية": {
        "hero_title": "استكشف مصر بالذكاء الاصطناعي",
        "subtitle": "اسأل عن الأماكن والأنشطة والمعالم في مصر.",
        "placeholder": "مثال: ما هي أهم المعالم السياحية في الأقصر؟",
        "button": "اسأل",
        "spinner": "جاري البحث في المصادر وإنشاء الإجابة...",
        "sources": "المصادر",
        "empty": "من فضلك اكتب سؤالاً أولاً.",
        "error": "تعذر الوصول إلى الخادم",
        "explore": "استكشف مصر",
        "ask_about": "اسأل عن",
        "try_asking": "جرّب أن تسأل",
        "can_ask": "عن ماذا يمكنني أن أسأل؟",
    },
}

HERO_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/e/e3/Kheops-Pyramid.jpg"

DESTINATIONS = [
    {"name": "Cairo", "img": "https://loremflickr.com/320/200/cairo,egypt",
     "desc_en": "The vibrant capital — Islamic Cairo and the Egyptian Museum.",
     "desc_ar": "العاصمة النابضة بالحياة — القاهرة الإسلامية والمتحف المصري.",
     "q_en": "What are the best attractions in Cairo?",
     "q_ar": "ماذا يمكنني زيارة في القاهرة؟"},
    {"name": "Giza", "img": "https://loremflickr.com/320/200/giza,pyramids",
     "desc_en": "Home of the Great Pyramids and the Sphinx.",
     "desc_ar": "موطن الأهرامات العظيمة وأبو الهول.",
     "q_en": "What are the main attractions in Giza?",
     "q_ar": "ما المعالم الأثرية في الجيزة؟"},
    {"name": "Luxor", "img": "https://loremflickr.com/320/200/luxor,temple",
     "desc_en": "Ancient temples and the Valley of the Kings.",
     "desc_ar": "معابد أثرية ووادي الملوك.",
     "q_en": "What can I visit in Luxor?",
     "q_ar": "ما أهم الأماكن التي يمكن زيارتها في الأقصر؟"},
    {"name": "Aswan", "img": "https://loremflickr.com/320/200/aswan,nile",
     "desc_en": "Nile-side calm, Philae Temple and Nubian villages.",
     "desc_ar": "هدوء النيل ومعبد فيلة والقرى النوبية.",
     "q_en": "What can I visit in Aswan?",
     "q_ar": "ما أفضل الأماكن السياحية في أسوان؟"},
    {"name": "Alexandria", "img": "https://loremflickr.com/320/200/alexandria,egypt",
     "desc_en": "Mediterranean coast and the Bibliotheca Alexandrina.",
     "desc_ar": "ساحل البحر المتوسط ومكتبة الإسكندرية.",
     "q_en": "What can I visit in Alexandria?",
     "q_ar": "ما أهم المعالم السياحية في الإسكندرية؟"},
    {"name": "Red Sea", "img": "https://loremflickr.com/320/200/redsea,diving",
     "desc_en": "Diving, coral reefs and Hurghada's beaches.",
     "desc_ar": "الغوص والشعاب المرجانية وشواطئ الغردقة.",
     "q_en": "What activities are available in the Red Sea area?",
     "q_ar": "ما الأنشطة المتاحة في منطقة البحر الأحمر؟"},
]

SUGGESTED = {
    "English": [
        "What can I visit in Luxor?",
        "What are the best attractions in Cairo?",
        "What can I visit in Aswan?",
        "What are the main attractions in Giza?",
        "What can I visit in Alexandria?",
    ],
    "العربية": [
        "ما أهم الأماكن التي يمكن زيارتها في الأقصر؟",
        "ماذا يمكنني زيارة في القاهرة؟",
        "ما أفضل الأماكن السياحية في أسوان؟",
        "ما المعالم الأثرية في الجيزة؟",
        "ما أهم المعالم السياحية في الإسكندرية؟",
    ],
}

CATEGORIES = [
    ("🏛", {"English": "Historical Sites", "العربية": "المواقع الأثرية"}),
    ("📍", {"English": "Destinations", "العربية": "الوجهات السياحية"}),
    ("🌊", {"English": "Activities & Experiences", "العربية": "الأنشطة والتجارب"}),
    ("🇪🇬", {"English": "Egyptian Tourism", "العربية": "السياحة المصرية"}),
]

CUSTOM_CSS = """
<style>
.block-container {padding-top: 1.5rem; max-width: 840px;}

.hero {
    position: relative;
    border-radius: 18px;
    overflow: hidden;
    margin-bottom: 1.8rem;
    height: 260px;
    display: flex;
    align-items: flex-end;
    box-shadow: 0 6px 20px rgba(90, 60, 20, 0.18);
}
.hero img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: brightness(0.98) saturate(1.05);
}
.hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, rgba(30,20,10,0.0) 40%, rgba(30,20,10,0.68) 100%);
}
.hero-content {position: relative; padding: 1.4rem 1.7rem; z-index: 1;}
.hero-content h1 {color: #FFF6E4; font-size: 2.2rem; margin: 0; text-shadow: 0 2px 8px rgba(0,0,0,0.55);}
.hero-content p {color: #FDF0DA; margin: 0.4rem 0 0 0; font-size: 1rem; text-shadow: 0 1px 5px rgba(0,0,0,0.55);}

.section-title {font-size: 1.2rem; font-weight: 700; color: #6E4A1F; margin: 1.7rem 0 0.7rem 0;}

.dest-card {background: #FFFBF2; border: 1px solid #E7D3A8; border-radius: 12px; overflow: hidden; margin-bottom: 0.7rem;}
.dest-card img {width: 100%; height: 110px; object-fit: cover;}
.dest-body {padding: 0.55rem 0.75rem 0.2rem 0.75rem;}
.dest-name {font-weight: 700; color: #A8681E; font-size: 0.95rem;}
.dest-desc {color: #6b5a44; font-size: 0.8rem; margin-top: 0.15rem; min-height: 2.4em;}

.cat-card {background: #FFFBF2; border: 1px solid #E7D3A8; border-radius: 12px; padding: 0.8rem; text-align: center; margin-bottom: 0.6rem;}
.cat-icon {font-size: 1.4rem;}
.cat-name {color: #4A3A22; font-size: 0.85rem; margin-top: 0.3rem;}

.qa-block {margin-top: 0.4rem; margin-bottom: 0.2rem;}
.question-label {color: #9c8a6a; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.03em;}
.question-text {color: #3B2A1A; font-size: 1.02rem; font-weight: 700; margin-top: 0.15rem;}
.answer-card {
    background: #FFFEF9;
    border: 1px solid #EEE0C0;
    border-left: 5px solid #C08A28;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    margin-top: 0.5rem;
    line-height: 1.65;
    color: #3B2A1A;
}
.source-card {
    background: #FFFBF2;
    border: 1px solid #E7D3A8;
    border-left: 3px solid #B5533C;
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.5rem;
}
.source-title {font-weight: 600; color: #A8681E; font-size: 0.92rem;}
.source-meta {color: #8a7757; font-size: 0.8rem;}

div.stButton > button {border-radius: 8px;}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.sidebar:
    lang = st.radio("Language / اللغة", ["English", "العربية"], horizontal=True)
    st.markdown("---")
    st.caption("Powered by ChromaDB · bge-m3 · bge-reranker-v2-m3 · Gemini")
    st.caption(f"Backend: `{API_URL}`")

t = UI_TEXT[lang]
desc_key = "desc_en" if lang == "English" else "desc_ar"
q_key = "q_en" if lang == "English" else "q_ar"
is_ar_ui = lang == "العربية"

if "history" not in st.session_state:
    st.session_state.history = []
if "question_input" not in st.session_state:
    st.session_state["question_input"] = ""


def ask_backend(q: str):
    """Send a question to the FastAPI backend and store the result — used by
    both the manual Ask button and the clickable suggestion/destination buttons."""
    try:
        response = requests.post(f"{API_URL}/ask", json={"question": q.strip()}, timeout=60)
        response.raise_for_status()
        data = response.json()
        st.session_state.history.append({"question": q.strip(), "result": data})
    except requests.exceptions.RequestException as e:
        st.session_state["last_error"] = f"{t['error']} ({API_URL}): {e}"


def trigger_question(q: str):
    """Button callback: queue a question to be asked on this rerun."""
    st.session_state["question_input"] = q
    st.session_state["pending_ask"] = q


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="hero">
        <img src="{HERO_IMAGE}" alt="Egypt" />
        <div class="hero-content">
            <h1>🏺 {t['hero_title']}</h1>
            <p>{t['subtitle']}</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Explore destinations
# ---------------------------------------------------------------------------
st.markdown(f"<div class='section-title'>🧭 {t['explore']}</div>", unsafe_allow_html=True)
cols = st.columns(3)
for i, d in enumerate(DESTINATIONS):
    with cols[i % 3]:
        st.markdown(
            f"""<div class="dest-card">
                <img src="{d['img']}" />
                <div class="dest-body">
                    <div class="dest-name">{d['name']}</div>
                    <div class="dest-desc">{d[desc_key]}</div>
                </div>
            </div>""",
            unsafe_allow_html=True,
        )
        st.button(f"{t['ask_about']} {d['name']}", key=f"dest_{d['name']}",
                  on_click=trigger_question, args=(d[q_key],), use_container_width=True)

# ---------------------------------------------------------------------------
# Suggested questions (language-specific keys so state doesn't clash)
# ---------------------------------------------------------------------------
st.markdown(f"<div class='section-title'>💬 {t['try_asking']}</div>", unsafe_allow_html=True)
sq_cols = st.columns(2)
for i, q in enumerate(SUGGESTED[lang]):
    with sq_cols[i % 2]:
        st.button(q, key=f"sugg_{lang}_{i}", on_click=trigger_question, args=(q,),
                  use_container_width=True)

# ---------------------------------------------------------------------------
# What can I ask about
# ---------------------------------------------------------------------------
st.markdown(f"<div class='section-title'>{t['can_ask']}</div>", unsafe_allow_html=True)
cat_cols = st.columns(4)
for i, (icon, names) in enumerate(CATEGORIES):
    with cat_cols[i]:
        st.markdown(
            f"""<div class="cat-card">
                <div class="cat-icon">{icon}</div>
                <div class="cat-name">{names[lang]}</div>
            </div>""",
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Ask form (manual typing still works exactly as before)
# ---------------------------------------------------------------------------
with st.form("ask_form", clear_on_submit=True):
    question = st.text_area(
        " ",
        placeholder=t["placeholder"],
        height=90,
        label_visibility="collapsed",
        key="question_input",
    )
    submitted = st.form_submit_button(t["button"], use_container_width=True)

if submitted:
    if not question or not question.strip():
        st.warning(t["empty"])
    else:
        with st.spinner(t["spinner"]):
            ask_backend(question)

# Handle a question triggered by a destination/suggestion button click.
pending = st.session_state.pop("pending_ask", None)
if pending:
    with st.spinner(t["spinner"]):
        ask_backend(pending)

last_error = st.session_state.pop("last_error", None)
if last_error:
    st.error(last_error)

# ---------------------------------------------------------------------------
# Conversation history
# ---------------------------------------------------------------------------
for entry in reversed(st.session_state.history):
    st.markdown("---")

    answer_text = entry["result"]["answer"]
    is_rtl = any("\u0600" <= ch <= "\u06FF" for ch in answer_text)
    direction = "rtl" if is_rtl else "ltr"
    align = "right" if is_rtl else "left"

    st.markdown(
        f"""<div class="qa-block" dir="{direction}" style="text-align:{align}">
            <div class="question-label">{t['button']}</div>
            <div class="question-text">{entry['question']}</div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='answer-card' dir='{direction}' style='text-align:{align}'>{answer_text}</div>",
        unsafe_allow_html=True,
    )

    sources = entry["result"].get("sources", [])
    if sources:
        with st.expander(f"📚 {t['sources']} ({len(sources)})"):
            for s in sources:
                title = s.get("title") or "Untitled"
                url = s.get("source_url")
                category = s.get("category")
                link_html = f"<a href='{url}' target='_blank'>{url}</a>" if url else ""
                st.markdown(
                    f"""<div class="source-card">
                        <div class="source-title">{title}</div>
                        <div class="source-meta">{category or ''}</div>
                        {link_html}
                    </div>""",
                    unsafe_allow_html=True,
                )