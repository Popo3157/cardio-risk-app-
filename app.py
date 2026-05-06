import streamlit as st
from groq import Groq
from fpdf import FPDF
from PIL import Image
import os

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

# 2. STYLE CSS AMÉLIORÉ
st.markdown("""
    <style>
    /* Fond de page gris très clair */
    .stApp { background-color: #f4f7f9; }
    
    /* Style des boutons */
    .stButton>button {
        background-color: #004d99;
        color: white;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
        height: 3.5em;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #003366;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Cartes blanches pour les formulaires */
    .css-1r6p78m, .stVerticalBlock {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Header Box */
    .header-box {
        text-align: center;
        padding: 10px;
        margin-bottom: 20px;
    }
    
    /* Footer */
    .footer-text {
        text-align: center;
        color: #888;
        padding: 30px;
        font-size: 13px;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGO ET EN-TÊTE
def load_logo():
    if os.path.exists("logo.png"):
        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
        with col_l2:
            st.image("logo.png", use_container_width=True)
    else:
        st.markdown('<div class="header-box"><h1>🛡️ L\'ALLIANCE PROTECTRICE</h1></div>', unsafe_allow_html=True)

load_logo()

# 4. BARRE LATÉRALE
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.header("👨‍⚕️ Praticien Référent")
    dr_nom = st.text_input("Nom du Docteur", placeholder="ex: Dr Pauline ROBERT")
    dr_spe = st.text_input("Spécialité", placeholder="ex: Cardiologie")
    dr_cab = st.text_input("Nom du Cabinet / Hôpital", placeholder="ex: Unité de Prévention")
    st.divider()
    api_key_groq = st.text_input("Clé API Groq", type="password")
    st.info("Cette application utilise l'IA pour synthétiser les recommandations basées sur le score SCORE2.")

# 5. FORMULAIRE PATIENT (Layout en colonnes)
st.subheader("📋 Informations du Patient")
with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        nom_p = st.text_input("Identité du Patient", placeholder="Nom et Prénom")
        age_p = st.number_input("Âge", min_value=18, max_value=100, value=55)
        sexe_p = st.radio("Sexe", ["Homme", "Femme"], horizontal=True)
    with c2:
        fumeur_p = st.radio("Tabagisme actif", ["Non", "Oui"], horizontal=True)
        systo_p = st.number_input("PAS (mmHg)", min_value=90, max_value=200, value=130, help="Pression Artérielle Systolique")
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

# 7. ACTIONS & RÉSULTATS
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("📊 1. ÉVALUER LE PROFIL"):
        cat, val = calculer_score(atcd_p, dfg_p, systo_p)
        st.session_state.cat_risque = cat
        st.session_state.score_estime = val
        st.toast("Calcul effectué avec succès !")

if st.session_state.cat_risque:
    st.success(f"**Analyse :** Risque **{st.session_state.cat_risque}** (Score estimé : {st.session_state.score_estime}%)")

# 8. GÉNÉRATION DE LA LETTRE IA
with col_btn2:
    if st.button("📝 2. GÉNÉRER LA SYNTHÈSE MÉDICALE"):
        if not api_key_groq:
            st.error("Veuillez saisir votre clé API Groq.")
        elif not dr_nom or not nom_p:
            st.warning("Veuillez remplir les noms du médecin et du patient.")
        else:
            try:
                client = Groq(api_key=api_key_groq)
                prompt = f"""
                Rédige un compte-rendu médical hospitalier SYNTHÉTIQUE.
                INTERDICTION : Pas d'étoiles (*), pas de hashtags (#), pas de gras Markdown.
                
                EN-TÊTE À INCLURE EN HAUT DU TEXTE :
                MÉDECIN : {dr_nom}, {dr_spe} ({dr_cab})
                PATIENT : {nom_p}, {age_p} ans
                DATE : Mai 2026

                DONNÉES CLINIQUES :
                - Risque ESC : {st.session_state.cat_risque}
                - Score SCORE2 : {st.session_state.score_estime}%
                - Tabagisme : {fumeur_p}
                - Tension : {systo_p} mmHg

                CONTENU REQUIS (Très synthétique) :
                1. Objet : Stratification du risque cardiovasculaire.
                2. Synthèse : Interprétation courte du score SCORE2.
                3. Recommandations : Cible LDL-C, sport (150min/sem), diététique, tabac.
                
                Mention de fin obligatoire : Application créée par Jennyfer Vari, Neli Ilieva et Pauline Robert.
                """
                completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
                st.session_state.lettre_generee = completion.choices[0].message.content
            except Exception as e:
                st.error(f"Erreur Groq : {e}")

if st.session_state.lettre_generee:
    st.markdown("### 📄 Aperçu du Compte-rendu")
    st.info(st.session_state.lettre_generee)

# 9. GÉNÉRATION PDF & TÉLÉCHARGEMENT
def create_pdf(text, dr, patient):
    pdf = FPDF()
    pdf.add_page()
    # En-tête bleu Alliance
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 77, 153)
    pdf.cell(0, 10, "L'ALLIANCE PROTECTRICE", ln=True, align='C')
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, "DÉTECTION & PRÉVENTION CARDIAQUE", ln=True, align='C')
    pdf.ln(10)
    
    # Corps du texte
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=clean_text)
    
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, f"Fait le 06/05/2026. Cachet et signature de {dr} :", ln=True, align='L')
    return pdf.output(dest='S').encode('latin-1')

if st.session_state.lettre_generee:
    pdf_data = create_pdf(st.session_state.lettre_generee, dr_nom, nom_p)
    st.download_button(
        "📥 TÉLÉCHARGER LE COMPTE-RENDU (PDF)", 
        data=pdf_data, 
        file_name=f"CR_Alliance_{nom_p}.pdf", 
        mime="application/pdf"
    )

# 10. FOOTER
st.markdown(f"""
    <div class="footer-text">
        Projet L'Alliance Protectrice<br>
        Développé par Jennyfer Vari, Neli Ilieva et Pauline Robert<br>
        © 2026 - Prévention Cardiaque
    </div>
    """, unsafe_allow_html=True)
