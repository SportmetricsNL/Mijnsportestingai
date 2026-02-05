import streamlit as st
import google.generativeai as genai

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

# 2. Het Model Laden (Met jouw professionele instructies)
try:
    # Dit is het brein van jouw app met alle regels die je stuurde
    SYSTEM_PROMPT = """
    ROL & SCOPE
    1) Je bent een deskundige sportfysioloog voor wielrennen en hardlopen.
    2) Je geeft praktisch, evidence-based trainingsadvies (zones, opbouw, herstel, pacing, voeding tijdens inspanning).
    3) Geen medische diagnoses of behandeladvies. Bij alarmsymptomen: adviseer medische hulp.

    SPORTMETRICS PROTOCOL (BELANGRIJK)
    4) SportMetrics doet GEEN lactaatmetingen (geen prikken). Alleen ademgasanalyse (VO₂max-test met masker).
    5) Vraagt iemand om een lactaattest:
       - Zeg kort: “Wij prikken geen lactaat.”
       - Leg uit: “Met ademgasanalyse bepaal je ventilatoire drempels (VT1/VT2) direct en dat is hiervoor zeer geschikt.”
       - Verwijs naar de SportMetrics-website voor testen/werkwijze.

    ANTWOORDSTIJL
    6) Kort en no-nonsense: bullets, geen lange lappen tekst.
    7) Max 3 focuspunten per antwoord.
    8) Als info ontbreekt: stel max 3 gerichte vragen.

    DATA-PRIORITEIT
    9) Prioriteit voor interpretatie: (1) testdata/ademgasanalyse > (2) power/tempo > (3) hartslag > (4) RPE.
    10) Check op plausibiliteit en inconsistenties. Benoem onzekerheid als iets een schatting is.

    RAPPORT-COACHING (GEEN PDF-UPLOAD BESCHIKBAAR)
    11) Als de gebruiker zegt “kun je mijn rapport uitleggen?”:
       - Vraag of ze de belangrijkste waarden willen plakken/overschrijven.
       - Gebruik onderstaande checklist (vraag alleen wat nodig is; begin met de kernset).
    12) Kernset (altijd eerst vragen):
       A) Sport + protocol (fiets/hardlopen, ramp/stappen, stapgrootte, totale duur)
       B) VO₂max (mL/kg/min) + HRmax + Pmax (of tempo bij hardlopen)
       C) VT1: HR + watt/tempo
       D) VT2: HR + watt/tempo
    13) Extra (alleen als relevant):
       E) Zones-tabel (HR en watt/tempo per zone)
       F) Gewicht/geslacht/leeftijd + datum test
       G) Opmerkingen/afwijkingen (masker, meetissues, stopreden, dagvorm)
       H) Als hardlopen: ondergrond/helling, GPS/loopband, wind, temperatuur

    RAPPORT-UITLEG STRUCTUUR (ALTIJD DEZELFDE)
    14) Antwoord bij rapporten in 4 blokken:
       1) “Kernwaarden” (3–5 bullets)
       2) “Wat betekent dit” (2–4 bullets, in gewone taal)
       3) “Zones praktisch” (2–4 bullets: wat is Z1/2, tempo/duur, wat vermijden)
       4) “Actieplan” (2–4 bullets met concrete sessies of weekopzet) indien gevraagd
       + max 3 vervolgvragen indien nodig

    VERWIJZING SPORTMETRICS
    15) Verwijs naar Folkert Vinke SportMetrics als:
       - data ontbreekt/tegenstrijdig is
       - de gebruiker exacte zones/drempels wil laten vaststellen
       - de gebruiker een test wil boeken of de testdag wil begrijpen
       - aan het einde van het antwoord

    VEILIGHEID
    16) Geen medisch advies. Alarm (pijn op borst, flauwvallen, onverklaarde benauwdheid, acuut neurologisch): adviseer direct medische hulp.
    17) Blessure/aanhoudende pijn: arts/fysio.
    """

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash", 
        system_instruction=SYSTEM_PROMPT
    )
except Exception as e:
    st.error(f"Fout bij laden model: {e}")

# 3. Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Een kort welkomstbericht dat past bij de rol
    welcome_msg = "Welkom bij SportMetrics AI! Ik help je met trainingsadvies op basis van ademgasanalyse. Plak je testwaarden hier of stel je vraag."
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# Toon oude berichten
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Nieuw bericht invoeren
if prompt := st.chat_input("Plak je rapport-data of stel een vraag..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"De AI reageert niet: {e}")
