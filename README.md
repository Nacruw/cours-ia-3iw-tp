# Les Fondamentaux de l'Intelligence Artificielle : 3IW

Dépôt de travail du module de 21 heures, ESGI, 3e année d'ingénierie du web.

Tout tourne sur votre machine avec des modèles locaux. **Aucun compte, aucune clé
d'API, aucun paiement.**

## Démarrer

À faire **avant la première séance**, chez vous : les téléchargements pèsent
environ 2,5 Go.

Commencez par créer **votre propre copie privée** de ce dépôt : bouton
**Use this template**, puis **Private**. Ne forkez pas : un fork d'un dépôt public
est public, et votre travail serait visible par toute la promotion.

```bash
git clone <l'adresse de VOTRE copie>
cd cours-ia-3iw

make outils          # installe uv et Ollama s'ils sont absents
make install         # environnement Python : tests, et FastAPI pour la voie Python
make ollama-pull     # le socle du cours
make setup-check     # diagnostic du poste (ou : make setup-check-node)
```

Le guide détaillé, avec la matrice modèle/machine et le dépannage, est dans
[docs/installation-ollama.md](docs/installation-ollama.md).

`make help` liste toutes les commandes.

## Choisir sa voie

Le cours est bilingue. Vous écrivez votre serveur **dans la langue de votre
choix** :

| Voie | Dossier | Prérequis |
| --- | --- | --- |
| Python | `app/python/` | Python 3.11 ou plus |
| JavaScript | `app/node/` | Node 20 ou plus, aucune dépendance npm |

Ce qui est évalué est le **contrat HTTP** décrit dans
[app/CONTRAT.md](app/CONTRAT.md), jamais votre code. Déclarez votre voie en début
de projet et tenez-vous-y.

## Comment on travaille

Vous construisez **une seule application**, qui grandit au fil des séances. Elle
est découpée en **un fichier par séance** : vous n'ouvrez que celui du jour.

| Séance | Travail | Fichier |
| --- | --- | --- |
| 4 | installer son poste et relever son débit | `tp/00_setup/` |
| 5 | améliorer un prompt, mesure à l'appui | `tp/05_prompt/` |
| 9 | la route « résumer », TODO 1 à 5 | `app/<voie>/s09_resumer` |
| 10 | l'assistant avec appel d'outil, TODO 6 à 8 | `app/<voie>/s10_assistant` |
| 11 | comparer des modèles au banc d'essai | `tp/11_banc/` |
| 13 | l'index de recherche, TODO 9 à 11 | `app/<voie>/s13_index` |
| 13 | le pipeline RAG, TODO 12 | `app/<voie>/s13_documents` |

Chaque fichier de séance commence par son objectif et la commande qui le
vérifie. Tant qu'un TODO n'est pas écrit, sa route répond « à écrire ».

Trois règles :

1. **Ne modifiez pas `app/front/`.** Le front est commun à toute la promotion ; le
   modifier est hors sujet.
2. **Ne modifiez ni `main` ni le dossier `fourni/`.** Votre travail est dans les
   fichiers de séance.
3. **Le navigateur ne parle jamais au modèle.** Il parle à votre serveur, qui
   parle au modèle.

## Vérifier son travail

Deux terminaux :

```bash
make app                     # terminal 1 : votre serveur (ou : make app-node)
make conformite SEANCE=9     # terminal 2 : les tests de la séance du jour
```

`SEANCE=9`, `10` ou `13` ne lance que les tests de cette séance, et **exige**
qu'elle soit écrite : un TODO oublié apparaît en rouge.

Sans `SEANCE`, `make conformite` lance tout et ignore les routes pas encore
écrites : vous voyez l'application passer au vert au fil du module. Pour le
CC2, toutes les routes sont exigées.

## Organisation du dépôt

| Dossier | Contenu |
| --- | --- |
| `slides/` | les supports du cours, un PDF par bloc |
| `app/` | l'application fil rouge : front, squelettes, données, contrat |
| `tp/` | les ateliers ponctuels : diagnostic, prompt, banc d'essai |
| `docs/` | installation et dépannage |
| `examen/conformite/` | la suite de tests du contrat |

## Évaluation

| Épreuve | Format | Poids |
| --- | --- | --- |
| CC1 | écrit de 45 min, fin de séance 7 | 25 % |
| CC2 | l'application, individuelle, rendu Git et démonstration de 5 min | 35 % |
| Partiel | écrit de 1 h 30 | 40 % |
