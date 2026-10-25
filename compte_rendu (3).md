# Compte rendu — TP 1 : Construire une chaîne de prétraitement en TAL

- **Module :** Natural Language Processing — Chapitre 2 (prétraitement et tokenisation)
- **Auteur(s) :** Souha Guezguez
- **Résultat :** 6/6 tests passés (T1 à T6)

---

## Exercice 0 — Prédictions

**0.1** Avec la règle « mots (contractions gardées) + chaque signe de ponctuation à part », `"Dr. Smith isn't home."` donne 6 tokens :
`['Dr', '.', 'Smith', "isn't", 'home', '.']`.

**0.2** Après mise en minuscules, le token le plus fréquent sera `the` (5 occurrences). Il sera suivi par la ponctuation, avec le point `.` (4 occurrences). On retrouve la loi de Zipf : quelques tokens très fréquents (mots vides, ponctuation), puis une longue traîne de mots rares.

**0.3** `"أحمد" == "احمد"` est **faux** : Python compare des points de code Unicode. La première lettre est `أ` (U+0623, alif avec hamza) dans le premier mot et `ا` (U+0627, alif simple) dans le second : ce sont deux caractères différents.

*Vérification :* 0.1 confirmée par T3, 0.2 confirmée à l'exercice 5, 0.3 confirmée à l'exercice 4.

---

## Exercice 1 — Normalisation

**1.1** Résultat : `(2, 1, 1)`.
- `"e\u0301"` contient 2 caractères : `e` suivi d'un accent aigu combinant (U+0301).
- `"é"` est un seul caractère précomposé (U+00E9).
- `unicodedata.normalize("NFC", "e\u0301")` compose les deux en un seul caractère, d'où 1.

Les deux « é » s'affichent de la même façon mais sont différents pour Python. La normalisation doit donc avoir lieu **avant** la tokenisation et les comparaisons, sinon deux mots visuellement identiques ne seraient jamais appariés et les comptages seraient faussés.

**1.3** `"Straße".lower()` donne `'straße'` et `"Straße".casefold()` donne `'strasse'`. `casefold()` est préférable pour apparier des mots : il est plus agressif (`ß` devient `ss`), donc « Straße » et « STRASSE » deviennent identiques, ce que `lower()` ne fait pas.

**1.5** `lower` est un paramètre car la casse porte parfois de l'information. Exemple : la reconnaissance d'entités nommées, où « Apple » (entreprise) se distingue de « apple » (fruit) grâce à la majuscule.

*Point de contrôle :* `normalize("Hello\tworld\n\n!")` renvoie `'hello world !'`. Tests T1 et T2 : PASS.

---

## Exercice 2 — Tokenisation en mots

Motif utilisé : `\b\w+(?:'\w+)?\b|[^\w\s]`

**2.4** Rôle de chaque élément :
- `\b` : frontière de mot (largeur nulle), pour commencer et finir un mot proprement.
- `\w+` : une ou plusieurs lettres, chiffres ou `_` (les lettres accentuées et arabes comptent aussi).
- `(?:'\w+)?` : groupe non capturant facultatif, une apostrophe suivie de caractères de mot. Le `?:` évite que `re.findall` renvoie seulement le contenu du groupe.
- `[^\w\s]` : un seul caractère qui n'est ni un caractère de mot ni un espacement, c'est-à-dire la ponctuation et les symboles.

Sans `(?:'\w+)?`, `isn't` serait coupé en trois tokens : `isn`, `'` et `t`.

**2.5** `word_tokenize("l'école aujourd'hui")` donne `["l'école", "aujourd'hui"]`. Cette sortie ne convient pas au français : `l'école` devrait être séparé en `l'` + `école` (élision), alors qu'`aujourd'hui` doit rester un seul mot. Notre règle traite toutes les apostrophes de la même façon et ne distingue pas ces cas.

*Point de contrôle :* `word_tokenize("It's 5.")` renvoie `["It's", '5', '.']` (3 tokens). Test T3 : PASS.

---

## Exercice 3 — Segmentation en phrases et diagnostic

Motif utilisé : `(?<=[.!?])\s+`

**3.3** Sorties :
- `"Dr. Smith arrived. He left."` → `['Dr.', 'Smith arrived.', 'He left.']`
- `"He lives in the U.S.A. and works there."` → `['He lives in the U.S.A.', 'and works there.']`

Les deux sont fausses : la règle coupe après tout point suivi d'un espace et ne peut pas distinguer un point d'abréviation (`Dr.`, `U.S.A.`) d'un point de fin de phrase.

**3.4** `buggy_sentence_tokenize("Hi there. How are you? I'm fine!")` donne `['Hi there', 'How are you', "I'm fine!"]`.

- **(a)** Les deux premières phrases ont perdu leur ponctuation finale (`.` et `?`).
- **(b)** `re.split` supprime tout ce que le motif reconnaît. Le motif `[.!?]\s+` reconnaît la ponctuation **et** l'espace, donc les deux disparaissent.
- **(c)** Le `!` final est à la toute fin du texte, sans espace derrière : `\s+` ne peut pas s'y accrocher, il n'y a pas de correspondance et le `!` reste.
- **(d)** L'assertion arrière `(?<=[.!?])` vérifie une condition sans consommer de caractères. Seul `\s+` est reconnu et retiré, donc la ponctuation reste dans sa phrase.

*Test T4 : PASS.*

---

## Exercice 4 — Normalisation de l'arabe

Implémentation : NFC, suppression des diacritiques (`DIAC`) et du tatwil U+0640, puis remplacement de U+0623, U+0625 et U+0622 par U+0627.

**4.1** `[hex(ord(c)) for c in "محـــمد"]` donne `['0x645', '0x62d', '0x640', '0x640', '0x640', '0x645', '0x62f']`. Le point de code répété est **U+0640** (tatwil), trois fois. Il **ne modifie pas le mot** : c'est un étirement purement visuel, le mot reste « محمد ».

**4.3** Résultat de `[normalize_arabic(w) for w in ARABIC]` : `['العربية', 'احمد الى اسيا', 'محمد']`. La prédiction 0.3 est confirmée : avant normalisation `"أحمد" == "احمد"` est faux, après normalisation les deux sont identiques (T5 : PASS).

**4.4** Un utilisateur peut chercher « احمد » (sans hamza) alors que le document contient « أحمد ». Après normalisation, les deux deviennent identiques, donc le moteur retrouve le document malgré la différence de graphie. Sans cela, le rappel (*recall*) serait mauvais.

**4.5** Informations détruites : les voyelles courtes (diacritiques), donc la distinction entre des mots qui ne diffèrent que par elles, et la distinction entre alif avec hamza et alif simple.
- **Pour** fusionner ى/ي et ة/ه : ces confusions sont très fréquentes dans les textes informels, donc on gagne en rappel.
- **Contre** : on risque de mélanger des mots différents (terminaisons qui changent le genre ou le sens), donc on perd en précision.

*Point de contrôle :* la sortie pour `"محـــمد"` compte exactement 4 caractères.

---

## Exercice 5 — Statistiques de corpus

Résultats obtenus :

| | occurrences | types | ratio | top5 |
|---|---|---|---|---|
| `lower=True` | 34 | 24 | 0.706 | the 5, `.` 4, cat 2, `,` 2, `/` 2 |
| `lower=False` | 34 | 25 | 0.735 | `.` 4, the 3, The 2, cat 2, `,` 2 |

**5.3**
- **(a)** La prédiction 0.2 est confirmée : `the` (5) est le plus fréquent, suivi du point `.` (4).
- **(b)** Avec `lower=False`, « The » et « the » sont deux types différents, d'où 25 types au lieu de 24. Les occurrences de `the` sont réparties entre `the` (3) et `The` (2), donc le point `.` devient le token le plus fréquent.
- **(c)** Un ratio types/occurrences **élevé** indique un vocabulaire varié (peu de répétitions), un ratio **faible** un texte répétitif. On ne compare ces ratios qu'entre textes de longueurs comparables, car plus un texte s'allonge, plus les mots se répètent : le ratio diminue mécaniquement avec la longueur.
- **(d)** Le top5 est dominé par `the`, `.` et `,`, c'est-à-dire des mots outils et de la ponctuation : c'est la loi de Zipf (quelques tokens très fréquents, une longue traîne de mots rares). Ces mots fréquents sont souvent des **mots vides** (*stop words*), qui portent peu de sens et sont souvent retirés en recherche d'information.

---

## Exercice 6 — Analyse d'erreurs

| # | Entrée | Fonction | Sortie | Qu'est-ce qui a échoué ? | Remède proposé |
|---|--------|----------|--------|--------------------------|----------------|
| a | `visit https://x.io now` | mots | `['visit', 'https', ':', '/', '/', 'x', '.', 'io', 'now']` | L'URL est cassée en 7 morceaux | Ajouter une alternative URL avant les autres dans le motif |
| b | `U.S.A.` | mots | `['U', '.', 'S', '.', 'A', '.']` | L'abréviation est éclatée en lettres et points | Motif `(?:[A-Z]\.){2,}` ou liste d'abréviations |
| c | `Smith’s car` (U+2019) | mots | `['Smith', '’', 's', 'car']` | Le motif ne reconnaît que l'apostrophe droite `'`, pas `’` | Remplacer `’` par `'` dans `normalize`, ou accepter `['’]` dans le motif |
| d | `rock'n'roll` | mots | `["rock'n", "'", 'roll']` | Le motif n'autorise qu'**une** apostrophe interne | Remplacer `?` par `*` : `(?:'\w+)*` |
| e | `state-of-the-art` | mots | `['state', '-', 'of', '-', 'the', '-', 'art']` | Le trait d'union est traité comme ponctuation | Autoriser les traits d'union internes : `(?:[-']\w+)*` |
| f | `Dr. Smith arrived. He left.` | phrases | `['Dr.', 'Smith arrived.', 'He left.']` | Coupure après l'abréviation `Dr.` | Liste d'abréviations, ou modèle appris (ex. Punkt) |

**6.2** Découper sur les traits d'union n'est **pas toujours** une erreur. Dans un moteur de recherche, découper `state-of-the-art` permet de retrouver un document avec la requête « state of the art ». Cela aide aussi pour `e-mail` / `email` ou pour des composés peu figés.

**6.3** Chaque règle corrige un cas mais en crée d'autres : abréviations, URL, apostrophes, traits d'union, langues différentes, argot, emoji. La liste des exceptions n'est jamais finie, et les règles ne connaissent pas la langue. Un tokeniseur en sous-mots appris comme **BPE** apprend à partir des données les fusions de caractères fréquentes. Il n'a pas de mot inconnu : un mot rare est découpé en morceaux connus, donc rien n'échoue, et il s'adapte à n'importe quelle langue sans règles écrites à la main.

---

## Synthèse

- La normalisation doit être appliquée **avant** la tokenisation, sinon des graphies identiques à l'écran restent différentes pour la machine.
- La mise en minuscules réduit le nombre de **types** mais fait perdre **l'information de casse**.
- Un tokeniseur à base de règles échoue sur **les abréviations** et **les URL** parce que ses règles sont locales et fixes, sans connaissance de la langue.

## Vérification individuelle

1. `word_tokenize("It's 5.")` renvoie `["It's", '5', '.']`.
2. Le ratio types/occurrences de `['a', 'b', 'a', 'c', 'a']` est 3 / 5 = **0.6**.
3. `normalize_arabic` rend `أحمد` et `احمد` identiques ; elle supprime la distinction entre alif avec hamza et alif simple.
