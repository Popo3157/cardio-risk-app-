import streamlit as st
import pandas as pd
from groq import Groq

# 1. CONFIGURATION (Doit être la première ligne)
st.set_page_config(page_title="L'Alliance Protectrice - Prévention Cardiaque", layout="wide")

# 2. INITIALISATION DE LA MÉMOIRE (Session State)
if 'cat_risque' not in st.session_state:
    st.session_state.cat_risque = None
if 'score_estime' not in st.session_state:
    st.session_state.score_estime = 0.0

# 3. STYLE CSS (Identité visuelle du projet)
st.markdown("""
    <style>
    .main { background-color: #f0f8ff; }
    .stButton>button { background-color: #004d99; color: white; border-radius: 10px; width: 100%; font-weight: bold; }
    .header-box { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 10px solid #004d99; 
        border-right: 10px solid #004d99; 
        margin-bottom: 25px; 
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    h1 { color: #004d99; margin-bottom: 0; }
    h2 { color: #0066cc; border-bottom: 2px solid #0066cc; padding-bottom: 10px; margin-top: 30px; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 4. EN-TÊTE ET LOGO [cite: 6, 7]
st.markdown('<div class="header-box">', unsafe_allow_html=True)
st.title("🛡️ L'ALLIANCE PROTECTRICE")
st.subheader("DÉTECTION & PRÉVENTION CARDIAQUE")
st.markdown('</div>', unsafe_allow_html=True)

# 5. BARRE LATÉRALE (Identité Médecin & API) [cite: 9]
with st.sidebar:
    st.header("👨‍⚕️ Identité du Médecin")
    dr_name = st.text_input("Nom du Docteur", placeholder="ex: Dr. Pauline Robert")
    specialty = st.text_input("Spécialité", "Médecine Générale")
    cabinet = st.text_input("Cabinet / Service")
    
    st.divider()
    st.header("🔑 Configuration IA (Gratuit)")
    api_key_groq = st.text_input("Clé API Groq", type="password")
    st.info("Modèle mis à jour : Llama-3.1-8b-instant")

# 6. PARAMÈTRES PATIENT [cite: 10, 15]
st.header("📋 Paramètres du Patient")
col1, col2, col3 = st.columns(3)

with col1:
    nom_patient = st.text_input("Nom du Patient")
    age = st.number_input("Âge (> 18 ans)", min_value=18, max_value=100, value=55) [cite: 5]
    sexe = st.radio("Sexe", ["Homme", "Femme"]) [cite: 15]

with col2:
    fumeur = st.radio("Tabagisme", ["Non", "Oui"]) [cite: 15, 210]
    systolique = st.number_input("Pression Systolique (mmHg)", min_value=90, max_value=200, value=130) [cite: 15, 220]
    chol_non_hdl = st.number_input("Cholestérol non-HDL (mmol/L)", min_value=2.0, max_value=10.0, value=3.9, step=0.1) [cite: 15, 267]

with col3:
    diabete = st.checkbox("Diabète") [cite: 225]
    insuffisance_renale = st.selectbox("Fonction rénale (DFG)", ["Normal", "30-59 mL/min", "<30 mL/min"]) [cite: 292, 298]
    atcd_cv = st.checkbox("Maladie cardiovasculaire avérée (AVC, IDM, AOMI)") [cite: 18, 303]

# 7. LOGIQUE DE CALCUL DU SCORE [cite: 11, 16, 17]
def calculer_risque(age, score_val, atcd_cv, dfg, systo):
    # Prévention secondaire [cite: 18, 301]
    if atcd_cv: return "Risque très élevé (Prévention secondaire)"
    # Facteurs de risque majeurs [cite: 18, 286]
    if systo >= 180 or dfg == "<30 mL/min": return "Risque très élevé"
    if dfg == "30-59 mL/min": return "Risque élevé"

    # Catégories de risque selon SCORE2 et l'âge [cite: 192, 193]
    if age < 50:
        if score_val >= 7.5: return "Risque très élevé"
        if score_val >= 2.5: return "Risque élevé"
    elif 50 <= age < 70:
        if score_val >= 10: return "Risque très élevé"
        if score_val >= 5: return "Risque élevé"
    else: # >= 70 ans
        if score_val >= 15: return "Risque très élevé"
        if score_val >= 7.5: return "Risque élevé"
    return "Risque faible à modéré"

# 8. ANALYSE ET RÉSULTATS [cite: 12]
st.header("📊 Évaluation du Risque")
if st.button("Calculer le risque et interpréter"): [cite: 11]
    # Score simulé (basé sur SCORE2) [cite: 14]
    score_final = 4.5 
    resultat = calculer_risque(age, score_final, atcd_cv, insuffisance_renale, systolique)
    
    st.session_state.cat_risque = resultat
    st.session_state.score_estime = score_final

    st.divider()
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric(label="Estimation SCORE2 à 10 ans", value=f"{score_final} %") [cite: 273]
    with res_col2:
        st.subheader(f"Catégorie : {resultat}") [cite: 275]

    # Objectifs lipidiques et tensionnels [cite: 315, 323]
    if "Très élevé" in resultat: obj_ldl = "< 1.4 mmol/L" [cite: 322]
    elif "Élevé" in resultat: obj_ldl = "< 1.8 mmol/L" [cite: 320]
    else: obj_ldl = "< 2.6 mmol/L" [cite: 318]
    
    st.info(f"🎯 **Objectif LDL-C :** {obj_ldl} | **Objectif Tensionnel :** < 140/90 mmHg") [cite: 325]

# 9. LETTRE DE RECOMMANDATION IA [cite: 13, 191]
st.header("📝 Lettre de Recommandation (IA)")
if st.button("Générer la lettre avec Groq"):
    if not api_key_groq:
        st.error("⚠️ Veuillez entrer votre clé API Groq.")
    elif st.session_state.cat_risque is None:
        st.error("⚠️ Veuillez d'abord calculer le risque.")
    else:
        try:
            client = Groq(api_key=api_key_groq)
            # Mise à jour du prompt avec les guidelines SFC [cite: 205, 309]
            prompt = f"""
            Tu es un cardiologue de l'Alliance Protectrice. Rédige une lettre médicale professionnelle.
            Médecin : Dr {dr_name} ({specialty}). Patient : {nom_patient}, {age} ans.
            Situation : Risque {st.session_state.cat_risque}, Score SCORE2 de {st.session_state.score_estime}%.
            Inclure impérativement les recommandations suivantes selon les guidelines SFC :
            1. Activité physique régulière (>= 150 min / semaine) [cite: 311]
            2. Arrêt du tabac (Statut : {fumeur}) [cite: 310]
            3. Alimentation riche en fruits et légumes [cite: 312]
            4. Objectifs tensionnels < 140/90 mmHg [cite: 325]
            """
            
            # UTILISATION DU MODÈLE MIS À JOUR : llama-3.1-8b-instant
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant", 
                messages=[{"role": "user", "content": prompt}]
            )
            
            lettre = completion.choices[0].message.content
            st.text_area("Lettre rédigée", value=lettre, height=400) [cite: 13]
            st.download_button("📥 Télécharger la lettre", lettre, file_name=f"Alliance_{nom_patient}.txt")
            
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")

st.divider()
st.caption("Application développée par Neli Ilieva, Jennyfer Vari et Pauline Robert.") [cite: 2, 3, 4]
