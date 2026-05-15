# Annexes, glossaire, références et fonction build_pdf — importé par generate_documentation.py
from __future__ import annotations
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import PageBreak, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
W, H = A4


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — ANNEXES TECHNIQUES
# ══════════════════════════════════════════════════════════════════════════════
def annexes_techniques(story: list, s: dict,
                        hr, spacer, colored_box, warning_box, note_box,
                        generic_table, section_banner,
                        GREEN_DARK, BLUE, PANEL, CORAL_BG, CORAL) -> None:

    story += section_banner("Section 7 — Annexes techniques", HexColor("#1a3450"), s)

    # 7.1 Dépendances
    story.append(Paragraph("7.1  Dépendances Python et versions recommandées", s["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "ORNI-LAB repose sur les bibliothèques scientifiques Python suivantes. "
        "Les versions indiquées sont celles testées et validées. "
        "Des versions antérieures peuvent fonctionner mais certaines corrections "
        "(notamment statsmodels >= 0.14 pour le modèle mixte) sont critiques.", s["body"]))
    story.append(spacer(0.2))
    story.append(generic_table(
        ["Bibliothèque", "Version min.", "Rôle principal"],
        [
            ["streamlit",    "1.40",   "Framework web interactif, gestion de session, widgets"],
            ["numpy",        "1.24",   "Calculs matriciels, algèbre linéaire (Leslie, KDE, PVA)"],
            ["pandas",       "2.0",    "Manipulation de DataFrames, import CSV, statistiques"],
            ["scipy",        "1.11",   "Tests statistiques, optimisation, intégration ODE, KDE"],
            ["statsmodels",  "0.14",   "GLM, modèles mixtes LMM (bse_fe critique >= 0.14)"],
            ["plotly",       "5.18",   "Graphiques interactifs (scatter, bar, heatmap, contour)"],
            ["reportlab",    "4.0",    "Génération des rapports PDF (export module)"],
            ["matplotlib",   "3.7",    "Figures de diagnostics (Q-Q plots, résidus)"],
        ],
        s,
        col_widths=[3.2 * cm, 2.2 * cm, 9.1 * cm],
    ))

    story.append(spacer(0.3))
    story.append(Paragraph("7.2  Sécurité et robustesse de l'application", s["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "ORNI-LAB a été audité pour les vecteurs d'attaque courants des applications "
        "web Streamlit. Voici les mesures de sécurité en place :", s["body"]))
    for item in [
        "<b>Aucun eval() / exec()</b> — le code n'évalue jamais de chaînes de caractères "
        "utilisateur comme du code Python (pas de RCE possible).",
        "<b>Lecture seule des CSV</b> — les fichiers uploadés sont lus en mémoire via pandas, "
        "jamais écrits sur le disque ni exécutés.",
        "<b>Pas de base de données</b> — pas de risque d'injection SQL.",
        "<b>Pas d'authentification</b> — l'application est locale (localhost:8501), "
        "non exposée sur Internet.",
        "<b>try/except global</b> — depuis v2.0, chaque renderer est encapsulé dans un "
        "try/except : une erreur dans un module n'expose pas de traceback brut à l'utilisateur "
        "final et ne plante pas l'application.",
        "<b>Nettoyage des données</b> — les valeurs nulles et types incorrects sont normalisés "
        "avant tout calcul (pas d'injection via les données).",
    ]:
        story.append(Paragraph(f"• {item}", s["bullet"]))

    story.append(spacer(0.3))
    story.append(Paragraph("7.3  Problèmes fréquents et solutions", s["h1"]))
    story.append(hr())

    problems = [
        (
            "L'application ne démarre pas — ModuleNotFoundError",
            "Vérifier que toutes les dépendances sont installées : "
            "pip install streamlit numpy scipy pandas statsmodels plotly reportlab. "
            "Utiliser un environnement virtuel dédié pour éviter les conflits de versions."
        ),
        (
            "Port 8501 déjà utilisé",
            "Le fichier ORNI-LAB.bat libère automatiquement le port avant de lancer Streamlit. "
            "En ligne de commande : netstat -ano | findstr :8501 pour trouver le PID, "
            "puis taskkill /F /PID <pid>."
        ),
        (
            "Erreur dans le modèle mixte : Length mismatch",
            "Causé par statsmodels < 0.14 où result.bse incluait 3 éléments au lieu de 2. "
            "La version 2.0 extrait les éléments par indice numpy [:n_fe] — correctif appliqué."
        ),
        (
            "Encodage incorrect dans le CSV (caractères corrompus)",
            "Utiliser l'encodage UTF-8 BOM lors de l'export Excel. "
            "Le module Analyse CSV essaie automatiquement 5 encodages. "
            "En dernier recours, ouvrir le fichier dans Notepad++ et reconvertir en UTF-8."
        ),
        (
            "Erreur linregress : Cannot calculate regression (std = 0)",
            "Une colonne constante (tous les individus ont la même valeur) ne permet pas "
            "de calculer une régression. Le module regression.py v2.0 affiche un avertissement "
            "clair et retourne sans planter."
        ),
        (
            "Les graphiques ne s'affichent pas dans le navigateur",
            "Vider le cache du navigateur (Ctrl+F5). Si l'erreur persiste, "
            "vérifier que use_container_width=True est bien passé à st.plotly_chart. "
            "Sous Firefox, désactiver les extensions de blocage de scripts."
        ),
    ]
    for prob, sol in problems:
        story.append(Paragraph(f"<b>Problème :</b> {prob}", s["h3"]))
        story.append(warning_box(sol, s))
        story.append(spacer(0.1))

    story.append(PageBreak())


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — GLOSSAIRE
# ══════════════════════════════════════════════════════════════════════════════
def glossaire(story: list, s: dict, hr, spacer, section_banner, GREEN_DARK) -> None:

    story += section_banner("Section 8 — Glossaire des termes statistiques", HexColor("#2d5016"), s)
    story.append(Paragraph("8. Glossaire des termes statistiques et écologiques", s["h1"]))
    story.append(hr())
    story.append(spacer(0.2))

    terms = [
        ("AIC (Akaike Information Criterion)",
         "Critère de sélection de modèle : AIC = -2*log(L) + 2*k. Plus l'AIC est bas, "
         "meilleur est le compromis ajustement/parcimonie. Différence ΔAIC > 2 indique "
         "un support substantiel pour le modèle à AIC plus bas."),
        ("Bandwidth (KDE)",
         "Paramètre de lissage de l'estimateur à noyau (KDE). Un bandwidth trop petit "
         "produit un sur-ajustement (nombreux pics), trop grand un sous-ajustement "
         "(zones trop étalées). La règle de Scott donne un bandwidth automatique optimal "
         "pour les distributions gaussiennes."),
        ("Capacité de charge (K)",
         "Taille de population maximale que peut supporter un environnement donné. "
         "Dans le modèle logistique, la population converge vers K. Dépend des ressources "
         "disponibles (habitat, nourriture, sites de nidification)."),
        ("CMR (Capture-Marquage-Recapture)",
         "Famille de méthodes pour estimer l'abondance et la survie à partir de "
         "données de capture répétées. Lincoln-Petersen (2 sessions) est le modèle de base ; "
         "Cormack-Jolly-Seber (CJS) estime la survie apparente avec sessions multiples."),
        ("Cohen d",
         "Taille d'effet standardisée pour la comparaison de deux moyennes : "
         "d = (x1_bar - x2_bar) / s_pooled. Conventions : 0.2 = faible, 0.5 = modéré, "
         "0.8 = fort. Indépendant de la taille d'échantillon."),
        ("Détectabilité (p)",
         "Probabilité qu'un individu présent sur un site soit détecté lors d'une visite. "
         "Si p < 1, l'absence apparente ne prouve pas l'absence réelle. "
         "La correction pour p est le fondement des modèles d'occupation et du distance sampling."),
        ("Distribution stable (Leslie)",
         "Répartition asymptotique de la population entre classes d'âge, atteinte "
         "indépendamment de la distribution initiale. Correspond au vecteur propre droit "
         "de la matrice de Leslie."),
        ("Élasticité",
         "Sensibilité relative d'une valeur propre (lambda) aux changements proportionnels "
         "d'un paramètre de la matrice de Leslie. Somme à 1 sur tous les éléments. "
         "Identifie les paramètres démographiques les plus importants pour la croissance."),
        ("ESW (Effective Strip Width)",
         "Largeur de bande hypothétique dans laquelle tous les individus seraient détectés "
         "avec certitude et qui donnerait le même nombre de détections que la bande réelle. "
         "ESW = intégrale de g(x) de 0 à W."),
        ("GLM (Generalized Linear Model)",
         "Extension de la régression linéaire pour des distributions non gaussiennes de Y. "
         "Le GLM Poisson est adapté aux comptages, le logistique aux présences/absences. "
         "Le lien canonique (log pour Poisson, logit pour binomial) relie le prédicteur linéaire "
         "à l'espérance de Y."),
        ("ICC (Intraclass Correlation Coefficient)",
         "Proportion de la variance totale d'une variable due aux différences entre groupes : "
         "ICC = sigma²_b / (sigma²_b + sigma²_e). ICC > 0.1 justifie l'usage d'un "
         "modèle mixte. ICC = 0 : toute la variance est intra-groupe."),
        ("IRR (Incidence Rate Ratio)",
         "Ratio des taux d'incidence dans un GLM Poisson ou BN : IRR = exp(beta). "
         "IRR = 1.5 pour l'habitat forêt signifie : l'abondance est 1.5x plus élevée "
         "en forêt qu'en habitat de référence."),
        ("Lambda (matrice de Leslie)",
         "Valeur propre dominante de la matrice de Leslie. lambda > 1 : croissance, "
         "lambda = 1 : stabilité, lambda < 1 : déclin. "
         "Relation avec r : lambda = exp(r)."),
        ("Mann-Kendall (test de)",
         "Test non paramétrique de détection d'une tendance monotone dans une série "
         "temporelle. Robuste aux non-normalités et aux valeurs aberrantes. "
         "H0 : pas de tendance. Statistique S = somme des signes des différences."),
        ("MCP (Minimum Convex Polygon)",
         "Plus petit polygone convexe contenant X% des localisations d'un individu. "
         "Méthode historique (Mohr 1947) pour estimer le domaine vital. "
         "Simple mais sensible aux localisations extrêmes."),
        ("OLS (Ordinary Least Squares)",
         "Méthode d'estimation de la régression linéaire minimisant la somme des carrés "
         "des résidus. Estimateur BLUE (Best Linear Unbiased Estimator) si les hypothèses "
         "de Gauss-Markov sont vérifiées."),
        ("p-value",
         "Probabilité d'observer un résultat au moins aussi extrême que celui observé "
         "si H0 est vraie. p < 0.05 : résultat significatif au seuil 5%. "
         "La p-value ne mesure pas l'importance biologique — toujours l'accompagner "
         "d'une taille d'effet."),
        ("PVA (Population Viability Analysis)",
         "Ensemble de méthodes stochastiques pour estimer le risque d'extinction d'une "
         "population à un horizon temporel donné. Intègre l'incertitude environnementale "
         "et démographique. Fondement des Plans Nationaux d'Action (PNA)."),
        ("R² (coefficient de détermination)",
         "Proportion de la variance de Y expliquée par le modèle : R² = 1 - SSE/SST. "
         "R² = 1 : ajustement parfait. R² = 0 : le modèle n'explique rien. "
         "Sensible aux valeurs aberrantes et non adapté aux GLM."),
        ("REML (Restricted Maximum Likelihood)",
         "Méthode d'estimation des composantes de variance dans les modèles mixtes. "
         "Corrige le biais de sous-estimation de sigma²_b du ML classique. "
         "Recommandé pour estimer les effets aléatoires ; utiliser ML uniquement "
         "pour comparer des modèles avec effets fixes différents."),
        ("Shannon (indice de)",
         "Indice de diversité : H' = -sum(p_i * ln(p_i)). H' = 0 : une seule espèce. "
         "H' = ln(S) : toutes les espèces également abondantes. "
         "Sensible à la richesse spécifique et à l'équitabilité."),
        ("Surdispersion",
         "Variance observée supérieure à la variance théorique d'un modèle. "
         "Dans un GLM Poisson : phi = chi²_Pearson / df > 1. "
         "Cause habituelle : agrégation spatiale, hétérogénéité non modélisée, "
         "excès de zéros. Solution : GLM Binomial Négatif ou quasi-Poisson."),
    ]

    for term, defn in terms:
        story.append(Paragraph(term, s["gloss_t"]))
        story.append(Paragraph(defn, s["gloss_b"]))


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — RÉFÉRENCES
# ══════════════════════════════════════════════════════════════════════════════
REFERENCES = [
    # Distance sampling
    "Buckland, S.T., Anderson, D.R., Burnham, K.P., Laake, J.L., Borchers, D.L. & Thomas, L. (2001). "
    "Introduction to Distance Sampling: Estimating Abundance of Biological Populations. "
    "Oxford University Press, Oxford.",
    # Leslie matrices
    "Caswell, H. (2001). Matrix Population Models: Construction, Analysis, and Interpretation, "
    "2nd ed. Sinauer Associates, Sunderland, MA.",
    # PVA
    "Beissinger, S.R. & McCullough, D.R. (eds, 2002). Population Viability Analysis. "
    "University of Chicago Press, Chicago.",
    # Occupancy
    "MacKenzie, D.I., Nichols, J.D., Lachman, G.B., Droege, S., Royle, J.A. & Langtimm, C.A. (2002). "
    "Estimating site occupancy rates when detection probabilities are less than one. "
    "Ecology 83(8): 2248-2255.",
    # MCP
    "Mohr, C.O. (1947). Table of equivalent populations of North American small mammals. "
    "American Midland Naturalist 37(1): 223-249.",
    # CMR
    "Lincoln, F.C. (1930). Calculating Waterfowl Abundance on the Basis of Banding Returns. "
    "U.S. Department of Agriculture Circular 118: 1-4.",
    # Logistic growth
    "Verhulst, P.F. (1838). Notice sur la loi que la population suit dans son accroissement. "
    "Correspondance Mathématique et Physique 10: 113-121.",
    # KDE
    "Silverman, B.W. (1986). Density Estimation for Statistics and Data Analysis. "
    "Chapman and Hall, London.",
    # Shannon
    "Shannon, C.E. & Weaver, W. (1949). The Mathematical Theory of Communication. "
    "University of Illinois Press, Urbana.",
    # Lotka-Volterra
    "Lotka, A.J. (1925). Elements of Physical Biology. Williams & Wilkins, Baltimore.",
    "Volterra, V. (1926). Fluctuations in the Abundance of a Species Considered Mathematically. "
    "Nature 118: 558-560.",
    # Mixed effects
    "Zuur, A.F., Ieno, E.N., Walker, N.J., Saveliev, A.A. & Smith, G.M. (2009). "
    "Mixed Effects Models and Extensions in Ecology with R. Springer, New York.",
    # GLM
    "McCullagh, P. & Nelder, J.A. (1989). Generalized Linear Models, 2nd ed. "
    "Chapman & Hall, London.",
    # Biostatistics
    "Sokal, R.R. & Rohlf, F.J. (2012). Biometry: The Principles and Practice of Statistics "
    "in Biological Research, 4th ed. W.H. Freeman, New York.",
    "Zar, J.H. (2010). Biostatistical Analysis, 5th ed. Prentice Hall, Upper Saddle River, NJ.",
    # Quantitative conservation
    "Morris, W.F. & Doak, D.F. (2002). Quantitative Conservation Biology: Theory and Practice "
    "of Population Viability Analysis. Sinauer Associates, Sunderland, MA.",
    # Mann-Kendall
    "Hirsch, R.M., Slack, J.R. & Smith, R.A. (1982). Techniques of trend analysis for monthly "
    "water quality data. Water Resources Research 18(1): 107-121.",
    # Data science
    "Wickham, H. & Grolemund, G. (2017). R for Data Science. O'Reilly Media, Sebastopol, CA.",
    # EDA
    "Tukey, J.W. (1977). Exploratory Data Analysis. Addison-Wesley, Reading, MA.",
]


def references_section(story: list, s: dict, hr, spacer, section_banner) -> None:
    story += section_banner("Section 9 — Références bibliographiques", HexColor("#2d2d2d"), s)
    story.append(Paragraph("9. Références bibliographiques", s["h1"]))
    story.append(hr())
    story.append(spacer(0.2))
    for ref in REFERENCES:
        story.append(Paragraph(ref, s["ref"]))
    story.append(spacer(0.5))


def closing_banner(story: list, s: dict, spacer, GREEN_DARK, white) -> None:
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    fin_data = [[Paragraph(
        "<b>ORNI-LAB v2.0</b>  —  Développé par <b>Abdoulaye Diop</b>  ·  "
        "Bioinformaticien · Biomathématicien<br/>"
        "Laboratoire Interactif de Modélisation Ornithologique  ·  Mai 2026<br/>"
        "dioplayes@gmail.com  ·  +221 77 113 07 48",
        ParagraphStyle("fin", parent=s["caption"], textColor=white,
                       fontSize=10, leading=16, alignment=TA_CENTER)
    )]]
    W_val = 21 * cm - 4 * cm
    fin_t = Table(fin_data, colWidths=[W_val])
    fin_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), GREEN_DARK),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(fin_t)
