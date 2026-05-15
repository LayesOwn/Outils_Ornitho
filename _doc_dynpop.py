# Données des 10 modules Dynamique des populations — importé par generate_documentation.py
DYNPOP_MODULES = [
    dict(
        num="6.1", title="Richesse spécifique et diversité", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Calcule et compare les indices de diversité alpha d'une communauté d'oiseaux : "
            "richesse spécifique (S), indice de Shannon (H'), indice de Simpson (1-D), "
            "équitabilité de Pielou (J'), et courbes d'accumulation d'espèces (raréfaction) "
            "avec intervalles de confiance à 95% par randomisation."
        ),
        methodology=(
            "Shannon : H' = -sum(p_i * ln(p_i)) avec p_i = n_i / N (proportion de l'espèce i). "
            "Simpson : D = sum(p_i²) ; l'indice affiché est 1-D (diversité). "
            "Pielou : J' = H' / ln(S) (0 = une espèce domine, 1 = toutes égales). "
            "Courbe d'accumulation : 50 randomisations de l'ordre des sites, "
            "calcul du nombre moyen d'espèces observées en fonction du nombre de sites cumulés. "
            "IC 95% par percentiles (2.5% et 97.5%) des 50 réplications."
        ),
        formulas=[
            "Shannon : H' = -sum(p_i * ln(p_i))   [bits si log2, nats si ln]",
            "Simpson : D = sum(p_i²)   ;   Diversité = 1 - D",
            "Pielou :  J' = H' / ln(S)   [0 = mono-dominance, 1 = équitabilité parfaite]",
            "S = nombre total d'espèces observées (richesse spécifique)",
        ],
        algorithm=[
            "Lecture de la matrice sites x espèces (ou CSV avec colonnes = espèces)",
            "Calcul de S, H', D, J' pour chaque site",
            "Comparaison graphique des indices entre sites (barres groupées)",
            "Randomisation de l'ordre des sites pour la courbe d'accumulation (50 itérations)",
            "Calcul de la richesse cumulée moyenne et des percentiles 2.5% et 97.5%",
            "Affichage de la courbe d'accumulation avec bande d'IC 95%",
        ],
        ornithology=(
            "Utilisé pour comparer la diversité des communautés d'oiseaux entre habitats "
            "(forêt vs lisière vs champ), entre saisons (hivernage vs reproduction), "
            "ou entre zones protégées et non protégées. Outil de base pour les évaluations "
            "écologiques des plans de gestion et études d'impact Natura 2000."
        ),
        inputs=[
            "Matrice sites x espèces (colonnes = espèces, valeurs = abondances)",
            "Ou CSV avec une colonne par espèce et une ligne par site",
            "Nombre d'itérations pour la courbe d'accumulation (défaut : 50)",
        ],
        outputs=[
            "Indices S, H', 1-D, J' par site dans un tableau récapitulatif",
            "Histogrammes comparatifs des indices entre sites",
            "Courbe d'accumulation d'espèces avec IC 95%",
            "Interprétation automatisée de l'équitabilité",
        ],
        interpretation=(
            "H' proche de ln(S) = communauté équitable (toutes les espèces également abondantes). "
            "H' faible = communauté dominée par une ou quelques espèces. "
            "J' > 0.8 : bonne équitabilité. J' < 0.5 : forte dominance. "
            "Une courbe d'accumulation qui atteint un plateau indique que "
            "le nombre de sites est suffisant pour estimer S — sinon : "
            "richesse sous-estimée par manque d'échantillonnage."
        ),
        pitfalls=[
            "Comparer H' entre sites avec des effectifs totaux très différents : "
            "H' est sensible au n total — raréfier les données au même effectif avant comparaison.",
            "Confondre richesse spécifique (S) et diversité (H') : "
            "S ne tient pas compte des abondances relatives.",
            "Interpréter J' = 1 comme une communauté 'optimale' : une communauté "
            "avec 2 espèces à abondances égales a J' = 1 mais une diversité très faible.",
        ],
        importance=(
            "La diversité aviaire est un indicateur reconnu de l'intégrité écologique. "
            "Ces indices sont utilisés dans les rapports d'impact environnemental, "
            "les évaluations Natura 2000, les plans de gestion des réserves naturelles, "
            "et le calcul des indicateurs nationaux de l'Observatoire de la Biodiversité."
        ),
        key_ref="Shannon, C.E. & Weaver, W. (1949). The Mathematical Theory of Communication. University of Illinois Press.",
    ),
    dict(
        num="6.2", title="Croissance exponentielle et logistique", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Simule et compare deux modèles de croissance de population : la croissance "
            "exponentielle (Malthus, densité-indépendante) et la croissance logistique "
            "(Verhulst, densité-dépendante) avec contrôle du taux d'accroissement intrinsèque r "
            "et de la capacité de charge K. Visualise la convergence vers K et calcule "
            "le temps de doublement."
        ),
        methodology=(
            "Exponentielle : N(t) = N0 * exp(r*t) — croissance illimitée, pas de régulation. "
            "Logistique : dN/dt = r*N*(1 - N/K). "
            "Solution analytique : N(t) = K / (1 + ((K-N0)/N0) * exp(-r*t)). "
            "La densité-dépendance est encodée par le terme freinage (1 - N/K). "
            "Temps de doublement (phase exponentielle) : T_d = ln(2) / r."
        ),
        formulas=[
            "Exponentielle : N(t) = N0 * exp(r * t)",
            "Logistique :    N(t) = K / (1 + ((K - N0)/N0) * exp(-r * t))",
            "dN/dt = r * N * (1 - N/K)   [terme de freinage densité-dépendant]",
            "Temps de doublement : T_d = ln(2) / r",
            "Point d'inflexion logistique : N = K/2  (croissance maximale)",
        ],
        algorithm=[
            "Calcul de N(t) exponentielle analytiquement pour t = 0, 1, ..., T",
            "Calcul de N(t) logistique analytiquement",
            "Tracé comparatif des deux courbes N(t)",
            "Affichage de K, T_d, et N(T) pour les deux modèles",
            "Interprétation automatisée : phase de croissance vs saturation",
        ],
        ornithology=(
            "Compréhension de la dynamique de récupération après un déclin (bécasse, spatule, "
            "outarde), croissance d'une population réintroduite (vautour fauve, cigogne blanche), "
            "impact d'une chasse sur une population à l'équilibre. Fondement conceptuel "
            "de tous les modèles de gestion cynégétique (grouse, faisan, perdrix)."
        ),
        inputs=[
            "Population initiale N0",
            "Taux d'accroissement intrinsèque r (positif = croissance)",
            "Capacité de charge K",
            "Durée de simulation T (années)",
        ],
        outputs=[
            "Courbes N(t) exponentielle et logistique superposées",
            "Temps de doublement T_d",
            "N final pour les deux modèles",
            "Marqueur de K sur le graphique",
        ],
        interpretation=(
            "r > 0 : population croissante. r = 0 : population stable. r < 0 : déclin. "
            "La logistique converge vers K quel que soit N0 (si r > 0). "
            "Le point d'inflexion (N = K/2) est le moment de croissance absolue maximale — "
            "c'est ici que le rendement durable maximal (MSY) est atteint. "
            "L'exponentielle diverge toujours — impossible biologiquement sur le long terme."
        ),
        pitfalls=[
            "Confondre r (taux intrinsèque) et lambda (ratio fini) : r = ln(lambda). "
            "Une population avec lambda = 0.95 a r = -0.051 (déclin de 5% par an).",
            "Appliquer le modèle logistique simple à des espèces à vie longue : "
            "la densité-dépendance est souvent retardée (time-lag) dans ces espèces.",
            "Interpréter la phase initiale d'une logistique comme une exponentielle réelle : "
            "la régulation par K existe dès N0 > 0 mais n'est visible qu'à N proche de K.",
        ],
        importance=(
            "Les modèles de croissance sont le fondement de la dynamique des populations. "
            "La distinction entre croissance densité-indépendante et densité-dépendante "
            "est essentielle pour dimensionner les efforts de conservation et "
            "comprendre les mécanismes de régulation naturelle des populations aviaires."
        ),
        key_ref="Verhulst, P.F. (1838). Notice sur la loi que la population suit dans son accroissement. Correspondance Mathématique et Physique 10: 113-121.",
    ),
    dict(
        num="6.3", title="Matrices de Leslie", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Projette une population féminine structurée en classes d'âge à partir d'une "
            "matrice de Leslie intégrant fécondités et probabilités de survie. Calcule la "
            "valeur propre dominante lambda (taux de croissance asymptotique), la distribution "
            "d'âge stable, les valeurs reproductives, et les matrices de sensibilité "
            "et d'élasticité permettant d'identifier les leviers démographiques clés."
        ),
        methodology=(
            "Projection : N(t+1) = A * N(t) avec A matrice de Leslie (fécondités en ligne 0, "
            "survies en sous-diagonale). "
            "Valeur propre dominante lambda_1 via np.linalg.eig(A). "
            "Distribution stable : vecteur propre droit w normalisé (N à long terme). "
            "Valeurs reproductives : vecteur propre gauche v de A^T (contribution reproductive). "
            "Sensibilité : S_ij = (v_i * w_j) / <v, w>. "
            "Elasticité : e_ij = (a_ij / lambda) * S_ij. Propriété : sum(e_ij) = 1."
        ),
        formulas=[
            "Projection : N(t+1) = A * N(t)",
            "Lambda : valeur propre dominante de A  (lambda > 1 : croissance)",
            "Sensibilité : S_ij = delta(lambda) / delta(a_ij) = v_i * w_j / <v,w>",
            "Elasticité : e_ij = (a_ij / lambda) * S_ij",
            "Propriété : sum_ij(e_ij) = 1  [les élasticités somment à 1]",
        ],
        algorithm=[
            "Construction de la matrice A depuis les fécondités et survies saisies",
            "Décomposition en valeurs propres via numpy.linalg.eig(A)",
            "Extraction du vecteur propre droit w (distribution stable) normalisé",
            "Calcul du vecteur propre gauche v de A^T (valeurs reproductives)",
            "Calcul des matrices de sensibilité et d'élasticité",
            "Projection temporelle N(t) sur T années",
            "Visualisation : courbes N(t) par classe, barres distribution stable, heatmaps",
        ],
        ornithology=(
            "Outil de référence pour la gestion d'espèces à vie longue : rapaces "
            "(vautour moine, aigle royal), grands plongeons, puffins, albatros. "
            "L'élasticité de la survie adulte est généralement la plus élevée chez ces "
            "espèces, orientant les priorités de conservation vers la réduction de la "
            "mortalité adulte (captures accessoires, empoisonnements, collision éolienne)."
        ),
        inputs=[
            "Fécondités par classe d'âge (F0, F1, ..., Fn)",
            "Probabilités de survie inter-classes (S0, S1, ..., Sn-1)",
            "Population initiale par classe d'âge",
            "Durée de projection (années)",
        ],
        outputs=[
            "Courbes de projection N(t) par classe d'âge",
            "Lambda dominant avec interprétation (croissance / déclin / stabilité)",
            "Distribution d'âge stable (barres normalisées)",
            "Valeurs reproductives par classe (importance de chaque classe)",
            "Heatmaps de sensibilité et d'élasticité",
        ],
        interpretation=(
            "lambda > 1 : population en croissance (lambda = 1.05 = +5% par an). "
            "lambda < 1 : population en déclin (lambda = 0.95 = -5% par an). "
            "lambda = 1 : population stable. "
            "L'élasticité la plus élevée indique le paramètre démographique à cibler en priorité. "
            "Pour les rapaces : améliorer la survie adulte (e élevée) est plus efficace "
            "qu'améliorer la fécondité (e faible)."
        ),
        pitfalls=[
            "Supposer que la distribution d'âge initiale est la distribution stable : "
            "la projection converge vers la distribution stable, mais les premières années "
            "reflètent la distribution initiale qui peut être très différente.",
            "Interpréter la sensibilité absolue sans considérer la plage biologique "
            "possible du paramètre : préférer l'élasticité pour les comparaisons.",
            "Appliquer une matrice de Leslie à une population bisexuée sans correction : "
            "le modèle ne projette que les femelles (ou les deux sexes si taux constant).",
        ],
        importance=(
            "Les matrices de Leslie sont l'outil le plus puissant pour cibler les actions "
            "de conservation : l'élasticité indique quel paramètre démographique améliorer "
            "en priorité pour maximiser lambda. Caswell (2001) reste la référence mondiale "
            "pour cette approche appliquée à la gestion des espèces menacées."
        ),
        key_ref="Caswell, H. (2001). Matrix Population Models, 2nd ed. Sinauer Associates, Sunderland, MA.",
    ),
    dict(
        num="6.4", title="Capture-Marquage-Recapture", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Estime l'abondance d'une population par l'estimateur de Lincoln-Petersen "
            "et sa correction non biaisée de Chapman. Calcule les intervalles de confiance "
            "à 95% par la méthode du log et le coefficient de variation. "
            "Illustre le principe de la détectabilité imparfaite et propose trois scénarios "
            "pédagogiques préconfigurés couvrant différents contextes ornithologiques."
        ),
        methodology=(
            "Lincoln-Petersen : N_hat = (M * C) / R. "
            "Correction Chapman (non biaisée pour petits R) : N_hat = (M+1)*(C+1)/(R+1) - 1. "
            "Variance de Chapman : Var = (M+1)*(C+1)*(M-R)*(C-R) / ((R+1)²*(R+2)). "
            "IC 95% par méthode du log : exp(log(N_hat) ± 1.96 * sqrt(Var) / N_hat). "
            "Hypothèses : population fermée, marquage sans effet, détectabilité homogène."
        ),
        formulas=[
            "Lincoln-Petersen : N_hat = (M * C) / R",
            "Chapman (non biaisé) : N_hat = (M+1)*(C+1) / (R+1) - 1",
            "CV = sqrt(Var(N_hat)) / N_hat   [coefficient de variation]",
            "IC 95% log : exp( log(N_hat) ± 1.96 * SE_log )",
        ],
        algorithm=[
            "Saisie ou simulation de M (marqués), C (capturés en 2ème session), R (recapturés)",
            "Calcul de N_hat par Lincoln-Petersen et Chapman",
            "Calcul de la variance, du CV et de l'IC 95%",
            "Graphique d'incertitude : N_hat ± IC 95%",
            "Interprétation automatisée de la précision (CV < 20% = acceptable)",
            "3 scénarios préconfigurés : petite population / grande population / fort taux de recapture",
        ],
        ornithology=(
            "Utilisé pour estimer les effectifs de passereaux (sessions de baguage printanières), "
            "de larolimicoles (captures-baguages sur vasières), de rapaces (piégeage-baguage). "
            "Permet d'obtenir une estimation absolue de l'abondance, contrairement aux IKA "
            "qui ne donnent qu'un indice relatif sans calibration."
        ),
        inputs=[
            "M : nombre d'individus capturés, marqués et relâchés (session 1)",
            "C : nombre d'individus capturés en session 2",
            "R : nombre d'individus recapturés (portant déjà une marque) en session 2",
        ],
        outputs=[
            "N_hat estimé par Lincoln-Petersen et Chapman",
            "Intervalle de confiance 95% et coefficient de variation",
            "Graphique d'incertitude de l'estimation",
            "Interprétation de la précision de l'estimation",
        ],
        interpretation=(
            "CV < 20% : estimation précise. CV 20-40% : estimation acceptable. CV > 40% : "
            "estimation très incertaine — augmenter l'effort de recapture. "
            "N_hat faible avec R/C élevé : population petite et bien détectée. "
            "N_hat élevé avec R/C faible : population grande ou détectabilité faible. "
            "La correction de Chapman réduit le biais quand R est petit (< 10)."
        ),
        pitfalls=[
            "Violer l'hypothèse de population fermée : des mouvements entre sessions "
            "(émigration, immigration) biaisent N_hat. Réaliser les deux sessions "
            "en courte période (1-2 jours pour les passereaux).",
            "Supposer une détectabilité homogène : si certains individus évitent les pièges "
            "(trap-shyness) ou les recherchent (trap-happiness), N_hat est biaisé.",
            "Utiliser Lincoln-Petersen sans correction de Chapman quand R est très petit : "
            "biais important pour R < 10 — toujours utiliser Chapman.",
        ],
        importance=(
            "L'estimation de l'abondance absolue est fondamentale pour évaluer l'état de "
            "conservation d'une population, dimensionner des programmes de réintroduction, "
            "et suivre les tendances dans le temps avec des estimations comparables. "
            "Les méthodes CMR sont enseignées dans tous les cursus d'écologie des populations."
        ),
        key_ref="Lincoln, F.C. (1930). Calculating Waterfowl Abundance on the Basis of Banding Returns. USDA Circular 118.",
    ),
    dict(
        num="6.5", title="Modèles d'occupation", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Estime séparément la probabilité d'occupation (psi) et la probabilité de "
            "détection (p) d'une espèce sur des sites visités plusieurs fois. Corrige le "
            "biais de l'occupation naïve (proportion de sites avec au moins une détection) "
            "dû à la détectabilité imparfaite. Modèle de MacKenzie et al. (2002, Ecology)."
        ),
        methodology=(
            "Vraisemblance : L(psi,p|y) = prod_i[psi*prod_k(p^y_ik*(1-p)^(1-y_ik)) + "
            "I(sum(y_ik)=0)*(1-psi)]. "
            "Pour un site i avec historique y_i1,...,y_iK de K visites : "
            "si au moins une détection : contribue psi * prod(termes détection). "
            "si jamais détecté : contribue psi*(1-p)^K + (1-psi). "
            "Estimation par Nelder-Mead en espace logit. "
            "Occupation naïve théorique : psi_naive = psi * (1 - (1-p)^K)."
        ),
        formulas=[
            "L(psi, p | y) = prod_i [ psi*p^d_i*(1-p)^(K-d_i) + I(d_i=0)*(1-psi) ]",
            "d_i = sum_k(y_ik)  [nombre de détections au site i]",
            "Occupation naive : psi_obs = proportion sites avec au moins 1 détection",
            "Biais : psi_naive sous-estime psi si p < 1",
            "Biais relatif = (psi - psi_naive) / psi * 100%",
        ],
        algorithm=[
            "Construction de l'historique de détections (matrice sites x visites, 0/1)",
            "Définition de la log-vraisemblance négative en espace logit(psi), logit(p)",
            "Minimisation par Nelder-Mead (scipy.optimize.minimize)",
            "Back-transformation logit -> probabilités",
            "Calcul de l'occupation naïve et du biais de sous-estimation",
            "Avertissement si convergence extrême (psi ou p proche de 0 ou 1)",
        ],
        ornithology=(
            "Indispensable pour les espèces discrètes ou rares : rapaces nocturnes "
            "(chevêchette, effraie des clochers), pics, passereaux forestiers, "
            "limicoles à faible détection. Fondement des programmes de surveillance STOC, "
            "où l'absence apparente n'implique pas l'absence réelle de l'espèce."
        ),
        inputs=[
            "Historique de détection : matrice sites x visites (0 = absent/non détecté, 1 = détecté)",
            "Ou paramètres de simulation : psi vraie, p vraie, K visites, N sites",
        ],
        outputs=[
            "psi estimée (occupation corrigée), p estimée (détection)",
            "Occupation naïve et biais de sous-estimation en %",
            "Graphique comparatif psi vraie / psi estimée / psi naïve",
            "Avertissement si convergence sur la limite des paramètres",
        ],
        interpretation=(
            "psi = 0.8 et p = 0.3 : 80% des sites sont occupés mais la détection est faible. "
            "psi naïve = 0.8 * (1-(1-0.3)^3) = 0.66 : si 3 visites, on observe seulement "
            "66% d'occupation alors que 80% des sites sont réellement occupés. "
            "p proche de 0 avec K faible : biais très élevé — augmenter le nombre de visites. "
            "p > 0.8 avec K = 3 : occupation naïve fiable."
        ),
        pitfalls=[
            "Utiliser l'occupation naïve sans correction quand p < 1 : sous-estime "
            "systématiquement l'occupation réelle, menant à des conclusions erronées "
            "sur le statut de conservation.",
            "Violer l'hypothèse d'indépendance conditionnelle entre sites : si la "
            "détection d'un individu voisin déclenche la détection, p est biaisée.",
            "Appliquer le modèle avec K = 1 visite : impossible d'estimer p sans visites "
            "répétées — le modèle d'occupation exige K >= 2.",
        ],
        importance=(
            "L'occupation corrigée pour la détection est devenue le standard international "
            "pour les inventaires et suivis d'espèces. Ignorer p produit des estimations "
            "fortement biaisées et des conclusions incorrectes sur l'état de conservation. "
            "MacKenzie et al. (2002) est l'un des articles les plus cités en écologie."
        ),
        key_ref="MacKenzie, D.I. et al. (2002). Estimating site occupancy rates when detection probabilities are less than one. Ecology 83(8): 2248-2255.",
    ),
    dict(
        num="6.6", title="Distance sampling", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Estime la densité et l'abondance d'une population à partir des distances "
            "d'observation sur des transects linéaires. Ajuste une fonction de détection "
            "demi-normale par maximum de vraisemblance, calcule la largeur efficace du "
            "transect (ESW), la densité et l'abondance avec avertissement si plus de 50% "
            "des distances sont filtrées par la limite W."
        ),
        methodology=(
            "Fonction de détection demi-normale : g(x) = exp(-x² / (2*sigma²)). "
            "La probabilité de détection à distance x chute avec la distance. "
            "ESW (Effective Strip Width) : integral de 0 à W de g(x) dx = "
            "sigma * sqrt(pi/2) * erf(W / (sigma*sqrt(2))). "
            "Sigma estimé par MLE (minimisation de -log(L) sur log(sigma)). "
            "Densité : D = n / (2 * ESW * L_total), avec L = longueur totale des transects."
        ),
        formulas=[
            "g(x) = exp(-x² / (2*sigma²))   [fonction de détection demi-normale]",
            "ESW = sigma * sqrt(pi/2) * erf(W / (sigma*sqrt(2)))",
            "Densité : D = n / (2 * ESW * L * K)   [L = longueur transect, K = nb transects]",
            "Abondance : N = D * A   [A = superficie de la zone d'étude]",
            "MLE sigma : minimize  n*log(ESW) + sum(x_i²) / (2*sigma²)",
        ],
        algorithm=[
            "Filtrage des distances : 0 <= x <= W (avec avertissement si > 50% filtrées)",
            "Ajustement sigma par MLE (minimize_scalar sur log-sigma, bounds log-echelle)",
            "Calcul ESW = effective_strip_width(sigma, W)",
            "Calcul densité D et abondance N",
            "Tracé histogramme des distances + courbe g(x) ajustée + ligne ESW",
        ],
        ornithology=(
            "Méthode standard pour les comptages sur transect linéaire de passereaux, "
            "rapaces, larolimicoles. Utilisée dans le STOC-EPS, les inventaires Natura 2000, "
            "les études préalables aux projets d'aménagement (éoliennes, routes). "
            "Permet d'obtenir une densité absolue sans hypothèse sur la détectabilité "
            "à distance nulle (g(0) = 1 postulé)."
        ),
        inputs=[
            "Distances d'observation perpendiculaires au transect (m)",
            "Demi-largeur maximale W du transect (m)",
            "Longueur totale des transects (m)",
            "Nombre de transects",
        ],
        outputs=[
            "Sigma estimé (portée caractéristique de détection en m)",
            "ESW (Effective Strip Width en m)",
            "Densité estimée (ind/ha ou ind/km²)",
            "Histogramme des distances + courbe de détection g(x)",
            "Avertissement si > 50% des distances filtrées",
        ],
        interpretation=(
            "ESW proche de W : g(x) reste élevée sur toute la largeur — très bonne détectabilité. "
            "ESW << W : détectabilité chute rapidement avec la distance — sigma petit. "
            "Histogramme avec mode > 0 (pic non à la distance nulle) : "
            "problème de détection en bord de transect ou évasion d'animaux. "
            "Densité en ind/ha : D = 5 ind/ha signifie 5 oiseaux pour 10000 m²."
        ),
        pitfalls=[
            "Regrouper des espèces aux fonctions de détection différentes : "
            "ajuster un modèle séparé pour chaque espèce ou groupe fonctionnel.",
            "Ne pas vérifier le pic à la distance zéro (g(0) = 1) : "
            "si les oiseaux fuient à l'approche, les distances proches sont sous-représentées "
            "et la densité est surestimée.",
            "Utiliser W trop large : inclure des distances où g(x) ≈ 0 ajoute du bruit "
            "sans information. Tronquer à W = 2*sigma pour un bon ajustement.",
        ],
        importance=(
            "Le distance sampling est l'une des méthodes les plus rigoureuses pour estimer "
            "des densités absolues en tenant compte de la détectabilité décroissante. "
            "Enseigné dans les formations LPO, Naturevolution et les cursus universitaires "
            "d'écologie. Buckland et al. (2001) est la référence fondamentale."
        ),
        key_ref="Buckland, S.T. et al. (2001). Introduction to Distance Sampling. Oxford University Press.",
    ),
    dict(
        num="6.7", title="Lotka-Volterra", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Simule les interactions proie-prédateur selon le modèle classique de "
            "Lotka-Volterra. Visualise les oscillations cycliques dans le temps et le "
            "portrait de phase (cycle limite elliptique dans l'espace proie-prédateur). "
            "Permet d'explorer la stabilité du point d'équilibre et l'effet des paramètres "
            "sur la période et l'amplitude des oscillations."
        ),
        methodology=(
            "Système d'équations différentielles : "
            "dN/dt = r*N - a*N*P (proies : croissance - prédation), "
            "dP/dt = b*a*N*P - m*P (prédateurs : gains - mortalité). "
            "r = taux de reproduction des proies, a = taux de prédation par prédateur, "
            "b = efficacité de conversion proie -> prédateur (0-1), "
            "m = taux de mortalité naturelle des prédateurs. "
            "Intégration numérique par scipy.integrate.odeint (RK4 adaptatif)."
        ),
        formulas=[
            "dN/dt = r*N - a*N*P   [proies : croissance - prédation]",
            "dP/dt = b*a*N*P - m*P   [prédateurs : gains - mortalité]",
            "Point d'équilibre : N* = m/(a*b),  P* = r/a",
            "Période des oscillations ≈ 2*pi / sqrt(r*m)   [approximation linéarisée]",
        ],
        algorithm=[
            "Définition du système d'ODE (lotka_volterra_ode)",
            "Intégration numérique via scipy.integrate.odeint sur T années",
            "Tracé des courbes N(t) et P(t) superposées",
            "Tracé du portrait de phase P vs N (cycle limite)",
            "Marquage du point d'équilibre (N*, P*)",
        ],
        ornithology=(
            "Illustre les cycles lemming-harfang des neiges, campagnol-busard, "
            "sauterelle-guifette, criquet-outarde. Fondement conceptuel pour comprendre "
            "les fluctuations annuelles des populations de rapaces liées aux cycles de "
            "rongeurs et les décisions de conservation qui en découlent "
            "(fermeture de la chasse aux années de faible densité de proies)."
        ),
        inputs=[
            "Population initiale des proies N0",
            "Population initiale des prédateurs P0",
            "Paramètres r (reproduction proies), a (prédation), b (conversion), m (mort prédateurs)",
            "Durée de simulation T (années)",
        ],
        outputs=[
            "Courbes N(t) et P(t) superposées avec axes secondaires",
            "Portrait de phase P vs N (cycle limite elliptique)",
            "Point d'équilibre théorique (N*, P*)",
            "Période approximative des oscillations",
        ],
        interpretation=(
            "Le cycle proie-prédateur est décalé : le pic des prédateurs suit le pic des proies. "
            "Point d'équilibre : N* = m/(a*b), P* = r/a. "
            "Si r grand : proies abondantes -> prédateurs nombreux -> effondrement proies "
            "-> chute prédateurs -> reprise des proies. "
            "Le portrait de phase fermé (cycle limite) indique la neutralité du modèle "
            "de base — une perturbation ne ramène pas au même état."
        ),
        pitfalls=[
            "Interpréter le cycle comme stable : le modèle de Lotka-Volterra de base est "
            "neutralement stable (cycles de taille variable selon les conditions initiales). "
            "Les modèles réalistes (logistique pour les proies) ont des cycles amortis.",
            "Ignorer les hypothèses simplificatrices : pas de structure d'âge, "
            "rencontres aléatoires, population fermée. Le modèle est conceptuel, non prédictif.",
            "Choisir des paramètres conduisant à une extinction numérique : "
            "si P0 >> P*, les prédateurs surexploitent les proies et s'effondrent.",
        ],
        importance=(
            "Le modèle de Lotka-Volterra est un pilier de l'écologie théorique. "
            "Il introduit les notions d'interaction spécifique, de dynamique couplée "
            "et de cycle limite — concepts applicables à la gestion des rapaces, "
            "à la prévision des explosions de proies et à la compréhension des "
            "cascades trophiques dans les écosystèmes."
        ),
        key_ref="Lotka, A.J. (1925). Elements of Physical Biology. Williams & Wilkins, Baltimore.",
    ),
    dict(
        num="6.8", title="Séries temporelles de population", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Analyse une série temporelle d'abondance annuelle pour détecter une tendance "
            "significative (croissance ou déclin). Applique le test non paramétrique de "
            "Mann-Kendall, une régression linéaire OLS (pente annuelle absolue), et un "
            "lissage par moyenne mobile. Calcule le taux de variation annuel et évalue "
            "la puissance statistique de la tendance détectée."
        ),
        methodology=(
            "Mann-Kendall : S = sum_{i&lt;j} sign(y_j - y_i). "
            "Var(S) = n*(n-1)*(2*n+5)/18 (sans ex aequo). "
            "Statistique z = (S - sign(S)) / sqrt(Var(S)). "
            "Hypothèse nulle : pas de tendance monotone. "
            "Régression OLS : pente = variation absolue annuelle (individus/an). "
            "Lissage : moyenne mobile sur une fenêtre de k années (ajustable 2-7 ans)."
        ),
        formulas=[
            "Mann-Kendall S = sum_{i&lt;j} sign(y_j - y_i)",
            "Var(S) = n*(n-1)*(2*n+5) / 18   [sans ex aequo]",
            "z = (S - sign(S)) / sqrt(Var(S))   [N(0,1) sous H0]",
            "Pente OLS : b = sum((t_i - t_bar)*(y_i - y_bar)) / sum((t_i - t_bar)²)",
            "Taux annuel = (b / y_bar) * 100%   [variation relative par an]",
        ],
        algorithm=[
            "Calcul du score S de Mann-Kendall (toutes les paires i < j)",
            "Calcul de la variance de S et de la statistique z",
            "Régression OLS (scipy.stats.linregress) pente et R²",
            "Lissage par moyenne mobile (pandas.rolling().mean())",
            "Tracé courbe des effectifs + lissage + droite OLS",
            "Interprétation : tendance (hausse/baisse/stable), significativité, magnitude",
        ],
        ornithology=(
            "Analyse des données STOC, BBS, Wetland Bird Survey, LPO. "
            "Détection des déclins ou reprises de populations (pinson des arbres, "
            "alouette des champs, hirondelle rustique, courlis cendré). "
            "Utilisé pour produire les Listes Rouges régionales et calibrer les alertes "
            "précoces de l'Observatoire National de la Biodiversité."
        ),
        inputs=[
            "Série temporelle : colonne année et colonne effectif (ou index)",
            "Ou paramètres de simulation (N0, r moyen, bruit stochastique)",
            "Fenêtre de lissage k (2-7 ans)",
        ],
        outputs=[
            "Courbe des effectifs + tendance lissée + droite de régression OLS",
            "Test Mann-Kendall : S, z, p-value, sens de la tendance",
            "Pente OLS (individus/an) et R²",
            "Taux de variation annuel relatif (%)",
        ],
        interpretation=(
            "Mann-Kendall p < 0.05 avec S < 0 : tendance à la baisse significative. "
            "S > 0 : tendance à la hausse. |z| > 1.96 : significatif à 5%. "
            "Pente OLS = -5 ind/an avec N_moyen = 100 : déclin de 5%/an. "
            "R² faible mais Mann-Kendall significatif : tendance monotone "
            "mais non linéaire (commun dans les comptages avec variabilité inter-annuelle)."
        ),
        pitfalls=[
            "Utiliser le test t sur la pente OLS sans vérifier l'autocorrélation temporelle : "
            "les comptages annuels sont souvent autocorrélés, gonflant la significativité. "
            "Mann-Kendall est plus robuste car non paramétrique.",
            "Confondre tendance à court terme et tendance à long terme : une série de "
            "5 ans peut montrer un déclin artificiel lié à une variabilité naturelle.",
            "Appliquer Mann-Kendall à des séries avec une forte saisonnalité non corrigée : "
            "le test suppose une tendance monotone, pas des cycles.",
        ],
        importance=(
            "La détection rigoureuse des tendances démographiques est la base des Listes "
            "Rouges UICN et des plans de conservation nationaux. Le test de Mann-Kendall "
            "est préféré car il ne suppose pas la normalité des résidus, fréquente dans "
            "les comptages d'oiseaux avec surdispersion."
        ),
        key_ref="Hirsch, R.M. et al. (1982). Techniques of trend analysis for monthly water quality data. Water Resources Research 18(1): 107-121.",
    ),
    dict(
        num="6.9", title="PVA et conservation", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Analyse de Viabilité des Populations (PVA) : simule stochastiquement "
            "1000 trajectoires possibles d'une population sur T années sous incertitude "
            "environnementale (variance du taux d'accroissement), avec capacité de charge K "
            "et seuil de quasi-extinction. Estime la probabilité d'extinction, "
            "la médiane et les IC 95% de la taille finale de population."
        ),
        methodology=(
            "Croissance log-normale stochastique : N(t+1) = min(N(t) * exp(r_t), K), "
            "avec r_t ~ N(mu_r, sigma_r²) tiré aléatoirement à chaque pas de temps. "
            "Stochasticité environnementale : sigma_r représente la variabilité inter-annuelle "
            "du taux d'accroissement (climat, proies, prédateurs). "
            "1000 réplications par défaut. "
            "Risque d'extinction = P(min_{t=1..T}(N(t)) < seuil). "
            "IC 95% par percentiles (2.5% et 97.5%) des 1000 trajectoires finales."
        ),
        formulas=[
            "N(t+1) = min( N(t) * exp(r_t), K )   [croissance log-normale bornée par K]",
            "r_t ~ N(mu_r, sigma_r²)   [stochasticité environnementale]",
            "P(extinction) = N_simulations avec min(N) < seuil / N_total",
            "Médiane finale = percentile 50% de {N_final[i], i=1..1000}",
            "IC 95% = [percentile 2.5%, percentile 97.5%] des N_finaux",
        ],
        algorithm=[
            "Initialisation de 1000 trajectoires à N0",
            "Pour chaque trajectoire i et chaque année t : tirer r_t ~ N(mu_r, sigma_r), "
            "calculer N(t+1) = min(N(t)*exp(r_t), K), appliquer perte annuelle",
            "Calcul du risque d'extinction pour chaque trajectoire",
            "Agrégation : médiane, IC 95%, risque d'extinction global",
            "Tracé de la bande d'enveloppe (IC 95%) + médiane",
            "Histogramme de distribution des effectifs finaux",
        ],
        ornithology=(
            "Outil clé pour les plans de sauvegarde d'espèces menacées : vautour moine, "
            "percnoptère, grand tétras, bécasseau maubèche, grèbe à cou noir. "
            "Utilisé par le Comité Français de l'UICN pour classer les espèces et par "
            "les gestionnaires de réserves pour dimensionner les effectifs minimaux viables."
        ),
        inputs=[
            "Population initiale N0",
            "Taux d'accroissement moyen mu_r et écart-type sigma_r",
            "Capacité de charge K",
            "Seuil de quasi-extinction (ex. 10 individus)",
            "Durée T (années) et nombre de simulations (défaut 1000)",
        ],
        outputs=[
            "Bande enveloppe des trajectoires stochastiques (IC 95% + médiane)",
            "Risque d'extinction (probabilité en %)",
            "Médiane et IC 95% de la taille finale de population",
            "Histogramme de distribution des effectifs finaux",
        ],
        interpretation=(
            "Risque d'extinction > 10% sur 100 ans : critère UICN d'espèce menacée (CR). "
            "Médiane finale > K/2 : population viable à long terme. "
            "Bande IC 95% très large : haute incertitude — sigma_r élevé. "
            "Trajectoires qui s'effondrent avant T : quasi-extinctions prématurées. "
            "Comparer la médiane avec et sans mesure de conservation pour évaluer l'impact."
        ),
        pitfalls=[
            "Ignorer la stochasticité démographique (en plus de la stochasticité "
            "environnementale) pour les très petites populations (N < 50) : "
            "les fluctuations dues au hasard des naissances/décès deviennent critiques.",
            "Utiliser une seule simulation plutôt que 1000 : la variabilité "
            "stochastique rend une trajectoire unique non représentative.",
            "Confondre mu_r et taux de croissance observé d'une seule période : "
            "calibrer mu_r sur des séries temporelles longues (> 10 ans) si possible.",
        ],
        importance=(
            "La PVA est l'outil de référence international pour la gestion des espèces "
            "vulnérables. Elle intègre l'incertitude environnementale — inévitable en "
            "écologie — pour fournir des probabilités d'extinction utiles à la décision "
            "politique. Beissinger & McCullough (2002) synthétisent les meilleures "
            "pratiques pour la PVA en conservation."
        ),
        key_ref="Beissinger, S.R. & McCullough, D.R. (eds, 2002). Population Viability Analysis. University of Chicago Press.",
    ),
    dict(
        num="6.10", title="Scénarios de gestion", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Compare quatre scénarios d'action de conservation sur une population simulée : "
            "sans action, restauration d'habitat (K plus élevé, mortalité réduite), "
            "réduction de mortalité (chasse, pièges, collisions), et action combinée. "
            "Visualise les trajectoires médianes par scénario et produit un tableau "
            "comparatif de la médiane finale, du risque d'extinction et du lambda apparent."
        ),
        methodology=(
            "Chaque scénario modifie les paramètres démographiques (mu_r, sigma_r, K, "
            "perte annuelle) et lance une simulation PVA indépendante. "
            "Comparaison par : médiane de la population à T ans, risque d'extinction "
            "sur T ans, lambda apparent (taux de croissance moyen sur la période). "
            "L'action combinée maximise généralement tous les indicateurs. "
            "Permet de classer les actions par efficacité relative avant décision."
        ),
        formulas=[
            "Lambda apparent : lambda_app = exp( log(N_median(T) / N0) / T )",
            "Gain médian : (N_scénario - N_sans_action) / N_sans_action * 100%",
            "Risque relatif : P_ext_sans_action / P_ext_scénario   [combien de fois réduit]",
        ],
        algorithm=[
            "Définition de 4 scénarios avec leurs paramètres spécifiques",
            "Lancement de la simulation PVA (1000 réplications) pour chaque scénario",
            "Extraction des médianes, IC 95% et risques d'extinction par scénario",
            "Construction du tableau comparatif",
            "Tracé des courbes médianes N(t) par scénario (couleurs distinctes)",
            "Identification du meilleur scénario (minimum risque d'extinction ou maximum médiane)",
        ],
        ornithology=(
            "Directement applicable aux Plans Nationaux d'Action (PNA) pour des espèces comme "
            "le gypaète barbu, le vautour percnoptère, le grand tétras, l'outarde canepetière. "
            "Compare les coûts-bénéfices de différents types d'intervention avant la "
            "décision politique et le budget alloué par les services de l'État."
        ),
        inputs=[
            "Paramètres de la population de référence (mu_r, sigma_r, K, N0, seuil)",
            "4 scénarios préconfigurés avec variation des paramètres clés",
            "Durée de projection T (années)",
        ],
        outputs=[
            "Courbes médianes N(t) par scénario sur un graphique commun",
            "Tableau comparatif : médiane finale, risque extinction %, lambda apparent",
            "Meilleur scénario identifié automatiquement",
            "Gain en médiane finale par rapport au scénario sans action (%)",
        ],
        interpretation=(
            "Un scénario avec risque d'extinction < 5% sur 100 ans est considéré comme "
            "viable selon les critères UICN. "
            "La différence entre 'Réduction mortalité' et 'Restauration habitat' dépend "
            "des paramètres biologiques de l'espèce : pour les espèces à forte longévité, "
            "réduire la mortalité adulte est généralement plus efficace. "
            "L'action combinée montre souvent des effets synergiques (gains > somme des effets séparés)."
        ),
        pitfalls=[
            "Supposer des effets additifs indépendants entre actions : restaurer l'habitat "
            "ET réduire la mortalité peut avoir des effets synergiques non capturés "
            "si les paramètres sont traités indépendamment.",
            "Ignorer l'incertitude sur les paramètres (mu_r, K) : présenter une seule "
            "projection déterministe sans intervalle de confiance sur les scénarios "
            "crée une fausse impression de précision.",
            "Comparer des scénarios avec des budgets très différents sans analyse coût-efficacité : "
            "l'action combinée est souvent la meilleure mais aussi la plus coûteuse.",
        ],
        importance=(
            "La comparaison systématique de scénarios est fondamentale pour la décision "
            "en conservation. Elle évite d'investir des ressources limitées dans des "
            "actions à faible impact démographique, et oriente vers les leviers les plus "
            "efficaces. Les PNA français utilisent désormais ce type d'analyse."
        ),
        key_ref="Morris, W.F. & Doak, D.F. (2002). Quantitative Conservation Biology. Sinauer Associates, Sunderland, MA.",
    ),
]
