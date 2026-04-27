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
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: #555;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #ddd;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# FONCTION GÉNÉRATION PDF
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 77, 153)
    pdf.cell(0, 10, "L'ALLIANCE PROTECTRICE - UNITE DE PREVENTION CARDIOVASCULAIRE", ln=True, align='L')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 5, "Evaluation du risque SCORE2 - Guidelines SFC/ESC", ln=True, align='L')
    pdf.ln(10)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=clean_text)
    
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 10, "Application creee par : Jennyfer Vari, Neli Ilieva et Pauline ROBERT", ln=True, align='L')
    return pdf.output(dest='S').encode('latin-1')

# 4. EN-TÊTE
st.markdown('<div class="header-box">', unsafe_allow_html=True)
st.title("🛡️ L'ALLIANCE PROTECTRICE")
st.subheader("DÉTECTION & PRÉVENTION CARDIAQUE")
st.markdown('</div>', unsafe_allow_html=True)

# 5. BARRE LATÉRALE
with st.sidebar:
    st.header("👨‍⚕️ Praticien Référent")
    dr_nom = st.text_input("Nom et Prénom", placeholder="Laisser vide pour signature manuelle")
    dr_spe = st.text_input("Spécialité")
    dr_cab = st.text_input("Service / Unité")
    st.divider()
    api_key_groq = st.text_input("Clé API Groq", type="password")

# 6. FORMULAIRE PATIENT
st.header("📋 Dossier Patient")
col1, col2, col3 = st.columns(3)
with col1:
    nom_patient = st.text_input("Nom du Patient")
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

# 7. CALCUL
def calculer_risque(age_p, score_p, atcd_p, dfg_p, systo_p):
    if atcd_p: return "TRES ELEVE (Prévention secondaire)"
    if systo_p >= 180 or dfg_p == "<30 mL/min": return "TRES ELEVE"
    if dfg_p == "30-59 mL/min": return "ELEVE"
    return "MODERE"

# 8. ACTIONS
if st.button("1. ÉVALUER LE PROFIL"):
    res = calculer_risque(age, 4.5, atcd_cv, insuffisance_renale, systolique)
    st.session_state.cat_risque = res
    st.success(f"Risque : {res}")

if st.button("2. GÉNÉRER LA LETTRE FORMELLE"):
    if not api_key_groq: st.error("Clé API manquante")
    else:
        try:
            client = Groq(api_key=api_key_groq)
            prompt = f"Rédige un compte-rendu hospitalier formel pour {nom_patient} ({age} ans). Risque: {st.session_state.cat_risque}. Inclure sport 150min, alimentation, arrêt tabac. Signé par: {dr_nom if dr_nom else 'Le praticien'}. Mentionner à la fin : Application créée par Jennyfer Vari, Neli Ilieva et Pauline ROBERT."
            completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            st.session_state.lettre_generee = completion.choices[0].message.content
            st.text_area("Aperçu", value=st.session_state.lettre_generee, height=300)
        except Exception as e: st.error(f"Erreur : {e}")

if st.session_state.lettre_generee:
    pdf_data = create_pdf(st.session_state.lettre_generee)
    st.download_button("📥 TÉLÉCHARGER LE PDF", data=pdf_data, file_name=f"CR_{nom_patient}.pdf", mime="application/pdf")

# 10. MENTION DES CRÉATEURS EN BAS DE LA PAGE (INTERFACE)
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.divider()
st.markdown("""
    <div style='text-align: center; color: #555; padding: 20px;'>
        <b>Application créée par :</b> Jennyfer Vari, Neli Ilieva et Pauline ROBERT
    </div>
    """, unsafe_allow_html=True)
