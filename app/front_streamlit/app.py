"""Un autre front pour l'application fil rouge, ecrit en Streamlit.

EXEMPLE : le front est libre, et celui-ci montre qu'il peut s'ecrire dans une
autre pile que la page fournie. Une seule regle : il n'appelle QUE les routes de
votre serveur, decrites dans app/CONTRAT.md, jamais le modele.

Streamlit s'execute sur un serveur : techniquement, rien n'empecherait d'y
appeler le modele. C'est justement ce qui est interdit, et verifie par
examen/conformite/test_architecture.py.

Lancer, votre serveur tournant deja sur le port 3000 :
    make front-streamlit
"""
import json
import os
import time

import httpx
import streamlit as st

# L'adresse de VOTRE serveur, pas celle du modele.
API = os.environ.get("API_URL", "http://localhost:3000").rstrip("/")
DELAI = 120


class ErreurApi(Exception):
    """Le serveur a refuse la requete. Son message est affiche tel quel."""


def evenements(route, charge):
    """POST sur une route SSE du contrat. Produit les evenements un par un."""
    try:
        with httpx.stream("POST", f"{API}{route}", json=charge, timeout=DELAI) as r:
            # Une erreur arrive en JSON classique, jamais en SSE : voir le contrat.
            if r.status_code != 200:
                r.read()
                try:
                    message = r.json().get("erreur")
                except ValueError:
                    message = None
                raise ErreurApi(message or f"Le serveur a répondu {r.status_code}.")
            for ligne in r.iter_lines():
                if not ligne.startswith("data: "):
                    continue
                charge_utile = ligne[6:].strip()
                if charge_utile and charge_utile != "[DONE]":
                    yield json.loads(charge_utile)
    except httpx.ConnectError as e:
        raise ErreurApi(f"Aucun serveur ne répond sur {API}. Est-il lancé ?") from e
    except httpx.TimeoutException as e:
        raise ErreurApi(f"Pas de réponse du serveur en {DELAI} secondes.") from e


def interroger(route, charge):
    """Appelle une route et affiche sources, texte au fil du flux, et usage."""
    zone_sources = st.empty()
    debut = time.perf_counter()
    mesures = {}

    def fragments():
        for evt in evenements(route, charge):
            if "sources" in evt:
                zone_sources.markdown("**Sources retenues** : " + ", ".join(
                    f"{s['titre']} `{float(s['score']):.2f}`" for s in evt["sources"]))
            if evt.get("delta"):
                mesures.setdefault("premier", time.perf_counter() - debut)
                yield evt["delta"]
            if evt.get("done"):
                mesures["usage"] = evt.get("usage") or {}

    try:
        texte = st.write_stream(fragments())
    except ErreurApi as e:
        st.error(str(e))
        return
    if not texte:
        st.info("Le serveur a répondu, mais sans aucun fragment.")
    u = mesures.get("usage", {})
    premier = round(mesures["premier"] * 1000) if "premier" in mesures else "?"
    st.caption(f"entrée **{u.get('entree', '?')}** tokens · "
               f"sortie **{u.get('sortie', '?')}** tokens · "
               f"serveur **{u.get('ms', '?')}** ms · "
               f"premier fragment **{premier}** ms")


st.set_page_config(page_title="Assistant support", page_icon="💬")
st.title("Assistant support")
st.caption(f"Front Streamlit : il n'appelle que les routes de {API}.")

resumer, assistant, documents = st.tabs(
    ["Résumer · S9", "Assistant · S10", "Documents · S13"])

with resumer, st.form("resumer"):
    texte = st.text_area("Texte du ticket à résumer",
                         placeholder="Collez ici le message d'un client.")
    ton = st.selectbox("Ton du résumé", ["neutre", "direct"])
    if st.form_submit_button("Résumer"):
        interroger("/api/resumer", {"texte": texte, "ton": ton})

with assistant, st.form("assistant"):
    question = st.text_input("Question sur une commande",
                             placeholder="Où en est la commande CMD-2024-118 ?")
    if st.form_submit_button("Demander"):
        interroger("/api/assistant", {"question": question})

with documents, st.form("documents"):
    question = st.text_input("Question sur la documentation",
                             placeholder="Comment demander un remboursement ?")
    if st.form_submit_button("Chercher"):
        interroger("/api/documents", {"question": question})
