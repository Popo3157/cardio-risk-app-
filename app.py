import streamlit as st
from groq import Groq
from fpdf import FPDF
import os

# --- SÉCURITÉ ET ACCÈS ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = None

SECRET_PASSWORD_MEDECIN = "Alliance2026"

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="L'Alliance Protectrice", page_icon="🛡️", layout="wide")

# INITIALISATION DU SESSION STATE
if 'cat_risque' not in st.session_state: st.session_state.cat_risque = None
if 'score_estime' not in st.session_state: st.session_state.score_estime = 0.0
if 'lettre_generee' not in st.session_state: st.session_state.lettre_generee = ""
if 'authenticated' not in st.session_state: st.session_state.authenticated = False

# 2. STYLE CSS
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] { background-color: #f4f7f9 !important; color: #333333 !important; }
    input, select, textarea, .stSelectbox, .stNumberInput { color: #333333 !important; background-color: #ffffff !important; }
    .stButton>button { background-color: #004d99 !important; color: white !important; border-radius: 8px; font-weight: bold; height: 3.5em; border: none; }
    [data-testid="stVerticalBlock"] > div { background-color: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- AUTHENTIFICATION ---
if not st.session_state.authenticated:
    st.markdown('<div style="text-align:center; padding:50px;"><h1>🛡️ Accès Sécurisé</h1></div>', unsafe_allow_html=True)
    pwd_input = st.text_input("Code d'accès", type="password")
    if st.button("Se connecter"):
        if pwd_input == SECRET_PASSWORD_MEDECIN:
            st.session_state.authenticated = True
            st.rerun()
        else: st.error("Code incorrect.")
    st.stop()

# 3. LOGO
if os.path.exists("logo.png"):
    c_l1, c_l2, c_l3 = st.columns([1, 2, 1])
    with c_l2: st.image("logo.png", use_container_width=True)

# 4. BARRE LATÉRALE
with st.sidebar:
    st.header("👨‍⚕️ Praticien")
    dr_nom = st.text_input("Nom du Docteur", value="Dr Pauline ROBERT")
    dr_spe = st.text_input("Spécialité", value="Cardiologie")
    dr_cab = st.text_input("Cabinet / Hôpital", value="Unité de Prévention Cardiovasculaire")
    if st.button("Se déconnecter"):
        st.session_state.authenticated = False
        st.rerun()

# 5. FORMULAIRE PATIENT
st.subheader("📋 Informations du Patient")
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        nom_p = st.text_input("Nom du Patient")
        age_p = st.number_input("Âge", min_value=18, max_value=100, value=55)
        sexe_p = st.radio("Sexe", ["Homme", "Femme"], horizontal=True)
    with c2:
        fumeur_p = st.radio("Tabagisme", ["Non", "Oui"], horizontal=True)
        systo_p = st.number_input("PAS (mmHg)", value=130)
        chol_p = st.number_input("Cholestérol non-HDL (mmol/L)", value=3.9, step=0.1)
    with c3:
        diabete_p = st.checkbox("Diabète")
        dfg_p = st.selectbox("Fonction rénale", ["Normal", "30-59 (Modéré)", "<30 (Sévère)"])
        atcd_p = st.checkbox("Antécédents (AVC, IDM)")

def calculer_score(atcd, dfg, systo):
    if atcd: return "TRÈS ÉLEVÉ (Prévention Secondaire)", 15.0
    if systo >= 180 or "<30" in dfg: return "TRÈS ÉLEVÉ", 12.0
    if "30-59" in dfg: return "ÉLEVÉ", 7.5
    return "MODÉRÉ", 3.5

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("📊 1. ÉVALUER LE PROFIL"):
        cat, val = calculer_score(atcd_p, dfg_p, systo_p)
        st.session_state.cat_risque = cat
        st.session_state.score_estime = val

if st.session_state.cat_risque:
    st.success(f"Risque : {st.session_state.cat_risque} ({st.session_state.score_estime}%)")

# 8. GÉNÉRATION DE LA LETTRE (CORRIGÉE)
with col_btn2:
    if st.button("📝 2. GÉNÉRER LE COURRIER"):
        if not GROQ_API_KEY: st.error("Clé API manquante dans les Secrets.")
        elif not nom_p: st.warning("Nom du patient requis.")
        else:
            try:
                client = Groq(api_key=GROQ_API_KEY)
                prompt = f"""Rédige une lettre de consultation médicale. 
                STRICTEMENT INTERDIT : Ne mets JAMAIS d'astérisques (*) ou de symboles Markdown.
                STYLE : Professionnel, médical, direct.
                CONTENU :
                - Objet : Stratification du risque cardiovasculaire (SCORE2).
                - Conclusion : Risque {st.session_state.cat_risque} à {st.session_state.score_estime}%.
                - Recommandations : Cible LDL-C, Sport (150min/sem), Diététique.
                - Fin : Mentionner 'Application développée par Jennyfer Vari, Neli Ilieva et Pauline Robert'."""
                
                completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                # On nettoie les résidus d'astérisques au cas où
                st.session_state.lettre_generee = completion.choices[0].message.content.replace('*', '')
            except Exception as e: st.error(f"Erreur : {e}")

if st.session_state.lettre_generee:
    st.info(st.session_state.lettre_generee)

# 9. PDF STYLE "CABINET MÉDICAL"
def create_pdf(text, dr, spe, cab, patient, age):
    pdf = FPDF()
    pdf.add_page()
    
    # EN-TÊTE CABINET (À GAUCHE)
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 77, 153)
    pdf.cell(0, 6, dr.upper(), ln=True)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 6, spe, ln=True)
    pdf.cell(0, 6, cab, ln=True)
    pdf.ln(10)
    
    # INFOS PATIENT (À DROITE)
    pdf.set_x(120)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Patient : {patient}", ln=True)
    pdf.set_x(120)
    pdf.cell(0, 8, f"Âge : {age} ans", ln=True)
    pdf.set_x(120)
    pdf.cell(0, 8, "Date : 06/05/2026", ln=True)
    pdf.ln(15)
    
    # CORPS DE LA LETTRE
    pdf.set_font("Arial", '', 11)
    # Nettoyage final des caractères non-compatibles
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=clean_text)
    
    # SIGNATURE
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, f"Signature et cachet du {dr} :", ln=True, align='R')
    
    return pdf.output(dest='S').encode('latin-1')

if st.session_state.lettre_generee:
    pdf_data = create_pdf(st.session_state.lettre_generee, dr_nom, dr_spe, dr_cab, nom_p, age_p)
    st.download_button("📥 TÉLÉCHARGER LE PDF PROFESSIONNEL", data=pdf_data, file_name=f"CR_{nom_p}.pdf", mime="application/pdf")
