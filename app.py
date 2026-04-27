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

# 3. STYLE CSS (Identité hospitalière et Footer)
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
        text-align: center; color: #666; padding: 20px; font-size: 14px;
        border-top: 1px solid #ddd; margin-top: 50px;
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
    # Encodage sécurisé pour le PDF
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=clean_text)
    
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
st.header("📋 Paramètres Cliniques")
col1, col2, col3 = st.columns(3)
with col1:
    nom_p = st.text_input("Nom du Patient")
    age_p = st.number_input("Âge", min_value=18, max_value=100, value=55)
    sexe_p = st.radio("Sexe", ["Homme", "Femme"])
with col2:
    fumeur_p = st.radio("Tabagisme", ["Non", "Oui"])
    systo_p = st.number_input("PAS (mmHg)", min_value=90, max_value=200, value=130)
    chol_p = st.number_input("Cholestérol non-HDL (mmol/L)", min_value=2.0, max_value=10.0, value=3.9, step=0.1)
with col3:
    diabete_p = st.checkbox("Diabète")
    dfg_p = st.selectbox("Fonction rénale (DFG)", ["Normal", "30-59 mL/min", "<30 mL/min"])
    atcd_p = st.checkbox("ATCD cardiovasculaires")

# 7. LOGIQUE DE CALCUL
def calculer_score(atcd, dfg, systo):
    if atcd: return "TRES ELEVE (Prévention secondaire)", 15.0
    if systo >= 180 or dfg == "<30 mL/min": return "TRES ELEVE", 12.0
    if dfg == "30-59 mL/min": return "ELEVE", 7.5
    return "MODERE", 3.5

# 8. ACTIONS
if st.button("1. ÉVALUER LE PROFIL SCORE ESC"):
    cat, val = calculer_score(atcd_p, dfg_p, systo_p)
    st.session_state.cat_risque = cat
    st.session_state.score_estime = val
    st.success(f"Résultat : Risque {cat} (Score SCORE2 : {val}%)")

if st.button("2. GÉNÉRER LA LETTRE SYNTHÉTIQUE"):
    if not api_key_groq:
        st.error("Clé API Groq manquante.")
    elif st.session_state.cat_risque is None:
        st.error("Veuillez évaluer le profil avant de générer la lettre.")
    else:
        try:
            client = Groq(api_key=api_key_groq)
            prompt = f"""
            Rédige un compte-rendu médical hospitalier SYNTHÉTIQUE et FORMEL. 
            INTERDICTION : N'utilise AUCUNE étoile (*), AUCUN hashtag (#) et AUCUN caractère spécial de mise en forme.
            
            DONNÉES :
            - Patient : {nom_p}, {age_p} ans.
            - Risque ESC : {st.session_state.cat_risque}.
            - Valeur Score SCORE2 : {st.session_state.score_estime}%.
            - Tabac : {fumeur_p}.
            - Médecin : {dr_nom if dr_nom else "Le praticien"}, {dr_spe if dr_spe else ""}.

            STRUCTURE :
            1. OBJET : Bilan de stratification du risque cardiovasculaire.
            2. SYNTHÈSE : Indiquer le score SCORE2 et la catégorie de risque selon les guidelines ESC.
            3. PRÉCONISATIONS : Sport 150min/semaine, régime méditerranéen, sevrage tabagique si besoin.
            4. CONCLUSION : Cible LDL-C adaptée au profil.
            
            Mention de fin obligatoire : Application créée par Jennyfer Vari, Neli Ilieva et Pauline ROBERT.
            """
            completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}])
            st.session_state.lettre_generee = completion.choices[0].message.content
            st.text_area("Aperçu clinique (Sans symboles)", value=st.session_state.lettre_generee, height=350)
        except Exception as e:
            st.error(f"Erreur : {e}")

if st.session_state.lettre_generee:
    pdf_data = create_pdf(st.session_state.lettre_generee)
    st.download_button("📥 TÉLÉCHARGER LE COMPTE-RENDU (PDF)", data=pdf_data, file_name=f"CR_Cardio_{nom_p}.pdf", mime="application/pdf")

# 10. FOOTER INTERFACE
st.markdown(f"""
    <div class="footer-text">
        <b>Application créée par :</b> Jennyfer Vari, Neli Ilieva et Pauline ROBERT
    </div>
    """, unsafe_allow_html=True)
