Marwane Birrou - more details coming soon

TP ia : test 1 :
  JSON valide  : 20/20  (100 %)
  Categorie    : 8/20  (40 %)
  Urgence      : 0/20  (0 %)

JSON valide  : 20/20  (100 %)
  Categorie    : 9/20  (45 %)
  Urgence      : 0/20  (0 %)
  
JSON valide  : 20/20  (100 %)
  Categorie    : 9/20  (45 %)
  Urgence      : 0/20  (0 %)
  
JSON valide  : 20/20  (100 %)
  Categorie    : 7/20  (35 %)
  Urgence      : 0/20  (0 %)

JSON valide  : 20/20  (100 %)
  Categorie    : 14/20  (70 %)
  Urgence      : 0/20  (0 %)

JSON valide  : 20/20  (100 %)
  Categorie    : 19/20  (95 %)
  Urgence      : 17/20  (85 %)
  
JSON valide  : 20/20  (100 %)
  Categorie    : 20/20  (100 %)
  Urgence      : 20/20  (100 %)

  Prompt dernier essai :

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
