import streamlit as st
from groq import Groq
from fpdf import FPDF

# 1. CONFIGURATION
st.set_page_config(page_title="L'Alliance Protectrice - Prévention Cardiaque", layout="wide")

# 2. INITIALISATION DU SESSION STATE
if 'cat_risque' not in st.session_state:
    st.session_state.cat_risque = None
if 'lettre_generee' not in st.session_state:
    st.session_state.lettre_generee = ""

# 3. STYLE CSS (Identité hospitalière + Footer)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { background-color: #004d99; color: white; border-radius: 5px; width: 100%; font-weight: bold; height: 3em; }
    .header-box { 
        background-color: #ffffff; padding: 20px; border-radius: 10px; 
        border-top: 5px solid #004d99; margin-bottom: 25px; text-align: center;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
    }
    .footer-text {
        text-align: center;
        color: #666;
        padding: 20px;
        font-size: 14px;
        border-top: 1px solid #ddd;
        margin-top: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# FONCTION GÉNÉRATION PDF
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    
    # En-tête Unité Hospitalière
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 77, 153)
    pdf.cell(0, 10, "L'ALLIANCE PROTECTRICE - UNITE DE PREVENTION CARDIOVASCULAIRE", ln=True, align='L')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 5, "Evaluation SCORE2 - Guidelines SFC/ESC", ln=True, align='L')
    pdf.ln(10)
    
    # Corps du texte
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=clean_text)
    
    # Espace Signature
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "Cachet et signature du praticien :", ln=True, align='L')
    
    return pdf.output(dest='S').encode('latin-1')

# 4. EN-TÊTE
st.markdown('<div class="header-box">', unsafe_allow_html=True)
st.title("🛡️ L'ALLIANCE PROTECTRICE")
st.subheader("DÉTECTION & PRÉVENTION CARDIAQUE")
st.markdown('</div>', unsafe_allow_html=True)

# 5. BARRE LATÉRALE
with st.sidebar:
    st.header("👨‍⚕️ Praticien Référent")
    dr_nom = st.text_input("Nom et Prénom", placeholder="ex: Dr Pauline ROBERT")
    dr_spe = st.text_input("Spécialité", placeholder="ex: Cardiologie")
    dr_cab = st.text_input("Service", placeholder="ex: Unité de Prévention")
    
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
    fumeur = st.radio("Tabagisme", ["Non", "Oui"])
    systolique = st.number_input("PAS (mmHg)", min_value=90, max_value=200, value=130)
    chol_non_hdl = st.number_input("Cholestérol non-HDL (mmol/L)", min_value=2.0, max_value=10.0, value=3.9, step=0.1)

with col3:
    diabete = st.checkbox("Diabète")
    insuffisance_renale = st.selectbox("Fonction rénale (DFG)", ["Normal", "30-59 mL/min", "<30 mL/min"])
    atcd_cv = st.checkbox("ATCD cardiovasculaires")

# 7. CALCUL RAPIDE
def calculer_risque(atcd, dfg, systo):
    if atcd: return "TRES ELEVE (Secondaire)"
    if systo >= 180 or dfg == "<30 mL/min": return "TRES ELEVE"
    if dfg == "30-59 mL/min": return "ELEVE"
    return "MODERE"

# 8. ACTIONS
if st.button("1. ÉVALUER LE RISQUE"):
    res = calculer_risque(atcd_cv, insuffisance_renale, systolique)
    st.session_state.cat_risque = res
    st.success(f"Risque identifié : {res}")

if st.button("2. GÉNÉRER LA LETTRE SYNTHÉTIQUE"):
    if not api_key_groq:
        st.error("Clé API manquante.")
    elif st.session_state.cat_risque is None:
        st.error("Veuillez d'abord évaluer le risque.")
    else:
        try:
            client = Groq(api_key=api_key_groq)
            
            prompt = f"""
            Rédige un compte-rendu médical SYNTHÉTIQUE et FORMEL (style hôpital).
            
            PATIENT : {nom_patient}, {age} ans.
            CONSTAT : Risque {st.session_state.cat_risque}. Tabac: {fumeur}.
            
            STRUCTURE :
            - Objet : Bilan de prévention cardiovasculaire.
            - Synthèse clinique : Rappel bref du risque et des objectifs (LDL-C).
            - Recommandations : Sport, alimentation, tabac.
            - Signature : {dr_nom if dr_nom else "Le praticien"}, {dr_spe if dr_spe else ""}.
            
            CONSIGNES :
            - Sois direct et clinique.
            - NE METS AUCUNE ADRESSE.
            - NE LAISSE AUCUN CROCHET [].
            - Termine par la mention exacte : "Application créée par Jennyfer Vari, Neli Ilieva et Pauline ROBERT".
            """
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}]
            )
            
            st.session_state.lettre_generee = completion.choices[0].message.content
            st.text_area("Aperçu de la lettre", value=st.session_state.lettre_generee, height=350)
            
        except Exception as e:
            st.error(f"Erreur : {e}")

# TÉLÉCHARGEMENT PDF
if st.session_state.lettre_generee:
    pdf_data = create_pdf(st.session_state.lettre_generee)
    st.download_button(
        label="📥 TÉLÉCHARGER LE COMPTE-RENDU (PDF)",
        data=pdf_data,
        file_name=f"CR_{nom_patient}.pdf",
        mime="application/pdf"
    )

# 10. MENTION DES CRÉATEURS EN BAS DE PAGE (INTERFACE)
st.markdown("""
    <div class="footer-text">
        <b>Application créée par :</b> Jennyfer Vari, Neli Ilieva et Pauline ROBERT
    </div>
    """, unsafe_allow_html=True)
