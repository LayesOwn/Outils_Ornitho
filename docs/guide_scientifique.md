# Guide Scientifique ORNI-LAB

Ce guide precise les variables, les hypotheses et les interpretations des simulateurs ORNI-LAB. Il est concu pour accompagner un cours, un TD ou une seance de travaux pratiques en ecologie quantitative des oiseaux.

## Principes Generaux

Un simulateur ne donne pas une verite biologique par lui-meme. Il permet de tester une idee sous hypotheses controlees. L'interpretation correcte suit toujours la meme logique :

1. identifier la question biologique ;
2. comprendre ce que chaque variable represente ;
3. modifier une variable a la fois ;
4. comparer les sorties numeriques et graphiques ;
5. discuter les hypotheses non representees dans le modele.

Les valeurs par defaut sont pedagogiques. Elles doivent etre remplacees par des estimations de terrain pour toute analyse appliquee.

## Statistiques Descriptives

### Variables

| Variable | Sens biologique | Importance |
| --- | --- | --- |
| Nombre de sites | Nombre de points d'ecoute, transects ou placettes | Controle la precision descriptive et la stabilite des indicateurs |
| Abondance moyenne attendue | Niveau moyen de comptage par site | Donne l'ordre de grandeur de la population observee |
| Agregation spatiale | Decrit si les individus sont repartis regulierement ou en paquets | Les oiseaux sont souvent agreges par habitat, ressource ou comportement social |
| Habitat | Type de milieu associe au site | Permet d'interpreter les differences de comptage biologiquement |
| Moyenne | Centre arithmetique de la distribution | Sensible aux sites tres riches |
| Mediane | Valeur centrale robuste | Utile quand la distribution est asymetrique |
| Ecart-type | Dispersion des valeurs | Mesure l'heterogeneite entre sites |

### Interpretation

Une moyenne superieure a la mediane indique souvent quelques sites tres abondants. En ornithologie, c'est frequent : colonies, dortoirs, zones humides concentrees ou ressources alimentaires localisees.

### Limites

Les comptages bruts melangent abondance reelle et detectabilite. Un habitat peut sembler pauvre simplement parce que les oiseaux y sont moins detectables.

## Croissance Exponentielle Et Logistique

### Variables

| Variable | Sens biologique | Importance |
| --- | --- | --- |
| `N0` | Effectif initial | Point de depart de la projection |
| `r` | Taux de croissance intrinseque | Resume naissances, morts, immigration et emigration nette |
| `K` | Capacite de charge | Taille maximale soutenable par l'habitat dans le modele logistique |
| Horizon | Nombre d'annees projetees | Plus il est long, plus les hypotheses constantes deviennent fortes |
| Effectif exponentiel | Projection sans limitation | Montre ce qui arrive si aucune ressource ne limite la croissance |
| Effectif logistique | Projection avec densite-dependance | Montre la stabilisation progressive vers `K` |

### Importance De `K`

`K` represente la capacite de l'habitat a soutenir une population : nourriture, sites de nidification, refuges, competition, pression humaine. Augmenter `K` simule une restauration d'habitat ou une extension de zone favorable. Diminuer `K` simule une perte d'habitat, une degradation ou une competition accrue.

### Lecture Des Courbes

- Si `N0 < K`, la courbe logistique monte puis ralentit.
- Si `N0` est proche de `K`, la croissance est faible.
- Si `N0 > K`, la population revient vers `K`.
- La courbe exponentielle sert de reference theorique, mais elle devient vite biologiquement irrealisable.

### Limites

Le modele ne represente pas l'age, la stochasticite environnementale, les catastrophes, la dispersion ou les changements de `K` au cours du temps.

## Analyse CSV

### Format Attendu

Le fichier doit etre un CSV avec une ligne d'en-tete. Les separateurs pris en charge dans l'interface sont la virgule, le point-virgule et la tabulation. Les colonnes numeriques peuvent utiliser le point ou la virgule comme separateur decimal.

### Variables

| Variable | Sens biologique | Importance |
| --- | --- | --- |
| Colonnes numeriques | Comptages, masses, longueurs, richesses, taux, distances | Base des statistiques descriptives, graphiques et regressions |
| Colonnes categorielles | Habitat, site, espece, sexe, annee, traitement | Permettent de comparer des groupes ou colorer les graphiques |
| Valeurs manquantes | Donnees absentes, non mesurees ou invalides | Peuvent biaiser les moyennes et reduire la puissance statistique |
| Coefficient de variation | Ecart-type divise par la moyenne absolue | Repere les variables tres heterogenes |
| Correlation/regression | Relation entre deux variables numeriques | Sert a explorer une hypothese biologique |
| Test de Welch | Comparaison d'une variable numerique entre deux groupes | Utile quand les variances ou tailles de groupes different |

### Analyses Disponibles

- Resume numerique : moyenne, mediane, ecart-type, quartiles, valeurs manquantes.
- Distribution : histogramme avec boite a moustaches.
- Relation : nuage de points et regression lineaire simple.
- Groupes : comparaison de deux groupes par test t de Welch.
- Export : donnees nettoyees en CSV et resume PDF.

### Precautions

Verifier les unites avant l'analyse. Une colonne melangeant grammes et kilogrammes, juveniles et adultes, ou plusieurs protocoles d'observation peut produire une conclusion incorrecte meme si le graphique semble propre.

Les analyses automatiques ne remplacent pas le protocole d'echantillonnage. Pour des donnees de terrain, il faut documenter la date, le site, l'observateur, l'effort d'echantillonnage et la detectabilite.

## Matrices De Leslie

### Variables

| Variable | Sens biologique | Importance |
| --- | --- | --- |
| Fecondites `F0`, `F1`, ... | Nombre moyen de jeunes femelles produites par classe d'age | Determine l'apport de nouveaux juveniles |
| Survies `S0`, `S1`, ... | Probabilite de passer a la classe d'age suivante | Controle la persistance des cohortes |
| Structure initiale | Nombre d'individus par classe d'age au depart | Influence fortement les premieres annees |
| `lambda` dominant | Taux de croissance asymptotique | Indicateur central de croissance, stabilite ou declin |

### Interpretation

- `lambda > 1` : croissance a long terme.
- `lambda = 1` : stabilite theorique.
- `lambda < 1` : declin a long terme.

Une population peut pourtant augmenter temporairement avec `lambda < 1` si sa structure initiale est favorable. Il faut donc distinguer dynamique transitoire et tendance asymptotique.

### Limites

Les fecundites et survies sont supposees constantes. En realite, elles varient avec la meteo, la densite, la predation, l'age exact, la qualite de l'habitat et les pratiques humaines.

## Correlation Et Regression

### Variables

| Variable | Sens biologique | Importance |
| --- | --- | --- |
| Taille d'echantillon `n` | Nombre d'oiseaux mesures | Influence la precision et la puissance statistique |
| Variabilite individuelle | Bruit autour de la relation moyenne | Diminue la force apparente de la relation |
| Pente | Variation attendue de `Y` pour une unite de `X` | Donne le sens et l'amplitude de la relation |
| Intercept | Valeur predite de `Y` quand `X = 0` | Souvent peu interpretable biologiquement si `X = 0` est hors domaine |
| `r` de Pearson | Force de relation lineaire | Va de -1 a 1 |
| `R2` | Proportion de variance expliquee | Mesure la qualite descriptive du modele |
| p-value | Compatibilite avec l'hypothese d'absence de relation | Ne mesure pas l'importance biologique |

### Interpretation

Une relation forte entre longueur d'aile et masse peut traduire une contrainte morphologique, une difference d'age, une difference de sexe ou une variation de condition corporelle. La regression decrit une association ; elle ne prouve pas le mecanisme causal.

### Limites

Les points doivent etre independants. Une regression simple ne controle pas les effets de site, sexe, age, saison ou espece.

## Capture-Marquage-Recapture

### Variables

| Variable | Sens biologique | Importance |
| --- | --- | --- |
| `M` | Nombre d'individus marques lors de la premiere session | Base de comparaison pour la recapture |
| `C` | Nombre d'individus captures lors de la seconde session | Taille de l'echantillon de controle |
| `R` | Nombre d'individus marques retrouves | Variable la plus critique pour la precision |
| Taux de recapture | `R / C` | Indique la detectabilite relative des marques |
| IC 95 % | Intervalle d'incertitude | Devient large quand `R` est faible |

### Interpretation

Si peu d'individus marques sont recaptures, l'estimation d'abondance augmente et devient tres incertaine. Cela peut indiquer une grande population, une faible detectabilite, une mauvaise homogeneisation des marques, une emigration ou une perte de marques.

### Hypotheses

- population fermee entre les deux sessions ;
- marques conservees et reconnues ;
- probabilites de capture similaires entre individus ;
- melange suffisant des individus marques et non marques.

## Lotka-Volterra

### Variables

| Variable | Sens biologique | Importance |
| --- | --- | --- |
| Proies initiales | Effectif initial de la ressource ou espece proie | Controle la phase initiale du cycle |
| Predateurs initiaux | Effectif initial des predateurs | Controle le decalage de reponse |
| `alpha` | Croissance des proies en absence de predateurs | Plus il est eleve, plus les proies recuperent vite |
| `beta` | Intensite de predation | Plus il est eleve, plus les predateurs reduisent les proies |
| `delta` | Conversion des proies en croissance des predateurs | Relie ressource consommee et reproduction/survie des predateurs |
| `gamma` | Mortalite des predateurs | Controle le declin quand les proies sont rares |

### Interpretation

Les oscillations indiquent un retard : les proies augmentent, les predateurs repondent ensuite, puis les proies diminuent, entrainant a leur tour une baisse des predateurs.

### Limites

Le modele n'inclut pas de capacite de charge, refuge spatial, saisonnalite, proies alternatives, comportement adaptatif ou stochasticite.

## Tests Statistiques

### Variables

| Variable | Sens biologique | Importance |
| --- | --- | --- |
| `n_a`, `n_b` | Nombre de nids ou observations par groupe | Controle la puissance du test |
| Moyennes de groupe | Niveau moyen du trait ou succes reproducteur | Donne la taille brute de l'effet |
| Variabilite | Dispersion intra-groupe | Plus elle est forte, plus la difference est difficile a detecter |
| t de Welch | Statistique de comparaison | Tient compte des tailles et variances |
| p-value | Probabilite d'un resultat aussi extreme sous hypothese nulle | Aide a juger la compatibilite avec le hasard |

### Interpretation

Une difference statistiquement significative peut etre biologiquement faible. Inversement, une difference biologiquement importante peut etre non significative si l'echantillon est petit ou tres variable.

### Limites

Le test suppose des observations independantes et une variable comparable entre groupes. Les effets de site, annee ou espece peuvent necessiter des modeles plus avances.

## PVA Et Conservation

### Variables

| Variable | Sens biologique | Importance |
| --- | --- | --- |
| `N0` | Effectif initial | Plus il est faible, plus le risque demographique augmente |
| Croissance moyenne `r` | Tendance moyenne annuelle | Determine la direction generale |
| Variabilite `sd_r` | Fluctuation environnementale autour de `r` | Peut augmenter fortement le risque meme si `r` est positif |
| `K` | Capacite de charge | Limite superieure liee a l'habitat disponible |
| Seuil de quasi-extinction | Effectif considere comme critique | Definit l'evenement de risque |
| Pertes annuelles | Mortalite ou perte fixe chaque annee | Simule collisions, prelevements, destruction de nids, etc. |
| Horizon | Duree de projection | Les incertitudes augmentent avec le temps |
| Iterations | Nombre de trajectoires simulees | Stabilise l'estimation du risque |

### Interpretation

Le risque de quasi-extinction est la proportion de simulations qui passent sous le seuil critique au moins une fois. Il ne predit pas exactement le futur ; il mesure la fragilite d'une population sous les hypotheses choisies.

### Importance De La Variance

Deux populations avec le meme `r` moyen peuvent avoir des risques tres differents si la variance environnementale differe. Une espece avec bonnes annees et tres mauvaises annees peut etre plus vulnerable qu'une espece au declin lent mais regulier.

### Limites

La PVA simplifiee ne represente pas explicitement la genetique, la structure d'age, les catastrophes rares, la dispersion, les effets Allee, la detectabilite ou la correlation temporelle des mauvaises annees.

## Scenarios De Gestion

### Variables

| Variable | Sens biologique | Importance |
| --- | --- | --- |
| Scenario | Hypothese d'action de conservation | Permet une comparaison explicite des strategies |
| Croissance moyenne | Effet attendu sur la dynamique moyenne | Peut representer restauration ou amelioration reproductive |
| Variabilite | Stabilite du systeme | Une action peut reduire le risque en reduisant la variance |
| Pertes | Pression annuelle persistante | Variable souvent directement gerable |
| `K` | Habitat disponible ou qualite maximale | Mesure l'effet d'une action sur la capacite du milieu |
| Risque | Probabilite de passer sous le seuil | Critere central de comparaison |

### Interpretation

Un scenario est preferable s'il reduit le risque de quasi-extinction, mais il faut aussi regarder la mediane finale et la plausibilite des hypotheses. Une action combinee peut etre meilleure, mais elle peut aussi etre plus couteuse ou moins realiste.

## Bonnes Pratiques D'enseignement

- Demander aux etudiants de predire le sens du changement avant de bouger un curseur.
- Comparer toujours au moins deux scenarios.
- Faire distinguer effet statistique, effet biologique et effet de gestion.
- Faire noter les hypotheses non representees par le simulateur.
- Utiliser les exports CSV pour refaire un graphique ou un calcul hors Streamlit.

## Erreurs D'interpretation Frequentes

- Confondre correlation et causalite.
- Interpretrer une p-value comme une taille d'effet.
- Croire qu'une PVA predit une date exacte d'extinction.
- Oublier que `K` peut changer avec le climat, l'habitat ou la gestion.
- Ignorer la detectabilite dans les comptages.
- Comparer des scenarios sans regarder leurs hypotheses de depart.
