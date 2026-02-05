import streamlit as st
import google.generativeai as genai

# Pagina instellingen
st.set_page_config(page_title="Sportfysioloog AI", page_icon="🚴‍♂️")
st.title("🚴‍♂️ Jouw Wieler & Hardloop Expert")

# 1. API Key ophalen
try:
    # We halen de sleutel op. De .strip() zorgt dat spaties geen probleem meer zijn.
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"].strip()
        genai.configure(api_key=api_key)
    else:
        st.error("De API Key ontbreekt in de Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Er ging iets mis met de sleutel: {e}")
    st.stop()

# 2. Het Model Laden (De CORRECTE naam)
# We gebruiken 'gemini-1.5-flash' zonder 'models/' ervoor.
try:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash", 
        system_instruction="Je bent een expert sportfysioloog voor wielrenners. Geef kort, krachtig en wetenschappelijk advies. Verwijs voor testen naar Sportmetrics."
    )
except Exception as e:
    st.error(f"Model fout: {e}")

# 3. Chatvenster
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Stel je vraag..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Fout tijdens het genereren: {e}")
        # Fallback tip als 1.5-flash echt niet bestaat in jouw regio:
        st.info("Als dit blijft gebeuren, probeer dan 'gemini-pro' als modelnaam in de code.")