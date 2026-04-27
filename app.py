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

# 5. BARRE LATÉRALE (Identité Médecin - Remplissage par défaut pour éviter le vide)
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
    score_final = 4.5 # Score simulé SCORE2
    resultat = calculer_risque(age, score_final, atcd_cv, insuffisance_renale, systolique)
    st.session_state.cat_risque = resultat
    st.session_state.score_estime = score_final
    
    st.success(f"Analyse terminée : {resultat}")
    
    if "Très élevé" in resultat: obj_ldl = "< 1.4 mmol/L"
    elif "Élevé" in resultat: obj_ldl = "< 1.8 mmol/L"
    else: obj_ldl = "< 2.6 mmol/L"
    st.info(f"Cible LDL-C recommandée : {obj_ldl}")

# 9. GÉNÉRATION DE LA LETTRE ENTIÈREMENT REMPLIE
st.header("📝 Lettre Personnalisée Finale")
if st.button("Générer la lettre complète"):
    if not api_key_groq:
        st.error("Veuillez saisir votre clé API Groq dans la barre latérale.")
    elif st.session_state.cat_risque is None:
        st.error("Veuillez d'abord cliquer sur 'Calculer le risque' pour définir le profil du patient.")
    else:
        try:
            client = Groq(api_key=api_key_groq)
            
            # CALCUL DE L'OBJECTIF POUR L'IA
            if "Très élevé" in st.session_state.cat_risque: obj_ldl_ia = "inférieur à 1.4 mmol/L"
            elif "Élevé" in st.session_state.cat_risque: obj_ldl_ia = "inférieur à 1.8 mmol/L"
            else: obj_ldl_ia = "inférieur à 2.6 mmol/L"

            # PROMPT ULTRA-STRICT POUR ÉVITER LES CHAMPS VIDES
            prompt = f"""
            Rédige une lettre médicale de recommandation officielle. 
            TU NE DOIS LAISSER AUCUN TEXTE ENTRE CROCHETS []. TU DOIS REMPLIR CHAQUE ZONE.

            Voici les informations obligatoires à utiliser pour construire la lettre :
            - EXPÉDITEUR : Dr {dr_name}, spécialiste en {specialty}, exerçant au {cabinet}.
            - DESTINATAIRE : {nom_patient}, âgé de {age} ans.
            - BILAN : Le risque cardiovasculaire est classé comme '{st.session_state.cat_risque}' avec un score SCORE2 de {st.session_state.score_estime}%.
            - PARAMÈTRES : Tension artérielle à {systolique} mmHg et cholestérol non-HDL à {chol_non_hdl} mmol/L.
            - TABAC : Le patient est {fumeur if fumeur == 'Oui' else 'non-fumeur'}.
            - OBJECTIF : La cible de cholestérol LDL-C doit être {obj_ldl_ia}.

            CONSIGNES DE RÉDACTION :
            1. Commence par l'en-tête de l'Alliance Protectrice.
            2. Rédige une introduction expliquant le bilan.
            3. Liste les conseils hygiéno-diététiques (sport 150min/semaine, alimentation).
            4. Si le patient est fumeur, insiste sur l'arrêt immédiat. Sinon, félicite-le.
            5. Signe la lettre au nom de Dr {dr_name}.
            
            INTERDICTION ABSOLUE de mettre des mentions comme '[Nom du patient]' ou '[Date]'. Utilise les données fournies ci-dessus.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Tu es un cardiologue expert qui rédige des rapports finaux parfaits, sans aucun champ manquant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            lettre_finale = completion.choices[0].message.content
            st.text_area("Aperçu de la lettre (Vérifiez qu'elle est complète)", value=lettre_finale, height=500)
            st.download_button("📥 Télécharger la lettre (TXT)", lettre_finale, file_name=f"Lettre_Alliance_{nom_patient}.txt")
            
        except Exception as e:
            st.error(f"Erreur de génération : {e}")

st.divider()
st.caption("Projet L'Alliance Protectrice - Développé par Neli Ilieva, Jennyfer Vari et Pauline Robert.")
