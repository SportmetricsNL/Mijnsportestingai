import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Sportfysioloog AI", page_icon="🚴‍♂️")
st.title("🚴‍♂️ Jouw Wieler & Hardloop Expert")

# 1. API Key Check
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"].strip()
        genai.configure(api_key=api_key)
    else:
        st.error("Geen API sleutel gevonden.")
        st.stop()
except Exception as e:
    st.error(f"Fout: {e}")

# 2. Model Laden (We gebruiken 'gemini-pro', die werkt altijd)
try:
    model = genai.GenerativeModel(
        model_name="gemini-pro", 
        system_instruction="Je bent een sportfysioloog. Geef kort en concreet advies."
    )
except Exception as e:
    st.error(f"Model fout: {e}")

# 3. Chat
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
        st.error(f"Er ging iets mis: {e}")