
import streamlit as st
import pandas as pd
from datetime import date, datetime
import os
from sentence_transformers import SentenceTransformer, util
# Configuration à faire **une seule fois et tout en haut**
st.set_page_config(page_title="Agent d'Accueil", layout="centered")
# === Fichier Excel ===
FICHIER_EXCEL = "C:\\Users\\lamiae\\Downloads\\chatbot_patient_app\\patients.xlsx"

def enregistrer_patient(nom, prenom, date_naissance, motifs):
    # Vérification des champs obligatoires
    if not nom or not prenom:
        return "⚠️ Les champs Nom et Prénom sont obligatoires."
    
    # Lecture ou création du fichier
    if os.path.exists(FICHIER_EXCEL):
        df = pd.read_excel(FICHIER_EXCEL)
    else:
        df = pd.DataFrame(columns=["ID", "Nom", "Prénom", "Date de naissance", 
                                   "Motif", "Date d'enregistrement"])
    
    # Génération d'un nouvel ID (auto-incrémenté)
    nouvel_id = df["ID"].max() + 1 if not df.empty else 1

    # Formater les motifs
    motif_texte = ", ".join(motifs) if isinstance(motifs, list) else str(motifs)

    # Création de la nouvelle entrée
    nouvelle_entree = {
        "ID": nouvel_id,
        "Nom": nom,
        "Prénom": prenom,
        "Date de naissance": date_naissance,
        "Motif": motif_texte,
        "Date d'enregistrement": datetime.today().strftime('%Y-%m-%d')
    }

    # Ajout et sauvegarde
    df = pd.concat([df, pd.DataFrame([nouvelle_entree])], ignore_index=True)
    df.to_excel(FICHIER_EXCEL, index=False)

    return f"✅ Patient {nom} {prenom} enregistré avec succès (ID {nouvel_id})."




# Charger un modèle de type BERT pour les embeddings
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# === FAQ DxCare ===
faq_dxcare = {
    "ajouter un compte rendu": [
        "1. Ouvrez DxCare.",
        "2. Allez dans 'Dossier médical'.",
        "3. Cliquez sur 'Ajouter un compte rendu'.",
        "4. Remplissez les champs requis et enregistrez."
    ],
    "créer un dossier patient": [
        "1. Dans l'accueil, cliquez sur 'Nouveau patient'.",
        "2. Entrez les informations personnelles du patient.",
        "3. Cliquez sur 'Créer le dossier'."
    ],
    "prescrire un médicament": [
        "1. Accédez au dossier du patient.",
        "2. Cliquez sur l'onglet 'Prescriptions'.",
        "3. Recherchez le médicament et ajoutez-le.",
        "4. Enregistrez la prescription."
    ],
    "planifier un rendez-vous": [
        "1. Accédez au planning.",
        "2. Sélectionnez un créneau disponible.",
        "3. Choisissez le patient et le motif.",
        "4. Validez le rendez-vous."
    ],
    "ajouter un document scanné": [
        "1. Allez dans le dossier patient.",
        "2. Cliquez sur 'Documents'.",
        "3. Cliquez sur 'Ajouter un document'.",
        "4. Sélectionnez et importez le fichier PDF ou image."
    ],
    "générer une ordonnance": [
        "1. Ouvrez le dossier patient.",
        "2. Accédez à 'Ordonnances'.",
        "3. Cliquez sur 'Nouvelle ordonnance'.",
        "4. Remplissez les détails et validez."
    ],
    "modifier les informations du patient": [
        "1. Accédez à la fiche patient.",
        "2. Cliquez sur 'Modifier'.",
        "3. Modifiez les informations nécessaires.",
        "4. Cliquez sur 'Enregistrer'."
    ],
    "exporter un dossier patient": [
        "1. Accédez au dossier du patient.",
        "2. Cliquez sur 'Exporter'.",
        "3. Choisissez le format (PDF, ZIP, etc.).",
        "4. Cliquez sur 'Télécharger'."
    ],
    "imprimer un compte rendu": [
        "1. Allez dans le dossier du patient.",
        "2. Cliquez sur le compte rendu à imprimer.",
        "3. Cliquez sur l’icône 'Imprimer'.",
        "4. Choisissez l’imprimante et validez."
    ],
    "créer un certificat médical": [
        "1. Allez dans l’onglet 'Documents administratifs'.",
        "2. Cliquez sur 'Nouveau certificat'.",
        "3. Remplissez les informations nécessaires.",
        "4. Signez et enregistrez."
    ],
    "envoyer un document par messagerie sécurisée": [
        "1. Sélectionnez le document depuis le dossier patient.",
        "2. Cliquez sur 'Partager' ou 'Envoyer'.",
        "3. Choisissez 'Messagerie sécurisée'.",
        "4. Sélectionnez le destinataire et envoyez."
    ], 
    "afficher les antécédents médicaux et chirurgicaux": [
        "1. Accédez au dossier du patient.",
        "2. Ouvrez l’onglet 'Antécédents'.",
        "3. Sélectionnez 'Médicaux' ou 'Chirurgicaux' pour consulter l'historique.",
    ],
    "consulter les allergies et traitements en cours": [
        "1. Accédez au dossier patient.",
        "2. Cliquez sur l’onglet 'Traitements en cours'.",
        "3. Les allergies sont généralement visibles dans l’encadré supérieur ou dans 'Antécédents'.",
    ],
    "accéder aux courriers médicaux et comptes rendus d’hospitalisation": [
        "1. Allez dans 'Documents cliniques' dans le dossier patient.",
        "2. Recherchez les documents par type : 'Courriers médicaux' ou 'CR d’hospitalisation'.",
        "3. Cliquez sur un document pour le consulter ou l’imprimer.",
    ],
    "voir l’historique des consultations et diagnostics": [
        "1. Ouvrez le dossier patient.",
        "2. Allez dans l’onglet 'Historique'.",
        "3. Vous verrez la liste des consultations, séjours et diagnostics posés.",
    ]
}


# Transformer toutes les questions en vecteurs
questions_connues = list(faq_dxcare.keys())
embeddings_connus = model.encode(questions_connues, convert_to_tensor=True)

def suggérer_question(user_input):
    # Encoder la question de l’utilisateur
    embedding_input = model.encode(user_input, convert_to_tensor=True)

    # Calculer la similarité cosinus
    scores = util.pytorch_cos_sim(embedding_input, embeddings_connus)[0]

    # Trouver la question la plus similaire
    meilleur_score_idx = scores.argmax()
    meilleure_question = questions_connues[meilleur_score_idx]

    # Seulement si le score est suffisamment élevé (> 0.6 par exemple)
    if scores[meilleur_score_idx] > 0.6:
        return meilleure_question
    else:
        return None
# === Interface Streamlit ===
# Onglet sélectionné
onglet = st.sidebar.radio("Choisissez une action", ["Enregistrer un patient", "Assistance DxCare"])

# Titre dynamique selon l’onglet
if onglet == "Enregistrer un patient":
    st.title("👩‍⚕️ Agent d'Accueil - Enregistrement")
else:
    st.title("🩺 DxCare Assist")


if onglet == "Enregistrer un patient":
    st.subheader("📝 Enregistrement d'un nouveau patient")
    with st.form("form_patient"):
        nom = st.text_input("Nom")
        prenom = st.text_input("Prénom")
        date_naissance = st.date_input("Date de naissance", min_value=date(1900, 1, 1),max_value=date.today())
        motif = st.selectbox("Motif de visite", ["Vaccination", "Médecin", "Pharmacie"])
        submitted = st.form_submit_button("Enregistrer")

        if submitted:
            message = enregistrer_patient(nom, prenom, date_naissance.strftime("%Y-%m-%d"),[motif])
            st.success(message)

elif onglet == "Assistance DxCare":
    st.subheader("🤖 Assistance sur DxCare")
    st.markdown("### 💬 Bonjour, je peux vous aider sur l'une des options suivantes :")

col1, col2 = st.columns(2)

suggestions = [
    "📁 Dossier Patient : historique, traitements, diagnostics...",
    "💊 Prescription : médicaments, alertes, soins...",
    "🩺 Suivi des soins : actes réalisés, planification...",
    "🧪 Examens : résultats biologiques et imagerie...",
    "📆 Planification : hospitalisations, lits, transferts...",
    "🔐 Sécurité : traçabilité, contrôle d’accès, RGPD...",
    "🧠 Aide à la décision : scores, protocoles, alertes...",
    "📊 Reporting : tableaux de bord, indicateurs de qualité..."
]

# Répartition en deux colonnes
for i, suggestion in enumerate(suggestions):
    if i % 2 == 0:
        col1.markdown(f" {suggestion}")
    else:
        col2.markdown(f" {suggestion}")

    
question = st.text_input("Posez une question (ex: 'ajouter un compte rendu')")
     
# Traitement de la question de l'utilisateur
if question:
    trouve = False

    # 1. Recherche exacte ou par inclusion de terme
    for terme, reponses in faq_dxcare.items():
        if terme in question.lower():
            st.write("Voici les étapes :")
            for ligne in reponses:
                st.markdown(f"{ligne}")
            trouve = True
            break

    # 2. Sinon, essayer de suggérer une question proche
    if not trouve:
        suggestion = suggérer_question(question)
        if suggestion:
            st.info(f"Voulez-vous dire : **{suggestion}** ?")
            st.write("Voici les étapes :")
            for ligne in faq_dxcare[suggestion]:
                st.markdown(f"{ligne}")
        else:
            st.warning("Désolé, je n'ai pas compris cette question. Essayez une autre.")