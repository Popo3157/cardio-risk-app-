import streamlit as st
from groq import Groq
from fpdf import FPDF
import base64

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
    .main { background-color: #f0f8ff; }
    .stButton>button { background-color: #004d99; color: white; border-radius: 10px; width: 100%; font-weight: bold; }
    .header-box { 
        background-color: #ffffff; padding: 20px; border-radius: 15px; 
        border-left: 10px solid #004d99; border-right: 10px solid #004d99; 
        margin-bottom: 25px; text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    h1 { color: #004d99; margin-bottom: 0; }
    h2 { color: #0066cc; border-bottom: 2px solid #0066cc; padding-bottom: 10px; margin-top: 30px; }
    </style>
    """, unsafe_allow_html=True)

# FONCTION POUR GÉNÉRER LE PDF
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Remplacement des caractères spéciaux pour éviter les erreurs PDF
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

# 4. EN-TÊTE
st.markdown('<div class="header-box">', unsafe_allow_html=True)
st.title("🛡️ L'ALLIANCE PROTECTRICE")
st.subheader("DÉTECTION & PRÉVENTION CARDIAQUE")
st.markdown('</div>', unsafe_allow_html=True)

# 5. BARRE LATÉRALE
with st.sidebar:
    st.header("👨‍⚕️ Identité du Médecin")
    dr_name = st.text_input("Nom du Docteur", value="Dr Pauline Robert")
    specialty = st.text_input("Spécialité", "Médecine Générale")
    
    st.divider()
    st.header("🔑 Configuration IA")
    api_key_groq = st.text_input("Clé API Groq", type="password")

# 6. FORMULAIRE PATIENT
st.header("📋 Paramètres du Patient")
col1, col2, col3 = st.columns(3)

with col1:
    nom_patient = st.text_input("Nom du Patient", value="Jean Dupont")
    age = st.number_input("Âge", min_value=18, max_value=100, value=55)
    sexe = st.radio("Sexe", ["Homme", "Femme"])

with col2:
    fumeur = st.radio("Tabagisme", ["Non", "Oui"])
    systolique = st.number_input("Pression Systolique (mmHg)", min_value=90, max_value=200, value=130)
    chol_non_hdl = st.number_input("Cholestérol non-HDL (mmol/L)", min_value=2.0, max_value=10.0, value=3.9, step=0.1)

with col3:
    diabete = st.checkbox("Diabète")
    insuffisance_renale = st.selectbox("Fonction rénale (DFG)", ["Normal", "30-59 mL/min", "<30 mL/min"])
    atcd_cv = st.checkbox("Maladie cardiovasculaire avérée")

# 7. LOGIQUE DE CALCUL
def calculer_risque(age, score_val, atcd_cv, dfg, systo):
    if atcd_cv: return "Risque très élevé (Prévention secondaire)"
    if systo >= 180 or dfg == "<30 mL/min": return "Risque très élevé"
    if dfg == "30-59 mL/min": return "Risque élevé"
    # Seuils simplifiés SCORE2
    if age < 50 and score_val >= 7.5: return "Risque très élevé"
    if 50 <= age < 70 and score_val >= 10: return "Risque très élevé"
    if age >= 70 and score_val >= 15: return "Risque très élevé"
    return "Risque modéré"

# 8. ANALYSE
if st.button("1. Calculer le risque"):
    score_final = 4.5 
    resultat = calculer_risque(age, score_final, atcd_cv, insuffisance_renale, systolique)
    st.session_state.cat_risque = resultat
    st.session_state.score_estime = score_final
    st.success(f"Risque identifié : {resultat}")

# 9. GÉNÉRATION ET PDF
st.header("📝 Lettre de Recommandation")
if st.button("2. Générer la lettre finale"):
    if not api_key_groq:
        st.error("Veuillez saisir votre clé API Groq.")
    elif st.session_state.cat_risque is None:
        st.error("Veuillez d'abord calculer le risque.")
    else:
        try:
            client = Groq(api_key=api_key_groq)
            
            if "Très élevé" in st.session_state.cat_risque: obj_ldl = "inférieur à 1.4 mmol/L"
            elif "Élevé" in st.session_state.cat_risque: obj_ldl = "inférieur à 1.8 mmol/L"
            else: obj_ldl = "inférieur à 2.6 mmol/L"

            prompt = f"""
            Rédige une lettre médicale de l'Alliance Protectrice pour le patient {nom_patient} ({age} ans).
            L'expéditeur est le {dr_name} ({specialty}).
            
            DONNÉES MÉDICALES :
            - Risque cardiovasculaire : {st.session_state.cat_risque}
            - Score SCORE2 : {st.session_state.score_estime}%
            - Statut tabagique : {fumeur}
            - Cible LDL-C : {obj_ldl}
            
            CONSIGNES :
            - NE METS AUCUNE ADRESSE POSTALE (ni pour le médecin, ni pour le patient).
            - Utilise un ton professionnel et bienveillant.
            - Inclure les conseils : 150min sport/semaine, alimentation équilibrée, arrêt tabac si nécessaire.
            - NE LAISSE AUCUN CHAMP VIDE ET AUCUN CROCHET []. Remplis tout le texte.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": "Tu es un cardiologue qui rédige des lettres complètes sans adresses."},
                          {"role": "user", "content": prompt}]
            )
            
            st.session_state.lettre_generee = completion.choices[0].message.content
            st.text_area("Aperçu du contenu", value=st.session_state.lettre_generee, height=400)
            
        except Exception as e:
            st.error(f"Erreur : {e}")

# BOUTON DE TÉLÉCHARGEMENT PDF (Apparaît si la lettre est générée)
if st.session_state.lettre_generee:
    pdf_data = create_pdf(st.session_state.lettre_generee)
    st.download_button(
        label="📥 Télécharger la lettre en PDF",
        data=pdf_data,
        file_name=f"Recommandation_{nom_patient}.pdf",
        mime="application/pdf"
    )
