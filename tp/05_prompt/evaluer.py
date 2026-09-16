#!/usr/bin/env python3
"""Atelier de la seance 5 : mesurer un prompt de classification.

Vous ne modifiez QUE la constante CONSIGNE. Tout le reste est l'instrument de
mesure : y toucher fausserait la comparaison.

    python3 tp/05_prompt/evaluer.py

Jumeau exact de evaluer.mjs : meme jeu de cas, meme score.
"""
import json
import os
import pathlib
import sys
import urllib.request

BASE = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
MODELE = os.environ.get("MODEL_BASE", "qwen2.5:3b")
CAS = json.loads((pathlib.Path(__file__).parent / "cas.json").read_text(encoding="utf-8"))

# =====================================================================
# LA SEULE CHOSE QUE VOUS MODIFIEZ
# =====================================================================
CONSIGNE = (
    "Tu es un classifieur strict de tickets de support client. "
    "Pour le texte du ticket fourni, determine sa categorie et son urgence selon les regles ci-dessous. "
    "Ne donne aucune explication, uniquement l'objet JSON demande.\n\n"
    "CATEGORIES (choisis-en une seule) :\n"
    "- paiement : carte bancaire, prelevement, facture, remboursement, virement, paiement refuse ou bloque.\n"
    "- livraison : colis physique deja expedie, transporteur, suivi, delai de livraison, article manquant ou casse a la reception.\n"
    "- compte : connexion, mot de passe, email du compte, donnees personnelles, suppression de compte, historique de commandes, "
    "changement de preferences ou d'adresse enregistree pour les FUTURES commandes (meme si le mot 'commande' ou 'adresse' apparait).\n\n"
    "URGENCE (choisis un chiffre 1, 2 ou 3) :\n"
    "1 = simple question informative, aucun probleme actuel (le client demande comment faire, un delai, une info generale).\n"
    "2 = un probleme reel gene le client mais SANS perte d'argent deja effective ni faille de securite : "
    "cela inclut un paiement refuse/bloque (l'argent n'a pas ete pris), une connexion qui ne marche pas, "
    "un colis simplement pas encore recu ou en retard (mais pas perdu/casse).\n"
    "3 = probleme grave : argent DEJA preleve a tort ou remboursement en retard, donnees d'un autre client visibles, "
    "colis confirme perdu/casse/ouvert avec article manquant, ou colis envoye a la mauvaise adresse.\n\n"
    "Exemples :\n"
    "Texte : \"Comment changer l'adresse email de mon compte ?\" -> {\"categorie\": \"compte\", \"urgence\": 1}\n"
    "Texte : \"Je voudrais recevoir mes commandes a mon adresse professionnelle desormais.\" -> {\"categorie\": \"compte\", \"urgence\": 1}\n"
    "Texte : \"Le mot de passe que je viens de creer n'est pas accepte.\" -> {\"categorie\": \"compte\", \"urgence\": 2}\n"
    "Texte : \"Je recois les emails de quelqu'un d'autre sur mon compte.\" -> {\"categorie\": \"compte\", \"urgence\": 3}\n"
    "Texte : \"Bonjour, je n'ai toujours pas recu mon colis commande il y a 12 jours.\" -> {\"categorie\": \"livraison\", \"urgence\": 2}\n"
    "Texte : \"Le suivi indique livre mais je n'ai rien dans ma boite aux lettres.\" -> {\"categorie\": \"livraison\", \"urgence\": 3}\n"
    "Texte : \"Mon colis est arrive ouvert et il manque un article.\" -> {\"categorie\": \"livraison\", \"urgence\": 3}\n"
    "Texte : \"Pouvez-vous m'envoyer la facture de la commande CMD-2024-120 ?\" -> {\"categorie\": \"paiement\", \"urgence\": 1}\n"
    "Texte : \"Mon paiement en trois fois a ete refuse alors que je remplis les conditions.\" -> {\"categorie\": \"paiement\", \"urgence\": 2}\n"
    "Texte : \"Impossible de valider le paiement, la page tourne dans le vide.\" -> {\"categorie\": \"paiement\", \"urgence\": 2}\n"
    "Texte : \"Ma carte a ete debitee deux fois pour la meme commande.\" -> {\"categorie\": \"paiement\", \"urgence\": 3}\n\n"
    "Reponds uniquement avec ce format exact, sans texte autour : "
    "{\"categorie\": \"paiement|livraison|compte\", \"urgence\": 1|2|3}"
)
# =====================================================================


def classer(texte):
    charge = json.dumps({
        "model": MODELE,
        "temperature": 0,
        "max_tokens": 80,
        "messages": [{"role": "system", "content": CONSIGNE},
                     {"role": "user", "content": texte}],
    }).encode()
    requete = urllib.request.Request(
        f"{BASE}/v1/chat/completions", data=charge,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        brut = json.loads(reponse.read())["choices"][0]["message"]["content"]
    debut, fin = brut.find("{"), brut.rfind("}")
    if debut == -1 or fin == -1:
        return None
    try:
        return json.loads(brut[debut:fin + 1])
    except json.JSONDecodeError:
        return None


def main():
    total = len(CAS["cas"])
    formes, categories, urgences = 0, 0, 0
    print(f"modele : {MODELE}   cas : {total}\n")
    for i, cas in enumerate(CAS["cas"], 1):
        obtenu = classer(cas["texte"])
        if obtenu is None:
            print(f"  {i:2d}. JSON illisible          <- {cas['texte'][:44]}")
            continue
        formes += 1
        bonne_categorie = obtenu.get("categorie") == cas["categorie"]
        bonne_urgence = obtenu.get("urgence") == cas["urgence"]
        categories += bonne_categorie
        urgences += bonne_urgence
        marque = "ok " if bonne_categorie and bonne_urgence else "   "
        print(f"  {i:2d}. {marque} attendu {cas['categorie']}/{cas['urgence']}"
              f"  obtenu {obtenu.get('categorie')}/{obtenu.get('urgence')}")

    print(f"\n  JSON valide  : {formes}/{total}  ({100 * formes // total} %)")
    print(f"  Categorie    : {categories}/{total}  ({100 * categories // total} %)")
    print(f"  Urgence      : {urgences}/{total}  ({100 * urgences // total} %)")
    print("\nNotez ce score, modifiez CONSIGNE, relancez. Gardez la trace de "
          "chaque version : elle est demandee au CC2.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
