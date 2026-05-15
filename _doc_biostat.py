# Données des 8 modules Biostatistique — importé par generate_documentation.py
BIOSTAT_MODULES = [
    dict(
        num="5.1", title="Statistiques descriptives", tag="BIOSTATISTIQUE",
        description=(
            "Module d'exploration initiale d'un jeu de données ornithologique. "
            "Il calcule les statistiques de position et de dispersion pour chaque variable "
            "numérique, trace des histogrammes de distribution, des boîtes à moustaches "
            "comparatives, et une matrice de corrélation visuelle (heatmap). "
            "Ce module est systématiquement le point d'entrée avant toute analyse inférentielle."
        ),
        methodology=(
            "Pour chaque variable numérique, le module calcule : n, moyenne, médiane, "
            "écart-type, variance, minimum, maximum, Q1, Q3, IQR = Q3 - Q1. "
            "La matrice de corrélation de Pearson est calculée sur toutes les paires de "
            "variables numériques (pandas.DataFrame.corr). "
            "Les boîtes à moustaches affichent la médiane, les quartiles et les valeurs "
            "aberrantes au-delà de Q1 - 1.5*IQR et Q3 + 1.5*IQR."
        ),
        formulas=[
            "Moyenne :  x_bar = (1/n) * sum(x_i)",
            "Variance : s² = (1/(n-1)) * sum((x_i - x_bar)²)",
            "IQR :      IQR = Q3 - Q1",
            "Outliers : x < Q1 - 1.5*IQR  OU  x > Q3 + 1.5*IQR",
            "Pearson :  r = cov(x,y) / (s_x * s_y)",
        ],
        algorithm=[
            "Chargement et typage automatique des colonnes du CSV",
            "Calcul des statistiques descriptives (pandas.describe + moments supplémentaires)",
            "Détection des valeurs aberrantes par la règle IQR",
            "Construction de la matrice de corrélation et affichage en heatmap",
            "Génération des histogrammes et boîtes à moustaches par groupe si variable catégorielle présente",
        ],
        ornithology=(
            "Utilisé pour explorer des jeux de données de morphométrie (envergure, masse, "
            "longueur du tarse), de comptages sur points d'écoute, ou de données de baguage. "
            "Permet de vérifier si les distributions sont approximativement normales avant "
            "d'appliquer des tests paramétriques, et d'identifier les valeurs aberrantes "
            "liées à des erreurs de saisie ou à des individus atypiques (juvéniles, hybrides)."
        ),
        inputs=[
            "Fichier CSV avec colonnes numériques et/ou catégorielles",
            "Sélection de la variable à visualiser",
            "Variable de groupement optionnelle",
        ],
        outputs=[
            "Tableau : n, moyenne, médiane, SD, min, Q1, Q3, max, IQR",
            "Histogramme de distribution avec courbe de densité",
            "Boîtes à moustaches (par groupe si applicable)",
            "Heatmap de la matrice de corrélation de Pearson",
            "Liste des valeurs aberrantes détectées",
        ],
        interpretation=(
            "Une distribution normale apparaît comme une cloche symétrique sur l'histogramme. "
            "Une médiane très différente de la moyenne indique une asymétrie. "
            "Un r de Pearson > 0.7 indique une forte corrélation linéaire ; "
            "r > 0.9 suggère quasi-colinéarité. Les points hors moustaches sont "
            "des candidats à vérification (erreur de saisie ou biologie réelle)."
        ),
        pitfalls=[
            "Confondre corrélation et causalité : deux variables corrélées (ex. masse et "
            "envergure) ne signifient pas que l'une cause l'autre — une troisième variable "
            "(âge, sexe) peut expliquer les deux.",
            "Utiliser la moyenne sur une distribution fortement asymétrique (ex. comptages) : "
            "préférer la médiane comme indicateur de position centrale.",
            "Ignorer les valeurs aberrantes avant l'analyse : elles peuvent inflater "
            "l'écart-type et masquer la vraie variabilité biologique.",
        ],
        importance=(
            "L'analyse exploratoire des données (AED) est la fondation de tout travail "
            "statistique rigoureux. Elle prévient les erreurs d'interprétation dues "
            "à des données non vérifiées, guide le choix des méthodes ultérieures, "
            "et permet de détecter les problèmes de qualité avant qu'ils ne biaisent "
            "les conclusions biologiques."
        ),
        key_ref="Tukey, J.W. (1977). Exploratory Data Analysis. Addison-Wesley, Reading, MA.",
    ),
    dict(
        num="5.2", title="Analyse CSV guidée", tag="BIOSTATISTIQUE",
        description=(
            "Module d'exploration automatisée et approfondie d'un fichier CSV de terrain. "
            "Il détecte l'encodage et le séparateur, nettoie les données (valeurs manquantes, "
            "virgules décimales, alias nuls), propose une analyse univariée complète par "
            "variable (16 statistiques, test de normalité), une analyse bivariée multi-types "
            "(numérique-numérique, numérique-catégorielle, catégorielle-catégorielle), "
            "une matrice de corrélation interactive, et un export structuré en 6 onglets."
        ),
        methodology=(
            "Détection d'encodage : essai successif UTF-8, UTF-8 BOM, Latin-1, CP1252, UTF-16. "
            "Séparateur : csv.Sniffer sur les 4096 premiers octets. "
            "Nettoyage : normalisation des valeurs null (NA, N/A, null, -, ?, --), "
            "correction décimale virgule->point, détection colonnes dates. "
            "Profil univarié : moyenne, médiane, mode, SD, skewness, kurtosis, "
            "IQR, N outliers IQR, N outliers Z>3, Shapiro-Wilk (n≤5000) ou KS (n>5000). "
            "Bivarié num-num : Pearson + Spearman + OLS. "
            "Bivarié num-cat 2 gr : Welch + Mann-Whitney. k gr : ANOVA + Kruskal-Wallis + eta². "
            "Bivarié cat-cat : chi-carré + V de Cramér."
        ),
        formulas=[
            "Skewness :   g1 = (1/n) * sum((x_i - x_bar)³) / s³",
            "Kurtosis :   g2 = (1/n) * sum((x_i - x_bar)^4) / s^4 - 3",
            "V de Cramér: V = sqrt(chi² / (n * (min(r,c) - 1)))",
            "Spearman :   r_s = Pearson calculé sur les rangs de x et y",
            "eta² :       eta² = SS_between / SS_total",
        ],
        algorithm=[
            "Tentative de lecture avec 5 encodages x séparateur sniffé, fallback tous séparateurs",
            "Nettoyage profond : NULL aliases, virgule->point, détection types, dates",
            "Classification des colonnes : numérique, catégorielle, date, texte",
            "Calcul du profil complet pour chaque colonne numérique (16 statistiques)",
            "Analyse bivariée adaptée au type des deux colonnes sélectionnées",
            "Construction de la matrice de corrélation (Pearson ou Spearman au choix)",
            "Affichage en 6 onglets : Aperçu, Qualité, Univarié, Relations, Corrélations, Export",
        ],
        ornithology=(
            "Point d'entrée universel pour tout fichier de terrain : données STOC, SHOC, BBS, "
            "LPO, baguage, transects, grilles EPS. Permet à un étudiant de charger ses propres "
            "données de TP sans connaissance préalable du format et d'obtenir une analyse "
            "statistique complète avec test d'hypothèse adapté au type de données."
        ),
        inputs=[
            "Fichier CSV (encodage et séparateur auto-détectés)",
            "Sélection des colonnes pour l'analyse bivariée",
            "Choix Pearson / Spearman pour la matrice de corrélation",
        ],
        outputs=[
            "Onglet Aperçu : premières lignes, types, dimensions du jeu de données",
            "Onglet Qualité : % valeurs manquantes, doublons, colonnes constantes",
            "Onglet Univarié : 16 statistiques + test normalité + histogramme + boxplot",
            "Onglet Relations : test adapté au type (Welch / ANOVA / chi² / Pearson+Spearman)",
            "Onglet Corrélations : heatmap matrice complète avec valeurs",
            "Onglet Export : téléchargement des données nettoyées en CSV",
        ],
        interpretation=(
            "Onglet Qualité : plus de 20% de valeurs manquantes sur une colonne clé doit "
            "alerter sur la fiabilité des analyses qui l'utilisent. "
            "Skewness > 1 ou < -1 indique une forte asymétrie — envisager une transformation log. "
            "V de Cramér > 0.3 indique une association substantielle entre deux variables catégorielles. "
            "Shapiro-Wilk p > 0.05 : pas d'écart significatif à la normalité à ce seuil."
        ),
        pitfalls=[
            "Ne pas vérifier l'encodage du fichier : les accents et noms d'espèces peuvent "
            "être corrompus si le fichier UTF-8 est ouvert en Latin-1.",
            "Confondre N outliers IQR et N outliers Z>3 : sur une distribution asymétrique, "
            "l'IQR est plus robuste et doit être préféré.",
            "Appliquer Pearson sans visualiser la relation : une corrélation de Pearson "
            "nulle n'exclut pas une relation non linéaire forte.",
        ],
        importance=(
            "Réduit la barrière d'entrée pour les étudiants sans compétences en programmation. "
            "Centralise la validation de la qualité des données, étape souvent négligée "
            "qui conduit à des analyses incorrectes. Idéal pour des TP avec données de terrain réelles."
        ),
        key_ref="Wickham, H. & Grolemund, G. (2017). R for Data Science. O'Reilly Media, Sebastopol.",
    ),
    dict(
        num="5.3", title="Corrélation et régression", tag="BIOSTATISTIQUE",
        description=(
            "Quantifie et visualise la relation linéaire entre deux variables continues. "
            "Propose la régression linéaire simple (OLS) avec nuage de points, droite ajustée "
            "et intervalle de confiance à 95%. Affiche un graphique de résidus pour diagnostiquer "
            "l'homoscédasticité et la linéarité. Calcule le coefficient de Pearson r, "
            "le coefficient de détermination R², et teste la significativité de la pente."
        ),
        methodology=(
            "Régression par Moindres Carrés Ordinaires (OLS) : minimise SSE = sum((y_i - y_hat_i)²). "
            "Pente et intercept estimés analytiquement. "
            "Test de la pente : t = b1 / SE(b1) suivant une loi de Student à n-2 degrés de liberté. "
            "IC 95% de la droite calculé par propagation des erreurs : "
            "y_hat ± t_{0.025,n-2} * SE(y_hat) avec SE variant le long de la droite. "
            "Guard : n >= 3 observations valides et std(X) > 0."
        ),
        formulas=[
            "b1 (pente) = sum((x_i - x_bar)(y_i - y_bar)) / sum((x_i - x_bar)²)",
            "b0 (intercept) = y_bar - b1 * x_bar",
            "R² = 1 - SSE/SST   où SST = sum((y_i - y_bar)²)",
            "SE(b1) = sqrt(MSE / sum((x_i - x_bar)²))",
            "t = b1 / SE(b1)  ~  Student(n-2)  sous H0 : b1 = 0",
        ],
        algorithm=[
            "Validation : n >= 3 observations valides, std(X) != 0",
            "Calcul OLS via scipy.stats.linregress(x, y)",
            "Construction de la droite ajustée sur 200 points (grille régulière)",
            "Calcul des résidus : e_i = y_i - (b0 + b1*x_i)",
            "Tracé nuage de points + droite + bande IC 95%",
            "Tracé résidus vs valeurs ajustées pour diagnostic",
        ],
        ornithology=(
            "Applications : relation masse-envergure (allométrie), régression du succès "
            "reproducteur sur la date de ponte (phénologie climatique), abondance en fonction "
            "de la surface d'habitat (écologie du paysage), longueur du tarse en fonction "
            "de l'altitude de nidification (gradient altitudinal)."
        ),
        inputs=[
            "Variable explicative X (continue)",
            "Variable réponse Y (continue)",
            "Mode simulation : n individus, bruit gaussien, graine aléatoire",
        ],
        outputs=[
            "b0 (intercept) et b1 (pente) avec erreurs-type et p-values",
            "R² et coefficient de Pearson r",
            "Nuage de points + droite de régression + bande IC 95%",
            "Graphique des résidus vs valeurs ajustées",
            "Export PDF du résumé statistique",
        ],
        interpretation=(
            "R² proche de 1 : la relation linéaire explique bien la variabilité de Y. "
            "R² proche de 0 : la relation linéaire est faible (mais une relation non "
            "linéaire peut exister — vérifier le nuage). "
            "Résidus en entonnoir = hétéroscédasticité (variance croissante avec Y_hat). "
            "Résidus en courbe = relation non linéaire : envisager une transformation (log, racine)."
        ),
        pitfalls=[
            "Extrapoler hors du domaine des données : la droite peut prédire des masses "
            "négatives ou biologiquement impossibles hors de la plage observée.",
            "Ignorer le diagnostic des résidus : un R² élevé n'implique pas un bon "
            "ajustement si les résidus montrent un pattern systématique.",
            "Appliquer une régression OLS quand Y est un comptage (entier ≥ 0) : "
            "utiliser le GLM Poisson qui est le modèle adapté.",
        ],
        importance=(
            "La régression linéaire est l'outil statistique le plus utilisé en écologie. "
            "Comprendre ses hypothèses (linéarité, normalité des résidus, homoscédasticité, "
            "indépendance) et les diagnostiquer via les graphiques de résidus est essentiel "
            "pour produire des conclusions biologiques fiables et reproductibles."
        ),
        key_ref="Zar, J.H. (2010). Biostatistical Analysis, 5th ed. Prentice Hall, Upper Saddle River.",
    ),
    dict(
        num="5.4", title="Tests statistiques", tag="BIOSTATISTIQUE",
        description=(
            "Compare des groupes d'oiseaux selon une variable quantitative continue. "
            "Pour deux groupes : t-test de Welch (paramétrique) et Mann-Whitney U "
            "(non paramétrique). Pour 3 à 6 groupes : ANOVA unidirectionnelle et "
            "Kruskal-Wallis. Inclut des tests de normalité (Shapiro-Wilk) avec graphiques Q-Q "
            "pour chaque groupe, et calcul des tailles d'effet (d de Cohen, eta²)."
        ),
        methodology=(
            "Normalité (Shapiro-Wilk) : H0 = distribution normale, recommandé pour n < 50. "
            "t-test de Welch : compare deux moyennes sans supposer l'égalité des variances "
            "(degrés de liberté de Welch-Satterthwaite, fractionnaires). "
            "Mann-Whitney U : test non paramétrique sur les rangs, robuste aux outliers. "
            "ANOVA : F = MS_between / MS_within (rapporte à la variabilité intra-groupe). "
            "Kruskal-Wallis : extension non paramétrique de l'ANOVA sur les rangs. "
            "Guard : au moins 2 groupes avec >= 2 observations chacun avant ANOVA/Kruskal."
        ),
        formulas=[
            "Welch t :  t = (x1_bar - x2_bar) / sqrt(s1²/n1 + s2²/n2)",
            "Cohen d :  d = (x1_bar - x2_bar) / s_pooled",
            "ANOVA F :  F = [SS_between / (k-1)] / [SS_within / (n-k)]",
            "eta² :     eta² = SS_between / SS_total  [0.01 faible, 0.06 moyen, 0.14 fort]",
            "Kruskal H: H = (12 / n(n+1)) * sum(R_j² / n_j) - 3(n+1)",
        ],
        algorithm=[
            "Test de Shapiro-Wilk par groupe (scipy.stats.shapiro)",
            "Tracé des graphiques Q-Q (scipy.stats.probplot) par groupe",
            "Si 2 groupes : Welch t-test + Mann-Whitney U + d de Cohen",
            "Si k groupes : ANOVA (f_oneway) + Kruskal-Wallis + eta² (SS_between/SS_total)",
            "Guard ANOVA/Kruskal : len(valid_series) >= 2",
            "Interprétation automatique de la significativité et de la taille d'effet",
        ],
        ornithology=(
            "Comparer la masse entre mâles et femelles, le succès de nidification entre "
            "habitats (forêt / bocage / zone humide), l'abondance entre saisons ou années, "
            "la longueur du tarse entre populations géographiques. Fondamental pour valider "
            "des différences biologiques avant de les interpréter écologiquement."
        ),
        inputs=[
            "Variable numérique à comparer",
            "Variable de groupement (2 à 6 modalités)",
            "Mode simulation ou CSV",
        ],
        outputs=[
            "Tableau Shapiro-Wilk : W et p-value par groupe",
            "Graphiques Q-Q par groupe (max 4)",
            "Statistique t / F / H, degrés de liberté, p-value",
            "Taille d'effet : d de Cohen (2 groupes) ou eta² (k groupes)",
            "Boîtes à moustaches comparatives avec annotation significativité",
        ],
        interpretation=(
            "p < 0.05 : différence statistiquement significative. "
            "d de Cohen : 0.2 = faible, 0.5 = modéré, 0.8 = fort. "
            "eta² : 0.01 = faible, 0.06 = modéré, 0.14 = fort. "
            "Si Welch significatif mais Mann-Whitney non : inspecter les valeurs aberrantes. "
            "Si Kruskal-Wallis significatif : des tests de Dunn post-hoc "
            "(correction Bonferroni) sont nécessaires pour identifier les paires différentes."
        ),
        pitfalls=[
            "Se fier uniquement à la p-value sans la taille d'effet : avec n = 1000 oiseaux, "
            "une différence de 0.1 g peut être très significative mais biologiquement nulle.",
            "Réaliser de multiples comparaisons sans correction : 20 tests à alpha = 0.05 "
            "génèrent en espérance 1 faux positif — appliquer la correction de Bonferroni.",
            "Ignorer le test de normalité avant le t-test : avec n < 20 et distribution "
            "asymétrique, les conclusions du test paramétrique sont non fiables.",
        ],
        importance=(
            "Les tests statistiques sont l'épine dorsale de l'écologie quantitative. "
            "Enseigner les tests paramétriques et non paramétriques avec vérification "
            "des hypothèses forme des scientifiques rigoureux capables de choisir "
            "le test adapté à leurs données plutôt que d'appliquer mécaniquement "
            "le t-test dans tous les contextes."
        ),
        key_ref="Sokal, R.R. & Rohlf, F.J. (2012). Biometry, 4th ed. W.H. Freeman, New York.",
    ),
    dict(
        num="5.5", title="GLM pour données de comptage", tag="BIOSTATISTIQUE",
        description=(
            "Modélise des données de comptage d'oiseaux (entiers non négatifs) avec un "
            "GLM Poisson ou Binomial Négatif. Contrôle simultanément pour l'habitat, "
            "la tendance temporelle et l'effort d'observation (offset). Compare les deux "
            "familles par AIC. Interprète les coefficients en Incidence Rate Ratio (IRR = exp(beta)). "
            "Propose des graphiques de diagnostics des résidus de Pearson."
        ),
        methodology=(
            "GLM Poisson : log(E[Y]) = X*beta + log(effort). "
            "Vérification surdispersion : phi = chi²_Pearson / df. Si phi >> 1, "
            "le Binomial Négatif est plus approprié. "
            "BN : Var(Y) = mu + mu²/r (paramètre de dispersion r estimé). "
            "Estimation par Maximum de Vraisemblance (IRLS : moindres carrés itérés reponderés). "
            "AIC = -2*log(L) + 2*k. IRR_j = exp(beta_j) : multiplicateur de l'abondance."
        ),
        formulas=[
            "Poisson : log(mu_i) = beta_0 + beta_1*X1_i + ... + log(effort_i)",
            "IRR_j = exp(beta_j)  [multiplicateur pour une unité de X_j]",
            "Surdispersion : phi = sum((y_i - mu_i)² / mu_i) / (n - p)",
            "AIC = -2 * log(L_max) + 2 * k  [k = nombre de paramètres]",
            "BN Variance : Var(Y) = mu + mu²/r   [r -> inf converge vers Poisson]",
        ],
        algorithm=[
            "Validation des colonnes (comptages >= 0, habitat catégoriel)",
            "Ajustement GLM Poisson (statsmodels.formula.api.glm, family=Poisson)",
            "Calcul du ratio de surdispersion phi",
            "Ajustement GLM Binomial Négatif (NegativeBinomial)",
            "Comparaison AIC Poisson vs BN avec recommandation automatique",
            "Tableau IRR avec IC 95% via exp(coef ± 1.96*SE)",
            "Graphiques diagnostics : résidus Pearson vs ajustés + Q-Q",
        ],
        ornithology=(
            "Standard pour les comptages sur points d'écoute (IPA, STOC-EPS), "
            "relevés de transects ou points fixes. Permet de séparer l'effet habitat de "
            "l'effet année tout en corrigeant pour des efforts d'écoute variables. "
            "La surdispersion est quasi-universelle dans les comptages d'oiseaux "
            "(agrégation spatiale) : le Binomial Négatif est souvent nécessaire."
        ),
        inputs=[
            "Colonne de comptages (entiers >= 0)",
            "Colonne habitat (catégorielle)",
            "Colonne année ou session (numérique)",
            "Colonne effort d'observation (offset, ex. durée en minutes)",
        ],
        outputs=[
            "Tableau IRR avec IC 95% et p-values pour chaque prédicteur",
            "AIC Poisson vs Binomial Négatif avec recommandation",
            "Ratio de surdispersion phi",
            "Graphiques de résidus de Pearson vs valeurs ajustées et Q-Q",
        ],
        interpretation=(
            "IRR = 1.5 pour l'habitat Forêt (référence = Champ) signifie : abondance "
            "1.5x plus élevée en forêt, toutes choses égales. "
            "IRR = 0.7 pour l'année signifie : déclin de 30% par an. "
            "phi > 2 confirme une surdispersion : le GLM Poisson sous-estime les "
            "erreurs-type, produisant de faux positifs. "
            "phi > 10 : envisager le BN ou un modèle à inflation de zéros."
        ),
        pitfalls=[
            "Utiliser la régression OLS sur des comptages : résidus non normaux, "
            "prédictions négatives possibles, p-values incorrectes.",
            "Ignorer la surdispersion (phi >> 1) : les erreurs-type Poisson sont sous-estimées "
            "— utiliser le BN ou la quasi-Poisson.",
            "Omettre l'offset : sans correction pour l'effort, les sites visités plus "
            "longtemps paraissent artificiellement plus riches en espèces.",
        ],
        importance=(
            "Les comptages d'oiseaux violent systématiquement les hypothèses de la "
            "régression linéaire. Le GLM est le modèle adéquat et son enseignement est "
            "indispensable pour analyser les données des programmes de surveillance long "
            "terme (STOC, BBS, Wetland Bird Survey) qui produisent les indicateurs de "
            "l'état de l'avifaune utilisés par les politiques de conservation."
        ),
        key_ref="McCullagh, P. & Nelder, J.A. (1989). Generalized Linear Models, 2nd ed. Chapman & Hall.",
    ),
    dict(
        num="5.6", title="Modèle mixte — LMM", tag="BIOSTATISTIQUE",
        description=(
            "Modèle Linéaire Mixte (LMM) séparant les effets fixes (prédicteurs biologiques) "
            "des effets aléatoires (sites, individus, sessions de baguage). Estime le coefficient "
            "de corrélation intraclasse (ICC) quantifiant la part de variance due au groupement. "
            "Affiche les composantes de variance et les effets fixes avec erreurs-type. "
            "Utilise l'estimateur REML non biaisé pour les composantes de variance."
        ),
        methodology=(
            "Modèle : y_ij = beta_0 + beta_1*x_ij + b_j + epsilon_ij, "
            "avec b_j ~ N(0, sigma²_b) et epsilon_ij ~ N(0, sigma²). "
            "Estimation par REML (Restricted Maximum Likelihood) : non biaisé pour sigma²_b "
            "contrairement au ML classique, recommandé pour estimer les composantes de variance. "
            "ICC = sigma²_b / (sigma²_b + sigma²). Un ICC > 0.1 justifie le LMM. "
            "Implémenté via statsmodels.formula.api.mixedlm."
        ),
        formulas=[
            "LMM : y_ij = (beta_0 + beta_1*x_ij) + b_j + epsilon_ij",
            "      b_j ~ N(0, sigma²_b)  [effet aléatoire groupe j]",
            "      epsilon_ij ~ N(0, sigma²_e)  [résidu intra-groupe]",
            "ICC = sigma²_b / (sigma²_b + sigma²_e)",
            "REML : maximise la vraisemblance des contrastes orthogonaux aux effets fixes",
        ],
        algorithm=[
            "Extraction des colonnes par valeurs numpy (évite collisions de noms)",
            "Validation : >= 2 groupes distincts, >= 5 observations, X non constante",
            "Ajustement LMM par REML : mixedlm('_Y ~ _X', sub, groups).fit(reml=True)",
            "Extraction des effets fixes tronqués à n_fe = len(fe_params)",
            "SE depuis bse_fe ou bse[:n_fe] selon version statsmodels (0.14+)",
            "Calcul ICC, AIC (avec fallback -2*llf + 2*k si NaN), n_groups",
            "Nuage de points coloré par groupe + droite d'effet fixe global",
        ],
        ornithology=(
            "Indispensable pour les données de morphométrie collectées sur plusieurs sites "
            "(effet site = variation entre localités), les suivis comportementaux avec individus "
            "mesurés plusieurs fois, les données de baguage avec passagers à sessions répétées. "
            "Un ICC > 0.1 signifie qu'ignorer la structure groupée gonfle les degrés de liberté "
            "et produit des p-values trop optimistes (taux de faux positifs > 5%)."
        ),
        inputs=[
            "Variable réponse Y (numérique continue)",
            "Prédicteur fixe X (numérique)",
            "Variable de groupement G (catégorielle, effet aléatoire)",
        ],
        outputs=[
            "Tableau effets fixes : coef., SE, z, p-value pour Intercept et X",
            "Composantes de variance : sigma²_b (entre groupes) et sigma²_e (résiduelle)",
            "ICC et AIC du modèle",
            "Nuage de points coloré par groupe + droite d'effet fixe global",
            "Graphique des résidus vs valeurs ajustées",
        ],
        interpretation=(
            "ICC proche de 0 : peu de variance expliquée par le groupement, OLS suffisant. "
            "ICC > 0.1 : le groupement explique plus de 10% de la variance — LMM justifié. "
            "ICC > 0.5 : structure de groupe très forte ; les effets fixes nécessitent "
            "beaucoup de groupes pour être bien estimés. "
            "La pente beta_1 est l'effet de X net de la variabilité inter-groupes."
        ),
        pitfalls=[
            "Utiliser ML au lieu de REML pour estimer les composantes de variance : "
            "ML sous-estime sigma²_b, particulièrement avec peu de groupes (< 10).",
            "Traiter le groupe comme effet fixe quand il représente un échantillon d'une "
            "population de groupes possibles : l'effet aléatoire est plus approprié et "
            "plus parcimonieux.",
            "Ignorer l'ICC et utiliser OLS sur données groupées : les erreurs-type des "
            "effets fixes sont sous-estimées, produisant un taux de faux positifs > 5%.",
        ],
        importance=(
            "La plupart des données ornithologiques de terrain sont groupées (par site, "
            "transect, colonie ou individu). Le LMM est la solution standard en écologie "
            "moderne pour respecter la structure des données. Son enseignement est "
            "indispensable dans tout cursus de biostatistique appliquée à l'ornithologie."
        ),
        key_ref="Zuur, A.F. et al. (2009). Mixed Effects Models and Extensions in Ecology with R. Springer.",
    ),
    dict(
        num="5.7", title="Domaine vital — MCP", tag="BIOSTATISTIQUE",
        description=(
            "Calcule le Minimum Convex Polygon (MCP) à partir de localisations GPS "
            "individuelles. Le MCP est le plus petit polygone convexe contenant X% "
            "des localisations d'un individu, paramétrable de 50% à 100%. "
            "Propose une carte interactive avec superposition des points et des polygones, "
            "et un tableau comparatif des aires MCP par individu et par percentile."
        ),
        methodology=(
            "Algorithme : (1) calculer le centroïde de toutes les localisations, "
            "(2) calculer les distances euclidiennes de chaque point au centroïde, "
            "(3) trier par distance croissante, (4) conserver les X% points les plus "
            "proches, (5) calculer l'enveloppe convexe via scipy.spatial.ConvexHull. "
            "L'aire correspond à ConvexHull.volume en 2D. "
            "Note : les coordonnées doivent être en projection métrique pour des aires en ha."
        ),
        formulas=[
            "Centroïde : (x_c, y_c) = (mean(x_i), mean(y_i))",
            "Distance : d_i = sqrt((x_i - x_c)² + (y_i - y_c)²)",
            "MCP X% : sélectionner les X/100 * n points les plus proches du centroïde",
            "Aire MCP = ConvexHull(points_selectionnes).volume  [unités : coords²]",
        ],
        algorithm=[
            "Chargement des colonnes X (lon) et Y (lat) par identifiant individuel",
            "Calcul du centroïde par individu",
            "Tri des localisations par distance euclidienne au centroïde",
            "Sélection du percentile choisi (50%, 75%, 90%, 95%, 100%)",
            "Calcul de l'enveloppe convexe (scipy.spatial.ConvexHull)",
            "Tracé interactif Plotly : points colorés par individu + polygone MCP",
            "Tableau des aires par individu et par percentile",
        ],
        ornithology=(
            "Utilisé pour estimer le domaine vital de rapaces (busard, milan, épervier), "
            "cigognes, limicoles en nidification, passereaux équipés de balises GPS legères "
            "(< 3% de la masse corporelle). Permet de comparer les domaines vitaux entre "
            "sexes, classes d'âge ou saisons, et d'identifier les zones d'habitat critiques."
        ),
        inputs=[
            "Colonne X (longitude) et Y (latitude) — coordonnées décimales ou métriques",
            "Colonne identifiant individuel",
            "Percentile MCP (50%, 75%, 90%, 95%, 100%)",
        ],
        outputs=[
            "Carte interactive Plotly avec points et polygone MCP par individu",
            "Tableau : N localisations totales, N utilisées, aire MCP par individu",
            "Graphique de comparaison des aires entre individus",
        ],
        interpretation=(
            "MCP 95% : domaine vital usuel, excluant 5% des localisations les plus "
            "excentrées (déplacements exceptionnels ou erreurs GPS). "
            "MCP 50% : zone cœur de l'activité principale. "
            "La taille du MCP augmente avec le nombre de localisations jusqu'à saturation : "
            "au moins 30 à 50 localisations sont recommandées pour un MCP stable."
        ),
        pitfalls=[
            "Comparer des MCP avec des effectifs de localisations très différents : "
            "un individu avec 100 points aura un MCP systématiquement plus grand "
            "qu'un individu avec 20 points, même si leurs territoires sont identiques.",
            "Utiliser le MCP 100% pour comparer des individus : une seule localisation "
            "extrême (erreur GPS) peut doubler la surface estimée.",
            "Calculer des superficies en degrés décimaux sans conversion métrique : "
            "convertir en projection UTM pour des aires comparables en hectares.",
        ],
        importance=(
            "Le MCP est la méthode de référence historique pour le domaine vital (Mohr 1947). "
            "Sa simplicité en fait un excellent outil pédagogique pour introduire les "
            "concepts d'utilisation de l'espace avant le KDE plus sophistiqué. "
            "Largement utilisé pour délimiter des zones tampons autour des nids "
            "dans les rapports d'évaluation d'impact."
        ),
        key_ref="Mohr, C.O. (1947). Table of equivalent populations of North American small mammals. American Midland Naturalist 37(1): 223-249.",
    ),
    dict(
        num="5.8", title="Domaine vital — KDE", tag="BIOSTATISTIQUE",
        description=(
            "Estime le domaine vital par Kernel Density Estimation (KDE) bivarié : "
            "construit une surface de densité de probabilité à partir des localisations GPS "
            "et extrait des isopleths (contours de probabilité) à 50%, 75%, 90%, 95% et 99%. "
            "Le bandwidth est estimé automatiquement par la règle de Scott, ajustable via un "
            "multiplicateur. L'isopleth 95% représente le domaine vital usuel, "
            "le 50% la zone cœur d'utilisation préférentielle."
        ),
        methodology=(
            "Estimateur à noyau gaussien bivarié : f_hat(x,y) = (1/(n*h²)) * sum(K((x-xi)/h, (y-yi)/h)). "
            "Bandwidth par règle de Scott : h = n^(-1/6) * sigma_hat. "
            "Ce bandwidth est optimal pour une distribution gaussienne bivariée, "
            "tendant à sur-lisser les distributions complexes. "
            "Isopleth X% : seuil de densité t tel que la proportion de la masse de probabilité "
            "au-dessus de t soit X/100. Implémenté avec scipy.stats.gaussian_kde."
        ),
        formulas=[
            "KDE : f_hat(x) = (1/n) * sum K_h(x - x_i)",
            "      K_h(u) = (1/h²) * K(u/h)  [noyau gaussien bivarié]",
            "Scott h : h = n^(-1/6) * sigma_hat  [sélection automatique du bandwidth]",
            "Isopleth X% : trouver t tel que integral_{f(x)>t} f(x) dx = X/100",
        ],
        algorithm=[
            "Chargement des localisations et séparation par individu",
            "Calcul du bandwidth par règle de Scott * facteur multiplicatif utilisateur",
            "Évaluation du KDE sur une grille 100x100 (scipy.stats.gaussian_kde)",
            "Calcul des seuils de densité pour chaque isopleth sélectionné",
            "Extraction des contours par interpolation et calcul des aires",
            "Tracé heatmap de densité + contours isopleths superposés",
            "Tableau des aires par individu et par isopleth",
        ],
        ornithology=(
            "Standard actuel en écologie du mouvement pour les oiseaux équipés de GPS "
            "ou balises PTT Argos. Utilisé pour identifier les habitats critiques, "
            "couloirs migratoires, zones de reproduction et d'hivernage. Supérieur au MCP "
            "pour les espèces aux mouvements asymétriques (migration) ou multimodaux "
            "(plusieurs zones de ressources). Requis dans les études d'impact éolien."
        ),
        inputs=[
            "Colonne X (longitude) et Y (latitude) des localisations GPS",
            "Colonne identifiant individuel",
            "Facteur de lissage : multiplicateur de Scott (0.1 à 2.0)",
            "Isopleths souhaités : 50%, 75%, 90%, 95%, 99%",
        ],
        outputs=[
            "Heatmap de densité KDE par individu (onglets séparés)",
            "Contours isopleths colorés en surimpression",
            "Tableau des aires par isopleth et par individu",
            "Comparaison des zones cœur (50%) et domaine complet (95%)",
        ],
        interpretation=(
            "Zone cœur 50% : utilisation préférentielle (gîte, alimentation principale). "
            "Domaine vital 95% : zone d'utilisation régulière, hors déplacements exceptionnels. "
            "Facteur < 1 (ex. 0.6) : moins de lissage, meilleure résolution, "
            "risque de sur-ajustement si peu de localisations. "
            "Facteur > 1 (ex. 1.5) : plus de lissage, zones fusionnées, utile pour distributions étalées."
        ),
        pitfalls=[
            "Utiliser la règle de Scott sans ajustement pour des distributions bimodales : "
            "les deux modes (ex. deux zones d'alimentation) peuvent être artificiellement "
            "fusionnés — réduire le facteur à 0.5-0.7.",
            "Comparer des KDE entre individus avec des effectifs de localisations très "
            "différents : le KDE est sensible à n pour les petits effectifs (n < 30).",
            "Interpréter les isopleths comme des limites strictes de territoire : "
            "ils représentent des probabilités d'utilisation, non des frontières.",
        ],
        importance=(
            "Le KDE est la méthode de choix en recherche contemporaine sur le domaine vital "
            "(> 80% des publications récentes). Comprendre le rôle du bandwidth et "
            "l'interprétation des isopleths est fondamental pour tout projet de "
            "radio-pistage ou de GPS-tracking ornithologique."
        ),
        key_ref="Silverman, B.W. (1986). Density Estimation for Statistics and Data Analysis. Chapman and Hall, London.",
    ),
]
