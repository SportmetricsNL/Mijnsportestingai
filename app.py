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

# --- GLOBAL STYLING (CLEAN LIGHT MODE / SOFT HIGH CONTRAST) ---
st.markdown(
    r"""
    <style>
      :root {
        /* Kleurenpalet: Soft High Contrast */
        --bg-color: #F4F6F9;       /* Zachte lichtgrijze achtergrond voor de hele pagina */
        --card-bg: #FFFFFF;        /* Puur wit voor de 'balken' (containers) */
        --text-color: #1E1E1E;     /* Zeer donkergrijs (beter dan puur zwart) */
        --muted-color: #666666;    /* Voor subtiele teksten */
        --accent-color: #2E86C1;   /* Professioneel blauw voor accenten */
        --border-color: #E0E0E0;   /* Subtiele lijntjes */
      }

      /* Algemene Pagina Settings */
      body, .stApp { 
          background-color: var(--bg-color); 
          color: var(--text-color); 
          font-family: "Inter", sans-serif; 
      }
      
      .block-container { 
          padding: 2rem 1rem; 
          max-width: 800px; 
      }
      
      /* --- 1. DE 'WITTE BALKEN' (CONTAINERS) --- */
      /* Dit creëert de witte blokken waar de content in leeft */
      .hero, .upload-card, .chat-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03); /* Heel subtiel schaduwtje voor diepte */
      }

      /* --- 2. HERO SECTIE --- */
      .hero h1 { 
          margin: 0 0 5px; 
          font-weight: 800; 
          color: var(--text-color); 
          font-size: 26px; 
          letter-spacing: -0.5px;
      }
      .hero p { 
          color: var(--muted-color); 
          font-size: 15px; 
          margin: 0; 
      }

      /* --- 3. COMPACTE UPLOAD KNOPPEN --- */
      .stFileUploader { padding-top: 0px; }
      .stFileUploader label { display: none; }
      
      .stFileUploader div[data-testid="stFileDropzone"] { 
        padding: 4px 10px !important;
        border-radius: 8px;
        border: 1px dashed var(--accent-color);
        background: #F8FBFF; /* Heel lichtblauw tintje */
        min-height: 0px !important;
        height: 48px;
        align-items: center;
        justify-content: center;
      }
      .stFileUploader div[data-testid="stFileDropzone"] div { font-size: 14px; color: var(--accent-color); }
      .stFileUploader small { display: none; }
      .stFileUploader button { display: none; }

      /* --- 4. ANALYSEER KNOP (High Visibility) --- */
      .stButton button { 
        width: 100%; 
        border-radius: 8px !important;
        background-color: var(--text-color) !important; /* Donkere knop */
        color: #FFFFFF !important; /* Witte tekst */
        font-weight: 600;
        font-size: 14px;
        border: none;
        height: 48px; /* Match height met upload */
        margin-top: 0px;
        transition: transform 0.1s ease;
      }
      .stButton button:hover {
        background-color: var(--accent-color) !important;
        transform: scale(1.01);
      }

      /* --- 5. INPUT VELD (Chat) --- */
      .stTextInput input {
        background: #FFFFFF !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-color) !important;
        border-radius: 8px !important;
        padding: 10px 15px;
        font-size: 15px;
      }
      .stTextInput input:focus {
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 0 2px rgba(46, 134, 193, 0.1);
      }
      .stTextInput label { display: none; }

      /* --- 6. CHAT BERICHTEN --- */
      .stChatMessage { background: transparent; padding: 0.5rem 0; }
      .stChatMessage[data-testid="stChatMessageAvatarUser"] { display: none; } /* Optioneel: verberg user avatar voor strakker beeld */
      
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

# A. TITEL (In een witte balk)
with st.container():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("<h1>SportMetrics Coach</h1>", unsafe_allow_html=True)
        st.markdown("<p>Geen poespas, alleen data → advies.</p>", unsafe_allow_html=True)
    with c2:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=100)
    st.markdown('</div>', unsafe_allow_html=True)

# B. UPLOAD + KNOP (In een witte balk)
with st.container():
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    
    # Layout optimalisatie voor mobiel/laptop
    # We gebruiken st.columns. Op mobiel worden deze automatisch gestacked door Streamlit, 
    # maar we houden de verhouding simpel voor een strakke lijn op desktop.
    col_up, col_btn = st.columns([3, 1], gap="small")
    
    with col_up:
        uploaded_file = st.file_uploader("Upload", type=["pdf", "docx"], label_visibility="collapsed")
    
    with col_btn:
        analyse_click = st.button("Analyseer Bestand", use_container_width=True)

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

    if analyse_click and "last_uploaded_text" in st.session_state:
        st.session_state.input_field = "Analyseer mijn geüploade zones en maak een samenvatting."
        submit_question()
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# C. CHAT & INPUT (In een witte balk)
with st.container():
    st.markdown('<div class="chat-card">', unsafe_allow_html=True)
    
    # Weergave berichten
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    
    # Input veld
    st.text_input(
        "Vraag", 
        key="input_field", 
        on_change=submit_question, 
        placeholder="Typ je vraag over de test...",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
