import streamlit as st
from groq import Groq
from fpdf import FPDF
from PIL import Image
import os

# --- SÉCURITÉ ET CLÉS ---
GROQ_API_KEY = "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"
# Mot de passe que le médecin devra saisir pour protéger la clé API 
SECRET_PASSWORD_MEDECIN = "Alliance2026"

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="L'Alliance Protectrice - Prévention Cardiaque", 
    page_icon="🛡️",
    layout="wide"
)

# INITIALISATION DU SESSION STATE
if 'cat_risque' not in st.session_state:
    st.session_state.cat_risque = None
if 'score_estime' not in st.session_state:
    st.session_state.score_estime = 0.0
if 'lettre_generee' not in st.session_state:
    st.session_state.lettre_generee = ""
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 2. STYLE CSS AMÉLIORÉ (Correction pour Apple/Safari)
st.markdown("""
    <style>
    /* Correction pour Safari : Forcer les couleurs de texte */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #f4f7f9 !important;
        color: #333333 !important;
    }
    
    /* Forcer la visibilité des textes dans les inputs et selects */
    input, select, textarea, .stSelectbox, .stNumberInput {
        color: #333333 !important;
        background-color: #ffffff !important;
    }

    /* Style des boutons */
    .stButton>button {
        background-color: #004d99 !important;
        color: white !important;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
        height: 3.5em;
        border: none;
    }
    
    /* Cartes blanches */
    [data-testid="stVerticalBlock"] > div {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        color: #333333 !important;
    }
    
    .footer-text {
        text-align: center; color: #666; padding: 20px; font-size: 14px;
        border-top: 1px solid #ddd; margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SYSTÈME D'AUTHENTIFICATION ---
if not st.session_state.authenticated:
    st.markdown('<div style="text-align:center; padding:50px;"><h1>🛡️ Accès Sécurisé</h1></div>', unsafe_allow_html=True)
    pwd_input = st.text_input("Entrez le code d'accès de l'Alliance Protectrice", type="password")
    if st.button("Se connecter"):
        if pwd_input == SECRET_PASSWORD_MEDECIN:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Code incorrect. Veuillez contacter l'administration.")
    st.stop() # Arrête le script ici tant que non authentifié

# --- SI AUTHENTIFIÉ, LE RESTE DU PROGRAMME S'EXÉCUTE ---

# 3. LOGO ET EN-TÊTE
def load_logo():
    if os.path.exists("logo.png"):
        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
        with col_l2:
            st.image("logo.png", use_container_width=True)
    else:
        st.markdown('<div style="text-align:center;"><h1>🛡️ L\'ALLIANCE PROTECTRICE</h1></div>', unsafe_allow_html=True)

load_logo()

# 4. BARRE LATÉRALE
with st.sidebar:
    st.header("👨‍⚕️ Praticien Référent")
    dr_nom = st.text_input("Nom du Docteur", placeholder="ex: Dr Pauline ROBERT")
    dr_spe = st.text_input("Spécialité", placeholder="ex: Cardiologie")
    dr_cab = st.text_input("Nom du Cabinet / Hôpital", placeholder="ex: Unité de Prévention")
    st.divider()
    if st.button("Se déconnecter"):
        st.session_state.authenticated = False
        st.rerun()

# 5. FORMULAIRE PATIENT
st.subheader("📋 Informations du Patient")
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        nom_p = st.text_input("Identité du Patient", placeholder="Nom et Prénom")
        age_p = st.number_input("Âge", min_value=18, max_value=100, value=55)
        sexe_p = st.radio("Sexe", ["Homme", "Femme"], horizontal=True)
    with c2:
        fumeur_p = st.radio("Tabagisme actif", ["Non", "Oui"], horizontal=True)
        systo_p = st.number_input("PAS (mmHg)", min_value=90, max_value=200, value=130)
        chol_p = st.number_input("Cholestérol non-HDL (mmol/L)", min_value=2.0, max_value=10.0, value=3.9, step=0.1)
    with c3:
        diabete_p = st.checkbox("Diabète sucré")
        dfg_p = st.selectbox("Fonction rénale (DFG)", ["Normal", "30-59 mL/min (Modéré)", "<30 mL/min (Sévère)"])
        atcd_p = st.checkbox("ATCD cardiovasculaires (AVC, IDM)")

# 6. LOGIQUE DE CALCUL
def calculer_score(atcd, dfg, systo):
    if atcd: return "TRÈS ÉLEVÉ (Secondaire)", 15.0
    if systo >= 180 or "<30" in dfg: return "TRÈS ÉLEVÉ", 12.0
    if "30-59" in dfg: return "ÉLEVÉ", 7.5
    return "MODÉRÉ", 3.5

# 7. ACTIONS
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("📊 1. ÉVALUER LE PROFIL"):
        cat, val = calculer_score(atcd_p, dfg_p, systo_p)
        st.session_state.cat_risque = cat
        st.session_state.score_estime = val
        st.toast("Calcul effectué !")

if st.session_state.cat_risque:
    st.success(f"**Analyse :** Risque **{st.session_state.cat_risque}** (Score : {st.session_state.score_estime}%)")

# 8. GÉNÉRATION DE LA LETTRE IA (SYNTHÉTIQUE)
with col_btn2:
    if st.button("📝 2. GÉNÉRER LA SYNTHÈSE"):
        if not dr_nom or not nom_p:
            st.warning("Veuillez remplir les noms du médecin et du patient.")
        else:
            try:
                client = Groq(api_key=GROQ_API_KEY)
                prompt = f"""
                Rédige un compte-rendu médical hospitalier TRÈS SYNTHÉTIQUE.
                PAS DE GRAS, PAS D'ÉTOILES, PAS DE HASHTAGS.
                
                EN-TÊTE :
                MÉDECIN : {dr_nom}, {dr_spe} ({dr_cab})
                PATIENT : {nom_p}, {age_p} ans

                DONNÉES :
                Risque ESC : {st.session_state.cat_risque} (Score SCORE2 : {st.session_state.score_estime}%)
                Tabac : {fumeur_p}. PAS : {systo_p} mmHg.

                CONTENU :
                1. Objet : Stratification du risque CV.
                2. Recommandations : Cible LDL-C, Sport (150min/sem), Régime, Tabac.
                
                Fin : Application créée par Jennyfer Vari, Neli Ilieva et Pauline Robert.
                """
                completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                st.session_state.lettre_generee = completion.choices[0].message.content
            except Exception as e:
                st.error(f"Erreur IA : {e}")

if st.session_state.lettre_generee:
    st.info(st.session_state.lettre_generee)

# 9. PDF
def create_pdf(text, dr, patient):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 77, 153)
    pdf.cell(0, 10, "L'ALLIANCE PROTECTRICE", ln=True, align='C')
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=clean_text)
    pdf.ln(10)
    pdf.cell(0, 10, f"Cachet et signature de {dr} :", ln=True)
    return pdf.output(dest='S').encode('latin-1')

if st.session_state.lettre_generee:
    pdf_data = create_pdf(st.session_state.lettre_generee, dr_nom, nom_p)
    st.download_button("📥 TÉLÉCHARGER LE PDF", data=pdf_data, file_name=f"CR_{nom_p}.pdf", mime="application/pdf")

# 10. FOOTER
st.markdown("""
    <div class="footer-text">
        Projet L'Alliance Protectrice | Créé par Jennyfer Vari, Neli Ilieva et Pauline Robert | © 2026
    </div>
    """, unsafe_allow_html=True)
