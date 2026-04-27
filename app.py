import streamlit as st
import pandas as pd
from groq import Groq

# 1. CONFIGURATION
st.set_page_config(page_title="L'Alliance Protectrice - Prévention Cardiaque", layout="wide")

# 2. INITIALISATION DU SESSION STATE
if 'cat_risque' not in st.session_state:
    st.session_state.cat_risque = None
if 'score_estime' not in st.session_state:
    st.session_state.score_estime = 0.0

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

# 4. EN-TÊTE
st.markdown('<div class="header-box">', unsafe_allow_html=True)
st.title("🛡️ L'ALLIANCE PROTECTRICE")
st.subheader("DÉTECTION & PRÉVENTION CARDIAQUE")
st.markdown('</div>', unsafe_allow_html=True)

# 5. BARRE LATÉRALE (Identité Médecin)
with st.sidebar:
    st.header("👨‍⚕️ Identité du Médecin")
    dr_name = st.text_input("Nom du Docteur", value="Pauline Robert")
    specialty = st.text_input("Spécialité", "Médecine Générale")
    cabinet = st.text_input("Cabinet / Service", "Cabinet Médical de l'Alliance")
    
    st.divider()
    st.header("🔑 Configuration IA")
    api_key_groq = st.text_input("Clé API Groq", type="password")

# 6. FORMULAIRE PATIENT
st.header("📋 Paramètres du Patient")
col1, col2, col3 = st.columns(3)

with col1:
    nom_patient = st.text_input("Nom du Patient", placeholder="Jean Dupont")
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

# 8. ANALYSE
st.header("📊 Évaluation")
if st.button("Calculer le risque"):
    score_final = 4.5 # Simulation
    resultat = calculer_risque(age, score_final, atcd_cv, insuffisance_renale, systolique)
    st.session_state.cat_risque = resultat
    st.session_state.score_estime = score_final
    
    st.success(f"Analyse terminée : {resultat}")
    
    if "Très élevé" in resultat: obj_ldl = "< 1.4 mmol/L"
    elif "Élevé" in resultat: obj_ldl = "< 1.8 mmol/L"
    else: obj_ldl = "< 2.6 mmol/L"
    st.info(f"Cible LDL-C : {obj_ldl}")

# 9. GÉNÉRATION DE LA LETTRE COMPLÈTE
st.header("📝 Lettre Personnalisée")
if st.button("Générer la lettre finale"):
    if not api_key_groq:
        st.error("Veuillez saisir votre clé API Groq.")
    elif st.session_state.cat_risque is None:
        st.error("Veuillez d'abord calculer le risque.")
    else:
        try:
            client = Groq(api_key=api_key_groq)
            
            # PROMPT PRÉCIS POUR ÉVITER LES ZONES VIDES
            prompt = f"""
            Rédige une lettre médicale complète et officielle de l'Alliance Protectrice.
            
            INFOS À INTÉGRER :
            - Expéditeur : Dr {dr_name}, {specialty}, {cabinet}.
            - Patient : {nom_patient}, {age} ans.
            - Diagnostic : Risque cardiovasculaire {st.session_state.cat_risque} (Score SCORE2 : {st.session_state.score_estime}%).
            - Statut Tabac : {fumeur}.
            
            RECOMMANDATIONS :
            - Activité physique : minimum 150 min par semaine.
            - Alimentation : Augmenter les fruits et légumes, réduire les graisses saturées.
            - Si fumeur : Arrêt impératif.
            
            CONSIGNE : Ne laisse aucune zone vide. Ne mets pas de crochets []. 
            La lettre doit être prête à être signée et envoyée.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": "Tu es un expert en cardiologie."},
                          {"role": "user", "content": prompt}]
            )
            
            lettre_finale = completion.choices[0].message.content
            st.text_area("Aperçu de la lettre", value=lettre_finale, height=450)
            st.download_button("📥 Télécharger la lettre complète", lettre_finale, file_name=f"Lettre_{nom_patient}.txt")
            
        except Exception as e:
            st.error(f"Erreur : {e}")
