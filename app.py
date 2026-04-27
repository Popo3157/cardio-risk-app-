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

# 3. STYLE CSS (Identité visuelle hospitalière)
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

# FONCTION GÉNÉRATION PDF (Mise en page médicale)
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    # En-tête type hôpital
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 77, 153)
    pdf.cell(0, 10, "L'ALLIANCE PROTECTRICE - UNITE DE PREVENTION CARDIOVASCULAIRE", ln=True, align='L')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 5, "Evaluation du risque SCORE2 - Guidelines SFC/ESC", ln=True, align='L')
    pdf.ln(10)
    
    # Corps du texte
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=11)
    # Encodage pour éviter les erreurs de caractères spéciaux
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=clean_text)
    
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "Document genere numeriquement - Valable apres signature et cachet.", align='R')
    return pdf.output(dest='S').encode('latin-1')

# 4. EN-TÊTE
st.markdown('<div class="header-box">', unsafe_allow_html=True)
st.title("🛡️ L'ALLIANCE PROTECTRICE")
st.subheader("SERVICE D'ÉVALUATION DU RISQUE CARDIOVASCULAIRE")
st.markdown('</div>', unsafe_allow_html=True)

# 5. BARRE LATÉRALE (Identité Médecin)
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

# 7. CALCUL DU RISQUE
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
            
            # Objectif LDL selon guidelines
            if "TRES ELEVE" in st.session_state.cat_risque: obj = "< 1.4 mmol/L"
            elif "ELEVE" in st.session_state.cat_risque: obj = "< 1.8 mmol/L"
            else: obj = "< 2.6 mmol/L"

            prompt = f"""
            Rédige une lettre de recommandation médicale FORMELLE et TYPIQUE d'un service de cardiologie hospitalier.
            
            STRUCTURE :
            1. OBJET : Évaluation du risque cardiovasculaire.
            2. MOTIF : Bilan de prévention.
            3. DONNÉES : Patient {nom_patient}, {age} ans. Risque {st.session_state.cat_risque}, SCORE2 de {st.session_state.score_estime}%.
            4. CONCLUSIONS : Expliquer l'objectif LDL-C ({obj}) et la gestion des facteurs (Tabac: {fumeur}).
            5. CONDUITE À TENIR : Mesures hygiéno-diététiques précises.
            
            MÉDECIN RÉFÉRENT : {dr_nom if dr_nom else "[NOM DU PRATICIEN]"}, {dr_spe if dr_spe else "[SPÉCIALITÉ]"}, {dr_cab if dr_cab else "[SERVICE]"}.

            CONSIGNES :
            - Ton très médical, factuel et structuré.
            - Utilise "Nous avons reçu ce jour..." ou "Le bilan de ce jour montre...".
            - NE METS AUCUNE ADRESSE POSTALE.
            - NE LAISSE AUCUN CROCHET []. Si le nom du médecin n'est pas fourni, laisse une ligne pointillée pour signature.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": "Tu es un secrétariat médical spécialisé en cardiologie hospitalière."},
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
