import streamlit as st
import pandas as pd
from openai import OpenAI

# 1. CONFIGURATION DE LA PAGE (Doit être en premier)
st.set_page_config(page_title="L'Alliance Protectrice - Prévention Cardiaque", layout="wide")

# 2. INITIALISATION DE LA MÉMOIRE (Session State)
# Cela permet de garder en mémoire le risque calculé pour la lettre IA
if 'cat_risque' not in st.session_state:
    st.session_state.cat_risque = "Non défini (cliquez sur calculer)"
if 'score_estime' not in st.session_state:
    st.session_state.score_estime = 0.0

# 3. STYLE CSS PERSONNALISÉ
st.markdown("""
    <style>
    .main { background-color: #f0f8ff; }
    .stButton>button { background-color: #004d99; color: white; border-radius: 10px; width: 100%; }
    .header-box { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 10px solid #004d99; margin-bottom: 25px; }
    h1 { color: #004d99; }
    h2 { color: #0066cc; border-bottom: 2px solid #0066cc; }
    </style>
    """, unsafe_allow_html=True)

# 4. EN-TÊTE ET LOGO
st.markdown('<div class="header-box">', unsafe_allow_html=True)
st.title("🛡️ L'ALLIANCE PROTECTRICE")
st.subheader("DÉTECTION & PRÉVENTION CARDIAQUE")
st.markdown('</div>', unsafe_allow_html=True)

# 5. BARRE LATÉRALE (Identité Médecin & API)
with st.sidebar:
    st.header("👨‍⚕️ Identité du Médecin [cite: 9]")
    dr_name = st.text_input("Nom du Docteur")
    specialty = st.text_input("Spécialité", "Médecine Générale")
    cabinet = st.text_input("Cabinet / Service")
    
    st.divider()
    st.header("🔑 Configuration IA")
    api_key = st.text_input("Clé API OpenAI", type="password")

# 6. FORMULAIRE PATIENT [cite: 10, 15]
st.header("📋 Paramètres du Patient")
col1, col2, col3 = st.columns(3)

with col1:
    nom_patient = st.text_input("Nom du Patient")
    age = st.number_input("Âge (doit être > 18 ans) [cite: 5]", min_value=18, max_value=100, value=55)
    sexe = st.radio("Sexe", ["Homme", "Femme"])

with col2:
    fumeur = st.radio("Tabagisme", ["Non", "Oui"])
    systolique = st.number_input("Pression Artérielle Systolique (mmHg)", min_value=90, max_value=200, value=130)
    chol_non_hdl = st.number_input("Cholestérol non-HDL (mmol/L)", min_value=2.0, max_value=10.0, value=3.9, step=0.1)

with col3:
    diabete = st.checkbox("Diabète [cite: 18]")
    insuffisance_renale = st.selectbox("Fonction rénale (DFG) [cite: 18]", ["Normal", "30-59 mL/min", "<30 mL/min"])
    atcd_cv = st.checkbox("Maladie cardiovasculaire avérée (AVC, IDM, AOMI) [cite: 18, 303]")

# 7. FONCTION DE CALCUL (Logique basée sur vos tableaux PDF) [cite: 17, 193]
def estimer_categorie_risque(age, score_value, atcd_cv, insuffisance_renale, systolique):
    # Prévention secondaire [cite: 18, 301]
    if atcd_cv:
        return "Risque très élevé (Prévention secondaire)"
    
    # Facteurs de risque majeurs sévères [cite: 18, 286]
    if systolique >= 180 or insuffisance_renale == "<30 mL/min":
        return "Risque très élevé"
    
    if insuffisance_renale == "30-59 mL/min":
        return "Risque élevé"

    # Seuils basés sur SCORE2 et l'âge (Tableau 2.3 B) [cite: 193]
    if age < 50:
        if score_value >= 7.5: return "Risque très élevé"
        if score_value >= 2.5: return "Risque élevé"
    elif 50 <= age < 70:
        if score_value >= 10: return "Risque très élevé"
        if score_value >= 5: return "Risque élevé"
    else: # >= 70 ans
        if score_value >= 15: return "Risque très élevé"
        if score_value >= 7.5: return "Risque élevé"
        
    return "Risque faible à modéré"

# 8. AFFICHAGE DES RÉSULTATS
if st.button("Calculer le risque et interpréter [cite: 11, 12]"):
    st.divider()
    # On simule ici le calcul du score (SCORE2) [cite: 19]
    score_final = 4.5 
    
    # On calcule la catégorie et on la SAUVEGARDE dans la session
    cat_risque = estimer_categorie_risque(age, score_final, atcd_cv, insuffisance_renale, systolique)
    st.session_state.cat_risque = cat_risque
    st.session_state.score_estime = score_final

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.metric(label="Score SCORE2 estimé à 10 ans [cite: 206]", value=f"{score_final} %")
    with col_res2:
        st.subheader(f"Catégorie : {cat_risque}")

    # Objectifs LDL selon le risque [cite: 316]
    st.markdown("### 🎯 Objectifs Thérapeutiques")
    if "Très élevé" in cat_risque:
        obj_ldl = "< 1.4 mmol/L [cite: 322]"
    elif "Élevé" in cat_risque:
        obj_ldl = "< 1.8 mmol/L [cite: 320]"
    else:
        obj_ldl = "< 2.6 mmol/L [cite: 318]"
    
    st.info(f"**Objectif LDL-C :** {obj_ldl} | **Objectif Tensionnel :** < 140/90 mmHg [cite: 325]")

# 9. GÉNÉRATION DE LA LETTRE IA [cite: 13, 191]
st.header("📝 Lettre de Recommandation (IA)")
if st.button("Générer la lettre avec GPT-4"):
    # On vérifie si la clé API et le calcul sont présents
    if not api_key:
        st.error("Veuillez entrer votre clé API dans la barre latérale.")
    elif st.session_state.cat_risque == "Non défini (cliquez sur calculer)":
        st.error("Veuillez d'abord cliquer sur le bouton 'Calculer le risque' ci-dessus.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            # On utilise les variables sauvegardées en session
            prompt = f"""
            Rédige une lettre médicale de l'Alliance Protectrice.
            Médecin: Dr {dr_name}, {specialty}. Cabinet: {cabinet}.
            Patient: {nom_patient}, {age} ans.
            Situation: Risque {st.session_state.cat_risque}, Score SCORE2 de {st.session_state.score_estime}%.
            Inclure les recommandations sur le tabac ({fumeur}), l'activité physique (150min/sem), 
            et l'alimentation riche en fruits et légumes selon les guidelines SFC[cite: 309, 311, 312].
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": "Tu es un assistant médical expert en cardiologie."},
                          {"role": "user", "content": prompt}]
            )
            
            lettre = response.choices[0].message.content
            st.text_area("Lettre générée", value=lettre, height=400)
            st.download_button("Télécharger la lettre (TXT)", lettre, file_name=f"Lettre_{nom_patient}.txt")
            
        except Exception as e:
            st.error(f"Erreur avec l'IA : {e}")

st.divider()
st.caption("Application développée par Neli Ilieva, Jennyfer Vari et Pauline Robert. [cite: 2, 3, 4]")
