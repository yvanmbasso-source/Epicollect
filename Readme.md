# 🏥 EpiCollect — Système de Suivi Épidémiologique

### TP INF 232 EC2 — Collecte et Analyse Descriptive de Données

-----

## 📌 Domaine choisi : **Santé Publique — Épidémiologie**

Application web de collecte et d’analyse descriptive de données de santé, centrée
sur le suivi épidémiologique en Côte d’Ivoire.

-----

## 🚀 Installation et lancement (local)

```bash
# 1. Cloner ou placer les fichiers dans un dossier
# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'application
streamlit run app.py
```

L’application s’ouvre automatiquement sur **http://localhost:8501**

-----

## 🌐 Déploiement en ligne (Streamlit Cloud — GRATUIT)

1. Créez un compte sur **https://streamlit.io/cloud**
1. Poussez les fichiers (`app.py`, `requirements.txt`) sur un dépôt GitHub public
1. Cliquez **“New app”** → sélectionnez votre dépôt → **Deploy**
1. Votre lien public est généré automatiquement (ex: `https://xxx.streamlit.app`)

-----

## 📋 Fonctionnalités

|Module               |Description                                                      |
|---------------------|-----------------------------------------------------------------|
|🏠 Tableau de bord    |KPIs temps réel, graphiques synthétiques, dernières saisies      |
|📝 Saisie de données  |Formulaire complet avec validation, stockage SQLite              |
|📊 Analyse descriptive|Stats, histogrammes, boxplots, corrélations, évolution temporelle|
|📋 Données collectées |Tableau avec recherche et suppression                            |
|📥 Export             |Téléchargement CSV                                               |

-----

## 🏗️ Architecture technique

- **Langage** : Python
- **Framework web** : Streamlit
- **Base de données** : SQLite (fichier local `epicollect.db`)
- **Librairies** : pandas, numpy, matplotlib, seaborn

-----

## 📊 Analyses descriptives implémentées

1. **Statistiques descriptives** : N, moyenne, écart-type, min, Q1, médiane, Q3, max
1. **Distributions catégorielles** : maladies, sexe, statut, vaccination
1. **Distributions numériques** : âge, température (histogrammes)
1. **Boxplots** : âge par maladie
1. **Matrice de corrélation** : variables numériques
1. **Évolution temporelle** : cas quotidiens

-----

## ✅ Critères de notation

|Critère              |Implémentation                                                |
|---------------------|--------------------------------------------------------------|
|**Idée / Créativité**|Épidémiologie — domaine critique et original                  |
|**Robustesse**       |Validation des saisies, gestion des erreurs, SQLite persistant|
|**Efficacité**       |Interface fluide, filtres dynamiques, KPIs instantanés        |
|**Fiabilité**        |Données persistantes, calculs statistiques exacts             |
