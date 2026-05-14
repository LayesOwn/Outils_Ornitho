#!/usr/bin/env python3
"""Génère la documentation PDF complète d'ORNI-LAB — Abdoulaye Diop."""

from __future__ import annotations

import datetime
from pathlib import Path

from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── Palette ──────────────────────────────────────────────────────────────────
GREEN       = HexColor("#39d98a")
GREEN_DARK  = HexColor("#1e7e5a")
GREEN_BG    = HexColor("#edf9f3")
BLUE        = HexColor("#4dabf7")
BLUE_BG     = HexColor("#eaf5ff")
DARK        = HexColor("#10161f")
TEXT        = HexColor("#1e2a38")
MUTED       = HexColor("#6b7a8d")
PANEL       = HexColor("#f4f7f9")
CORAL       = HexColor("#e05252")
YELLOW_BG   = HexColor("#fffbea")
YELLOW_ACC  = HexColor("#c47f00")
W, H        = A4

OUT = Path("ORNI-LAB_Documentation.pdf")


# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles() -> dict:
    base = getSampleStyleSheet()
    s: dict = {}

    def ps(name, **kw) -> ParagraphStyle:
        parent = kw.pop("parent", "Normal")
        return ParagraphStyle(name, parent=base[parent], **kw)

    s["cover_title"] = ps("cover_title", fontSize=46, leading=54,
                           textColor=white, alignment=TA_LEFT, fontName="Helvetica-Bold")
    s["cover_sub"]   = ps("cover_sub",   fontSize=17, leading=24,
                           textColor=HexColor("#c8e6d9"), alignment=TA_LEFT, fontName="Helvetica")
    s["cover_meta"]  = ps("cover_meta",  fontSize=12, leading=18,
                           textColor=HexColor("#a0c4b5"), alignment=TA_LEFT, fontName="Helvetica")

    s["h_part"]  = ps("h_part",  fontSize=22, leading=28, textColor=white,
                       fontName="Helvetica-Bold", alignment=TA_LEFT, spaceBefore=0, spaceAfter=6)
    s["h1"]      = ps("h1",      fontSize=16, leading=22, textColor=GREEN_DARK,
                       fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=6)
    s["h2"]      = ps("h2",      fontSize=13, leading=18, textColor=TEXT,
                       fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4)
    s["h3"]      = ps("h3",      fontSize=11, leading=16, textColor=MUTED,
                       fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=3)
    s["body"]    = ps("body",    fontSize=10, leading=15, textColor=TEXT,
                       alignment=TA_JUSTIFY, spaceAfter=4, fontName="Helvetica")
    s["bullet"]  = ps("bullet",  fontSize=10, leading=14, textColor=TEXT,
                       leftIndent=16, bulletIndent=4, spaceAfter=2, fontName="Helvetica",
                       bulletText="•")
    s["caption"] = ps("caption", fontSize=8.5, leading=12, textColor=MUTED,
                       fontName="Helvetica-Oblique", alignment=TA_CENTER)
    s["toc_h"]   = ps("toc_h",   fontSize=11, leading=16, textColor=GREEN_DARK,
                       fontName="Helvetica-Bold", leftIndent=0)
    s["toc_m"]   = ps("toc_m",   fontSize=10, leading=14, textColor=TEXT,
                       fontName="Helvetica", leftIndent=18)
    s["tag_bio"] = ps("tag_bio", fontSize=9, textColor=BLUE,
                       fontName="Helvetica-Bold", alignment=TA_RIGHT)
    s["tag_dyn"] = ps("tag_dyn", fontSize=9, textColor=GREEN_DARK,
                       fontName="Helvetica-Bold", alignment=TA_RIGHT)
    s["formula"] = ps("formula", fontSize=9.5, leading=14, textColor=HexColor("#1a3450"),
                       fontName="Courier", leftIndent=20, spaceAfter=4)
    s["ref"]     = ps("ref",     fontSize=9, leading=13, textColor=MUTED,
                       fontName="Helvetica", leftIndent=12, spaceAfter=3)
    return s


# ── Helpers ───────────────────────────────────────────────────────────────────
def spacer(h: float = 0.3) -> Spacer:
    return Spacer(1, h * cm)


def hr(color=GREEN, thickness=1.2) -> HRFlowable:
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=4)


def section_banner(label: str, color: HexColor, s: dict, tag_style: str) -> list:
    """Bandeau coloré de séparation de section."""
    data = [[Paragraph(label, s["h_part"])]]
    t = Table(data, colWidths=[W - 4.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 18),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 18),
        ("ROUNDEDCORNERS", [8]),
    ]))
    return [spacer(0.4), t, spacer(0.5)]


def info_box(text: str, s: dict, bg=BLUE_BG, border=BLUE) -> Table:
    data = [[Paragraph(text, s["body"])]]
    t = Table(data, colWidths=[W - 4.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), bg),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBEFORE",    (0, 0), (0, -1), 3, border),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return t


def module_card(
    num: str, title: str, tag: str, tag_color: HexColor,
    description: str, methodology: str, ornithology: str,
    inputs: list[str], outputs: list[str], importance: str,
    s: dict,
) -> list:
    """Bloc complet pour un module."""
    story = []

    # En-tête du module
    header_data = [
        [
            Paragraph(f"<b>{num}. {title}</b>", s["h1"]),
            Paragraph(tag, ParagraphStyle("_tag", parent=s["body"], textColor=tag_color,
                                           fontName="Helvetica-Bold", fontSize=9, alignment=TA_RIGHT)),
        ]
    ]
    ht = Table(header_data, colWidths=[W - 7 * cm, 2.5 * cm])
    ht.setStyle(TableStyle([
        ("VALIGN",  (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(KeepTogether([ht, hr()]))

    # Description
    story.append(Paragraph("<b>Description</b>", s["h2"]))
    story.append(Paragraph(description, s["body"]))

    # Fondements méthodologiques
    story.append(Paragraph("<b>Fondements méthodologiques</b>", s["h2"]))
    story.append(Paragraph(methodology, s["body"]))

    # Application ornithologique
    story.append(Paragraph("<b>Application ornithologique</b>", s["h2"]))
    story.append(info_box(ornithology, s, bg=GREEN_BG, border=GREEN))
    story.append(spacer(0.2))

    # Entrées / Sorties côte à côte
    in_items  = [Paragraph(f"• {x}", s["body"]) for x in inputs]
    out_items = [Paragraph(f"• {x}", s["body"]) for x in outputs]
    io_data = [
        [Paragraph("<b>Paramètres d'entrée</b>", s["h3"]),
         Paragraph("<b>Sorties et résultats</b>", s["h3"])],
        [in_items, out_items],
    ]
    io_t = Table(io_data, colWidths=[(W - 4.5 * cm) / 2, (W - 4.5 * cm) / 2])
    io_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), PANEL),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("LINEABOVE",     (0, 0), (-1, 0), 0.5, HexColor("#d0d8e4")),
        ("LINEBELOW",     (0, -1), (-1, -1), 0.5, HexColor("#d0d8e4")),
        ("LINEBETWEEN",   (0, 0), (-1, -1), 0.5, HexColor("#d0d8e4")),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(io_t)
    story.append(spacer(0.2))

    # Importance
    story.append(Paragraph("<b>Importance en écologie et conservation</b>", s["h2"]))
    story.append(info_box(importance, s, bg=YELLOW_BG, border=YELLOW_ACC))
    story.append(spacer(0.5))

    return story


# ── Page number callback ──────────────────────────────────────────────────────
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(W - 2 * cm, 1.4 * cm, f"Page {doc.page}")
    canvas.drawString(2 * cm, 1.4 * cm, "ORNI-LAB — Documentation © Abdoulaye Diop, 2026")
    canvas.setStrokeColor(HexColor("#d0d8e4"))
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, 1.7 * cm, W - 2 * cm, 1.7 * cm)
    canvas.restoreState()


# ── Cover page ────────────────────────────────────────────────────────────────
def cover_page(story: list, s: dict) -> None:
    # Bloc vert supérieur
    cover_data = [[
        Paragraph("ORNI-LAB", s["cover_title"]),
    ]]
    top = Table(cover_data, colWidths=[W - 4 * cm], rowHeights=[7 * cm])
    top.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), GREEN_DARK),
        ("LEFTPADDING",   (0, 0), (-1, -1), 30),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 30),
        ("TOPPADDING",    (0, 0), (-1, -1), 30),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("ROUNDEDCORNERS", [10]),
    ]))
    story.append(spacer(2))
    story.append(top)
    story.append(spacer(0.4))

    # Sous-titre
    sub_data = [[Paragraph(
        "Laboratoire Interactif de Modélisation Ornithologique",
        s["cover_sub"]
    )]]
    sub_t = Table(sub_data, colWidths=[W - 4 * cm])
    sub_t.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, -1), HexColor("#1a5c42")),
        ("LEFTPADDING", (0, 0), (-1, -1), 30),
        ("TOPPADDING",  (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(sub_t)
    story.append(spacer(3))

    # Métadonnées
    meta = [
        ("Auteur",    "Abdoulaye Diop"),
        ("Version",   "1.0 — Mai 2026"),
        ("Modules",   "18 modules interactifs"),
        ("Sections",  "Biostatistique · Dynamique des populations"),
        ("Audience",  "Licence 3 · Master 1 & 2 · Doctorat"),
        ("Langage",   "Python · Streamlit · SciPy · Statsmodels"),
    ]
    for key, val in meta:
        row_data = [[
            Paragraph(f"<b>{key}</b>", s["body"]),
            Paragraph(val, s["body"]),
        ]]
        row_t = Table(row_data, colWidths=[3.5 * cm, W - 8.5 * cm])
        row_t.setStyle(TableStyle([
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LINEBELOW",     (0, 0), (-1, -1), 0.3, HexColor("#d0d8e4")),
        ]))
        story.append(row_t)

    story.append(PageBreak())


# ── Table of Contents ─────────────────────────────────────────────────────────
def table_of_contents(story: list, s: dict) -> None:
    story.append(Paragraph("Table des matières", s["h1"]))
    story.append(hr())
    story.append(spacer(0.3))

    toc = [
        ("1.", "Introduction", None),
        ("2.", "Architecture générale", None),
        ("3.", "Guide d'utilisation", None),
        ("4.", "Section Biostatistique", None),
        ("4.1", "Statistiques descriptives", "BIOSTAT"),
        ("4.2", "Analyse CSV", "BIOSTAT"),
        ("4.3", "Corrélation et régression", "BIOSTAT"),
        ("4.4", "Tests statistiques", "BIOSTAT"),
        ("4.5", "GLM pour données de comptage", "BIOSTAT"),
        ("4.6", "Modèle mixte — LMM", "BIOSTAT"),
        ("4.7", "Domaine vital — MCP", "BIOSTAT"),
        ("4.8", "Domaine vital — KDE", "BIOSTAT"),
        ("5.", "Section Dynamique des populations", None),
        ("5.1",  "Richesse spécifique et diversité", "DYN"),
        ("5.2",  "Croissance exponentielle/logistique", "DYN"),
        ("5.3",  "Matrices de Leslie", "DYN"),
        ("5.4",  "Capture-Marquage-Recapture", "DYN"),
        ("5.5",  "Modèles d'occupation", "DYN"),
        ("5.6",  "Distance sampling", "DYN"),
        ("5.7",  "Lotka-Volterra", "DYN"),
        ("5.8",  "Séries temporelles de population", "DYN"),
        ("5.9",  "PVA et conservation", "DYN"),
        ("5.10", "Scénarios de gestion", "DYN"),
        ("6.",  "Références bibliographiques", None),
    ]

    for num, title, tag in toc:
        indent = 18 if "." in num and num != "6." and len(num) > 2 else 0
        color = BLUE if tag == "BIOSTAT" else (GREEN_DARK if tag == "DYN" else TEXT)
        style = ParagraphStyle(f"toc_{num}", parent=s["body"],
                                leftIndent=indent, textColor=color,
                                fontName="Helvetica-Bold" if not tag else "Helvetica",
                                spaceAfter=3)
        story.append(Paragraph(f"{num}&nbsp;&nbsp;&nbsp;{title}", style))

    story.append(PageBreak())


# ── Introduction ──────────────────────────────────────────────────────────────
def introduction(story: list, s: dict) -> None:
    story.append(Paragraph("1. Introduction", s["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "ORNI-LAB est un laboratoire interactif de modélisation ornithologique développé "
        "pour l'enseignement universitaire en écologie des populations et en biologie de la "
        "conservation. Il offre une interface web intuitive permettant aux étudiants et aux "
        "enseignants d'explorer, de visualiser et d'analyser des données ornithologiques "
        "sans prérequis en programmation.", s["body"]))
    story.append(spacer(0.2))
    story.append(Paragraph(
        "L'outil propose 18 modules couvrant deux grandes disciplines : la biostatistique "
        "appliquée aux oiseaux et la dynamique des populations. Chaque module est "
        "conçu selon le même principe pédagogique :", s["body"]))

    for item in [
        "Mode <b>simulation</b> : paramètres ajustables, données générées automatiquement "
        "pour illustrer les concepts de manière contrôlée.",
        "Mode <b>terrain</b> : import d'un fichier CSV de données réelles — l'interface s'adapte "
        "automatiquement aux colonnes détectées.",
        "Mode <b>Étudiant</b> : résultats et interprétations automatiques, sans surcharge "
        "mathématique.",
        "Mode <b>Enseignant</b> : formules LaTeX, notes pédagogiques avancées et erreurs "
        "fréquentes révélées pour accompagner le cours.",
        "Export <b>PDF</b> de résumés et export <b>CSV</b> des données pour prolonger "
        "l'analyse hors de l'outil.",
    ]:
        story.append(Paragraph(item, s["bullet"]))

    story.append(spacer(0.3))
    story.append(Paragraph(
        "ORNI-LAB est conçu pour être utilisé en travaux dirigés, en travaux pratiques "
        "ou en autonomie, du niveau L3 au doctorat. Son architecture modulaire permet "
        "également d'intégrer de nouveaux outils analytiques au fil de l'évolution "
        "des besoins pédagogiques.", s["body"]))

    story.append(spacer(0.5))
    story.append(Paragraph("2. Architecture générale", s["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "L'application est développée en Python avec le framework Streamlit. "
        "La structure est organisée en couches indépendantes :", s["body"]))

    arch_data = [
        ["Couche",         "Description",                      "Fichiers principaux"],
        ["Interface",      "Pages, navigation, session state", "app/main.py, app/config.py"],
        ["Modules",        "18 simulateurs spécialisés",      "modules/*.py"],
        ["UI partagée",    "Composants visuels réutilisables", "utils/ui.py"],
        ["Export",         "Génération PDF et CSV",         "core/export.py"],
        ["Données",   "Valeurs défaut et exemples",         "data/examples.py"],
        ["Tests",          "Suite de tests unitaires (28)",    "tests/test_models.py"],
    ]
    arch_t = Table(arch_data, colWidths=[3 * cm, 5.5 * cm, 6 * cm])
    arch_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), GREEN_DARK),
        ("TEXTCOLOR",     (0, 0), (-1, 0), white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, PANEL]),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.4, HexColor("#c8d6e0")),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(spacer(0.2))
    story.append(arch_t)

    story.append(spacer(0.5))
    story.append(Paragraph("3. Guide d'utilisation", s["h1"]))
    story.append(hr())

    steps = [
        ("1 — Choisir un mode",
         "Dans la barre latérale gauche, sélectionner le mode d'affichage : "
         "Étudiant (résultats et interprétations) ou Enseignant "
         "(+ formules, notes pédagogiques, erreurs fréquentes)."),
        ("2 — Charger des données (optionnel)",
         "Déposer un fichier CSV via la zone de chargement de la sidebar. "
         "Le séparateur (virgule ou point-virgule) est sélectionnable. "
         "Sans fichier, chaque module génère une simulation pédagogique."),
        ("3 — Naviguer vers un module",
         "Depuis la page d'accueil, cliquer sur une des deux cartes de section "
         "(Biostatistique ou Dynamique des populations), puis sélectionner "
         "un module dans la sidebar."),
        ("4 — Explorer et ajuster",
         "Les curseurs et champs de la sidebar modifient les paramètres en temps réel. "
         "Les graphiques, tableaux et interprétations se mettent à jour instantanément."),
        ("5 — Exporter les résultats",
         "Chaque module propose un bouton d'export PDF (résumé avec interprétation) "
         "et/ou un export CSV des données utilisées."),
    ]
    for title, desc in steps:
        story.append(Paragraph(f"<b>{title}</b>", s["h2"]))
        story.append(Paragraph(desc, s["body"]))
    story.append(PageBreak())


# ── Modules data ──────────────────────────────────────────────────────────────
BIOSTAT_MODULES = [
    dict(
        num="4.1", title="Statistiques descriptives", tag="BIOSTATISTIQUE",
        description=(
            "Ce module permet de résumer et de visualiser un jeu de données ornithologique "
            "complet : distribution des variables numériques (histogrammes, boîtes à moustaches), "
            "matrices de corrélation, statistiques de position et de dispersion, ainsi que "
            "des tableaux croisés pour les variables catégorielles. Il constitue la première "
            "étape indispensable de toute analyse de données."
        ),
        methodology=(
            "Le module calcule pour chaque variable numérique : la moyenne, la médiane, "
            "l'écart-type, les quartiles, le minimum et le maximum. Les histogrammes "
            "permettent d'évaluer visuellement la normalité. La matrice de corrélation "
            "de Pearson donne une vue d'ensemble des associations linéaires. "
            "Les boîtes à moustaches identifient les valeurs aberrantes et comparent "
            "les distributions entre groupes."
        ),
        ornithology=(
            "Utilisé pour explorer des données de morphométrie (envergure, masse, longueur "
            "du tarse), de comptages sur points d'écoute, ou de suivis de baguage. "
            "Permet d'évaluer rapidement si les distributions sont normales avant "
            "d'appliquer des tests paramétriques, et d'identifier des valeurs "
            "aberrantes liées à des erreurs de saisie ou à des individus atypiques."
        ),
        inputs=["Fichier CSV avec colonnes numériques et catégorielles",
                "Sélection de la variable à analyser",
                "Variable de groupement optionnelle"],
        outputs=["Tableau de statistiques (n, moyenne, médiane, SD, IQR, min, max)",
                 "Histogramme de distribution",
                 "Boîte à moustaches par groupe",
                 "Matrice de corrélation (heatmap)"],
        importance=(
            "L'analyse exploratoire des données (AED) est la fondation de tout travail "
            "statistique rigoureux. Elle prévient les erreurs d'interprétation dues "
            "à des données non vérifiées et guide le choix des méthodes ultérieures."
        ),
    ),
    dict(
        num="4.2", title="Analyse CSV guidée", tag="BIOSTATISTIQUE",
        description=(
            "Module d'exploration automatisée d'un fichier CSV terrain. Il détecte "
            "automatiquement les colonnes numériques et catégorielles, nettoie les "
            "données (virgules décimales, espaces, colonnes vides), propose une "
            "régression linéaire interactive et une comparaison de deux groupes "
            "avec test de Mann-Whitney."
        ),
        methodology=(
            "Nettoyage automatique : suppression des colonnes entièrement vides, "
            "conversion des virgules en points pour les décimales, détection heuristique "
            "du type de colonne (numérique si ≥70% des valeurs sont convertibles). "
            "Régression par moindres carrés ordinaires (OLS). Comparaison de groupes "
            "par test de Mann-Whitney U non paramétrique."
        ),
        ornithology=(
            "Point d'entrée universel pour des données de terrain hors format standard : "
            "fichiers STOC, LPO, BBS, données de baguage, relevés de transects. "
            "Permet à un étudiant de charger ses propres données de TP et d'obtenir "
            "une analyse guidée en quelques clics."
        ),
        inputs=["Fichier CSV (virgule ou point-virgule)",
                "Sélection des colonnes X et Y pour la régression",
                "Sélection du groupe et de la variable pour la comparaison"],
        outputs=["Aperçu des premières lignes et types de colonnes",
                 "Régression OLS : pente, intercept, R², p-value",
                 "Comparaison de groupes : différence de médianes, p-value Mann-Whitney",
                 "Nuage de points avec droite de régression"],
        importance=(
            "Réduit la barrière d'entrée pour les étudiants sans compétences en "
            "programmation. Permet d'intégrer des données réelles dans tous les TP, "
            "renforçant le lien entre théorie statistique et pratique de terrain."
        ),
    ),
    dict(
        num="4.3", title="Corrélation et régression", tag="BIOSTATISTIQUE",
        description=(
            "Quantifie la relation linéaire entre deux variables ornithologiques continues. "
            "Propose la régression linéaire simple (OLS) avec visualisation du nuage de "
            "points, de la droite ajustée et de l'intervalle de confiance à 95%. "
            "Affiche les résidus et permet d'évaluer la qualité de l'ajustement."
        ),
        methodology=(
            "Régression par moindres carrés : minimise la somme des carrés des résidus. "
            "Coefficient de corrélation de Pearson (r) et coefficient de détermination (R²). "
            "Test de significativité de la pente (t-test). Intervalles de confiance "
            "de la droite de régression. Analyse des résidus pour vérifier "
            "l'homogénéité de la variance et la normalité."
        ),
        ornithology=(
            "Applications classiques : relation masse-envergure, relation taille du tarse-altitude "
            "d'une espce, corrélation entre abondance et surface d'habitat, régression "
            "du succès reproducteur sur la date de ponte. C'est l'outil de base pour "
            "tester des hypothèses alléométriques ou écologiques."
        ),
        inputs=["Variable explicative X (continue)",
                "Variable réponse Y (continue)",
                "Optionnel : variable de coloration des points (groupe)"],
        outputs=["Coefficients de régression (intercept, pente), erreurs-type, p-values",
                 "R² et R² ajusté",
                 "Nuage de points avec droite et IC 95%",
                 "Graphique des résidus vs valeurs ajustées"],
        importance=(
            "La régression linéaire est l'outil statistique le plus utilisé en écologie. "
            "Comprendre ses hypothèses (normalité des résidus, homoscédasticité, "
            "indépendance) est essentiel pour éviter les interprétations erronées."
        ),
    ),
    dict(
        num="4.4", title="Tests statistiques", tag="BIOSTATISTIQUE",
        description=(
            "Compare des groupes d'oiseaux selon une variable continue. Pour deux groupes, "
            "applique automatiquement le t-test de Welch et le test de Mann-Whitney U. "
            "Pour trois groupes ou plus, applique l'ANOVA unidirectionnelle et le test "
            "de Kruskal-Wallis. Inclut des tests de normalité (Shapiro-Wilk) et des "
            "graphiques Q-Q pour chaque groupe."
        ),
        methodology=(
            "Normalité : test de Shapiro-Wilk avec représentation Q-Q (scipy.stats.probplot). "
            "Comparaison 2 groupes : t-test de Welch (variances inégales tolérées) "
            "et Mann-Whitney U (non paramétrique). Comparaison k groupes : "
            "ANOVA (F de Fisher) + Kruskal-Wallis (H). Taille d'effet ANOVA : eta² = SS_between/SS_total."
        ),
        ornithology=(
            "Compare la masse moyenne entre mâles et femelles, l'abondance entre habitats, "
            "le succès de nidification entre sites. Fondamental pour valider des "
            "différences biologiques observées sur le terrain avant de les "
            "interpréter en termes écologiques."
        ),
        inputs=["Variable numérique à comparer",
                "Variable de groupement (2 à 6 groupes)",
                "Seuil alpha (0.05 par défaut)"],
        outputs=["Tableau de normalité (W, p-value) par groupe",
                 "Graphiques Q-Q par groupe",
                 "Statistique de test, degrés de liberté, p-value",
                 "Taille d'effet (eta² pour ANOVA)",
                 "Boîtes à moustaches avec annotation de significativité"],
        importance=(
            "Les tests statistiques sont l'épine dorsale de l'écologie quantitative. "
            "Enseigner conjointement tests paramétriques et non paramétriques, "
            "avec vérification des hypothèses, forme des scientifiques rigoureux."
        ),
    ),
    dict(
        num="4.5", title="GLM pour données de comptage", tag="BIOSTATISTIQUE",
        description=(
            "Modélise des données de comptage (nombres entiers non négatifs) avec "
            "un modèle linéaire généralisé (GLM) Poisson ou binomial négatif. "
            "Contrôle simultanément pour l'habitat, la tendance temporelle et l'effort "
            "d'échantillonnage (offset). Compare les deux familles via l'AIC et "
            "propose des diagnostics de résidus."
        ),
        methodology=(
            "GLM Poisson : log(mu) = X*beta + log(effort). Vérification de la "
            "surdispersion via phi = chi²_Pearson/df. GLM Binomial négatif : "
            "Var(Y) = mu + mu²/r (un paramètre de surdispersion supplémentaire). "
            "Coefficients interprétés en IRR (Incidence Rate Ratio = exp(beta)). "
            "Comparaison par AIC (Akaike Information Criterion)."
        ),
        ornithology=(
            "Standard pour les comptages sur points d'écoute (IPA, STOC), les relevés de "
            "transects ou les listes d'épandage. Permet de séparer l'effet habitat "
            "de l'effet année tout en corrigeant pour des efforts d'écoute variables. "
            "Utilisé par les programmes de surveillance long terme (BBS, STOC)."
        ),
        inputs=["Colonne de comptages (entiers >= 0)",
                "Colonne habitat (catégorielle)",
                "Colonne année",
                "Colonne effort (offset)"],
        outputs=["Tableau des IRR avec IC 95% et p-values",
                 "AIC Poisson vs Binomial négatif",
                 "Ratio de surdispersion Pearson/df",
                 "Graphiques diagnostics : résidus vs ajustés, Q-Q"],
        importance=(
            "Les comptages d'oiseaux violent systématiquement les hypothèses de la "
            "régression linéaire (non-normalité, variance non constante). Le GLM "
            "est le modèle adéquat et son enseignement est indispensable pour "
            "l'analyse des programmes de surveillance."
        ),
    ),
    dict(
        num="4.6", title="Modèle mixte — LMM", tag="BIOSTATISTIQUE",
        description=(
            "Modèle linéaire mixte (LMM) séparant les effets fixes (prédicteurs biologiques) "
            "des effets aléatoires (sites, individus, sessions). Estime le coefficient "
            "de corrélation intraclasse (ICC) qui quantifie la part de variance due "
            "au groupement, et affiche les composantes de variance."
        ),
        methodology=(
            "Modèle : y_ij = beta_0 + beta_1*x_ij + b_j + epsilon_ij, "
            "avec b_j ~ N(0, sigma²_b) et epsilon_ij ~ N(0, sigma²). "
            "Estimation par REML (Restricted Maximum Likelihood) via statsmodels.mixedlm. "
            "ICC = sigma²_b / (sigma²_b + sigma²). "
            "Diagnostics : résidus vs valeurs ajustées, AIC du modèle."
        ),
        ornithology=(
            "Indispensable pour les données de morphométrie collectées sur plusieurs sites "
            "(effet site = variation entre localités), pour les suivis de béhévior avec "
            "individus mesurés plusieurs fois, ou pour les données de baguage avec "
            "passagers multiples. Un ICC > 0.1 justifie systématiquement le LMM plutôt "
            "qu'un OLS qui donnerait des faux positifs."
        ),
        inputs=["Variable réponse Y numérique",
                "Prédicteur fixe X numérique",
                "Variable de groupement (effet aléatoire)"],
        outputs=["Tableau des effets fixes (coef., SE, z, p)",
                 "Composantes de variance (sigma²_b, sigma²)",
                 "ICC et AIC",
                 "Nuage de points coloré par groupe + droite d'effet fixe",
                 "Graphique des résidus"],
        importance=(
            "La plupart des données ornithologiques de terrain sont groupées (par site, "
            "transect ou individu). Ignorer cette structure induit des faux positifs et "
            "des p-values incorrectes. Le LMM est la solution standard en écologie moderne."
        ),
    ),
    dict(
        num="4.7", title="Domaine vital — MCP", tag="BIOSTATISTIQUE",
        description=(
            "Calcule le Minimum Convex Polygon (MCP) à partir de localisations GPS "
            "individuelles. Le MCP est le plus petit polygone convexe contenant X% "
            "des localisations d'un individu. Propose une visualisation cartographique "
            "interactive avec superposition des points et des polygones."
        ),
        methodology=(
            "Algorithme : (1) calculer le centroide des localisations, (2) trier par "
            "distance au centroide, (3) conserver les X% les plus proches, (4) calculer "
            "l'enveloppe convexe (scipy.spatial.ConvexHull). L'aire du MCP correspond "
            "à ConvexHull.volume en 2D. Paramétrable de 50% à 100%. "
            "Rférence fondatrice : Mohr (1947)."
        ),
        ornithology=(
            "Utilisé pour estimer le domaine vital de rapaces (épervier, busard, milan), "
            "de cigognes, de limicoles en période de nidification, ou de passereaux "
            "équipés de balises GPS légères. Permet de comparer les domaines vitaux "
            "entre sexes, âges ou saisons, et d'identifier les zones habitat critiques."
        ),
        inputs=["Colonnes X (longitude) et Y (latitude) des localisations",
                "Colonne identifiant individuel",
                "Percentile MCP (50-100%)"],
        outputs=["Carte interactive avec points et polygones MCP",
                 "Tableau des aires MCP par individu",
                 "N localisations utilisées vs total"],
        importance=(
            "Le MCP est la méthode de référence historique pour le domaine vital. "
            "Sa simplicité en fait un excellent outil pédagogique pour introduire "
            "les concepts d'utilisation de l'espace avant le KDE plus sophistiqué."
        ),
    ),
    dict(
        num="4.8", title="Domaine vital — KDE", tag="BIOSTATISTIQUE",
        description=(
            "Estime le domaine vital par Kernel Density Estimation : construit une surface "
            "de densité de probabilité à partir des localisations GPS et extrait des "
            "isopleths (contours de probabilité). Les isopleths à 50% (zone cœur) "
            "et 95% (domaine vital complet) sont les plus couramment utilisés."
        ),
        methodology=(
            "Estimateur à noyau gaussien bivarié : f_hat(x) = (1/n*h²) * sum(K((x-xi)/h)). "
            "Bandwidth par règle de Scott : h = n^(-1/6) * sigma_hat (optimal pour "
            "une distribution gaussienne bivariée). Isopleth X% : seuil de densité "
            "tel que X% de la masse totale de probabilité soit au-dessus. "
            "Implémenté avec scipy.stats.gaussian_kde."
        ),
        ornithology=(
            "Standard actuel en écologie du mouvement pour les oiseaux équipés de GPS "
            "ou balises PTT (Argos). Utilisé pour identifier les habitats critiques, "
            "couloirs migratoires, zones de reproduction et d'hivernage. "
            "Supérieur au MCP pour les espèces aux mouvements asymétriques ou multimodaux."
        ),
        inputs=["Colonnes X, Y des localisations GPS",
                "Colonne individu",
                "Facteur de lissage (multiplicateur de Scott : 0.1-2.0)",
                "Isopleths souhaités (50%, 75%, 90%, 95%, 99%)"],
        outputs=["Heatmap de densité KDE par individu (onglets)",
                 "Contours des isopleths en surimpression",
                 "Tableau des aires par isopleth et par individu",
                 "Export CSV des localisations"],
        importance=(
            "Le KDE est la méthode de choix pour l'analyse du domaine vital en recherche "
            "contemporaine. Comprendre le rôle du bandwidth et l'interprétation des "
            "isopleths est fondamental pour tout projet de radio-pistage ou de GPS-tracking."
        ),
    ),
]

DYNPOP_MODULES = [
    dict(
        num="5.1", title="Richesse spécifique et diversité", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Calcule et compare les indices de diversité alpha d'une communauté "
            "d'oiseaux : richesse spécifique (S), indice de Shannon (H'), indice "
            "de Simpson (1-D), équitabilité de Pielou (J') et courbes d'accumulation "
            "d'espèces (rareféfaction) avec intervalles de confiance."
        ),
        methodology=(
            "Shannon : H' = -sum(p_i * ln(p_i)). Simpson : D = sum(p_i²). "
            "Equitabilité : J' = H'/ln(S). Courbe d'accumulation : "
            "randomisation de l'ordre des sites, calcul du nombre moyen "
            "d'espèces observées en fonction du nombre de sites cumulés "
            "(50 réplications par défaut). IC 95% par percentiles."
        ),
        ornithology=(
            "Utilisé pour comparer la diversité des communautés d'oiseaux entre "
            "habitats (forêt vs lisire vs champ), entre saisons, ou entre zones "
            "protégées et non protégées. Outil de base pour l'évaluation "
            "écologique des plans de gestion et des études d'impact."
        ),
        inputs=["Matrice sites x espèces (colonnes = espèces)",
                "Ou fichier CSV avec colonnes d'abondance par espèce",
                "Nombre d'itérations pour les courbes d'accumulation"],
        outputs=["Indices S, H', 1-D, J' par site",
                 "Histogramme de comparaison des indices",
                 "Courbe d'accumulation avec IC 95%",
                 "Interprétation automatisée"],
        importance=(
            "La diversité aviaire est un indicateur reconnu de l'intégrité écologique. "
            "Ces indices sont utilisés dans les rapports d'impact environnemental, "
            "les évaluations Natura 2000 et les plans de gestion des réserves."
        ),
    ),
    dict(
        num="5.2", title="Croissance exponentielle et logistique", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Simule et compare deux modèles de croissance de population : la croissance "
            "exponentielle (Malthus) et la croissance logistique (Verhulst), avec "
            "contrôle du taux d'accroissement intrinèque (r) et de la capacité "
            "de charge (K). Visualise la convergence vers K et l'effet Allee."
        ),
        methodology=(
            "Exponentielle : N(t) = N0 * exp(r*t). "
            "Logistique : dN/dt = r*N*(1 - N/K), solution N(t) = K/(1 + ((K-N0)/N0)*exp(-r*t)). "
            "La densité-dépendance est encodée par le terme (1 - N/K). "
            "Temps de doublement : T_d = ln(2)/r."
        ),
        ornithology=(
            "Modèle de base pour comprendre la dynamique de récupération après un "
            "déclin (bécasse, spatule, outarde), la croissance d'une population "
            "introduite (vautour fauve réintroduit), ou l'impact d'une chasse "
            "sur une population en équilibre."
        ),
        inputs=["Population initiale N0",
                "Taux d'accroissement r",
                "Capacité de charge K",
                "Durée de simulation (années)"],
        outputs=["Courbes N(t) exponentielle et logistique",
                 "Temps de doublement",
                 "Valeurs à t final",
                 "Comparaison des deux trajectoires"],
        importance=(
            "Les modèles de croissance sont le fondement de la dynamique des populations. "
            "La distinction entre croissance densité-indépendante et densité-dépendante "
            "est essentielle pour dimensionner les efforts de conservation."
        ),
    ),
    dict(
        num="5.3", title="Matrices de Leslie", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Projette une population féminine structurée en classes d'âge à partir "
            "d'une matrice de Leslie intgrant fécondités et probabilités de survie. "
            "Calcule la valeur propre dominante (lambda), la distribution d'âge stable, "
            "les valeurs reproductives, et les matrices de sensibilité et d'élasticité."
        ),
        methodology=(
            "Projection : N(t+1) = A * N(t). Valeur propre dominante lambda_1 "
            "via np.linalg.eig(A). Distribution stable : vecteur propre droit w "
            "normalisé. Valeurs reproductives : vecteur propre gauche v de A^T. "
            "Sensibilité : S_ij = v_i*w_j/<v,w>. "
            "Elasticité : e_ij = (a_ij/lambda)*S_ij. Propriété : sum(e_ij) = 1."
        ),
        ornithology=(
            "Outil de référence pour la gestion d'espèces à vie longue : rapaces "
            "(vautour moine, aigle royal), grands plongéons, puffins, albatros. "
            "L'élasticité de la survie adulte est généralement la plus élevée chez "
            "ces espèces, orientée les priorités de conservation vers la réduction "
            "de la mortalité adulte (captures accessoires, hélicoltées)."
        ),
        inputs=["Fécondités par classe d'âge (F0...Fn)",
                "Probabilités de survie inter-classes (S0...Sn-1)",
                "Population initiale par classe",
                "Durée de projection"],
        outputs=["Courbes de projection N(t) par classe",
                 "Lambda dominant avec interprétation",
                 "Distribution d'âge stable (barres)",
                 "Valeurs reproductives par classe",
                 "Heatmaps de sensibilité et d'élasticité"],
        importance=(
            "Les matrices de Leslie sont l'outil le plus puissant pour cibler les "
            "actions de conservation : l'élasticité indique quel paramètre "
            "démographique améliorer en priorité pour maximiser la croissance "
            "de la population (Caswell, 2001)."
        ),
    ),
    dict(
        num="5.4", title="Capture-Marquage-Recapture", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Estime l'abondance d'une population d'oiseaux par l'estimateur de "
            "Lincoln-Petersen et ses variantes (avec correction de Chapman). "
            "Calcule les intervalles de confiance et explique le principe de "
            "la détectabilité imparfaite."
        ),
        methodology=(
            "Lincoln-Petersen : N_hat = (M * C) / R, avec M = marqués, "
            "C = capturés en deuxième occasion, R = recapturés. "
            "Correction de Chapman (non biaisée) : N_hat = (M+1)*(C+1)/(R+1) - 1. "
            "IC 95% par méthode du log. Coefficient de variation : CV = sqrt(Var(N_hat))/N_hat."
        ),
        ornithology=(
            "Utilisé pour estimer les effectifs de passereaux (sessions de baguage), "
            "de larolimicoles, de rapaces (piégeage-baguage). Permet d'obtenir "
            "une estimation absolue de l'abondance, contrairement aux IKA qui ne "
            "donnent qu'un indice relatif non calibré."
        ),
        inputs=["N individus capturés et marqués (M)",
                "N individus capturés en 2ème occasion (C)",
                "N recapturés (R)",
                "Optionnel : historiques multi-occasions"],
        outputs=["Estimation N_hat avec IC 95%",
                 "Erreur standard et CV",
                 "Graphique d'incertitude",
                 "Interprétation automatisée"],
        importance=(
            "L'estimation de l'abondance absolue est fondamentale pour évaluer l'état "
            "de conservation d'une population, dimensionner des programmes de "
            "réintroduction, et suivre les tendances dans le temps avec des "
            "estimations comparables."
        ),
    ),
    dict(
        num="5.5", title="Modèles d'occupation", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Estime séparément la probabilité d'occupation (psi) et la probabilité "
            "de détection (p) d'une espèce sur des sites visités plusieurs fois. "
            "Corrige le biais de l'occupation naïve (proportion de sites avec au "
            "moins une détection) due à la détectabilité imparfaite."
        ),
        methodology=(
            "Vraisemblance : L(psi, p | y) = prod_i[psi*p^yi*(1-p)^(K-yi) + 1_{yi=0}*(1-psi)]. "
            "Estimation par optimisation Nelder-Mead (logit-link). "
            "Occupation naïve théorique : psi_naive = psi * (1 - (1-p)^K). "
            "Modèle de MacKenzie et al. (2002, Ecology)."
        ),
        ornithology=(
            "Outil indispensable pour les espèces discrètes ou rares : rapaces nocturnes "
            "(chevechette, effraie), pics, passereaux forestiers, limicoles à faible "
            "détection. Fondement des programmes de surveillance type STOC, où "
            "l'absence apparente n'implique pas l'absence réelle de l'espèce."
        ),
        inputs=["Historique de détection : matrice sites x visites (0/1)",
                "Optionnel : psi vraie et p vraie pour simulation",
                "Nombre de sites et de visites"],
        outputs=["psi estimée, p estimée, occupation naïve",
                 "Biais de l'occupation naïve",
                 "Graphique de comparaison psi vraie / estimée / naïve",
                 "Avertissement si convergence extrême"],
        importance=(
            "L'occupation corrigée pour la détection est devenue le standard international "
            "pour les inventaires et suivis d'espèces. Ignorer p produit des estimations "
            "fortement biaisées et des conclusions incorrectes sur l'état de conservation."
        ),
    ),
    dict(
        num="5.6", title="Distance sampling", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Estime la densité et l'abondance d'une population d'oiseaux à partir "
            "des distances d'observation sur des transects linéaires. Ajuste une "
            "fonction de détection demi-normale et calcule la largeur efficace "
            "du transect (ESW) et la densité."
        ),
        methodology=(
            "Fonction de détection demi-normale : g(x) = exp(-x² / 2*sigma²). "
            "ESW (Effective Strip Width) : integral de g(x) de 0 à W_max. "
            "Estimation du sigma par MLE. Densité : D = n / (2 * ESW * L * K), "
            "avec L = longueur totale de transect, K = nombre de transects. "
            "Fondé sur Buckland et al. (2001, Introduction to Distance Sampling)."
        ),
        ornithology=(
            "Méthode standard pour les comptages sur transect linéaire de passereaux, "
            "rapaces, larolimicoles ou grands échéiers. Utilisée dans le cadre "
            "des programmes STOC-EPS, des inventaires Natura 2000, et des "
            "études préalables aux éoliennes et aux projets d'aménagement."
        ),
        inputs=["Distances d'observation (m)",
                "Largeur maximale du transect W_max",
                "Longueur de transect",
                "Nombre de transects"],
        outputs=["Sigma estimé (portée de détection)",
                 "ESW (Effective Strip Width)",
                 "Densité estimée (ind/ha ou ind/km²)",
                 "Histogramme des distances + courbe g(x)"],
        importance=(
            "Le distance sampling est l'une des méthodes les plus rigoureuses pour "
            "estimer des densités absolues d'oiseaux en tenant compte de la "
            "détectabilité décroissante avec la distance. Enseigné dans les "
            "formations LPO, Naturevolution et les cursus écologie universitaires."
        ),
    ),
    dict(
        num="5.7", title="Lotka-Volterra", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Simule les interactions proie-prédateur selon le modèle classique de "
            "Lotka-Volterra. Visualise les oscillations cycliques des deux populations "
            "dans le temps et le portrait de phase (portrait cyclique dans l'espace proie-prédateur). "
            "Permet d'explorer la stabilité et le point d'équilibre."
        ),
        methodology=(
            "Système d'équations différentielles : "
            "dN/dt = r*N - a*N*P (proies), dP/dt = b*a*N*P - m*P (prédateurs). "
            "r = taux de reproduction des proies, a = taux de prédation, "
            "b = efficacité de conversion, m = mortalité des prédateurs. "
            "Intégration numérique par scipy.integrate.odeint."
        ),
        ornithology=(
            "Illustre la dynamique lemming-harfang des neiges, campagnol-busard, "
            "sauterelles-guifette. Fondement conceptuel pour comprendre les fluctuations "
            "annuelles des populations de rapaces liées aux cycles de rongeurs, "
            "et les décisions de conservation qui en découlent."
        ),
        inputs=["Populations initiales (proies N0, prédateurs P0)",
                "Paramètres r, a, b, m",
                "Durée de simulation"],
        outputs=["Courbes N(t) et P(t) superposées",
                 "Portrait de phase (cycle limite)",
                 "Point d'équilibre théorique"],
        importance=(
            "Le modèle de Lotka-Volterra est un pilier de l'écologie théorique. "
            "Il enseigne la notion d'interaction spécifique, de dynamique couplée "
            "et de cycle limite — concepts applicables à la gestion des rapaces "
            "et à la prévision des explosions de proies."
        ),
    ),
    dict(
        num="5.8", title="Séries temporelles de population", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Analyse une série temporelle d'abondance annuelle pour détecter une "
            "tendance significative. Applique le test non paramétrique de Mann-Kendall, "
            "une régression linéaire (OLS) et un lissage par moyenne mobile. "
            "Calcule le taux de déclin annuel et évalue la puissance statistique."
        ),
        methodology=(
            "Mann-Kendall : S = sum_{i&lt;j} sign(y_j - y_i). "
            "Statistique z = (S - sign(S)) / sqrt(Var(S)), Var(S) = n*(n-1)*(2n+5)/18. "
            "Régression OLS : pente = variation absolue annuelle, R² = part de variance "
            "expliquée. Lissage : moyenne mobile sur fenetre de k années (ajustable)."
        ),
        ornithology=(
            "Analyse des données STOC, BBS, Wetland Bird Survey, LPO. "
            "Détection des déclins ou reprises de populations (pinson, alouette, "
            "hirondelle rustique). Utilisé pour produire les listes rouges régionales "
            "et calibrer les alertes précoces de l'Observatoire des Oiseaux."
        ),
        inputs=["Série temporelle : année et effectif",
                "Ou paramètres de simulation (N0, r, bruit)",
                "Fenêtre de lissage (2-7 ans)"],
        outputs=["Courbe des effectifs + tendance lissée + droite OLS",
                 "Test Mann-Kendall : S, z, p-value, tendance",
                 "Pente OLS et R²",
                 "Taux de variation annuel simulé"],
        importance=(
            "La détection rigoureuse des tendances démographiques est la base des "
            "listes rouges UICN et des plans de conservation nationaux. Le test "
            "de Mann-Kendall est préféré car il ne suppose pas la normalité "
            "des résidus, fréquente dans les comptages d'oiseaux."
        ),
    ),
    dict(
        num="5.9", title="PVA et conservation", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Analyse de Viabilité des Populations (PVA) : simule stochastiquement "
            "l'évolution d'une population pendant T années sous incertitude "
            "environnementale, avec capacité de charge et seuil de quasi-extinction. "
            "Estime le risque d'extinction et la médiane de la taille finale."
        ),
        methodology=(
            "Croissance log-normale stochastique : N(t+1) = N(t) * exp(r_t), "
            "avec r_t ~ N(mu_r, sigma_r²) tronqué par la capacité de charge K. "
            "1000 réplications par défaut. Risque d'extinction = P(min(N) < seuil). "
            "Intervalles de confiance par percentiles (2.5% - 97.5%)."
        ),
        ornithology=(
            "Outil clé pour les plans de sauvegarde d'espèces menacées : vautours, "
            "bécasse des bois, outarde canepètire, grèbe à cou noir. "
            "Utilisé par le Comité Français de l'UICN pour classer les espèces "
            "et par les gestionnaires de réserves pour dimensionner les effectifs "
            "minimaux viables."
        ),
        inputs=["Population initiale N0",
                "Taux d'accroissement moyen et écart-type",
                "Capacité de charge K",
                "Seuil de quasi-extinction",
                "Durée et nombre de simulations"],
        outputs=["Trajectoires stochastiques (courbes enveloppe)",
                 "Risque d'extinction (probabilité)",
                 "Médiane et IC 95% de la taille finale",
                 "Distribution des effectifs finaux"],
        importance=(
            "La PVA est l'outil de référence international pour la gestion des "
            "espèces vulnérables. Elle intègre l'incertitude environnementale — "
            "inévitable en écologie — pour fournir des probabilités d'extinction "
            "utiles à la décision politique et de conservation."
        ),
    ),
    dict(
        num="5.10", title="Scénarios de gestion", tag="DYNAMIQUE DES POPULATIONS",
        description=(
            "Compare plusieurs scénarios d'action de conservation sur une population "
            "d'oiseaux simulée : augmentation de la survie adulte, de la survie "
            "juvénile, du succès reproducteur, réduction de la chasse, création "
            "d'une aire protégée. Visualise l'impact sur la trajectoire et le lambda."
        ),
        methodology=(
            "Chaque scénario modifie un ou plusieurs paramètres démographiques "
            "(r, K, mortalité) et relance la simulation stochastique. "
            "Comparaison par la médiane de la population à T années, "
            "le risque d'extinction et le lambda apparent. "
            "Permet de classer les actions par efficacité relative."
        ),
        ornithology=(
            "Directement applicable à la mise en place d'un plan national d'action "
            "(PNA) pour des espèces comme le gypaete barbu, le vautour percnoptère, "
            "le grand tétras, ou le bécasseau maubche. Compare les coûts-bénéfices "
            "de différents types d'intervention avant la décision politique."
        ),
        inputs=["Paramètres de base de la population",
                "Définition de 2 à 5 scénarios avec variation des paramètres",
                "Durée de projection"],
        outputs=["Courbes de population par scénario",
                 "Tableau comparatif : médiane finale, risque d'extinction, lambda",
                 "Meilleur scénario identifié automatiquement"],
        importance=(
            "La comparaison systématique de scénarios est fondamentale pour "
            "la décision en conservation. Elle évite d'investir des ressources "
            "limitées dans des actions dont l'impact démographique est faible, "
            "et oriente vers les leviers les plus efficaces."
        ),
    ),
]


# ── References ────────────────────────────────────────────────────────────────
REFERENCES = [
    "Buckland, S.T. et al. (2001). Introduction to Distance Sampling. Oxford University Press.",
    "Caswell, H. (2001). Matrix Population Models. Sinauer Associates, 2ème édition.",
    "MacKenzie, D.I. et al. (2002). Estimating site occupancy rates when detection "
    "probabilities are less than one. Ecology 83(8): 2248-2255.",
    "Mohr, C.O. (1947). Table of equivalent populations of North American small "
    "mammals. American Midland Naturalist 37(1): 223-249.",
    "Mann, H.B. & Kendall, M.G. — Mann-Kendall Trend Test. Non-parametric test "
    "for detecting monotonic trends in time series.",
    "Lincoln, F.C. (1930). Calculating Waterfowl Abundance on the Basis of Banding "
    "Returns. US Department of Agriculture Circular 118: 1-4.",
    "Verhulst, P.F. (1838). Notice sur la loi que la population suit dans son "
    "accroissement. Correspondance Mathématique et Physique 10: 113-121.",
    "Silverman, B.W. (1986). Density Estimation for Statistics and Data Analysis. "
    "Chapman and Hall, Londres.",
    "Shannon, C.E. & Weaver, W. (1949). The Mathematical Theory of Communication. "
    "University of Illinois Press.",
    "Lotka, A.J. (1925). Elements of Physical Biology. Williams & Wilkins, Baltimore.",
    "Volterra, V. (1926). Fluctuations in the Abundance of a Species Considered "
    "Mathematically. Nature 118: 558-560.",
]


# ── Main builder ──────────────────────────────────────────────────────────────
def build_pdf() -> None:
    s = make_styles()
    story: list = []

    # Cover
    cover_page(story, s)

    # TOC
    table_of_contents(story, s)

    # Introduction + Architecture + Guide
    introduction(story, s)

    # ── Biostatistique ────────────────────────────────────────────────────────
    story += section_banner("Section 4 — Biostatistique (8 modules)", GREEN_DARK, s, "tag_bio")

    for i, mod in enumerate(BIOSTAT_MODULES):
        story += module_card(
            num=mod["num"], title=mod["title"], tag=mod["tag"],
            tag_color=BLUE, **{k: mod[k] for k in
                                ("description", "methodology", "ornithology",
                                 "inputs", "outputs", "importance")}, s=s,
        )
        if i < len(BIOSTAT_MODULES) - 1 and i % 2 == 1:
            story.append(PageBreak())

    story.append(PageBreak())

    # ── Dynamique des populations ─────────────────────────────────────────────
    story += section_banner("Section 5 — Dynamique des populations (10 modules)", HexColor("#145c3a"), s, "tag_dyn")

    for i, mod in enumerate(DYNPOP_MODULES):
        story += module_card(
            num=mod["num"], title=mod["title"], tag=mod["tag"],
            tag_color=GREEN_DARK, **{k: mod[k] for k in
                                      ("description", "methodology", "ornithology",
                                       "inputs", "outputs", "importance")}, s=s,
        )
        if i < len(DYNPOP_MODULES) - 1 and i % 2 == 1:
            story.append(PageBreak())

    story.append(PageBreak())

    # ── Références ────────────────────────────────────────────────────────────
    story.append(Paragraph("6. Références bibliographiques", s["h1"]))
    story.append(hr())
    story.append(spacer(0.2))
    for ref in REFERENCES:
        story.append(Paragraph(ref, s["ref"]))
    story.append(spacer(0.5))

    # Pied de page de fin
    fin_data = [[Paragraph(
        "<b>ORNI-LAB</b> — Développé par <b>Abdoulaye Diop</b> · "
        "Laboratoire Interactif de Modélisation Ornithologique · Mai 2026",
        ParagraphStyle("fin", parent=s["caption"], textColor=white, fontSize=10)
    )]]
    fin_t = Table(fin_data, colWidths=[W - 4 * cm])
    fin_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), GREEN_DARK),
        ("LEFTPADDING",   (0, 0), (-1, -1), 20),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(fin_t)

    # Build
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2 * cm,
        bottomMargin=2.2 * cm,
        title="ORNI-LAB — Documentation complète",
        author="Abdoulaye Diop",
        subject="Laboratoire interactif de modélisation ornithologique",
    )
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"\n Documentation générée : {OUT.resolve()}\n")


if __name__ == "__main__":
    build_pdf()
