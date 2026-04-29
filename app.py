import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import date, datetime
import sqlite3
import os
import io

# ── Configuration ──────────────────────────────────────────────────────────────

st.set_page_config(
page_title=“EpiCollect — Suivi Épidémiologique”,
page_icon=“🏥”,
layout=“wide”,
initial_sidebar_state=“expanded”,
)

# ── Palette ────────────────────────────────────────────────────────────────────

COLOR_PRIMARY  = “#0A74DA”
COLOR_ACCENT   = “#E63946”
COLOR_SUCCESS  = “#2DC653”
COLOR_WARN     = “#F4A261”
COLOR_BG       = “#F0F4F8”
COLOR_CARD     = “#FFFFFF”
COLOR_TEXT     = “#1A1A2E”
PALETTE        = [COLOR_PRIMARY, COLOR_ACCENT, COLOR_SUCCESS, COLOR_WARN,
“#6A0572”, “#457B9D”, “#F1C40F”, “#1ABC9C”]

# ── CSS ────────────────────────────────────────────────────────────────────────

st.markdown(f”””

<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Space Grotesk', sans-serif;
    background-color: {COLOR_BG};
    color: {COLOR_TEXT};
  }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0A74DA 0%, #023E8A 100%);
    color: white;
  }}
  section[data-testid="stSidebar"] * {{ color: white !important; }}
  section[data-testid="stSidebar"] .stSelectbox label,
  section[data-testid="stSidebar"] .stRadio label {{ color: white !important; }}

  /* Metric cards */
  .metric-card {{
    background: {COLOR_CARD};
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 4px 16px rgba(10,116,218,.12);
    border-left: 5px solid {COLOR_PRIMARY};
    margin-bottom: 12px;
  }}
  .metric-card h2 {{ margin: 0; font-size: 2rem; font-weight: 700; color: {COLOR_PRIMARY}; }}
  .metric-card p  {{ margin: 4px 0 0; font-size: .85rem; color: #555; }}

  /* Section titles */
  .section-title {{
    font-size: 1.3rem; font-weight: 700;
    border-bottom: 3px solid {COLOR_PRIMARY};
    padding-bottom: 6px; margin: 24px 0 16px;
    color: {COLOR_TEXT};
  }}

  /* Success / warning banners */
  .banner-ok  {{ background:#D4EDDA; border-left:5px solid {COLOR_SUCCESS}; border-radius:8px; padding:12px 16px; }}
  .banner-err {{ background:#F8D7DA; border-left:5px solid {COLOR_ACCENT};  border-radius:8px; padding:12px 16px; }}

  /* Header strip */
  .app-header {{
    background: linear-gradient(90deg, #0A74DA, #023E8A);
    color: white; border-radius: 14px;
    padding: 28px 36px; margin-bottom: 28px;
  }}
  .app-header h1 {{ margin:0; font-size:2rem; font-weight:700; }}
  .app-header p  {{ margin:4px 0 0; opacity:.85; font-size:.95rem; }}
</style>

“””, unsafe_allow_html=True)

# ── Database ────────────────────────────────────────────────────────────────────

DB_PATH = “epicollect.db”

def get_conn():
return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
conn = get_conn()
conn.execute(”””
CREATE TABLE IF NOT EXISTS patients (
id          INTEGER PRIMARY KEY AUTOINCREMENT,
date_saisie TEXT    NOT NULL,
nom         TEXT    NOT NULL,
prenom      TEXT    NOT NULL,
age         INTEGER NOT NULL,
sexe        TEXT    NOT NULL,
region      TEXT    NOT NULL,
maladie     TEXT    NOT NULL,
statut      TEXT    NOT NULL,
temperature REAL,
tension_sys INTEGER,
tension_dia INTEGER,
hospitalise INTEGER NOT NULL DEFAULT 0,
vaccin      TEXT    NOT NULL,
symptomes   TEXT,
notes       TEXT
)”””)
conn.commit()
conn.close()

init_db()

def load_data() -> pd.DataFrame:
conn = get_conn()
df = pd.read_sql(“SELECT * FROM patients ORDER BY id DESC”, conn)
conn.close()
if not df.empty:
df[“date_saisie”] = pd.to_datetime(df[“date_saisie”])
return df

def insert_patient(data: dict):
conn = get_conn()
conn.execute(”””
INSERT INTO patients
(date_saisie, nom, prenom, age, sexe, region, maladie, statut,
temperature, tension_sys, tension_dia, hospitalise, vaccin, symptomes, notes)
VALUES
(:date_saisie,:nom,:prenom,:age,:sexe,:region,:maladie,:statut,
:temperature,:tension_sys,:tension_dia,:hospitalise,:vaccin,:symptomes,:notes)
“””, data)
conn.commit()
conn.close()

def delete_patient(pid: int):
conn = get_conn()
conn.execute(“DELETE FROM patients WHERE id=?”, (pid,))
conn.commit()
conn.close()

# ── Helpers ────────────────────────────────────────────────────────────────────

MALADIES  = [“Paludisme”,“Dengue”,“Tuberculose”,“VIH/SIDA”,“Choléra”,
“COVID-19”,“Typhoïde”,“Méningite”,“Rougeole”,“Autre”]
REGIONS   = [“Abidjan”,“Bouaké”,“Daloa”,“Korhogo”,“San-Pédro”,
“Yamoussoukro”,“Man”,“Gagnoa”,“Divo”,“Autre”]
STATUTS   = [“Confirmé”,“Suspect”,“Guéri”,“Décédé”,“En traitement”]
VACCINS   = [“Complètement vacciné”,“Partiellement vacciné”,“Non vacciné”,“Inconnu”]
SYMPTOMES = [“Fièvre”,“Toux”,“Maux de tête”,“Vomissements”,“Diarrhée”,
“Éruption cutanée”,“Fatigue”,“Difficultés respiratoires”]

def fig_to_buf(fig):
buf = io.BytesIO()
fig.savefig(buf, format=“png”, bbox_inches=“tight”, dpi=130)
buf.seek(0)
return buf

# ══════════════════════════════════════════════════════════════════════════════

# SIDEBAR NAVIGATION

# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
st.markdown(”## 🏥 EpiCollect”)
st.markdown(”*Suivi Épidémiologique*”)
st.markdown(”—”)
page = st.radio(“Navigation”, [
“🏠 Accueil / Tableau de bord”,
“📝 Saisie de données”,
“📊 Analyse descriptive”,
“📋 Données collectées”,
“📥 Export des données”,
])
st.markdown(”—”)
st.markdown(”**INF 232 — EC2**\nAnalyse de données\n\n👨‍🎓 TP — Collecte & Analyse”)

# ══════════════════════════════════════════════════════════════════════════════

# PAGE 1 : TABLEAU DE BORD

# ══════════════════════════════════════════════════════════════════════════════

if page == “🏠 Accueil / Tableau de bord”:
st.markdown(”””
<div class="app-header">
<h1>🏥 EpiCollect — Système de Suivi Épidémiologique</h1>
<p>Collecte, gestion et analyse descriptive des données de santé publique · Côte d’Ivoire</p>
</div>
“””, unsafe_allow_html=True)

```
df = load_data()

if df.empty:
    st.info("Aucune donnée disponible. Commencez par saisir des patients via le menu **Saisie de données**.")
else:
    total        = len(df)
    gueris       = (df["statut"] == "Guéri").sum()
    decedes      = (df["statut"] == "Décédé").sum()
    hospitalises = df["hospitalise"].sum()
    taux_guerison = round(gueris / total * 100, 1) if total else 0
    taux_letal    = round(decedes / total * 100, 1) if total else 0

    # KPI cards
    c1, c2, c3, c4 = st.columns(4)
    for col, val, label, border in [
        (c1, total,        "Total patients enregistrés", COLOR_PRIMARY),
        (c2, gueris,       f"Guéris  ({taux_guerison} %)",  COLOR_SUCCESS),
        (c3, decedes,      f"Décès   ({taux_letal} %)",     COLOR_ACCENT),
        (c4, int(hospitalises), "Hospitalisés",             COLOR_WARN),
    ]:
        col.markdown(f"""
        <div class="metric-card" style="border-left-color:{border}">
          <h2>{val}</h2>
          <p>{label}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Two mini-charts
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<p class="section-title">Répartition par maladie</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(5, 4))
        counts = df["maladie"].value_counts()
        wedges, texts, autotexts = ax.pie(
            counts.values, labels=counts.index,
            autopct="%1.1f%%", colors=PALETTE[:len(counts)],
            startangle=140, pctdistance=0.8
        )
        for t in autotexts: t.set_fontsize(8)
        ax.set_title("Maladies", fontweight="bold")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col_b:
        st.markdown('<p class="section-title">Cas par région</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(5, 4))
        reg = df["region"].value_counts()
        bars = ax.barh(reg.index, reg.values, color=PALETTE[:len(reg)], edgecolor="white")
        ax.bar_label(bars, padding=4, fontsize=8)
        ax.set_xlabel("Nombre de cas")
        ax.set_title("Régions", fontweight="bold")
        ax.invert_yaxis()
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    # Derniers enregistrements
    st.markdown('<p class="section-title">5 dernières saisies</p>', unsafe_allow_html=True)
    cols_show = ["date_saisie","nom","prenom","age","sexe","region","maladie","statut"]
    st.dataframe(df[cols_show].head(5).rename(columns={
        "date_saisie":"Date","nom":"Nom","prenom":"Prénom",
        "age":"Âge","sexe":"Sexe","region":"Région",
        "maladie":"Maladie","statut":"Statut"
    }), use_container_width=True)
```

# ══════════════════════════════════════════════════════════════════════════════

# PAGE 2 : SAISIE

# ══════════════════════════════════════════════════════════════════════════════

elif page == “📝 Saisie de données”:
st.markdown(’<p class="section-title">📝 Formulaire de saisie patient</p>’, unsafe_allow_html=True)

```
with st.form("form_patient", clear_on_submit=True):
    st.markdown("#### Informations personnelles")
    c1, c2, c3 = st.columns(3)
    nom    = c1.text_input("Nom *")
    prenom = c2.text_input("Prénom *")
    age    = c3.number_input("Âge *", min_value=0, max_value=120, value=25)

    c4, c5 = st.columns(2)
    sexe   = c4.selectbox("Sexe *", ["Masculin","Féminin","Autre"])
    region = c5.selectbox("Région *", REGIONS)

    st.markdown("#### Données cliniques")
    c6, c7 = st.columns(2)
    maladie = c6.selectbox("Maladie *", MALADIES)
    statut  = c7.selectbox("Statut *", STATUTS)

    c8, c9, c10 = st.columns(3)
    temperature  = c8.number_input("Température (°C)", min_value=34.0, max_value=42.0, value=37.0, step=0.1)
    tension_sys  = c9.number_input("Tension systolique (mmHg)", min_value=60, max_value=250, value=120)
    tension_dia  = c10.number_input("Tension diastolique (mmHg)", min_value=40, max_value=150, value=80)

    c11, c12 = st.columns(2)
    hospitalise = c11.checkbox("Hospitalisé ?")
    vaccin      = c12.selectbox("Statut vaccinal *", VACCINS)

    symptomes_sel = st.multiselect("Symptômes observés", SYMPTOMES)
    notes         = st.text_area("Notes complémentaires", height=80)

    submitted = st.form_submit_button("💾 Enregistrer le patient", use_container_width=True)

if submitted:
    errors = []
    if not nom.strip():   errors.append("Le nom est obligatoire.")
    if not prenom.strip(): errors.append("Le prénom est obligatoire.")
    if age == 0:           errors.append("L'âge doit être supérieur à 0.")

    if errors:
        for e in errors:
            st.markdown(f'<div class="banner-err">❌ {e}</div>', unsafe_allow_html=True)
    else:
        insert_patient({
            "date_saisie": datetime.now().isoformat(),
            "nom":         nom.strip().upper(),
            "prenom":      prenom.strip().capitalize(),
            "age":         age,
            "sexe":        sexe,
            "region":      region,
            "maladie":     maladie,
            "statut":      statut,
            "temperature": temperature,
            "tension_sys": tension_sys,
            "tension_dia": tension_dia,
            "hospitalise": int(hospitalise),
            "vaccin":      vaccin,
            "symptomes":   ", ".join(symptomes_sel),
            "notes":       notes.strip(),
        })
        st.markdown('<div class="banner-ok">✅ Patient enregistré avec succès !</div>', unsafe_allow_html=True)
        st.balloons()
```

# ══════════════════════════════════════════════════════════════════════════════

# PAGE 3 : ANALYSE DESCRIPTIVE

# ══════════════════════════════════════════════════════════════════════════════

elif page == “📊 Analyse descriptive”:
st.markdown(’<p class="section-title">📊 Analyse descriptive des données</p>’, unsafe_allow_html=True)

```
df = load_data()
if df.empty:
    st.warning("Aucune donnée à analyser. Veuillez d'abord saisir des patients.")
    st.stop()

# ── Filtres ──
with st.expander("🔍 Filtres"):
    f_maladie = st.multiselect("Maladie", MALADIES, default=df["maladie"].unique().tolist())
    f_region  = st.multiselect("Région",  REGIONS,  default=df["region"].unique().tolist())
    f_statut  = st.multiselect("Statut",  STATUTS,  default=df["statut"].unique().tolist())

mask = (
    df["maladie"].isin(f_maladie) &
    df["region"].isin(f_region) &
    df["statut"].isin(f_statut)
)
dff = df[mask].copy()

if dff.empty:
    st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    st.stop()

st.markdown(f"**{len(dff)} enregistrements** analysés")

# ── 1. Statistiques descriptives numériques ──
st.markdown('<p class="section-title">1. Statistiques descriptives</p>', unsafe_allow_html=True)
num_cols = ["age","temperature","tension_sys","tension_dia"]
desc = dff[num_cols].describe().round(2)
desc.index = ["N","Moyenne","Écart-type","Min","Q1","Médiane","Q3","Max"]
desc.columns = ["Âge","Température (°C)","Tension sys.","Tension dia."]
st.dataframe(desc, use_container_width=True)

# ── 2. Distribution des variables catégorielles ──
st.markdown('<p class="section-title">2. Distributions catégorielles</p>', unsafe_allow_html=True)
r1c1, r1c2 = st.columns(2)

with r1c1:
    fig, ax = plt.subplots(figsize=(6, 4))
    counts = dff["maladie"].value_counts()
    bars = ax.bar(counts.index, counts.values, color=PALETTE[:len(counts)], edgecolor="white", linewidth=1.2)
    ax.bar_label(bars, padding=3, fontsize=9, fontweight="bold")
    ax.set_title("Cas par maladie", fontweight="bold", fontsize=12)
    ax.set_xlabel("Maladie"); ax.set_ylabel("Effectif")
    plt.xticks(rotation=30, ha="right", fontsize=8)
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)

with r1c2:
    fig, ax = plt.subplots(figsize=(6, 4))
    sex_stat = dff.groupby(["maladie","sexe"]).size().unstack(fill_value=0)
    sex_stat.plot(kind="bar", ax=ax, color=PALETTE[:sex_stat.shape[1]], edgecolor="white")
    ax.set_title("Cas par maladie et sexe", fontweight="bold", fontsize=12)
    ax.set_xlabel(""); ax.set_ylabel("Effectif")
    plt.xticks(rotation=30, ha="right", fontsize=8)
    ax.legend(title="Sexe", fontsize=8)
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)

r2c1, r2c2 = st.columns(2)

with r2c1:
    fig, ax = plt.subplots(figsize=(6, 4))
    stat_counts = dff["statut"].value_counts()
    wedges, texts, autotexts = ax.pie(
        stat_counts.values, labels=stat_counts.index,
        autopct="%1.1f%%", colors=PALETTE[:len(stat_counts)],
        startangle=90, pctdistance=0.82,
        wedgeprops=dict(edgecolor="white", linewidth=2)
    )
    for t in autotexts: t.set_fontsize(9)
    ax.set_title("Répartition par statut", fontweight="bold", fontsize=12)
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)

with r2c2:
    fig, ax = plt.subplots(figsize=(6, 4))
    vacc_counts = dff["vaccin"].value_counts()
    colors_v = [COLOR_SUCCESS, COLOR_WARN, COLOR_ACCENT, "#999"][:len(vacc_counts)]
    ax.barh(vacc_counts.index, vacc_counts.values, color=colors_v, edgecolor="white")
    ax.bar_label(ax.containers[0], padding=4, fontsize=9, fontweight="bold")
    ax.set_title("Statut vaccinal", fontweight="bold", fontsize=12)
    ax.set_xlabel("Effectif")
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)

# ── 3. Distributions numériques ──
st.markdown('<p class="section-title">3. Distributions des variables numériques</p>', unsafe_allow_html=True)
r3c1, r3c2 = st.columns(2)

with r3c1:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(dff["age"].dropna(), bins=15, color=COLOR_PRIMARY, edgecolor="white", alpha=0.85)
    ax.axvline(dff["age"].mean(), color=COLOR_ACCENT, linewidth=2, linestyle="--", label=f"Moyenne: {dff['age'].mean():.1f}")
    ax.set_title("Distribution de l'âge", fontweight="bold", fontsize=12)
    ax.set_xlabel("Âge"); ax.set_ylabel("Fréquence")
    ax.legend(fontsize=9)
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)

with r3c2:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(dff["temperature"].dropna(), bins=12, color=COLOR_ACCENT, edgecolor="white", alpha=0.85)
    ax.axvline(dff["temperature"].mean(), color=COLOR_PRIMARY, linewidth=2, linestyle="--",
               label=f"Moyenne: {dff['temperature'].mean():.1f}°C")
    ax.set_title("Distribution de la température", fontweight="bold", fontsize=12)
    ax.set_xlabel("Température (°C)"); ax.set_ylabel("Fréquence")
    ax.legend(fontsize=9)
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)

# ── 4. Boxplots ──
st.markdown('<p class="section-title">4. Boxplots — Âge par maladie</p>', unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(12, 5))
groups  = [dff[dff["maladie"] == m]["age"].dropna().values for m in dff["maladie"].unique()]
labels  = list(dff["maladie"].unique())
bp = ax.boxplot(groups, labels=labels, patch_artist=True, notch=False,
                medianprops=dict(color="white", linewidth=2.5))
for patch, color in zip(bp["boxes"], PALETTE):
    patch.set_facecolor(color)
    patch.set_alpha(0.75)
ax.set_title("Distribution de l'âge par maladie", fontweight="bold", fontsize=13)
ax.set_xlabel("Maladie"); ax.set_ylabel("Âge")
plt.xticks(rotation=20, ha="right")
fig.tight_layout(); st.pyplot(fig); plt.close(fig)

# ── 5. Corrélations ──
st.markdown('<p class="section-title">5. Matrice de corrélation</p>', unsafe_allow_html=True)
corr = dff[num_cols].corr().round(2)
fig, ax = plt.subplots(figsize=(6, 4))
sns.heatmap(corr, annot=True, fmt=".2f", cmap="Blues", ax=ax,
            linewidths=0.5, linecolor="white",
            annot_kws={"size": 11, "weight": "bold"})
ax.set_title("Corrélation entre variables numériques", fontweight="bold", fontsize=12)
ax.set_xticklabels(["Âge","Temp.","T.sys","T.dia"], rotation=30)
ax.set_yticklabels(["Âge","Temp.","T.sys","T.dia"], rotation=0)
fig.tight_layout(); st.pyplot(fig); plt.close(fig)

# ── 6. Évolution temporelle ──
if "date_saisie" in dff.columns and dff["date_saisie"].notna().sum() > 1:
    st.markdown('<p class="section-title">6. Évolution temporelle des cas</p>', unsafe_allow_html=True)
    dff2 = dff.copy()
    dff2["date_j"] = dff2["date_saisie"].dt.date
    evol = dff2.groupby("date_j").size().reset_index(name="cas")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.fill_between(evol["date_j"], evol["cas"], alpha=0.2, color=COLOR_PRIMARY)
    ax.plot(evol["date_j"], evol["cas"], color=COLOR_PRIMARY, linewidth=2.5, marker="o", markersize=5)
    ax.set_title("Évolution quotidienne des cas enregistrés", fontweight="bold", fontsize=12)
    ax.set_xlabel("Date"); ax.set_ylabel("Nombre de cas")
    fig.tight_layout(); st.pyplot(fig); plt.close(fig)
```

# ══════════════════════════════════════════════════════════════════════════════

# PAGE 4 : DONNÉES COLLECTÉES

# ══════════════════════════════════════════════════════════════════════════════

elif page == “📋 Données collectées”:
st.markdown(’<p class="section-title">📋 Base de données patients</p>’, unsafe_allow_html=True)

```
df = load_data()
if df.empty:
    st.info("Aucun patient enregistré.")
else:
    # Recherche rapide
    search = st.text_input("🔍 Rechercher (nom, prénom, maladie, région…)")
    if search:
        mask = df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        df_view = df[mask]
    else:
        df_view = df.copy()

    st.markdown(f"**{len(df_view)} enregistrement(s)**")
    st.dataframe(df_view.drop(columns=["id"]).rename(columns={
        "date_saisie":"Date","nom":"Nom","prenom":"Prénom",
        "age":"Âge","sexe":"Sexe","region":"Région","maladie":"Maladie",
        "statut":"Statut","temperature":"Temp. (°C)","tension_sys":"T.sys",
        "tension_dia":"T.dia","hospitalise":"Hospitalisé",
        "vaccin":"Vaccin","symptomes":"Symptômes","notes":"Notes"
    }), use_container_width=True, height=400)

    # Suppression
    st.markdown("---")
    st.markdown("#### Supprimer un enregistrement")
    ids = df["id"].tolist()
    del_id = st.selectbox("Sélectionner l'ID à supprimer", ids)
    row = df[df["id"] == del_id].iloc[0]
    st.info(f"Patient sélectionné : **{row['nom']} {row['prenom']}** — {row['maladie']} ({row['statut']})")
    if st.button("🗑️ Supprimer cet enregistrement", type="primary"):
        delete_patient(del_id)
        st.success("Enregistrement supprimé.")
        st.rerun()
```

# ══════════════════════════════════════════════════════════════════════════════

# PAGE 5 : EXPORT

# ══════════════════════════════════════════════════════════════════════════════

elif page == “📥 Export des données”:
st.markdown(’<p class="section-title">📥 Export des données</p>’, unsafe_allow_html=True)

```
df = load_data()
if df.empty:
    st.warning("Aucune donnée à exporter.")
else:
    st.markdown(f"**{len(df)} enregistrements** disponibles pour l'export.")

    # CSV
    csv_data = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="⬇️ Télécharger en CSV",
        data=csv_data,
        file_name=f"epicollect_{date.today()}.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("---")
    st.markdown("#### Aperçu des données")
    st.dataframe(df.head(20), use_container_width=True)
```
