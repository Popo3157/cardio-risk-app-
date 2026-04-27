import streamlit as st
from groq import Groq
from fpdf import FPDF

# 1. CONFIGURATION (Impérativement en premier)
st.set_page_config(page_title="L'Alliance Protectrice - Prévention Cardiaque", layout="wide")

# 2. INITIALISATION DE LA MÉMOIRE (Session State)
if 'cat_risque' not in st.session_state:
    st.session_state.cat_risque = None
if 'score_estime' not in st.session_state:
    st.session_state.score_estime = 0.0
if 'lettre_generee' not in st.session_state:
    st.session_state.lettre_generee = ""

# 3. STYLE CSS (Identité visuelle L'Alliance Protectrice)
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
    # En-tête Alliance Protectrice dans le PDF
    pdf.set_text_color(0, 77, 153)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "L'ALLIANCE PROTECTRICE", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, "Detection & Prevention Cardiaque", ln=True, align='C')
    pdf.ln(10)
    
    # Corps du texte
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=12)
    # Remplacement des caractères spéciaux pour compatibilité PDF
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=clean_text)
    return pdf.output(dest='S').encode('latin-1')

# 4. EN-TÊTE
st.markdown('<div class="header-box">', unsafe_allow_html=True)
st.title("🛡️ L'ALLIANCE PROTECTRICE")
st.subheader("DÉTECTION & PRÉVENTION CARDIAQUE")
st.markdown('</div>', unsafe_allow_html=True)

# 5. BARRE LATÉRALE (Identité Médecin - Champs Libres)
with st.sidebar:
    st.header("👨‍⚕️ Identité du Médecin")
    dr_nom_manuel = st.text_input("Nom du Docteur (ex: Dr Robert)", value="")
    dr_spe_manuel = st.text_input("Spécialité", value="")
    dr_cab_manuel = st.text_input("Cabinet / Service", value="")
    
    st.divider()
    st.header("🔑 Configuration IA")
    api_key_groq = st.text_input("Clé API Groq", type="password")

# 6. FORMULAIRE PATIENT
st.header("📋 Paramètres du Patient")
col1, col2, col3 = st.columns(3)

with col1:
    nom_patient = st.text_input("Nom du Patient", value="")
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

# 7. LOGIQUE DE CALCUL (SCORE2 & SFC)
def calculer_risque(age_p, score_p, atcd_p, dfg_p, systo_p):
    if atcd_p: return "Risque tres eleve (Prevention secondaire)"
    if systo_p >= 180 or dfg_p == "<30 mL/min": return "Risque tres eleve"
    if dfg_p == "30-59 mL/min": return "Risque eleve"
    
    if age_p < 50 and score_p >= 7.5: return "Risque tres eleve"
    if 50 <= age_p < 70 and score_p >= 10: return "Risque tres eleve"
    if age_p >= 70 and score_p >= 15: return "Risque tres eleve"
    return "Risque modere"

# 8. ANALYSE ET RÉSULTATS
st.header("📊 Évaluation du Risque")
if st.button("1. Calculer le risque"):
    score_final = 4.5 
    resultat = calculer_risque(age, score_final, atcd_cv, insuffisance_renale, systolique)
    st.session_state.cat_risque = resultat
    st.session_state.score_estime = score_final
    st.success(f"Risque identifié : {resultat}")
    
    # Objectifs LDL
    if "Tres eleve" in resultat: obj = "< 1.4 mmol/L"
    elif "Eleve" in resultat: obj = "< 1.8 mmol/L"
    else: obj = "< 2.6 mmol/L"
    st.info(f"Objectif LDL-C : {obj}")

# 9. GÉNÉRATION DE LA LETTRE (IA)
st.header("📝 Lettre de Recommandation")
if st.button("2. Générer la lettre finale"):
    if not api_key_groq:
        st.error("Veuillez saisir votre clé API Groq dans la barre latérale.")
    elif st.session_state.cat_risque is None:
        st.error("Veuillez d'abord cliquer sur 'Calculer le risque'.")
    else:
        try:
            client = Groq(api_key=api_key_groq)
            
            # Préparation des infos médecin pour le prompt
            info_dr = f"Dr {dr_nom_manuel}" if dr_nom_manuel else "le médecin traitant"
            info_spe = f"spécialisé en {dr_spe_manuel}" if dr_spe_manuel else ""
            info_cab = f"au sein du {dr_cab_manuel}" if dr_cab_manuel else ""

            prompt = f"""
            Rédige une lettre de recommandation médicale de l'Alliance Protectrice.
            
            MÉDECIN : {info_dr} {info_spe} {info_cab}.
            PATIENT : {nom_patient}, {age} ans.
            BILAN : Risque {st.session_state.cat_risque}, Score SCORE2 de {st.session_state.score_estime}%.
            TABAC : {fumeur}.
            
            CONSIGNES :
            - NE METS AUCUNE ADRESSE POSTALE.
            - Utilise les noms fournis pour le médecin et le patient. Si le nom du médecin est vide, utilise une formulation générale.
            - Inclure les conseils : sport 150min/semaine, alimentation, arrêt tabac.
            - NE LAISSE AUCUN CHAMP VIDE ET AUCUN CROCHET [].
            """
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": "Tu es un cardiologue. Tu rédiges des lettres complètes sans adresses."},
                          {"role": "user", "content": prompt}]
            )
            
            st.session_state.lettre_generee = completion.choices[0].message.content
            st.text_area("Aperçu du contenu", value=st.session_state.lettre_generee, height=400)
            
        except Exception as e:
            st.error(f"Erreur de génération : {e}")

# BOUTON TÉLÉCHARGEMENT PDF
if st.session_state.lettre_generee:
    pdf_data = create_pdf(st.session_state.lettre_generee)
    st.download_button(
        label="📥 Télécharger la lettre en PDF",
        data=pdf_data,
        file_name=f"Lettre_Alliance_{nom_patient}.pdf",
        mime="application/pdf"
    )

st.divider()
st.caption("Application développée par Neli Ilieva, Jennyfer Vari et Pauline Robert.")
