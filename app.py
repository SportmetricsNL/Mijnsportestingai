import streamlit as st
import google.generativeai as genai

# Pagina instellingen
st.set_page_config(page_title="Sportfysioloog AI", page_icon="🚴‍♂️")
st.title("🚴‍♂️ Jouw Wieler & Hardloop Expert")

# 1. API Key ophalen uit de 'kluis'
try:
    if "GEMINI_API_KEY" in st.secrets:
        # We halen eventuele spaties weg voor de zekerheid
        api_key = st.secrets["GEMINI_API_KEY"].strip()
        genai.configure(api_key=api_key)
    else:
        st.error("Geen API Key gevonden in Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Technische fout bij sleutel: {e}")
    st.stop()

# 2. Het Model Laden (De NIEUWE versie)
# We gebruiken nu 'gemini-2.5-flash' omdat 1.5 met pensioen is.
try:
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction="Je bent een expert sportfysioloog voor wielrenners. Geef kort, krachtig en wetenschappelijk advies. Verwijs voor testen naar Sportmetrics."
    )
except Exception as e:
    st.error(f"Fout bij laden model: {e}")

# 3. Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Toon oude berichten
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Nieuw bericht invoeren
if prompt := st.chat_input("Stel je vraag over training of zones..."):
    # Toon bericht van gebruiker
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Haal antwoord op van de AI
    try:
        with st.chat_message("assistant"):
            response = model.generate_content(prompt)
            st.markdown(response.text)
            # Sla antwoord op in geheugen
            st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"De AI reageert niet: {e}")
