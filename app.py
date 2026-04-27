import streamlit as st
import pandas as pd
from openai import OpenAI

# 1. CONFIGURATION DE LA PAGE (Impérativement en premier)
st.set_page_config(page_title="L'Alliance Protectrice - Prévention Cardiaque", layout="wide")

# 2. INITIALISATION DE LA MÉMOIRE (Session State)
# Empêche l'erreur "cat_risque not defined"
if 'cat_risque' not in st.session_state:
    st.session_state.cat_risque = None
if 'score_estime' not in st.session_state:
    st.session_state.score_estime = 0.0

# 3. STYLE CSS PERSONNALISÉ (Couleurs Alliance Protectrice)
st.markdown("""
    <style>
    .main { background-color: #f0f8ff; }
    .stButton>button { background-color: #004d99; color: white; border-radius: 10px; width: 100%; font-weight: bold; }
    .header-box { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 10px solid #004d99; border-right: 10px solid #004d99; margin-bottom: 25px; text-align: center; }
    h1 { color: #004d99; margin-bottom: 0; }
    h2 { color: #0066cc; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# 4. EN-TÊTE ET LOGO
st.markdown('<div class="header-box">', unsafe_allow_html=True)
st.title("🛡️ L'ALLIANCE PROTECTRICE")
st.subheader("DÉTECTION & PRÉVENTION CARDIAQUE")
st.markdown('</div>', unsafe_allow_html=True)

# 5. BARRE LATÉRALE (Médecin & API)
with st.sidebar:
    st.header("👨‍⚕️ Identité du Médecin")
    dr_name = st.text_input("Nom du Docteur", placeholder="ex: Dr. Martin")
    specialty = st.text_input("Spécialité", "Médecine Générale")
    cabinet = st.text_input("Cabinet / Service")
    
    st.divider()
    st.header("🔑 Configuration IA")
    # Remplacez "votre_cle_ici" par votre clé réelle ou laissez vide pour la saisir manuellement
    api_key = st.text_input("Clé API OpenAI", type="password")
    st.info("Utilise le modèle : gpt-4o")

# 6. FORMULAIRE PATIENT
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

# 7. LOGIQUE DE CALCUL (Basée sur vos tableaux SFC)
def estimer_categorie_risque(age, score_value, atcd_cv, insuffisance_renale, systolique):
    if atcd_cv:
        return "Risque très élevé (Prévention secondaire)"
    
    if systolique >= 180 or insuffisance_renale == "<30 mL/min":
        return "Risque très élevé"
    
    if insuffisance_renale == "30-59 mL/min":
        return "Risque élevé"

    # Seuils SCORE2 selon l'âge (Tableau 2.3 B du projet)
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

# 8. SECTION RÉSULTATS
st.header("📊 Évaluation du Risque")
if st.button("Calculer le risque et interpréter"):
    # Score simulé (À remplacer par la formule complète si nécessaire)
    score_final = 4.5 
    
    # Calcul et sauvegarde en session
    resultat = estimer_categorie_risque(age, score_final, atcd_cv, insuffisance_renale, systolique)
    st.session_state.cat_risque = resultat
    st.session_state.score_estime = score_final

    st.divider()
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric(label="Score SCORE2 à 10 ans", value=f"{score_final} %")
    with res_col2:
        st.subheader(f"Catégorie : {resultat}")

    # Objectifs LDL (Tableau Objectifs lipidiques du PDF)
    st.markdown("### 🎯 Objectifs Thérapeutiques")
    if "Très élevé" in resultat:
        obj_ldl = "< 1.4 mmol/L"
    elif "Élevé" in resultat:
        obj_ldl = "< 1.8 mmol/L"
    else:
        obj_ldl = "< 2.6 mmol/L"
    
    st.info(f"**Objectif LDL-C :** {obj_ldl} | **Objectif Tensionnel :** < 140/90 mmHg")

# 9. GÉNÉRATION DE LA LETTRE (Modification gpt-4o ici)
st.header("📝 Lettre de Recommandation (IA)")
if st.button("Générer la lettre avec GPT-4o"):
    if not api_key:
        st.error("Veuillez saisir votre clé API dans la barre latérale.")
    elif st.session_state.cat_risque is None:
        st.error("Veuillez d'abord calculer le risque du patient.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            prompt = f"""
            Rédige une lettre médicale professionnelle de l'Alliance Protectrice.
            Médecin: Dr {dr_name}, {specialty}. Cabinet: {cabinet}.
            Patient: {nom_patient}, {age} ans.
            Situation: Risque {st.session_state.cat_risque}, Score SCORE2 de {st.session_state.score_estime}%.
            Inclure impérativement ces recommandations :
            1. Arrêt du tabac (Statut : {fumeur})
            2. Activité physique >= 150 min / semaine
            3. Alimentation riche en fruits et légumes, réduction graisses saturées.
            Format: Professionnel, bienveillant, structuré.
            """
            
            # UTILISATION DE GPT-4o (pour éviter l'erreur 404)
            response = client.chat.completions.create(
                model="gpt-4o", 
                messages=[
                    {"role": "system", "content": "Tu es un expert cardiologue de l'Alliance Protectrice."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            lettre = response.choices[0].message.content
            st.text_area("Aperçu de la lettre", value=lettre, height=400)
            st.download_button("📥 Télécharger la lettre", lettre, file_name=f"Alliance_Protectrice_{nom_patient}.txt")
            
        except Exception as e:
            st.error(f"Erreur lors de la génération : {e}")

st.divider()
st.caption("Projet médical : Neli Ilieva, Jennyfer Vari, Pauline Robert.")
