import streamlit as st
import google.generativeai as genai
import pypdf

# Pagina instellingen
st.set_page_config(page_title="Sportfysioloog AI", page_icon="🚴‍♂️")
st.title("🚴‍♂️ Jouw Wieler & Hardloop Expert")

# 1. API Key ophalen
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"].strip()
        genai.configure(api_key=api_key)
    else:
        st.error("Geen API Key gevonden in Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Technische fout bij sleutel: {e}")
    st.stop()

# 2. Het Model Laden
try:
    SYSTEM_PROMPT = """
    ROL: Je bent een behulpzame sportfysioloog van SportMetrics.
    DOEL: Geef DIRECT praktisch advies.
    
    BELANGRIJKE REGELS:
    1. GEEN kruisverhoor. Als data ontbreekt (bv protocol details), doe een aanname (schatting) en zeg dat erbij. Geef ALTIJD antwoord.
    2. SportMetrics doet GEEN lactaatmetingen, alleen ademgasanalyse. Leg dit alleen uit als ernaar gevraagd wordt.
    3. RAPPORTEN: Als iemand een PDF uploadt of data plakt, haal daar de kernwaarden uit (VO2max, Drempels, Zones).
    4. STIJL: Enthousiast, kort, bulletpoints. Geen medisch jargon zonder uitleg.
    5. DATA INTERPRETATIE:
       - VT1 / Aerobe drempel = Zone 2 bovengrens (duurtraining).
       - VT2 / Anaerobe drempel = Omslagpunt (Zone 4/5 grens).
    """

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction=SYSTEM_PROMPT
    )
except Exception as e:
    st.error(f"Fout bij laden model: {e}")

# 3. Chat Interface & PDF Upload
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Hoi! Upload je SportMetrics rapport (PDF) of stel je vraag, dan kijken we naar je zones!"})

# PDF Uploader
with st.sidebar:
    st.header("📄 Upload je Rapport")
    uploaded_file = st.file_uploader("Sleep je PDF hierheen", type="pdf")
    
    pdf_text = ""
    if uploaded_file is not None:
        try:
            reader = pypdf.PdfReader(uploaded_file)
            for page in reader.pages:
                pdf_text += page.extract_text() + "\n"
            st.success("Rapport succesvol ingelezen! De AI weet nu je waardes.")
        except Exception as e:
            st.error(f"Kon PDF niet lezen: {e}")

# Toon oude berichten
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Nieuw bericht invoeren
prompt = st.chat_input("Stel je vraag of zeg 'Analyseer mijn rapport'...")

if prompt:
    # We voegen de PDF tekst onzichtbaar toe aan het bericht als die er is
    full_prompt = prompt
    if pdf_text:
        full_prompt = f"Hier is de data uit mijn PDF rapport:\n{pdf_text}\n\nGebruikersvraag: {prompt}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"De AI reageert niet: {e}")
