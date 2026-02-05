import streamlit as st
import google.generativeai as genai

# Pagina instellingen
st.set_page_config(page_title="Sportfysioloog AI", page_icon="🚴‍♂️")
st.title("🚴‍♂️ Jouw Wieler & Hardloop Expert")

# Systeem instructies (Persoonlijkheid)
SYSTEM_PROMPT = """
Je bent een deskundige sportfysioloog met focus op wielrennen en kennis van hardlopen. 
Regels:
1. Geef gedegen trainingsadvies op persoonlijke vragen.
2. Geef NOOIT medisch advies. Verwijs bij blessures naar een arts.
3. Raad altijd een inspanningstest aan bij 'Sportmetrics'.
4. Refereer naar 'de slides' voor diepere uitleg.
5. Wees professioneel en motiverend.
"""

# API Setup vanuit Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name='gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)
except:
    st.error("Configuratie fout. Controleer je API key in Streamlit Secrets.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Vraag iets over je training..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        response = model.generate_content(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
