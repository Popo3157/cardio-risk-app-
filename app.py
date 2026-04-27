import streamlit as st
import pandas as pd
from groq import Groq

# 1. CONFIGURATION (Toujours en premier)
st.set_page_config(page_title="L'Alliance Protectrice - Prévention Cardiaque", layout="wide")

# 2. INITIALISATION DE LA MÉMOIRE (Session State)
# Empêche l'erreur de variable non définie si on clique sur la lettre avant le calcul
if 'cat_risque' not in st.session_state:
    st.session_state.cat_risque = None
if 'score_estime' not in st.session_state:
    st.session_state.score_estime = 0.0

# 3. STYLE CSS (Identité visuelle de l'Alliance Protectrice)
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

# 4. EN-TÊTE
st.markdown('<div class="header-box">', unsafe_allow_html=True)
st.title("🛡️ L'ALLIANCE PROTECTRICE")
st.subheader("DÉTECTION & PRÉVENTION CARDIAQUE")
st.markdown('</div>', unsafe_allow_html=True)

# 5. BARRE LATÉRALE
with st.sidebar:
    st.header("👨‍⚕️ Identité du Médecin")
    dr_name = st.text_input("Nom du Docteur", placeholder="ex: Dr. Robert")
    specialty = st.text_input("Spécialité", "Médecine Générale")
    cabinet = st.text_input("Cabinet / Service")
    
    st.divider()
    st.header("🔑 Configuration IA (Gratuit)")
    st.markdown("[Obtenez une clé Groq gratuite ici](https://console.groq.com/keys)")
    api_key_groq = st.text_input("Clé API Groq", type="password")

# 6. FORMULAIRE PATIENT
st.header("📋 Paramètres du Patient")
col1, col2, col3 = st.columns(3)

with col1:
    nom_patient = st.text_input("Nom du Patient")
    age = st.number_input("Âge (> 18 ans)", min_value=18, max_value=100, value=55)
    sexe = st.radio("Sexe", ["Homme", "Femme"])

with col2:
    fumeur = st.radio("Tabagisme", ["Non", "Oui"])
    systolique = st.number_input("Pression Systolique (mmHg)", min_value=90, max_value=200, value=130)
    chol_non_hdl = st.number_input("Cholestérol non-HDL (mmol/L)", min_value=2.0, max_value=10.0, value=3.9, step=0.1)

with col3:
    diabete = st.checkbox("Diabète")
    insuffisance_renale = st.selectbox("Fonction rénale (DFG)", ["Normal", "30-59 mL/min", "<30 mL/min"])
    atcd_cv = st.checkbox("Maladie cardiovasculaire avérée (AVC, IDM, AOMI)")

# 7. LOGIQUE DE CALCUL (Guidelines SFC)
def calculer_risque(age, score_val, atcd_cv, dfg, systo):
    if atcd_cv: return "Risque très élevé (Prévention secondaire)"
    if systo >= 180 or dfg == "<30 mL/min": return "Risque très élevé"
    if dfg == "30-59 mL/min": return "Risque élevé"

    if age < 50:
        if score_val >= 7.5: return "Risque très élevé"
        if score_val >= 2.5: return "Risque élevé"
    elif 50 <= age < 70:
        if score_val >= 10: return "Risque très élevé"
        if score_val >= 5: return "Risque élevé"
    else:
        if score_val >= 15: return "Risque très élevé"
        if score_val >= 7.5: return "Risque élevé"
    return "Risque faible à modéré"

# 8. ANALYSE ET RÉSULTATS
st.header("📊 Évaluation du Risque")
if st.button("Calculer le risque et interpréter"):
    # Score SCORE2 simulé pour l'exemple
    score_final = 4.5 
    resultat = calculer_risque(age, score_final, atcd_cv, insuffisance_renale, systolique)
    
    # Sauvegarde en mémoire
    st.session_state.cat_risque = resultat
    st.session_state.score_estime = score_final

    st.divider()
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric(label="Estimation SCORE2", value=f"{score_final} %")
    with res_col2:
        st.subheader(f"Catégorie : {resultat}")

    # Objectifs Lipidiques (Basés sur le PDF)
    if "Très élevé" in resultat: obj_ldl = "< 1.4 mmol/L"
    elif "Élevé" in resultat: obj_ldl = "< 1.8 mmol/L"
    else: obj_ldl = "< 2.6 mmol/L"
    
    st.info(f"🎯 **Objectif LDL-C :** {obj_ldl} | **Objectif Tensionnel :** < 140/90 mmHg")

# 9. GÉNÉRATION DE LA LETTRE IA (Groq)
st.header("📝 Lettre de Recommandation (IA)")
if st.button("Générer la lettre (Gratuit avec Groq)"):
    if not api_key_groq:
        st.error("⚠️ Veuillez entrer votre clé API Groq dans la barre latérale.")
    elif st.session_state.cat_risque is None:
        st.error("⚠️ Veuillez d'abord cliquer sur 'Calculer le risque'.")
    else:
        try:
            client = Groq(api_key=api_key_groq)
            prompt = f"""
            Tu es un cardiologue de l'Alliance Protectrice. Rédige une lettre médicale pour :
            Médecin : Dr {dr_name} ({specialty}). Patient : {nom_patient}, {age} ans.
            Situation : Risque {st.session_state.cat_risque}, Score SCORE2 de {st.session_state.score_estime}%.
            Inclure impérativement les recommandations SFC :
            - Sport : >= 150 min / semaine
            - Tabac : Statut {fumeur} (arrêt impératif si Oui)
            - Alimentation : Fruits, légumes, moins de graisses saturées.
            Sois professionnel et bienveillant.
            """
            
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}]
            )
            
            lettre = completion.choices[0].message.content
            st.text_area("Lettre rédigée", value=lettre, height=400)
            st.download_button("📥 Télécharger la lettre", lettre, file_name=f"Alliance_{nom_patient}.txt")
            
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")

st.divider()
st.caption("Application développée par Neli Ilieva, Jennyfer Vari et Pauline Robert.")
