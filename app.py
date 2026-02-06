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
    
    # We splitsen de tekst in twee delen om de foutmelding te voorkomen
    deel1 = "Hoi! Ik geef antwoord op basis van mijn AI-kennis en de best beschikbare literatuur over trainingsleer."
    deel2 = "\n\nUpload je testresultaten of stel direct een vraag!"
    intro = deel1 + deel2
    
    st.session_state.messages.append({"role": "assistant", "content": intro})

# -- MOBIELVRIENDELIJKE UPLOAD KNOP VOOR KLANTEN --
with st.expander("📄 Klik hier om een PDF Rapport te uploaden", expanded=False):
    uploaded_file = st.file_uploader("Kies je testresultaten", type="pdf", key="mobile_uploader")
    
    if uploaded_file is not None:
        try:
            reader = pypdf.PdfReader(uploaded_file)
            client_pdf_text = ""
            for page in reader.pages:
                client_pdf_text += page.extract_text() + "\n"
            
            st.session_state['last_uploaded_text'] = client_pdf_text
            st.success("✅ Rapport ontvangen! Typ hieronder je vraag.")
        except Exception as e:
            st.error(f"Fout bij lezen rapport: {e}")

# Toon geschiedenis
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input veld
prompt = st.chat_input("Stel je vraag of zeg 'Maak mijn zones'...")

if prompt:
    extra_context = ""
    # Kijk of er net een bestand is geüpload door de klant
    if 'last_uploaded_text' in st.session_state:
        extra_context = f"\n\nHIER IS HET RAPPORT VAN DE KLANT:\n{st.session_state['last_uploaded_text']}\n\n"
        # We verwijderen het uit de sessie zodat het niet bij elke volgende vraag opnieuw wordt meegestuurd als 'nieuw'
        del st.session_state['last_uploaded_text']

    full_prompt_for_ai = prompt + extra_context

    # Gebruiker bericht toevoegen aan sessie en scherm
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            # 1. ANIMATIE: Fietsjes die van links naar rechts bewegen
            loading_placeholder = st.empty()
            loading_placeholder.markdown("""
            <div style="width: 100%; overflow: hidden; padding: 10px 0;">
                <div style="display: inline-block; white-space: nowrap; animation: moveRight 3s linear infinite;">
                    🚴‍♂️ 💨 🚴‍♂️ 💨 🚴‍♂️
                </div>
            </div>
            <style>
                @keyframes moveRight {
                    0% { transform: translateX(-20%); }
                    100% { transform: translateX(120%); }
                }
            </style>
            """, unsafe_allow_html=True)

            # Antwoord genereren
            response = model.generate_content(full_prompt_for_ai)
            
            # Animatie weghalen (leegmaken)
            loading_placeholder.empty()

            # 2. DISCLAIMER TOEVOEGEN
            final_text = response.text + "\n\n---\n*Disclaimer: Dit is geen medisch advies.*"
            
            # Antwoord tonen
            st.markdown(final_text)
            
            # Opslaan in geschiedenis
            st.session_state.messages.append({"role": "assistant", "content": final_text})
            
    except Exception as e:
        st.error(f"De AI reageert niet of er is een fout opgetreden: {e}")
