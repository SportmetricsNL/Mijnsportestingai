import os
import time
import streamlit as st
import google.generativeai as genai
import pypdf
import docx

# --- 0. PAGE & THEME -------------------------------------------------------
st.set_page_config(
    page_title="Sportfysioloog AI",
    page_icon="🚴‍♂️",
    layout="wide",
)

# Global look & feel
st.markdown(
    r"""
    <style>
      :root {
        --bg: linear-gradient(145deg, #061428 0%, #0a2f4a 55%, #0c4c63 100%);
        --text: #eef5ff;
        --muted: #b9c6da;
        --accent: #7be0ff;
        --input-bg: rgba(255, 255, 255, 0.08);
      }
      body, .stApp { background: var(--bg); color: var(--text); font-family: "Inter", sans-serif; }
      .block-container { padding: 2rem 2rem; max-width: 800px; }
      
      /* --- 1. BALKEN WEGHALEN (TRANSPARANT) --- */
      .hero, .upload-card, .chat-card {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0.5rem 0;
        margin-bottom: 0.5rem;
      }

      /* --- 2. UPLOAD KNOP SUPER COMPACT & ROND --- */
      .stFileUploader { padding-top: 0px; }
      .stFileUploader label { display: none; } /* Label 'Upload rapport' weg */
      
      .stFileUploader div[data-testid="stFileDropzone"] { 
        padding: 4px 10px !important; /* Heel weinig ruimte binnenin */
        border-radius: 50px; /* Pilvorm */
        border: 1px solid rgba(255,255,255,0.2);
        background: var(--input-bg);
        min-height: 0px !important;
        height: 42px; /* Vaste kleine hoogte */
        align-items: center;
      }
      
      /* Tekst binnen upload kleiner */
      .stFileUploader div[data-testid="stFileDropzone"] div { font-size: 14px; gap: 5px; }
      .stFileUploader small { display: none; } /* 'Limit 200MB' tekst weg */
      .stFileUploader button { display: none; } /* 'Browse files' knop weg, dropzone is genoeg */

      /* --- 3. ANALYSEER KNOP --- */
      .stButton button { 
        width: 100%; 
        border-radius: 50px !important;
        background-color: #eef5ff !important; 
        color: #000000 !important;
        font-weight: 600;
        font-size: 14px;
        border: none;
        height: 42px; /* Zelfde hoogte als upload */
        padding: 0px !important;
        margin-top: 0px;
      }
      .stButton button:hover {
        background-color: var(--accent) !important;
        color: #000000 !important;
      }

      /* --- 4. INPUT BALK --- */
      .stTextInput input {
        background: var(--input-bg) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: var(--text) !important;
        border-radius: 50px !important;
        padding: 8px 20px;
        font-size: 14px;
      }
      .stTextInput label { display: none; }
      
      /* Hero tekst */
      .hero h1 { margin: 0 0 5px; font-weight: 700; color: var(--text); font-size: 28px; }
      .hero p { color: var(--muted); font-size: 14px; margin: 0; }

      /* Chat */
      .stChatMessage { background: transparent; padding: 0.5rem 0; }
      .stMarkdown p { color: var(--text); font-size: 15px; line-height: 1.5; }
      
      /* Loader */
      .bike-loader { display:flex; gap:6px; font-size:20px; margin: 4px 0 0; color: var(--muted); }
      .bike-loader div { animation: ride 0.9s ease-in-out infinite; }
      .bike-loader div:nth-child(2) { animation-delay: .15s; }
      .bike-loader div:nth-child(3) { animation-delay: .3s; }
      @keyframes ride { 0% { transform: translateX(0px); } 50% { transform: translateX(10px); } 100% { transform: translateX(0px); } }
      
      header { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 1. CONFIGURATIE ---
LOGO_PATH = "1.png" 
MODEL_NAME = "gemini-2.5-flash"

try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"].strip()
        genai.configure(api_key=api_key)
    else:
        pass 
except Exception as e:
    st.error(f"Error: {e}")

# --- 2. KENNIS LADEN ---
@st.cache_resource(show_spinner=False)
def load_all_knowledge():
    combined_text = ""
    for filename in os.listdir("."):
        try:
            if filename.lower().endswith(".pdf"):
                reader = pypdf.PdfReader(filename)
                for page in reader.pages:
                    text = page.extract_text()
                    if text: combined_text += text + "\n"
            elif filename.lower().endswith(".docx"):
                doc = docx.Document(filename)
                for para in doc.paragraphs:
                    combined_text += para.text + "\n"
        except:
            pass
    return combined_text

knowledge_base = load_all_knowledge()

# --- 3. AI SETUP ---
SYSTEM_PROMPT = f"""
ROL: Je bent een expert sportfysioloog van SportMetrics.
BRONMATERIAAL: Gebruik DEZE INFORMATIE als waarheid:
===
{knowledge_base}
===
REGELS:
1. SportMetrics doet GEEN lactaatmetingen (prikken), alleen ademgasanalyse.
2. Gebruik de principes (zoals Seiler zones) uit de literatuur.
3. Wees praktisch, enthousiast, gebruik bulletpoints.
4. Geen medisch advies.
5. Geef props aan de klant.
"""

try:
    model = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=SYSTEM_PROMPT)
except:
    pass

# --- 4. STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Hoi! Upload je testresultaten of stel direct een vraag."
    })

def submit_question():
    user_input = st.session_state.input_field
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        extra_context = ""
        if "last_uploaded_text" in st.session_state:
            extra_context = f"\n\nRAPPORT KLANT:\n{st.session_state['last_uploaded_text']}\n\n"

        full_prompt = user_input + extra_context
        
        try:
            response = model.generate_content(full_prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except:
            st.session_state.messages.append({"role": "assistant", "content": "Even geen verbinding."})
        
        st.session_state.input_field = ""

# --- 5. LAYOUT ---

# A. TITEL (Geen kader meer)
with st.container():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("<h1>SportMetrics Coach</h1>", unsafe_allow_html=True)
        st.markdown("<p>Geen poespas, alleen data → advies.</p>", unsafe_allow_html=True)
    with c2:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=120)
    st.markdown('</div>', unsafe_allow_html=True)

# B. UPLOAD + KNOP (Compact & Rond)
with st.container():
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    
    # 3 kolommen: Upload (groot), witruimte (mini), Knop (klein)
    col_up, col_space, col_btn = st.columns([3, 0.1, 1])
    
    with col_up:
        uploaded_file = st.file_uploader("Upload", type=["pdf", "docx"], label_visibility="collapsed")
    
    with col_btn:
        analyse_click = st.button("Analyseer", use_container_width=True)

    if uploaded_file is not None:
        try:
            txt = ""
            if uploaded_file.name.endswith(".pdf"):
                r = pypdf.PdfReader(uploaded_file)
                for p in r.pages: txt += p.extract_text() + "\n"
            elif uploaded_file.name.endswith(".docx"):
                d = docx.Document(uploaded_file)
                for p in d.paragraphs: txt += p.text + "\n"
            
            st.session_state["last_uploaded_text"] = txt
            st.toast("Bestand ontvangen", icon="✅")
        except:
            pass

    # DE FIX VOOR DE ERROR: Alles op 1 regel of triple quotes
    if analyse_click and "last_uploaded_text" in st.session_state:
        st.session_state.input_field = "Analyseer mijn geüploade zones en maak een samenvatting."
        submit_question()
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# C. CHAT & INPUT
with st.container():
    st.markdown('<div class="chat-card">', unsafe_allow_html=True)
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    
    st.text_input(
        "Vraag", 
        key="input_field", 
        on_change=submit_question, 
        placeholder="Typ je vraag...",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
