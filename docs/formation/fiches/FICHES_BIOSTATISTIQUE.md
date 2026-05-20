# Fiches pédagogiques — Section Biostatistique

> Huit fiches, une par module. Chaque fiche contient : objectif, concept clé, manipulation guidée, questions d'interprétation, erreurs fréquentes.

---

## Fiche 1 — Analyse CSV

### Objectif pédagogique
Explorer et nettoyer un fichier de terrain réel. Identifier les problèmes de qualité de données avant toute analyse.

### Concept clé
Un fichier de terrain brut contient presque toujours des valeurs manquantes, des unités mélangées ou des colonnes mal typées. L'exploration préalable est une étape incontournable.

### Manipulation guidée

**Étape 1 — Importer le fichier**
1. Dans la barre latérale, sélectionner "Analyse CSV"
2. Cliquer sur "Parcourir" et choisir votre fichier `.csv`
3. Observer le résumé automatique : nombre de lignes, colonnes, valeurs manquantes

**Étape 2 — Explorer les distributions**
1. Sélectionner une colonne numérique (ex. : comptage)
2. Observer l'histogramme et la boîte à moustaches
3. Comparer la moyenne et la médiane

**Étape 3 — Explorer une relation**
1. Choisir deux colonnes numériques
2. Tracer le nuage de points
3. Observer la droite de régression et le R²

**Étape 4 — Comparer des groupes**
1. Choisir une colonne numérique et une colonne catégorielle
2. Lancer le test de Welch
3. Lire la p-value et la différence de moyennes

**Étape 5 — Exporter**
1. Télécharger les données nettoyées en CSV
2. Télécharger le résumé en PDF

### Questions d'interprétation

1. La moyenne est supérieure à la médiane pour la colonne "comptage". Qu'est-ce que cela indique sur la distribution ?
2. Le coefficient de variation est de 85%. Que dit cela sur l'hétérogénéité inter-sites ?
3. La p-value du test de Welch est de 0.23. Peut-on conclure que les deux habitats ont la même abondance ?
4. Deux colonnes sont fortement corrélées (r = 0.91). Cela prouve-t-il un lien de causalité ?

### Erreurs fréquentes

- Mélanger des unités dans une même colonne (grammes et kilogrammes)
- Interpréter une corrélation comme une causalité
- Ignorer les valeurs manquantes avant de calculer une moyenne
- Comparer des groupes sans vérifier les effectifs

---

## Fiche 2 — Statistiques descriptives

### Objectif pédagogique
Résumer une distribution de comptages ou de mesures morphologiques. Choisir le bon indicateur selon la forme de la distribution.

### Concept clé
La moyenne seule ne suffit pas. Une distribution asymétrique (fréquente en ornithologie) nécessite la médiane et les quartiles. L'écart-type mesure la dispersion, pas la forme.

### Manipulation guidée

**Étape 1 — Paramétrer la simulation**
1. Régler le nombre de sites (ex. : 50)
2. Régler l'abondance moyenne attendue (ex. : 15 individus/site)
3. Choisir le niveau d'agrégation spatiale

**Étape 2 — Observer les indicateurs**
- Lire la moyenne, la médiane, l'écart-type, le minimum, le maximum
- Identifier si la distribution est symétrique ou asymétrique

**Étape 3 — Faire varier un paramètre**
- Augmenter l'agrégation spatiale → observer l'effet sur la médiane vs moyenne
- Augmenter le nombre de sites → observer la stabilisation des indicateurs

### Questions d'interprétation

1. Avec une forte agrégation, la moyenne est 18 et la médiane est 8. Quelle valeur est la plus représentative pour 70% des sites ?
2. L'écart-type est plus grand que la moyenne. Que cela implique-t-il pour un test statistique basé sur la normalité ?
3. Pourquoi les ornithologues utilisent-ils souvent des modèles de comptage (Poisson) plutôt que des tests classiques ?
4. Quel indicateur utiliser pour comparer des distributions très différentes en taille ?

### Erreurs fréquentes

- Utiliser la moyenne pour décrire une distribution très asymétrique
- Confondre écart-type (dispersion) et erreur standard (précision de la moyenne)
- Conclure sur la population générale à partir d'un seul indicateur

---

## Fiche 3 — Corrélation et régression

### Objectif pédagogique
Quantifier la relation linéaire entre deux variables biologiques. Distinguer la force d'association (r de Pearson, R²) de la signification statistique (p-value).

### Concept clé
Un R² élevé décrit bien une relation, mais ne prouve pas la causalité. Une p-value faible avec un R² de 0.05 signifie une relation réelle mais biologiquement négligeable.

### Manipulation guidée

**Étape 1 — Paramétrer**
1. Régler la taille d'échantillon n (commencer à n = 20, puis n = 200)
2. Régler la variabilité individuelle (bruit autour de la relation)
3. Choisir la pente de la relation

**Étape 2 — Observer**
1. Lire r de Pearson et R²
2. Observer la p-value associée
3. Comparer le nuage de points avec la droite de régression

**Étape 3 — Expériences clés**
- Fixer r = 0.3, augmenter n de 20 à 200 : observer la p-value → Elle devient significative pour une relation faible
- Fixer n = 50, augmenter la variabilité : observer la dégradation de R²
- Comparer deux relations avec même r mais n différents

### Questions d'interprétation

1. Avec n = 200 et r = 0.15, la p-value est 0.02. La relation est-elle biologiquement importante ?
2. La pente est de 2.3 g/mm. Que signifie ce chiffre biologiquement (ex. : masse en fonction de la longueur d'aile) ?
3. R² = 0.62. Quelle proportion de la variance n'est pas expliquée par la relation linéaire ?
4. Citer deux variables biologiques qui pourraient être corrélées sans lien de causalité direct.

### Erreurs fréquentes

- Confondre r de Pearson (corrélation) et R² (proportion de variance expliquée)
- Penser qu'une p-value faible implique une relation forte
- Utiliser une régression simple quand les données sont groupées (plusieurs observations par site)
- Interpréter l'intercept quand X = 0 n'est pas biologiquement réaliste

---

## Fiche 4 — Tests statistiques

### Objectif pédagogique
Comparer des groupes biologiques (habitats, années, traitements). Choisir le bon test selon la structure des données.

### Concept clé
Le choix du test dépend du type de variable (numérique vs catégorielle), du nombre de groupes, et de la distribution. La signification statistique (p-value) ne mesure pas l'importance biologique.

### Tests disponibles dans ORNI-LAB

| Test | Quand l'utiliser |
|------|-----------------|
| t-test de Welch | Comparer 2 groupes, variable continue, variances potentiellement inégales |
| ANOVA | Comparer 3 groupes ou plus, variable continue |
| Mann-Whitney | Alternative non-paramétrique au t-test |
| Khi-deux | Comparer des fréquences ou proportions |

### Manipulation guidée

**Étape 1 — t-test de Welch**
1. Régler n_a = 30, n_b = 30
2. Régler les moyennes des deux groupes (différence initiale = 0)
3. Observer que p-value ≈ 0.5 (pas de différence)
4. Augmenter la différence de moyennes → observer la diminution de p-value

**Étape 2 — Effet de la taille d'échantillon**
1. Fixer une petite différence de moyennes (ex. : 2 unités)
2. Passer de n = 10 à n = 200
3. Observer la p-value : même petite différence devient "significative"

**Étape 3 — ANOVA**
1. Comparer 3 habitats
2. Observer le F-statistique et la p-value globale
3. Identifier quel habitat se distingue des autres

### Questions d'interprétation

1. p-value = 0.04 avec n = 10. Que faut-il faire avant de conclure ?
2. Deux habitats ont des moyennes de 12 et 18 individus. La différence est significative (p = 0.001). Est-elle biologiquement importante ?
3. Le test de Mann-Whitney donne une conclusion différente du t-test. Quelle information cela apporte-t-il sur la distribution ?
4. Pourquoi l'ANOVA donne-t-elle un résultat global et non par paire ?

### Erreurs fréquentes

- Interpréter p > 0.05 comme "les groupes sont identiques"
- Effectuer de multiples comparaisons sans correction (Bonferroni)
- Utiliser un test paramétrique sur des données très asymétriques avec petit n
- Oublier que les observations doivent être indépendantes

---

## Fiche 5 — GLM Comptage (Poisson / Binomial négatif)

### Objectif pédagogique
Modéliser des données de comptage d'oiseaux en tenant compte de leur nature discrète et de la surdispersion fréquente.

### Concept clé
Les comptages (0, 1, 2, …) ne suivent pas une loi normale. Le GLM Poisson est la base ; le binomial négatif est utilisé quand la variance est supérieure à la moyenne (surdispersion), situation très fréquente en ornithologie.

### Vocabulaire clé

| Terme | Définition |
|-------|-----------|
| Surdispersion | Variance des comptages > moyenne (agrégation spatiale, hétérogénéité) |
| Fonction de lien | Log : lien entre le prédicteur et la moyenne des comptages |
| Coefficient β | Effet d'une covariable sur le log du comptage moyen |
| AIC | Critère de comparaison de modèles (plus bas = mieux) |

### Manipulation guidée

**Étape 1 — Poisson sans surdispersion**
1. Simuler des comptages avec faible agrégation
2. Ajuster un GLM Poisson
3. Observer le ratio déviance/degrés de liberté ≈ 1

**Étape 2 — Avec surdispersion**
1. Augmenter l'agrégation spatiale
2. Observer le ratio déviance/ddl >> 1 (surdispersion détectée)
3. Basculer sur le modèle binomial négatif
4. Comparer les AIC des deux modèles

**Étape 3 — Interpréter les coefficients**
1. Observer l'effet d'un habitat sur le comptage
2. Calculer exp(β) pour l'effet multiplicatif

### Questions d'interprétation

1. Le ratio déviance/ddl = 3.8 pour le modèle Poisson. Quelle décision prendre ?
2. β_habitat_foret = 0.72. Combien de fois plus d'individus en forêt qu'en prairie (référence) ?
3. L'AIC du binomial négatif est 12 points plus faible que celui du Poisson. Quel modèle choisir ?
4. Pourquoi ne pas simplement faire une ANOVA sur les comptages bruts ?

### Erreurs fréquentes

- Appliquer un modèle linéaire classique à des comptages (violation des hypothèses)
- Ignorer la surdispersion et sous-estimer les erreurs standards
- Interpréter β directement sans prendre l'exponentielle

---

## Fiche 6 — Modèles mixtes (LMM)

### Objectif pédagogique
Modéliser des données groupées (plusieurs observations par site, individu ou session) en contrôlant la pseudo-réplication.

### Concept clé
Quand plusieurs mesures viennent du même site ou individu, elles ne sont pas indépendantes. Un modèle mixte ajoute des effets aléatoires pour capturer cette structure.

### Vocabulaire clé

| Terme | Définition |
|-------|-----------|
| Effet fixe | Variable d'intérêt dont on veut estimer l'effet moyen (habitat, traitement) |
| Effet aléatoire | Variable de groupement dont on veut contrôler la variabilité (site, individu) |
| Variance inter-groupe | Part de la variabilité due aux différences entre groupes |
| ICC | Corrélation intra-classe : proportion de variance due au groupement |

### Manipulation guidée

**Étape 1 — Données groupées**
1. Simuler des données avec plusieurs sites et plusieurs observations par site
2. Observer la variabilité entre sites vs au sein des sites

**Étape 2 — Modèle simple vs modèle mixte**
1. Ajuster une régression simple (ignorer le site)
2. Ajuster un LMM avec site comme effet aléatoire
3. Comparer les erreurs standards des coefficients

**Étape 3 — Interpréter l'ICC**
1. ICC = 0.6 → 60% de la variance est due aux différences entre sites
2. Que conclure sur la nécessité d'un effet aléatoire ?

### Questions d'interprétation

1. ICC = 0.05. Le modèle mixte est-il nécessaire dans ce cas ?
2. L'effet fixe "habitat" a un p = 0.03 en modèle mixte mais p = 0.001 en régression simple. Pourquoi ?
3. Peut-on comparer des espèces en ignorant le site d'observation si les espèces ont des préférences d'habitat différentes ?
4. Quand utiliser l'individu comme effet aléatoire plutôt que le site ?

### Erreurs fréquentes

- Traiter des répétitions sur le même site comme des observations indépendantes (pseudo-réplication)
- Ajouter un effet aléatoire avec trop peu de niveaux (< 5-6 groupes)
- Interpréter la variance de l'effet aléatoire comme un effet fixe

---

## Fiche 7 — Domaines vitaux (MCP et KDE)

### Objectif pédagogique
Estimer et comparer les domaines vitaux d'oiseaux à partir de données GPS. Comprendre les différences entre approches géométriques et probabilistes.

### Concept clé

| Approche | Description | Avantage | Limite |
|----------|-------------|----------|--------|
| **MCP** (Minimum Convex Polygon) | Polygone convexe minimum contenant tous les points | Simple, universel | Sensible aux points extrêmes, ignore les zones peu utilisées |
| **KDE** (Kernel Density Estimation) | Distribution de probabilité de présence | Probabiliste, isoplètes ajustables | Nécessite plus de points, paramètre h à choisir |

### Manipulation guidée

**Module MCP :**
1. Importer des coordonnées GPS (CSV avec colonnes x, y)
2. Calculer le MCP 100%
3. Réduire à 95% (exclure les points aberrants)
4. Observer la réduction de surface
5. Comparer deux individus ou deux saisons

**Module KDE :**
1. Charger les mêmes données GPS
2. Choisir la bande passante h (lissage)
3. Observer l'isoplèthe 50% (zone noyau) et 95% (domaine complet)
4. Augmenter h → observer le lissage du contour
5. Diminuer h → observer la sur-ajustement aux données

### Questions d'interprétation

1. Le MCP 100% est de 45 ha mais le KDE 95% est de 28 ha. Comment expliquer cette différence ?
2. Un point GPS isolé à 3 km du reste des localisations. Faut-il l'inclure dans le MCP ? Dans le KDE 95% ?
3. L'isoplèthe KDE 50% représente quoi biologiquement ?
4. Un individu a un MCP plus grand en hiver qu'en été. Quelle hypothèse peut-on former ?

### Erreurs fréquentes

- Comparer des MCP calculés avec des nombres de points très différents
- Choisir h sans critère (utiliser la sélection automatique par défaut ou LSCV)
- Confondre l'isoplèthe 95% KDE avec le MCP 95%
- Interpréter une grande surface de domaine vital comme un indicateur de bonne qualité d'habitat

---

## Fiche 8 — Récapitulatif Biostatistique

### Choisir la bonne méthode

| Situation | Module recommandé |
|-----------|-----------------|
| Résumer mes données de terrain | Analyse CSV + Statistiques descriptives |
| Deux variables continues à comparer | Corrélation & régression |
| Deux groupes à comparer | Tests statistiques (t-test ou Mann-Whitney) |
| Trois groupes ou plus | Tests statistiques (ANOVA) |
| Modéliser des comptages | GLM Comptage |
| Données groupées par site/individu | Modèles mixtes |
| Positions GPS → domaine vital polygone | Domaine vital MCP |
| Positions GPS → domaine vital probabiliste | Domaine vital KDE |

### Hiérarchie des questions statistiques

```
1. Quelle est la nature de ma variable réponse ?
   → Continue → Régression / t-test / ANOVA / LMM
   → Comptage (entier ≥ 0) → GLM Poisson / Binomial négatif
   → Binaire (présence/absence) → GLM Binomial / Modèle d'occupation

2. Mes données sont-elles indépendantes ?
   → Oui → Modèle simple
   → Non (groupées) → Ajouter un effet aléatoire (LMM)

3. Quelle est ma question ?
   → Décrire → Statistiques descriptives / Analyse CSV
   → Estimer une relation → Régression
   → Comparer des groupes → Tests / ANOVA
   → Prédire → GLM avec covariables
```
