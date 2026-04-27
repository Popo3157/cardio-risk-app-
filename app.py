import streamlit as st
import pandas as pd
from openai import OpenAI

# Configuration de la page
st.set_page_config(page_title="L'Alliance Protectrice - Prévention Cardiaque", layout="wide")

# --- STYLE CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    .main { background-color: #f0f8ff; }
    .stButton>button { background-color: #004d99; color: white; border-radius: 10px; }
    .header-box { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 10px solid #004d99; margin-bottom: 25px; }
    h1 { color: #004d99; }
    h2 { color: #0066cc; border-bottom: 2px solid #0066cc; }
    </style>
    """, unsafe_allow_html=True)

# --- EN-TÊTE ET LOGO ---
# Note : Remplacez l'URL par le chemin local de votre image si nécessaire
st.markdown('<div class="header-box">', unsafe_allow_html=True)
st.title("🛡️ L'ALLIANCE PROTECTRICE")
st.subheader("DÉTECTION & PRÉVENTION CARDIAQUE")
st.markdown('</div>', unsafe_allow_html=True)

# --- BARRE LATÉRALE (Identité Médecin & API) ---
with st.sidebar:
    st.header("👨‍⚕️ Identité du Médecin")
    dr_name = st.text_input("Nom du Docteur")
    specialty = st.text_input("Spécialité", "Médecine Générale")
    cabinet = st.text_input("Cabinet / Service")
    
    st.divider()
    st.header("🔑 Configuration IA")
    api_key = st.text_input("Clé API OpenAI", type="password", value="votre_cle_ici")

# --- FORMULAIRE PATIENT ---
st.header("📋 Paramètres du Patient")
col1, col2, col3 = st.columns(3)

with col1:
    nom_patient = st.text_input("Nom du Patient")
    age = st.number_input("Âge (doit être > 18 ans)", min_value=18, max_value=100, value=55)
    sexe = st.radio("Sexe", ["Homme", "Femme"])

with col2:
    fumeur = st.radio("Tabagisme", ["Non", "Oui"])
    systolique = st.number_input("Pression Artérielle Systolique (mmHg)", min_value=90, max_value=200, value=130)
    chol_non_hdl = st.number_input("Cholestérol non-HDL (mmol/L)", min_value=2.0, max_value=10.0, value=3.9, step=0.1)

with col3:
    diabete = st.checkbox("Diabète")
    insuffisance_renale = st.selectbox("Fonction rénale (DFG)", ["Normal", "30-59 mL/min", "<30 mL/min"])
    atcd_cv = st.checkbox("Maladie cardiovasculaire avérée (AVC, IDM, AOMI)")

# --- LOGIQUE DE CALCUL DU SCORE ---
def estimer_categorie_risque(age, score_value, atcd_cv, insuffisance_renale, chol_total, systolique):
    # Prévention secondaire (Risque très élevé d'office) [cite: 18, 301]
    if atcd_cv:
        return "Risque très élevé (Prévention secondaire)"
    
    # Facteurs de risque majeurs sévères [cite: 18, 286]
    if systolique >= 180 or chol_total > 8 or insuffisance_renale == "<30 mL/min":
        return "Risque très élevé"
    
    if insuffisance_renale == "30-59 mL/min":
        return "Risque élevé"

    # Basé sur SCORE2 et l'âge 
    if age < 50:
        if score_value >= 7.5: return "Risque très élevé"
        if score_value >= 2.5: return "Risque élevé"
        return "Risque faible à modéré"
    elif 50 <= age < 70:
        if score_value >= 10: return "Risque très élevé"
        if score_value >= 5: return "Risque élevé"
        return "Risque faible à modéré"
    else: # >= 70 ans
        if score_value >= 15: return "Risque très élevé"
        if score_value >= 7.5: return "Risque élevé"
        return "Risque faible à modéré"

# Simulation simple du score basé sur les tables SCORE2 [cite: 19]
# Pour un vrai outil, il faudrait implanter la formule mathématique complète ou la table entière.
score_estime = 4.5 # Valeur d'exemple pour la démonstration

# --- AFFICHAGE DES RÉSULTATS ---
if st.button("Calculer le risque et interpréter"):
    st.divider()
    cat_risque = estimer_categorie_risque(age, score_estime, atcd_cv, insuffisance_renale, 5.0, systolique)
    
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.metric(label="Score SCORE2 estimé à 10 ans", value=f"{score_estime} %")
    with col_res2:
        st.subheader(f"Catégorie : {cat_risque}")

    # Objectifs LDL selon le risque [cite: 308, 316]
    st.markdown("### 🎯 Objectifs Thérapeutiques")
    if "Très élevé" in cat_risque:
        obj_ldl = "< 1.4 mmol/L"
    elif "Élevé" in cat_risque:
        obj_ldl = "< 1.8 mmol/L"
    else:
        obj_ldl = "< 2.6 mmol/L"
    
    st.info(f"**Objectif LDL-C :** {obj_ldl} | **Objectif Tensionnel :** < 140/90 mmHg [cite: 325]")

# --- GÉNÉRATION DE LA LETTRE IA ---
st.header("📝 Lettre de Recommandation (IA)")
if st.button("Générer la lettre avec GPT-4"):
    if not api_key or api_key == "votre_cle_ici":
        st.error("Veuillez entrer votre clé API dans la barre latérale.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            prompt = f"""
            Rédige une lettre médicale professionnelle de l'Alliance Protectrice.
            Médecin: Dr {dr_name}, {specialty}.
            Patient: {nom_patient}, {age} ans.
            Situation: Risque {cat_risque}, Score SCORE2 de {score_estime}%.
            Inclure des recommandations sur le tabac ({fumeur}), l'activité physique (150min/sem), 
            et l'alimentation selon les guidelines SFC[cite: 205, 309].
            Format: Professionnel, structuré, prêt à être envoyé.
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "Tu es un assistant médical expert en cardiologie."},
                          {"role": "user", "content": prompt}]
            )
            
            lettre = response.choices[0].message.content
            st.text_area("Lettre générée", value=lettre, height=400)
            st.download_button("Télécharger la lettre (TXT)", lettre, file_name=f"Recommandation_{nom_patient}.txt")
            
        except Exception as e:
            st.error(f"Erreur avec l'IA : {e}")

st.divider()
st.caption("Application développée par Neli Ilieva, Jennyfer Vari et Pauline Robert. [cite: 2, 3, 4]")
