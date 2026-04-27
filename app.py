import streamlit as st
from openai import OpenAI
from fpdf import FPDF

# --- CONFIG PAGE ---
st.set_page_config(
    page_title="CardioProtect",
    page_icon="❤️",
    layout="centered"
)

# --- STYLE CSS ---
st.markdown("""
<style>
body {
    background-color: #f4f8fb;
}
.title {
    text-align: center;
    font-size: 40px;
    font-weight: bold;
    color: #1b4f72;
}
.subtitle {
    text-align: center;
    color: #5d6d7e;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# --- TITRE ---
st.markdown('<div class="title">CardioProtect ❤️</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Prévention cardiovasculaire intelligente</div>', unsafe_allow_html=True)

st.markdown("---")

# --- FORMULAIRE ---
with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)

    age = st.slider("Âge", 30, 80, 50)
    sexe = st.selectbox("Sexe", ["Homme", "Femme"])
    tabac = st.selectbox("Fumeur", ["Non", "Oui"])
    pas = st.number_input("Pression artérielle systolique (mmHg)", 90, 200, 120)
    chol = st.number_input("Cholestérol (mmol/L)", 2.0, 10.0, 5.0)

    st.markdown('</div>', unsafe_allow_html=True)

# --- CALCUL ---
def calcul_score(age, pas, chol, tabac):
    score = (age * 0.1) + (pas * 0.01) + (chol * 0.5)
    if tabac == "Oui":
        score += 2
    return round(score, 2)

def interpretation(score):
    if score < 1:
        return "Bas"
    elif score < 5:
        return "Modéré"
    elif score < 10:
        return "Élevé"
    else:
        return "Très élevé"

# --- BOUTON ---
if st.button("Analyser le risque"):

    score = calcul_score(age, pas, chol, tabac)
    risque = interpretation(score)

    st.success(f"Score estimé : {score}% → Risque {risque}")

    # --- IA ---
    client = OpenAI()

    prompt = f"""
    Rédige une lettre médicale professionnelle.

    Patient : {age} ans, {sexe}
    Tabac : {tabac}
    PAS : {pas}
    Cholestérol : {chol}

    Score cardiovasculaire : {score}% ({risque})

    Inclure :
    - résumé clinique
    - interprétation
    - recommandations
    """

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    texte = response.output_text

    st.markdown("### 📝 Lettre générée")
    st.write(texte)

    # --- PDF ---
    if st.button("Télécharger le PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for line in texte.split("\n"):
            pdf.multi_cell(0, 10, line)

        pdf.output("lettre_patient.pdf")

        with open("lettre_patient.pdf", "rb") as f:
            st.download_button(
                label="📄 Télécharger la lettre",
                data=f,
                file_name="lettre_patient.pdf",
                mime="application/pdf"
            )
