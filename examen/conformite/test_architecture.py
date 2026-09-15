"""Verifications d'architecture, independantes du langage de rendu.

Elles portent sur la frontiere de confiance : le front ne parle qu'a votre
serveur, jamais au modele. Le front est libre (celui fourni, un autre en
JavaScript, ou un front serveur comme Streamlit) : la regle est la meme pour tous.
"""
import pathlib
import re

from conftest import BASE_URL, appeler

RACINE = pathlib.Path(__file__).resolve().parents[2]

# Extensions d'un front qui part chez le client.
EXTENSIONS_CLIENT = (".html", ".htm", ".js", ".mjs", ".jsx", ".ts", ".tsx", ".vue", ".svelte")
# Extensions d'un front qui s'execute sur un serveur (Streamlit, Gradio, PHP) :
# le navigateur ne voit pas son code, mais il doit passer par l'API comme les autres.
EXTENSIONS_SERVEUR = (".py", ".php")
# Dossiers dont le contenu est du front. Un fichier de serveur porte souvent la
# meme extension : on ne peut pas se fier a elle seule, sous peine d'accuser a
# tort un serveur Express nomme serveur.js. S'y ajoute tout dossier dont le nom
# commence par "front" (front, frontend, front_streamlit).
# "src" est volontairement absent : il abrite aussi souvent du code serveur.
DOSSIERS_CLIENT = {"public", "static", "client", "assets", "www"}
IGNORES = {"node_modules", ".git", ".venv", "__pycache__", "dist", "build",
           ".next", ".nuxt", "examen", "td", "coverage"}
# Un script Python qui importe une de ces bibliotheques est un front, ou qu'il soit.
IMPORT_FRONT_PYTHON = re.compile(
    r"^\s*(?:import|from)\s+(?:streamlit|gradio|chainlit|nicegui)\b", re.MULTILINE)

# Ce qui trahit un appel direct au modele, quelle que soit la pile du front.
# Compare en minuscules.
TRACES_DU_MODELE = (
    "11434",                                  # le port d'Ollama
    "chat/completions",                       # sa route compatible OpenAI
    "import ollama", "from ollama",           # son client Python
    '"ollama"', "'ollama'", "ollama/browser",  # son client JavaScript
    "langchain_ollama", "@langchain/ollama",
    "ollama_host", "ollama_base_url",
)
# Une cle d'API a une forme reconnaissable. "sk-" seul accuserait a tort du CSS
# (mask-image) ou du texte (risk-free).
CLE_SK = re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{16,}")


def _dans_un_dossier_de_front(parties):
    return any(p in DOSSIERS_CLIENT or p.lower().startswith("front") for p in parties)


def _fichiers_de_front():
    """Les fichiers qui constituent le front, quelle que soit sa pile.

    Trois familles : tout HTML ou qu'il soit, le contenu des dossiers de front,
    et tout script Python qui importe une bibliotheque d'interface. Le code du
    serveur n'est jamais inspecte : il a le droit, et le devoir, de connaitre
    l'adresse du modele.
    """
    for chemin in RACINE.rglob("*"):
        suffixe = chemin.suffix.lower()
        if not chemin.is_file() or suffixe not in EXTENSIONS_CLIENT + EXTENSIONS_SERVEUR:
            continue
        parties = chemin.relative_to(RACINE).parts
        if IGNORES & set(parties):
            continue
        if suffixe in (".html", ".htm") or _dans_un_dossier_de_front(parties[:-1]):
            yield chemin
        elif suffixe == ".py" and IMPORT_FRONT_PYTHON.search(_lire(chemin)):
            yield chemin


def _lire(chemin):
    return chemin.read_text(encoding="utf-8", errors="ignore")


def test_le_front_n_appelle_pas_le_modele():
    """Aucune trace du modele dans le front : ni son port, ni son client, ni sa route."""
    coupables = []
    for chemin in _fichiers_de_front():
        texte = _lire(chemin).lower()
        traces = [t for t in TRACES_DU_MODELE if t in texte]
        if traces:
            coupables.append(f"{chemin.relative_to(RACINE)} ({', '.join(traces)})")
    assert not coupables, (
        "ces fichiers de front joignent le modele directement, au lieu de passer "
        "par vos routes : " + ", ".join(coupables))


def test_aucun_secret_dans_le_front():
    # "_API_KEY" couvre toutes les variables de cle, quel que soit le fournisseur.
    coupables = []
    for chemin in _fichiers_de_front():
        texte = _lire(chemin)
        motifs = [m for m in ("Bearer ", "_API_KEY") if m in texte]
        if CLE_SK.search(texte):
            motifs.append("sk-")
        coupables += [f"{chemin.relative_to(RACINE)} ({m})" for m in motifs]
    assert not coupables, "secret potentiel dans le front : " + ", ".join(coupables)


def test_le_serveur_n_expose_pas_sa_configuration():
    """Une erreur ne doit pas fuiter l'URL du modele ni une trace d'execution."""
    r = appeler("/api/resumer", {"texte": ""})
    corps = r.text.lower()
    for fuite in ("11434", "traceback", "at object.", "ollama_base_url"):
        assert fuite not in corps, (
            f"le corps d'erreur laisse fuiter {fuite!r} : renvoyez un message neutre")


def test_le_serveur_de_l_etudiant_n_est_pas_le_modele():
    """Erreur classique : donner l'URL d'Ollama au lieu de celle de son serveur."""
    assert "11434" not in BASE_URL, (
        "BASE_URL pointe sur le modele, pas sur votre serveur")
