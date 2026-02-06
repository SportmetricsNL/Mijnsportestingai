import os
import time
import streamlit as st
import google.generativeai as genai
import pypdf
import docx

# --- 0. PAGE CONFIG -------------------------------------------------------
st.set_page_config(
    page_title="SportMetrics Coach",
    page_icon="🚴‍♂️",
    layout="wide",
)

# --- 1. VISUELE STYLING (CSS) ---------------------------------------------
st.markdown(
    """
    <style>
    /* --- ACHTERGROND GRADIENT (Blauw -> Grijs -> Zwart) --- */
    .stApp {
        background: linear-gradient(180deg, #2A75B7 0%, #707981 50%, #0E0E0E 100%);
        background-attachment: fixed; /* Zorgt dat gradient mooi blijft staan bij scrollen */
    }

    /* --- ALGEMENE TEKST --- */
    h1, h2, h3, p, label, .stMarkdown {
        color: #FFFFFF !important;
        font-family: "Inter", sans-serif;
    }
    
    /* Titel styling */
    h1 {
        font-weight: 800;
        margin-bottom: 0px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    .subtitle {
        color: #E0E0E0 !important;
        margin-bottom: 30px;
        font-size: 16px;
    }

    /* --- UPLOAD CONTAINER (WIT & COMPACT) --- */
    /* Dit forceert de upload box om kleiner (half zo hoog) te zijn */
    div[data-testid="stFileUploader"] section {
        background-color: #FFFFFF;
        padding: 10px !important; /* Minder padding = minder hoog */
        min-height: 0px !important;
    }
    
    div[data-testid="stFileDropzone"] {
        background-color: #FFFFFF;
        border: none;
        color: #000000 !important;
        min-height: 60px !important; /* Geforceerde hoogte */
        height: 60px;
        align-items: center;
    }
    
    /* Tekst in de uploader moet ZWART zijn op de witte achtergrond */
    div[data-testid="stFileDropzone"] div, 
    div[data-testid="stFileDropzone"] span,
    div[data-testid="stFileDropzone"] small {
        color: #333333 !important;
    }
    
    /* Icoon kleur in uploader */
    div[data-testid="stFileDropzone"] svg {
        fill: #2A75B7 !important;
    }

    /* Verberg de standaard 'Limit 200MB' tekst als het te druk is */
    .stFileUploader small { display: none; }

    /* --- KNOPPEN (ZWART) --- */
    .stButton button {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border: 1px solid #333;
        border-radius: 8px;
        height: 60px; /* Even hoog als de upload box */
        font-weight: 600;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #333333 !important;
        border-color: #FFFFFF;
    }

    /* --- INPUT VELD (WIT) --- */
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 8px;
        border: none;
        padding: 12px;
    }
