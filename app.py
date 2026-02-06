import streamlit as st
import google.generativeai as genai
import pypdf
import docx
import os

# Pagina instellingen
st.set_page_config(page_title="Sportfysioloog AI", page_icon="🚴‍♂️")
st.title("🚴‍♂️ Jouw Wieler & Hardloop Expert")

# --- 1. CONFIGURATIE & API ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"].strip()
        genai.configure(api_key=api_key)
    else:
        st.error("Geen API Key gevonden. Voeg deze toe aan secrets.toml")
        st.stop()
except Exception as e:
    st.error(f"Error bij configureren API: {e}")
    st.stop()

# --- 2. KENNIS LADEN (PDF & DOCX) ---
@st.cache_resource
def load_all_knowledge():
    """Zoekt automatisch naar alle PDF en DOCX bestanden en leest ze."""
    combined_text = ""
    # We kijken in de huidige map naar alle bestanden
    for filename in os.listdir("."):
        try:
            # Als het een PDF is
            if filename.lower().endswith(".pdf"):
                reader = pypdf.PdfReader(filename)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        combined_text += text + "\n"
            
            # Als het een Word bestand is
            elif filename.lower().endswith(".docx"):
                doc = docx.Document(filename)
                for para in doc.paragraphs:
                    combined_text += para.text + "\n"
                
        except Exception as e:
            print(f"Kon bestand {filename} niet lezen: {e}")

    return combined_text

# Hier laden we alles in (gebeurt onzichtbaar voor de klant)
knowledge_base = load_all_knowledge()

# --- 3. DE AI INSTRUCTIES ---
SYSTEM_PROMPT = f"""
ROL: Je bent een expert sportfysioloog van SportMetrics.

BRONMATERIAAL:
Je hebt toegang tot specifieke literatuur over trainingsleer (zie hieronder).
Gebruik DEZE INFORMATIE als de absolute waarheid.

=== START LITERATUUR ===
{knowledge_base}
=== EINDE LITERATUUR ===

BELANGRIJKE REGELS:
1. SportMetrics doet GEEN lactaatmetingen (prikken), alleen ademgasanalyse.
2. Gebruik de principes (zoals Seiler zones) zoals beschreven in de geüploade literatuur.
3. Wees praktisch, enthousiast en gebruik bulletpoints.
4. Geen medisch advies.
5. Geef altijd een props aan de persoon voor de test en bedank dat hij of zij dat bij SportMetrics heeft gedaan.
"""

# Model laden
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction=SYSTEM_PROMPT
    )
except Exception as e:
    st.error(f"Model fout: {e}")

# --- 4. CHAT INTERFACE ---

if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # Begroeting
    intro = "Hoi! Ik geef antwoord op basis van mijn AI-kennis en de best beschikbare literatuur over trainingsleer. \n\nUpload je testresult
