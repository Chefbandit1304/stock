
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Gestion de Stock", layout="centered")

@st.cache_data
def charger_donnees(path):
    xls = pd.ExcelFile(path)
    articles = xls.parse("Articles")
    mouvements = xls.parse("Mouvements")
    return articles, mouvements

# Chargement des données
articles_df, mouvements_df = charger_donnees("catalogue_articles_with_mouvements.xlsx")

st.title("Catalogue & Gestion de Stock")

# Calcul du stock courant
stock_df = mouvements_df.copy()
stock_df["Quantité"] = stock_df.apply(lambda row: row["Quantité"] if row["Type"] == "Entrée" else -row["Quantité"], axis=1)
stock_par_article = stock_df.groupby("Article")["Quantité"].sum().reset_index()
stock_par_article.columns = ["Article", "Stock Disponible"]

# Jointure avec articles
catalogue_stock = pd.merge(articles_df, stock_par_article, how="left", left_on="Nom", right_on="Article")
catalogue_stock["Stock Disponible"] = catalogue_stock["Stock Disponible"].fillna(0).astype(int)

# Affichage du catalogue avec stock
st.subheader("Catalogue des articles")
st.dataframe(catalogue_stock.drop(columns=["Article"]))

# Formulaire de mouvement
st.subheader("Enregistrer une entrée ou sortie de stock")
with st.form("mouvement_form"):
    article = st.selectbox("Article", options=articles_df["Nom"].unique())
    type_mvt = st.radio("Type de mouvement", options=["Entrée", "Sortie"])
    quantite = st.number_input("Quantité", min_value=1, step=1)
    submit = st.form_submit_button("Ajouter le mouvement")

if submit:
    new_mvt = {
        "Article": article,
        "Type": type_mvt,
        "Quantité": quantite,
        "Date": datetime.now()
    }
    mouvements_df = mouvements_df.append(new_mvt, ignore_index=True)
    st.success(f"Mouvement enregistré : {type_mvt} de {quantite}x {article}")

    # Optionnel : afficher nouveau stock
    st.rerun()

# Historique
st.subheader("Historique des mouvements")
st.dataframe(mouvements_df.sort_values(by="Date", ascending=False"))
