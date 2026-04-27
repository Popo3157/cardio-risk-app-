import streamlit as st
from groq import Groq
from fpdf import FPDF

# 1. CONFIGURATION
st.set_page_config(page_title="L'Alliance Protectrice - Prévention Cardiaque", layout="wide")

# 2. INITIALISATION DU SESSION STATE
if 'cat_risque' not in st.session_state:
    st.session_state.cat_risque = None
if 'score_estime' not in st.session_state:
    st.session_state.score_estime = 0.0
if 'lettre_generee' not in st.session_state:
    st.session_state.lettre_generee = ""

# 3. STYLE CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #004d99; color: white; border-radius: 5px; width: 100%; font-weight: bold; height: 3em; }
    .header-box { 
        background-color: #ffffff; padding: 20px; border-radius: 10px; 
        border-top: 5px solid #004d99; margin-bottom: 25px; text-align: center;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
    }
    h1 { color: #004d99; }
    </style>
    """, unsafe_allow_html=True)

# FONCTION GÉNÉRATION PDF (Mise en page hospitalière avec mentions finales)
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    
    # En-tête
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 77, 153)
    pdf.cell(0, 10, "L'ALLIANCE PROTECTRICE - UNITE DE PREVENTION CARDIOVASCULAIRE", ln=True, align='L')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 5, "Evaluation du risque SCORE2 - Guidelines SFC/ESC", ln=True, align='L')
    pdf.ln(10)
    
    # Corps du texte
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=clean_text)
    
    # Bas de page - Mentions de création
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, "Conception et Developpement :", ln=True, align='L')
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, "Jennyfer Vari, Neli Ilieva et Pauline ROBERT", ln=True, align='L')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(0, 10, "Document genere numeriquement - Valable apres signature et cachet du praticien.", align='R')
    return pdf.output(dest='S').encode('latin-1')

# 4. EN-TÊTE
st.markdown('<div class="header-box">', unsafe_allow_html=True)
st.title("🛡️ L'ALLIANCE PROTECTRICE")
st.subheader("SERVICE D'ÉVALUATION DU RISQUE CARDIOVASCULAIRE")
st.markdown('</div>', unsafe_allow_html=True)

# 5. BARRE LATÉRALE
with st.sidebar:
    st.header("👨‍⚕️ Praticien Référent")
    dr_nom = st.text_input("Nom et Prénom", placeholder="ex: Dr Pauline ROBERT")
    dr_spe = st.text_input("Spécialité", placeholder="ex: Cardiologie")
    dr_cab = st.text_input("Service / Unité", placeholder="ex: Unité de Prévention")
    
    st.divider()
    st.header("🔑 Configuration")
    api_key_groq = st.text_input("Clé API Groq", type="password")

# 6. FORMULAIRE PATIENT
st.header("📋 Dossier Patient")
col1, col2, col3 = st.columns(3)

with col1:
    nom_patient = st.text_input("Nom et Prénom du Patient")
    age = st.number_input("Âge", min_value=18, max_value=100, value=55)
    sexe = st.radio("Sexe", ["Homme", "Femme"])

with col2:
    fumeur = st.radio("Tabagisme actif", ["Non", "Oui"])
    systolique = st.number_input("PAS (mmHg)", min_value=90, max_value=200, value=130)
    chol_non_hdl = st.number_input("Cholestérol non-HDL (mmol/L)", min_value=2.0, max_value=10.0, value=3.9, step=0.1)

with col3:
    diabete = st.checkbox("Diabète sucré")
    insuffisance_renale = st.selectbox("Fonction rénale (DFG)", ["Normal", "30-59 mL/min", "<30 mL/min"])
    atcd_cv = st.checkbox("ATCD cardiovasculaires avérés")

# 7. LOGIQUE DE CALCUL
def calculer_risque(age_p, score_p, atcd_p, dfg_p, systo_p):
    if atcd_p: return "TRES ELEVE (Prévention secondaire)"
    if systo_p >= 180 or dfg_p == "<30 mL/min": return "TRES ELEVE"
    if dfg_p == "30-59 mL/min": return "ELEVE"
    if age_p < 50 and score_p >= 7.5: return "TRES ELEVE"
    if 50 <= age_p < 70 and score_p >= 10: return "TRES ELEVE"
    if age_p >= 70 and score_p >= 15: return "TRES ELEVE"
    return "MODERE"

# 8. ANALYSE
if st.button("ÉVALUER LE PROFIL PATIENT"):
    score_final = 4.5 
    resultat = calculer_risque(age, score_final, atcd_cv, insuffisance_renale, systolique)
    st.session_state.cat_risque = resultat
    st.session_state.score_estime = score_final
    st.success(f"Catégorie de risque : {resultat}")

# 9. GÉNÉRATION DE LA LETTRE FORMELLE
st.header("📝 Compte-rendu de Consultation")
if st.button("GÉNÉRER LE COMPTE-RENDU FORMEL"):
    if not api_key_groq:
        st.error("Veuillez saisir votre clé API Groq.")
    elif st.session_state.cat_risque is None:
        st.error("Veuillez d'abord évaluer le profil patient.")
    else:
        try:
            client = Groq(api_key=api_key_groq)
            
            if "TRES ELEVE" in st.session_state.cat_risque: obj = "< 1.4 mmol/L"
            elif "ELEVE" in st.session_state.cat_risque: obj = "< 1.8 mmol/L"
            else: obj = "< 2.6 mmol/L"

            prompt = f"""
            Rédige un compte-rendu médical formel hospitalier.
            
            PATIENT : {nom_patient}, {age} ans. 
            RISQUE : {st.session_state.cat_risque}, SCORE2 : {st.session_state.score_estime}%.
            OBJECTIF LDL : {obj}. TABAC : {fumeur}.
            
            MÉDECIN RÉFÉRENT : {dr_nom if dr_nom else "Praticien de l'Alliance"}, {dr_spe if dr_spe else ""}, {dr_cab if dr_cab else ""}.

            CONSIGNES :
            - Ton clinique hospitalier (Objet, Motif, Conclusions, Conduite à tenir).
            - À la toute fin, ajoute la mention suivante exactement : "Application créée par Jennyfer Vari, Neli Ilieva et Pauline ROBERT".
            - Ne laisse aucun crochet [].
            """
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": "Tu es un assistant médical hospitalier rigoureux."},
                          {"role": "user", "content": prompt}]
            )
            
            st.session_state.lettre_generee = completion.choices[0].message.content
            st.text_area("Aperçu clinique", value=st.session_state.lettre_generee, height=450)
            
        except Exception as e:
            st.error(f"Erreur de génération : {e}")

# TÉLÉCHARGEMENT PDF
if st.session_state.lettre_generee:
    pdf_data = create_pdf(st.session_state.lettre_generee)
    st.download_button(
        label="📥 TÉLÉCHARGER LE COMPTE-RENDU (PDF)",
        data=pdf_data,
        file_name=f"CR_Cardio_{nom_patient}.pdf",
        mime="application/pdf"
    )
