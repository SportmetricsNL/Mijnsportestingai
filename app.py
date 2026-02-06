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

# Global look & feel (strak, blauwe achtergrond)
st.markdown(
    r"""
    <style>
      :root {
        --bg: linear-gradient(145deg, #061428 0%, #0a2f4a 55%, #0c4c63 100%);
        --card: rgba(255, 255, 255, 0.05);
        --border: rgba(255, 255, 255, 0.12);
        --text: #eef5ff;
        --muted: #b9c6da;
        --accent: #7be0ff;
      }
      body, .stApp { background: var(--bg); color: var(--text); font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
      .block-container { padding: 1.5rem 2rem 2.5rem; max-width: 900px; }
      
      /* CARDS STYLING */
      .hero, .upload-card, .chat-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 20px; /* Ronder */
        padding: 1.5rem;
        box-shadow: 0 20px 70px rgba(0,0,0,0.25);
        margin-bottom: 1rem;
      }

      /* HEADINGS */
      .hero h1 { margin: 0 0 .35rem; font-weight: 700; color: var(--text); font-size: 32px; }
      .hero p { color: var(--muted); font-size: 0.95rem; margin: 0.1rem 0 0; }

      /* UPLOAD ZONE COMPACT & ROUND */
      .stFileUploader div[data-testid="stFileDropzone"] { 
        padding: 0.5rem 0.8rem; 
        border-radius: 50px; /* Helemaal rond */
        border: 1px dashed var(--muted);
        min-height: 0px !important; /* Kleiner maken */
      }
      .stFileUploader div[data-testid="stFileDropzone"] div {
         gap: 0px;
      }
      .stFileUploader small { display: none; } /* Verberg 'limit 200mb' tekst voor compactheid */

      /* ANALYSEER KNOP (Zwart, Rond, Wit/Blauw) */
      .stButton button { 
        width: 100%; 
        border-radius: 50px !important; /* Rond knopje */
        background-color: #eef5ff !important; 
        color: #000000 !important; /* Zwarte tekst */
        font-weight: 700;
        border: none;
        padding: 0.5rem 1rem;
      }
      .stButton button:hover {
        background-color: var(--accent) !important;
        color: #000000 !important;
      }

      /* CHAT STYLING */
      .stChatMessage { background: transparent; }
      .stMarkdown p { color: var(--text); }
      .chat-card .stChatMessage[data-testid="stChatMessage"] div { color: var(--text); }
      
      /* LOADING ANIMATION */
      .bike-loader { display:flex; gap:6px; font-size:24px; margin: 4px 0 0; color: var(--muted); }
      .bike-loader div { animation: ride 0.9s ease-in-out infinite; }
      .bike-loader div:nth-child(2) { animation-delay: .15s; }
      .bike-loader div:nth-child(3) { animation-delay: .3s; }
      @keyframes ride { 0% { transform: translateX(0px); } 50% { transform: translateX(10px); } 100% { transform: translateX(0px); } }

      /* INPUT BAR INSIDE CARD */
      .stTextInput input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 50px !important; /* Ronde input balk */
        padding: 10px 20px;
      }
      .stTextInput label { display: none; } /* Label verbergen voor strakke look */
      
      header { margin-bottom: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 1. LOGO & MODEL -------------------------------------------------------
LOGO_PATH = "1.png" 
MODEL_NAME = "gemini-2.5-flash"

# --- 2. CONFIGURATIE & API ------------------------------------------------
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"].strip()
        genai.configure(api_key=api_key)
    else:
        # Fallback voor lokaal testen als secrets file ontbreekt (haal dit weg in productie)
        pass 
except Exception as e:
    st.error(f"Error: {e}")

# --- 3. KENNIS LADEN (PDF & DOCX) -----------------------------------------
@st.cache_resource(show_spinner=False)
def load_all_knowledge():
    combined_text = ""
    # Simpele check voor bestanden in huidige map
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

# --- 4. AI INSTRUCTIES ----------------------------------------------------
SYSTEM_PROMPT = f"""
ROL: Je bent een expert sportfysioloog van SportMetrics.

BRONMATERIAAL:
Je hebt toegang tot specifieke literatuur over trainingsleer.
Gebruik DEZE INFORMATIE als de absolute waarheid.

=== START LITERATUUR ===
{knowledge_base}
=== EINDE LITERATUUR ===

BELANGRIJKE REGELS:
1. SportMetrics doet GEEN lactaatmetingen (prikken), alleen ademgasanalyse.
2. Gebruik de principes (zoals Seiler zones) zoals beschreven in de geüploade literatuur.
3. Wees praktisch, enthousiast en gebruik bulletpoints.
4. Geen medisch advies.
5. Geef altijd een props aan de persoon voor de test en bedankt dat hij of zij dit bij SportMetrics heeft gedaan.
"""

try:
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SYSTEM_PROMPT,
    )
except:
    pass

# --- 5. INITIALIZE STATE --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
    intro = (
        "Hoi! Ik geef antwoord op basis van mijn AI-kennis en de best beschikbare literatuur over trainingsleer.\n\n"
        "Upload je testresultaten of stel direct een vraag!"
    )
    st.session_state.messages.append({"role": "assistant", "content": intro})

# Functie om input te verwerken
def submit_question():
    user_input = st.session_state.input_field
    if user_input:
        # Voeg user bericht toe
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Context ophalen
        extra_context = ""
        if "last_uploaded_text" in st.session_state:
            extra_context = f"\n\nHIER IS HET RAPPORT VAN DE KLANT:\n{st.session_state['last_uploaded_text']}\n\n"
            # We verwijderen het niet direct zodat context blijft hangen voor vervolgvragen, 
            # of je kan het hier wissen: del st.session_state["last_uploaded_text"]

        full_prompt = user_input + extra_context
        
        # AI Genereren
        try:
            response = model.generate_content(full_prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": "Sorry, ik kon even geen verbinding maken met het brein."})
        
        # Input veld leegmaken
        st.session_state.input_field = ""

# --- 6. LAYOUT OPBOUW -----------------------------------------------------

# A. HERO SECTION
with st.container():
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("<h1>SportMetrics Coach</h1>", unsafe_allow_html=True)
        st.markdown("<p>Geen poespas, alleen data → advies.</p>", unsafe_allow_html=True)
    with col2:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=150)
    st.markdown('</div>', unsafe_allow_html=True)

# B. UPLOAD & ANALYSE SECTION (Compact)
with st.container():
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    
    # We gebruiken kolommen om de knop NAAST de upload te krijgen
    # Col 1: Upload (Breed), Col 2: Knop (Smal)
    c1, c2 = st.columns([3, 1], gap="small")
    
    with c1:
        uploaded_file = st.file_uploader("Upload rapport", type=["pdf", "docx"], label_visibility="collapsed")
    
    with c2:
        # Een beetje witruimte om de knop verticaal te centreren met de uploadbox
        st.markdown("<div style='height: 4px'></div>", unsafe_allow_html=True)
        analyse_click = st.button("Analyseer", use_container_width=True)

    if uploaded_file is not None:
        try:
            client_pdf_text = ""
            if uploaded_file.name.lower().endswith(".pdf"):
                reader = pypdf.PdfReader(uploaded_file)
                for page in reader.pages:
                    client_pdf_text += page.extract_text() + "\n"
            elif uploaded_file.name.lower().endswith(".docx"):
                doc = docx.Document(uploaded_file)
                for para in doc.paragraphs:
                    client_pdf_text += para.text + "\n"
            
            st.session_state["last_uploaded_text"] = client_pdf_text
            st.toast("Rapport ingeladen! Klaar voor analyse.", icon="✅")
        except:
            st.error("Kon bestand niet lezen.")

    if analyse_click and "last_uploaded_text" in st.session_state:
        # Trigger een analyse prompt als men op de knop drukt
        st.session_state.input_field = "Analyseer mijn geüploade zones
