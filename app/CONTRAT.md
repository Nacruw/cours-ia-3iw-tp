# Contrat de route : l'application fil rouge

Ce fichier fait foi. En cas de divergence entre un squelette, une slide et ce
document, c'est ce document qui a raison.

Il décrit **le seul point de contact** entre le front et votre serveur.
Ce que vous écrivez derrière, et dans quelle langue, ne regarde que vous.

## Principe

```
Front        ---->  Votre serveur  ---->  Modèle (Ollama)
(au choix)          (votre travail)       (localhost:11434)
```

Le front n'appelle jamais le modèle directement. Il n'appelle que vos routes.
Tout front qui joint le port 11434, ou qui importe un client du modèle, est une
non-conformité.

## Le front est libre

Trois possibilités, toutes recevables :

1. **Garder la page fournie** (`app/front/`), telle quelle. C'est le chemin
   garanti : elle consomme déjà tout le contrat.
2. **La modifier**, ou **la remplacer** par votre propre front : React, Vue,
   Svelte, PHP, ou ce que vous voulez.
3. **Écrire un front en Python** avec Streamlit ou Gradio. Un exemple complet est
   fourni dans `app/front_streamlit/` : `make front-streamlit`.

Une seule règle, quelle que soit la pile : **le front ne parle qu'à vos routes**.
Elle vaut aussi pour un front qui s'exécute sur un serveur, comme Streamlit : le
navigateur ne voit pas son code, mais y appeler le modèle revient à court-circuiter
votre API, ce qui annule tout le travail des séances 9 à 13.

Une interface de chat toute faite (Open WebUI, AnythingLLM, LibreChat) n'est
**pas** recevable : elle parle au modèle directement, ou attend une API au format
OpenAI, et ne consomme donc pas ce contrat.

### Où le ranger

Votre front vit dans un dossier dont le nom commence par `front` : `app/front/`,
`front/`, `frontend/`, `app/front_streamlit/`. Un script Python qui importe
Streamlit, Gradio, Chainlit ou NiceGUI est reconnu comme front où qu'il soit.
Ne mélangez pas de code serveur dans ce dossier : une route d'API Next.js qui
appelle le modèle depuis `frontend/` serait signalée à juste titre.

Laissez `app/front/` en place même si vous ne l'utilisez pas : le squelette le
sert à la racine de votre serveur.

### Comment le brancher

| Front | Où il tourne | Comment il joint vos routes |
| --- | --- | --- |
| la page fournie, modifiée ou non | servie par votre serveur, port 3000 | `fetch("/api/resumer")` : même origine, rien à configurer |
| une application avec son serveur de développement (Vite, Next) | un autre port, 5173 par exemple | un proxy du serveur de développement renvoie `/api` vers le port 3000, ce qui évite de configurer CORS |
| un front serveur (Streamlit, Gradio, PHP) | son propre processus | un appel HTTP vers `http://localhost:3000/api/...` |

### Comment il est évalué

La suite de conformité ne teste que votre API, avec un seul contrôle sur le front :
il ne contient ni trace du modèle ni secret. Le front lui-même est noté pendant la
démonstration : il affiche le texte au fil du flux, montre les erreurs `400` et
`503` de façon lisible, et affiche les sources du RAG. Voir la grille du CC2.

## Route 1 : résumer un texte (séance 9)

### Requête

```
POST /api/resumer
Content-Type: application/json

{ "texte": "le contenu a resumer", "ton": "neutre" }
```

| Champ | Type | Obligatoire | Valeurs |
| --- | --- | --- | --- |
| `texte` | chaîne | oui | non vide, 20 000 caractères maximum |
| `ton` | chaîne | non | `neutre` (défaut) ou `direct` |

### Réponse nominale

Code `200`, en-tête `Content-Type: text/event-stream`.

Un événement SSE par fragment produit par le modèle :

```
data: {"delta":"Le client"}

data: {"delta":" ne parvient pas"}

data: {"done":true,"usage":{"entree":312,"sortie":88,"ms":2140}}

```

- Chaque événement est une ligne `data: ` suivie de **deux** retours à la ligne.
- Le dernier événement porte `done: true` et l'objet `usage`.
- `usage.entree` et `usage.sortie` sont des nombres de tokens, `usage.ms` la
  durée totale en millisecondes.

### Réponses d'erreur

| Situation | Code | Corps |
| --- | --- | --- |
| `texte` absent, vide ou trop long | `400` | `{ "erreur": "texte invalide" }` |
| `ton` inconnu | `400` | `{ "erreur": "ton invalide" }` |
| Modèle injoignable ou en timeout | `503` | `{ "erreur": "modele indisponible" }` |

Les erreurs sont du JSON classique, **pas** du SSE. Elles doivent arriver avant
le début du flux.

## Route 2 : rechercher une commande (séance 10)

Ajoutée lors de la séance sur l'appel d'outils. Même principe, même gestion
d'erreurs.

```
POST /api/assistant
{ "question": "ou en est la commande CMD-2024-118 ?" }
```

La réponse est un flux SSE de même forme. Le serveur a le droit d'appeler le
modèle plusieurs fois (boucle d'appel d'outil) avant de commencer à streamer.

## Route 3 : interroger le corpus (séance 13)

```
POST /api/documents
{ "question": "comment demander un remboursement ?" }
```

Réponse SSE de même forme, avec un événement supplémentaire **avant** les
fragments, listant les sources retenues :

```
data: {"sources":[{"titre":"Remboursements","score":0.81}]}

```

## Règles communes à toutes les routes

1. Le prompt est assemblé **côté serveur**. Le client n'envoie jamais de prompt.
2. Toute entrée est validée avant d'atteindre le modèle.
3. Tout appel au modèle a un timeout explicite, et un repli en cas d'échec.
4. Chaque appel est journalisé : modèle, tokens d'entrée et de sortie, durée, issue.
5. Aucun secret, aucune URL de modèle, aucune configuration serveur n'est
   exposée au client, ni présente dans le front, même quand il s'exécute sur un
   serveur.

## Comment votre rendu est vérifié

```bash
# depuis la racine du depot, votre serveur devant tourner sur le port 3000
make conformite SEANCE=9     # une seance, qui doit etre ecrite
make conformite              # tout ; les routes pas encore ecrites sont ignorees
```

La suite est écrite en Python et n'interroge que le HTTP. Elle donne le même
verdict que votre serveur soit en FastAPI, en Express, en Symfony ou en Go.

Une route prévue mais pas encore écrite doit répondre **`501`** : la suite
ignore alors ses tests, ce qui permet de la lancer dès la séance 9. Les deux
squelettes fournis le font déjà. Pour la correction du CC2, toutes les routes
sont exigées : une route en `501` y compte comme un échec.

## Voies fournies

| Dossier | Pile | État |
| --- | --- | --- |
| `app/front/` | HTML et JavaScript statiques | fourni, utilisable tel quel, modifiable ou remplaçable |
| `app/front_streamlit/` | Streamlit | exemple d'un autre front, complet |
| `app/python/` | FastAPI | un fichier par séance, TODO à remplir |
| `app/node/` | Node, sans dépendance | un fichier par séance, TODO à remplir |

Dans les deux voies, les fichiers de séance sont identiques d'une langue à
l'autre : `s09_resumer`, `s10_assistant`, `s13_index`, `s13_documents`. Le point
d'entrée `main` et le dossier `fourni/` ne se modifient pas.

Déclarez votre voie au début du projet et tenez-vous-y. Une autre pile est
acceptée si vous l'assumez : le contrat est le même, mais le squelette est à
votre charge.
