import os
import uuid

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AI Travel Assistant",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════
# Styling  (ocean / sand palette)
# ══════════════════════════════════════════════════════════
st.markdown(
    """
<style>
:root {
  --sky:#c8e6f5; --ocean:#0a6e9f; --deep:#04374f; --deeper:#021e2c;
  --sand:#f2e9d8; --amber:#e8a040; --foam:#eaf6fb; --muted:#7fb0c6;
  --line:#1a4a63;
}

/* page */
.stApp { background: radial-gradient(1200px 600px at 70% -10%, #06456a33, transparent), var(--deeper); }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stAppDeployButton"] { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.6rem; max-width: 880px; }

/* headings use a serif face */
h1, h2, h3, .brand-title, .hero-title { font-family: Georgia, 'Times New Roman', serif !important; letter-spacing: .2px; }

/* sidebar */
section[data-testid="stSidebar"] { background: var(--deep); border-right: 1px solid var(--line); }
section[data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }
.brand { display:flex; align-items:center; gap:.65rem; margin-bottom:.2rem; }
.brand-mark { width:38px; height:38px; border-radius:11px; display:grid; place-items:center;
  background: linear-gradient(145deg, var(--ocean), #0b4f73); font-size:20px; border:1px solid #2a7da6; }
.brand-title { font-size:1.12rem; font-weight:700; color:var(--sand); line-height:1.1; }
.brand-sub { font-size:.74rem; color:var(--muted); }
.side-label { font-size:.7rem; text-transform:uppercase; letter-spacing:.12em; color:var(--muted);
  margin:1.1rem 0 .35rem; font-weight:600; }

/* file uploader */
[data-testid="stFileUploaderDropzone"] { background:#021e2c88; border:1.5px dashed #2a7da6; border-radius:12px; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--amber); }

/* buttons */
.stButton > button { border-radius:10px; border:1px solid var(--line); background:#021e2c99;
  color:var(--sand); font-weight:500; transition:all .15s ease; }
.stButton > button:hover { border-color:var(--amber); color:var(--amber); background:#021e2ccc; }
.stButton > button[kind="primary"] { background:var(--amber); color:#2a1a00; border-color:var(--amber); font-weight:600; }
.stButton > button[kind="primary"]:hover { background:#f0b45e; color:#2a1a00; }

/* selectbox */
[data-baseweb="select"] > div { background:#021e2c99; border-color:var(--line); border-radius:10px; }

/* top bar */
.topbar { display:flex; align-items:center; justify-content:space-between; padding:.2rem 0 1rem;
  border-bottom:1px solid var(--line); margin-bottom:1.1rem; }
.top-title { font-family:Georgia,serif; font-size:1.45rem; font-weight:700; color:var(--sand); margin-bottom:.15rem; }
.topbar span { font-size:.82rem; color:var(--muted); }
.pill { font-size:.72rem; color:var(--sky); border:1px solid var(--line); border-radius:999px;
  padding:.18rem .65rem; background:#04374f88; }

/* hero / empty state */
.hero { text-align:center; padding:2.2rem 0 1.4rem; }
.hero-title { font-size:2.2rem; font-weight:700; color:var(--sand); margin:0 0 .5rem; }
.hero-title em { color:var(--amber); font-style:normal; }
.hero-sub { color:var(--muted); font-size:1rem; max-width:520px; margin:0 auto; line-height:1.55; }
.steps { display:flex; gap:.7rem; justify-content:center; margin:1.6rem 0 .4rem; flex-wrap:wrap; }
.step { background:#04374f66; border:1px solid var(--line); border-radius:12px; padding:.7rem .95rem;
  font-size:.82rem; color:var(--sky); min-width:150px; text-align:left; }
.step b { display:block; color:var(--amber); font-size:.7rem; letter-spacing:.1em; margin-bottom:.15rem; }
.try-label { text-align:center; font-size:.72rem; letter-spacing:.12em; text-transform:uppercase;
  color:var(--muted); margin:1.6rem 0 .6rem; }

/* chat */
[data-testid="stChatMessage"] { background:#04374f55; border:1px solid var(--line); border-radius:16px;
  padding:.9rem 1.1rem; margin-bottom:.75rem; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background: linear-gradient(135deg, #0a6e9f55, #0a6e9f33); border-color:#2a7da6; }
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li { line-height:1.62; }
[data-testid="stChatMessageAvatarAssistant"] { background:var(--amber) !important; }
[data-testid="stChatMessageAvatarUser"] { background:var(--ocean) !important; }
[data-testid="stCaptionContainer"] { color:var(--muted); }

/* chat input */
[data-testid="stChatInput"] { border-radius:14px; border:1px solid var(--line); background:var(--deep); }
[data-testid="stChatInput"]:focus-within { border-color:var(--amber); }

/* notes under answers */
.note { display:inline-block; font-size:.74rem; color:var(--sky); background:#04374f99;
  border:1px solid var(--line); border-radius:8px; padding:.15rem .6rem; margin-top:.5rem; }
.note.warn { color:#f4c986; border-color:#7a5a24; background:#3a2a0f66; }

/* confirm card */
.confirm { border:1px solid #7a5a24; background:#3a2a0f55; border-radius:14px; padding:.9rem 1.1rem; margin:.2rem 0 .6rem; }
.confirm b { color:var(--amber); }

/* expander */
[data-testid="stExpander"] { border:1px solid var(--line); border-radius:12px; background:#021e2c66; }
hr { border-color: var(--line) !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ══════════════════════════════════════════════════════════
# Session state
# ══════════════════════════════════════════════════════════
ss = st.session_state
ss.setdefault("session_id", str(uuid.uuid4()))
ss.setdefault("messages", [])
ss.setdefault("pending_general_query", None)
ss.setdefault("queued_prompt", None)
ss.setdefault("uploaded_names", [])

LANGUAGES = [
    "English", "Tamil", "Hindi", "Telugu", "Malayalam", "Kannada",
    "French", "German", "Spanish", "Japanese", "Chinese", "Arabic",
]

SUGGESTIONS = [
    "Plan a 5-day trip to Bali",
    "Best beaches in Thailand",
    "Hotels in Paris under $150",
    "Food guide for Tokyo",
]


# ══════════════════════════════════════════════════════════
# Backend helpers
# ══════════════════════════════════════════════════════════
def friendly_error(resp: requests.Response) -> str:
    """Turn a backend failure into a readable message."""
    try:
        detail = resp.json().get("detail", "")
    except Exception:
        detail = ""
    if "model_not_found" in detail or "does not exist" in detail:
        return "The chat model is not available on this API key. Set a valid model in GROQ_MODEL."
    if "429" in detail or "rate" in detail.lower():
        return "The model is rate-limited right now. Please wait a few seconds and try again."
    return f"The server could not answer this time. {detail[:200]}".strip()


def ask_backend(query: str, language: str, use_general: bool = False) -> dict:
    """Call /ask. Always returns a dict: {ok, answer, rewritten, error}."""
    try:
        r = requests.post(
            f"{FASTAPI_URL}/ask",
            json={
                "query": query,
                "session_id": ss.session_id,
                "language": language,
                "use_general": use_general,
            },
            timeout=120,
        )
    except requests.exceptions.RequestException:
        return {"ok": False, "error": "Cannot reach the server. If it was idle, give it a minute to wake up and retry."}
    if r.status_code != 200:
        return {"ok": False, "error": friendly_error(r)}
    data = r.json()
    return {
        "ok": True,
        "answer": data.get("response"),
        "rewritten": data.get("rewritten_query", query),
    }


def add_assistant(content, **extra):
    ss.messages.append({"role": "assistant", "content": content, **extra})


def handle_query(prompt: str, language: str, use_general: bool = False, show_user: bool = True):
    """Run one question end to end and store the result in session state."""
    if show_user:
        ss.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Searching your guides…" if not use_general else "Thinking…"):
            res = ask_backend(prompt, language, use_general)

    if not res["ok"]:
        add_assistant(res["error"], error=True)
    elif res["answer"] is None:
        ss.pending_general_query = prompt
        add_assistant(
            "I couldn't find this in your uploaded guides.",
            confirm=True,
        )
    else:
        add_assistant(
            res["answer"],
            original_query=prompt,
            rewritten_query=res["rewritten"],
            general=use_general,
        )
    st.rerun()


# ══════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        """
<div class="brand">
  <div class="brand-mark">🧭</div>
  <div><div class="brand-title">Travel Assistant</div>
  <div class="brand-sub">Answers from your own guides</div></div>
</div>""",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-label">Travel guides</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload PDF guides", type="pdf", accept_multiple_files=True, label_visibility="collapsed"
    )
    if uploaded_files and st.button("Process guides", type="primary", use_container_width=True):
        for f in uploaded_files:
            with st.spinner(f"Reading {f.name}…"):
                try:
                    r = requests.post(f"{FASTAPI_URL}/upload", files={"file": f}, timeout=300)
                    msg = r.json().get("message", "") if r.status_code == 200 else ""
                    if r.status_code == 200 and "success" in msg.lower():
                        st.success(f.name)
                        if f.name not in ss.uploaded_names:
                            ss.uploaded_names.append(f.name)
                    else:
                        st.error(f"{f.name}: {msg or 'upload failed'}")
                except Exception as e:
                    st.error(f"{f.name}: {e}")

    if ss.uploaded_names:
        st.caption("In this session: " + ", ".join(ss.uploaded_names))

    st.markdown('<div class="side-label">Reply language</div>', unsafe_allow_html=True)
    selected_language = st.selectbox("Reply language", LANGUAGES, label_visibility="collapsed")

    st.markdown('<div class="side-label">Session</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Clear chat", use_container_width=True):
            try:
                requests.post(f"{FASTAPI_URL}/clear", params={"session_id": ss.session_id}, timeout=15)
            except Exception:
                pass
            ss.messages = []
            ss.pending_general_query = None
            st.rerun()
    with c2:
        if st.button("Clear DB", use_container_width=True):
            try:
                r = requests.post(f"{FASTAPI_URL}/clear-db", timeout=30)
                if r.status_code == 200:
                    ss.uploaded_names = []
                    st.success("All guides removed")
                else:
                    st.error("Could not clear")
            except Exception as e:
                st.error(str(e))
    st.caption("Clear chat keeps your PDFs. Clear DB deletes them.")

    with st.expander("How to use"):
        st.markdown(
            """
1. Upload one or more PDF guides and press **Process guides**.
2. Pick a reply language.
3. Ask a question, then follow-ups like *what about food there?*

Guides stay stored after you close the app, so you only upload once.
Use **Clear DB** to start over with new guides.
"""
        )

    st.caption(f"Session `{ss.session_id[:8]}`")


# ══════════════════════════════════════════════════════════
# Main area
# ══════════════════════════════════════════════════════════
st.markdown(
    """
<div class="topbar">
  <div><div class="top-title">Travel Itinerary Assistant</div>
  <span>Ask about any destination. Upload guides for deeper answers.</span></div>
  <div class="pill">Grounded in your PDFs</div>
</div>""",
    unsafe_allow_html=True,
)

# ── Empty state ───────────────────────────────────────────
if not ss.messages:
    st.markdown(
        """
<div class="hero">
  <div class="hero-title">Where do you want to <em>go</em>?</div>
  <div class="hero-sub">Upload your travel guides and get itineraries, hotels and food tips
  taken straight from them, in the language you choose.</div>
  <div class="steps">
    <div class="step"><b>1 · UPLOAD</b>Add PDF travel guides</div>
    <div class="step"><b>2 · ASK</b>Type a question or follow-up</div>
    <div class="step"><b>3 · TRAVEL</b>Get answers from your guides</div>
  </div>
  <div class="try-label">Try asking</div>
</div>""",
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, text in enumerate(SUGGESTIONS):
        if cols[i % 2].button(text, key=f"sugg{i}", use_container_width=True):
            ss.queued_prompt = text
            st.rerun()

# ── Conversation ──────────────────────────────────────────
last_index = len(ss.messages) - 1
for idx, m in enumerate(ss.messages):
    with st.chat_message(m["role"]):
        if m.get("error"):
            st.markdown(f'<div class="confirm"><b>Something went wrong.</b><br>{m["content"]}</div>', unsafe_allow_html=True)
        elif m.get("confirm"):
            st.markdown(
                f'<div class="confirm"><b>Not found in your guides.</b><br>'
                f"Do you want me to answer from general travel knowledge instead?</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(m["content"])
            if m["role"] == "assistant":
                if m.get("general"):
                    st.markdown('<span class="note warn">General knowledge, not from your guides</span>', unsafe_allow_html=True)
                rq, oq = m.get("rewritten_query"), m.get("original_query", "")
                if rq and rq.lower().strip() != oq.lower().strip():
                    st.markdown(f'<span class="note">Searched as: {rq}</span>', unsafe_allow_html=True)

# ── Yes / No for general knowledge ────────────────────────
if ss.pending_general_query is not None:
    b1, b2, _ = st.columns([1.3, 1, 2])
    if b1.button("Yes, use general knowledge", type="primary", key="gen_yes"):
        q = ss.pending_general_query
        ss.pending_general_query = None
        handle_query(q, selected_language, use_general=True, show_user=False)
    if b2.button("No thanks", key="gen_no"):
        ss.pending_general_query = None
        add_assistant("No problem. Upload a PDF guide for this destination and I'll answer from it.")
        st.rerun()

# ── Input ─────────────────────────────────────────────────
typed = st.chat_input("Ask about any destination…")
prompt = typed or ss.queued_prompt
ss.queued_prompt = None
if prompt:
    ss.pending_general_query = None  # a new question replaces any open yes/no
    handle_query(prompt, selected_language)
