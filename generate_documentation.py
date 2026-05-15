#!/usr/bin/env python3
"""Génère la documentation PDF complète et détaillée d'ORNI-LAB — Abdoulaye Diop."""

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
GREEN_MID   = HexColor("#145c3a")
BLUE        = HexColor("#4dabf7")
BLUE_DARK   = HexColor("#1971c2")
BLUE_BG     = HexColor("#eaf5ff")
DARK        = HexColor("#10161f")
TEXT        = HexColor("#1e2a38")
MUTED       = HexColor("#6b7a8d")
PANEL       = HexColor("#f4f7f9")
PANEL2      = HexColor("#eef2f7")
CORAL       = HexColor("#e05252")
CORAL_BG    = HexColor("#fff0f0")
YELLOW_BG   = HexColor("#fffbea")
YELLOW_ACC  = HexColor("#c47f00")
PURPLE      = HexColor("#7048e8")
PURPLE_BG   = HexColor("#f3f0ff")
W, H        = A4

OUT = Path("ORNI-LAB_Documentation.pdf")
TODAY = datetime.date.today().strftime("%d %B %Y")


# ══════════════════════════════════════════════════════════════════════════════
# STYLES
# ══════════════════════════════════════════════════════════════════════════════
def make_styles() -> dict:
    base = getSampleStyleSheet()

    def ps(name, **kw) -> ParagraphStyle:
        parent = kw.pop("parent", "Normal")
        return ParagraphStyle(name, parent=base[parent], **kw)

    s: dict = {}
    s["cover_title"]  = ps("cover_title",  fontSize=48, leading=56, textColor=white,
                            alignment=TA_LEFT, fontName="Helvetica-Bold")
    s["cover_sub"]    = ps("cover_sub",    fontSize=18, leading=26,
                            textColor=HexColor("#c8e6d9"), alignment=TA_LEFT, fontName="Helvetica")
    s["cover_meta"]   = ps("cover_meta",   fontSize=11, leading=17,
                            textColor=HexColor("#a0c4b5"), alignment=TA_LEFT, fontName="Helvetica")
    s["cover_author"] = ps("cover_author", fontSize=13, leading=20,
                            textColor=white, alignment=TA_LEFT, fontName="Helvetica-Bold")

    s["h_part"]  = ps("h_part",  fontSize=20, leading=26, textColor=white,
                       fontName="Helvetica-Bold", alignment=TA_LEFT, spaceBefore=0, spaceAfter=4)
    s["h1"]      = ps("h1",      fontSize=16, leading=22, textColor=GREEN_DARK,
                       fontName="Helvetica-Bold", spaceBefore=16, spaceAfter=5)
    s["h2"]      = ps("h2",      fontSize=13, leading=18, textColor=TEXT,
                       fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=3)
    s["h3"]      = ps("h3",      fontSize=11, leading=16, textColor=MUTED,
                       fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=2)
    s["h4"]      = ps("h4",      fontSize=10, leading=14, textColor=BLUE_DARK,
                       fontName="Helvetica-Bold", spaceBefore=4, spaceAfter=2)
    s["body"]    = ps("body",    fontSize=10, leading=15, textColor=TEXT,
                       alignment=TA_JUSTIFY, spaceAfter=4, fontName="Helvetica")
    s["body_l"]  = ps("body_l",  fontSize=10, leading=15, textColor=TEXT,
                       alignment=TA_LEFT, spaceAfter=4, fontName="Helvetica")
    s["bullet"]  = ps("bullet",  fontSize=10, leading=14, textColor=TEXT,
                       leftIndent=14, spaceAfter=2, fontName="Helvetica")
    s["bullet2"] = ps("bullet2", fontSize=9.5, leading=13, textColor=MUTED,
                       leftIndent=28, spaceAfter=2, fontName="Helvetica")
    s["caption"] = ps("caption", fontSize=8.5, leading=12, textColor=MUTED,
                       fontName="Helvetica-Oblique", alignment=TA_CENTER)
    s["formula"] = ps("formula", fontSize=9, leading=13, textColor=HexColor("#1a3450"),
                       fontName="Courier", leftIndent=18, spaceAfter=3,
                       backColor=HexColor("#f0f4f8"), borderPadding=4)
    s["code"]    = ps("code",    fontSize=8.5, leading=12, textColor=HexColor("#2d3748"),
                       fontName="Courier", leftIndent=12, spaceAfter=3)
    s["ref"]     = ps("ref",     fontSize=9, leading=13, textColor=MUTED,
                       fontName="Helvetica", leftIndent=14, spaceAfter=4,
                       firstLineIndent=-14)
    s["toc_h"]   = ps("toc_h",   fontSize=11, leading=16, textColor=GREEN_DARK,
                       fontName="Helvetica-Bold", leftIndent=0, spaceAfter=2)
    s["toc_m"]   = ps("toc_m",   fontSize=10, leading=14, textColor=TEXT,
                       fontName="Helvetica", leftIndent=20, spaceAfter=1)
    s["toc_s"]   = ps("toc_s",   fontSize=9.5, leading=13, textColor=MUTED,
                       fontName="Helvetica", leftIndent=36, spaceAfter=1)
    s["gloss_t"] = ps("gloss_t", fontSize=10, leading=14, textColor=GREEN_DARK,
                       fontName="Helvetica-Bold", spaceAfter=1)
    s["gloss_b"] = ps("gloss_b", fontSize=9.5, leading=13, textColor=TEXT,
                       fontName="Helvetica", leftIndent=12, spaceAfter=5,
                       alignment=TA_JUSTIFY)
    s["warn"]    = ps("warn",    fontSize=9.5, leading=14, textColor=HexColor("#7c3d00"),
                       fontName="Helvetica", leftIndent=10, spaceAfter=2)
    s["note"]    = ps("note",    fontSize=9.5, leading=14, textColor=HexColor("#1a3450"),
                       fontName="Helvetica", leftIndent=10, spaceAfter=2)
    return s


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def spacer(h: float = 0.3) -> Spacer:
    return Spacer(1, h * cm)


def hr(color=GREEN, thickness=1.0) -> HRFlowable:
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceAfter=4, spaceBefore=2)


def hr_thin() -> HRFlowable:
    return HRFlowable(width="100%", thickness=0.4, color=HexColor("#d0d8e4"),
                      spaceAfter=3, spaceBefore=3)


def section_banner(label: str, color: HexColor, s: dict) -> list:
    data = [[Paragraph(label, s["h_part"])]]
    t = Table(data, colWidths=[W - 4.4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), color),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LEFTPADDING",   (0, 0), (-1, -1), 18),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 18),
        ("ROUNDEDCORNERS", [8]),
    ]))
    return [spacer(0.4), t, spacer(0.5)]


def colored_box(text: str, s: dict, bg=BLUE_BG, border=BLUE,
                style_key="body") -> Table:
    data = [[Paragraph(text, s[style_key])]]
    t = Table(data, colWidths=[W - 4.4 * cm])
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


def warning_box(text: str, s: dict) -> Table:
    return colored_box("⚠ " + text, s, bg=YELLOW_BG, border=YELLOW_ACC, style_key="warn")


def note_box(text: str, s: dict) -> Table:
    return colored_box("ℹ " + text, s, bg=BLUE_BG, border=BLUE, style_key="note")


def formula_block(formulas: list[str], s: dict) -> list:
    items = []
    for f in formulas:
        items.append(Paragraph(f, s["formula"]))
    return items


def bullet_list(items: list[str], s: dict, indent=0) -> list:
    key = "bullet2" if indent else "bullet"
    return [Paragraph(f"• {item}", s[key]) for item in items]


def two_col_table(left_title: str, right_title: str,
                  left_items: list[str], right_items: list[str],
                  s: dict, bg_header=PANEL) -> Table:
    col_w = (W - 4.4 * cm) / 2
    in_items  = [Paragraph(f"• {x}", s["bullet"]) for x in left_items]
    out_items = [Paragraph(f"• {x}", s["bullet"]) for x in right_items]
    data = [
        [Paragraph(f"<b>{left_title}</b>", s["h3"]),
         Paragraph(f"<b>{right_title}</b>", s["h3"])],
        [in_items, out_items],
    ]
    t = Table(data, colWidths=[col_w, col_w])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), bg_header),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("LINEABOVE",     (0, 0), (-1, 0), 0.5, HexColor("#d0d8e4")),
        ("LINEBELOW",     (0, -1), (-1, -1), 0.5, HexColor("#d0d8e4")),
        ("LINEBETWEEN",   (0, 0), (-1, -1), 0.5, HexColor("#d0d8e4")),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def generic_table(headers: list[str], rows: list[list[str]], s: dict,
                  col_widths: list[float] | None = None) -> Table:
    total_w = W - 4.4 * cm
    n = len(headers)
    if col_widths is None:
        col_widths = [total_w / n] * n
    data = [[Paragraph(f"<b>{h}</b>", s["h3"]) for h in headers]]
    for row in rows:
        data.append([Paragraph(cell, s["body_l"]) for cell in row])
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), GREEN_DARK),
        ("TEXTCOLOR",     (0, 0), (-1, 0), white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, PANEL]),
        ("LINEBELOW",     (0, 0), (-1, -1), 0.3, HexColor("#c8d6e0")),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    return t


# ══════════════════════════════════════════════════════════════════════════════
# PAGE DECORATIONS
# ══════════════════════════════════════════════════════════════════════════════
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(W - 2 * cm, 1.3 * cm, f"Page {doc.page}")
    canvas.drawString(2 * cm, 1.3 * cm, "ORNI-LAB — Documentation Technique © Abdoulaye Diop, 2026")
    canvas.setStrokeColor(HexColor("#d0d8e4"))
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, 1.6 * cm, W - 2 * cm, 1.6 * cm)
    canvas.restoreState()


# ══════════════════════════════════════════════════════════════════════════════
# MODULE CARD (enrichi)
# ══════════════════════════════════════════════════════════════════════════════
def module_card(
    num: str,
    title: str,
    tag: str,
    tag_color: HexColor,
    description: str,
    methodology: str,
    formulas: list[str],
    algorithm: list[str],
    ornithology: str,
    inputs: list[str],
    outputs: list[str],
    interpretation: str,
    pitfalls: list[str],
    importance: str,
    key_ref: str,
    s: dict,
) -> list:
    story = []

    # ── En-tête
    header_data = [[
        Paragraph(f"<b>{num}. {title}</b>", s["h1"]),
        Paragraph(tag, ParagraphStyle(
            "_tag", parent=s["body"], textColor=tag_color,
            fontName="Helvetica-Bold", fontSize=9, alignment=TA_RIGHT)),
    ]]
    ht = Table(header_data, colWidths=[W - 7 * cm, 2.5 * cm])
    ht.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(KeepTogether([ht, hr()]))

    # ── Description
    story.append(Paragraph("<b>Description</b>", s["h2"]))
    story.append(Paragraph(description, s["body"]))

    # ── Fondements méthodologiques
    story.append(Paragraph("<b>Fondements méthodologiques</b>", s["h2"]))
    story.append(Paragraph(methodology, s["body"]))
    if formulas:
        story.append(spacer(0.1))
        story.extend(formula_block(formulas, s))

    # ── Algorithme
    if algorithm:
        story.append(Paragraph("<b>Algorithme pas à pas</b>", s["h2"]))
        for step in algorithm:
            story.append(Paragraph(f"• {step}", s["bullet"]))

    # ── Application ornithologique
    story.append(Paragraph("<b>Application ornithologique</b>", s["h2"]))
    story.append(colored_box(ornithology, s, bg=GREEN_BG, border=GREEN))
    story.append(spacer(0.15))

    # ── Entrées / Sorties
    story.append(two_col_table("Paramètres d'entrée", "Sorties et résultats",
                               inputs, outputs, s))
    story.append(spacer(0.15))

    # ── Interprétation
    story.append(Paragraph("<b>Comment interpréter les résultats</b>", s["h2"]))
    story.append(note_box(interpretation, s))
    story.append(spacer(0.1))

    # ── Pièges fréquents
    if pitfalls:
        story.append(Paragraph("<b>Erreurs fréquentes à éviter</b>", s["h2"]))
        for p in pitfalls:
            story.append(warning_box(p, s))
            story.append(spacer(0.05))

    # ── Importance
    story.append(Paragraph("<b>Importance en écologie et conservation</b>", s["h2"]))
    story.append(colored_box(importance, s, bg=YELLOW_BG, border=YELLOW_ACC))
    story.append(spacer(0.1))

    # ── Référence clé
    if key_ref:
        story.append(Paragraph("<b>Référence clé</b>", s["h3"]))
        story.append(Paragraph(key_ref, s["ref"]))

    story.append(spacer(0.5))
    return story


# ══════════════════════════════════════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════════════════════════════════════
def cover_page(story: list, s: dict) -> None:
    top_data = [[Paragraph("ORNI-LAB", s["cover_title"])]]
    top = Table(top_data, colWidths=[W - 4 * cm], rowHeights=[6.5 * cm])
    top.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), GREEN_DARK),
        ("LEFTPADDING",   (0, 0), (-1, -1), 28),
        ("TOPPADDING",    (0, 0), (-1, -1), 28),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
        ("ROUNDEDCORNERS", [10]),
    ]))
    story.append(spacer(1.8))
    story.append(top)
    story.append(spacer(0.3))

    sub_data = [[Paragraph("Laboratoire Interactif de Modélisation Ornithologique", s["cover_sub"])]]
    sub_t = Table(sub_data, colWidths=[W - 4 * cm])
    sub_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), HexColor("#1a5c42")),
        ("LEFTPADDING",   (0, 0), (-1, -1), 28),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(sub_t)
    story.append(spacer(0.3))

    bird_data = [[Paragraph("🦅  🐦  🦉  🦢  🦆  🦩  🐧  🦜", s["cover_sub"])]]
    bird_t = Table(bird_data, colWidths=[W - 4 * cm])
    bird_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), HexColor("#12402d")),
        ("LEFTPADDING",   (0, 0), (-1, -1), 28),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(bird_t)
    story.append(spacer(2.5))

    meta_rows = [
        ("Auteur",           "Abdoulaye Diop — Bioinformaticien · Biomathématicien"),
        ("Spécialisation",   "Analyse & modélisation des systèmes biologiques · Écologie quantitative"),
        ("Contact",          "dioplayes@gmail.com · +221 77 113 07 48"),
        ("Version",          "2.0 — Mai 2026"),
        ("Modules",          "18 modules interactifs répartis en 2 sections"),
        ("Sections",         "Biostatistique (8 modules) · Dynamique des populations (10 modules)"),
        ("Audience",         "Licence 3 · Master 1 & 2 · Doctorat · Formation professionnelle"),
        ("Technologies",     "Python 3.11 · Streamlit · SciPy · Statsmodels · Plotly · ReportLab"),
        ("Date de génération", TODAY),
    ]
    for key, val in meta_rows:
        row_data = [[
            Paragraph(f"<b>{key}</b>", s["body"]),
            Paragraph(val, s["body"]),
        ]]
        row_t = Table(row_data, colWidths=[3.8 * cm, W - 9 * cm])
        row_t.setStyle(TableStyle([
            ("LEFTPADDING",   (0, 0), (-1, -1), 6),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LINEBELOW",     (0, 0), (-1, -1), 0.3, HexColor("#d0d8e4")),
        ]))
        story.append(row_t)

    story.append(PageBreak())


# ══════════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ══════════════════════════════════════════════════════════════════════════════
def table_of_contents(story: list, s: dict) -> None:
    story.append(Paragraph("Table des matières", s["h1"]))
    story.append(hr())
    story.append(spacer(0.3))

    entries = [
        ("1.", "Introduction et philosophie pédagogique", None, "h"),
        ("2.", "Architecture technique", None, "h"),
        ("3.", "Installation et configuration", None, "h"),
        ("4.", "Guide d'utilisation détaillé", None, "h"),
        ("",   "4.1  Démarrage et navigation", None, "m"),
        ("",   "4.2  Chargement de données CSV", None, "m"),
        ("",   "4.3  Mode Étudiant / Enseignant", None, "m"),
        ("",   "4.4  Exports PDF et CSV", None, "m"),
        ("5.", "Section Biostatistique — 8 modules", None, "h"),
        ("",   "5.1  Statistiques descriptives", "BIOSTAT", "m"),
        ("",   "5.2  Analyse CSV guidée", "BIOSTAT", "m"),
        ("",   "5.3  Corrélation et régression", "BIOSTAT", "m"),
        ("",   "5.4  Tests statistiques", "BIOSTAT", "m"),
        ("",   "5.5  GLM pour données de comptage", "BIOSTAT", "m"),
        ("",   "5.6  Modèle mixte — LMM", "BIOSTAT", "m"),
        ("",   "5.7  Domaine vital — MCP", "BIOSTAT", "m"),
        ("",   "5.8  Domaine vital — KDE", "BIOSTAT", "m"),
        ("6.", "Section Dynamique des populations — 10 modules", None, "h"),
        ("",   "6.1  Richesse spécifique et diversité", "DYN", "m"),
        ("",   "6.2  Croissance exponentielle et logistique", "DYN", "m"),
        ("",   "6.3  Matrices de Leslie", "DYN", "m"),
        ("",   "6.4  Capture-Marquage-Recapture", "DYN", "m"),
        ("",   "6.5  Modèles d'occupation", "DYN", "m"),
        ("",   "6.6  Distance sampling", "DYN", "m"),
        ("",   "6.7  Lotka-Volterra", "DYN", "m"),
        ("",   "6.8  Séries temporelles de population", "DYN", "m"),
        ("",   "6.9  PVA et conservation", "DYN", "m"),
        ("",   "6.10 Scénarios de gestion", "DYN", "m"),
        ("7.", "Annexes techniques", None, "h"),
        ("",   "7.1  Dépendances Python et versions", None, "m"),
        ("",   "7.2  Sécurité et robustesse", None, "m"),
        ("",   "7.3  Erreurs fréquentes et solutions", None, "m"),
        ("8.", "Glossaire des termes statistiques", None, "h"),
        ("9.", "Références bibliographiques", None, "h"),
    ]

    for num, title, tag, level in entries:
        if level == "h":
            color = TEXT if not tag else (BLUE_DARK if tag == "BIOSTAT" else GREEN_DARK)
            style = ParagraphStyle(f"_toc_h_{title[:8]}", parent=s["body"],
                                   leftIndent=0, textColor=color,
                                   fontName="Helvetica-Bold", spaceAfter=3, fontSize=11)
            text = f"{num}  {title}" if num else title
        elif level == "m":
            color = BLUE_DARK if tag == "BIOSTAT" else (GREEN_DARK if tag == "DYN" else TEXT)
            style = ParagraphStyle(f"_toc_m_{title[:8]}", parent=s["body"],
                                   leftIndent=20, textColor=color,
                                   fontName="Helvetica", spaceAfter=1.5, fontSize=10)
            text = title
        else:
            style = ParagraphStyle(f"_toc_s_{title[:8]}", parent=s["body"],
                                   leftIndent=36, textColor=MUTED,
                                   fontName="Helvetica", spaceAfter=1, fontSize=9.5)
            text = title
        story.append(Paragraph(text, style))

    story.append(PageBreak())


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1–4 : INTRODUCTION, ARCHITECTURE, INSTALLATION, GUIDE
# ══════════════════════════════════════════════════════════════════════════════
def intro_and_guide(story: list, s: dict) -> None:

    # ── 1. Introduction ───────────────────────────────────────────────────────
    story.append(Paragraph("1. Introduction et philosophie pédagogique", s["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "ORNI-LAB est un laboratoire interactif de modélisation ornithologique développé "
        "pour l'enseignement universitaire en écologie des populations et en biologie de la "
        "conservation. Conçu comme un outil pédagogique à part entière, il offre une "
        "interface web intuitive permettant aux étudiants et aux enseignants d'explorer, "
        "de visualiser et d'analyser des données ornithologiques sans prérequis en "
        "programmation.", s["body"]))
    story.append(spacer(0.15))
    story.append(Paragraph(
        "L'application repose sur cinq principes pédagogiques fondamentaux :", s["body"]))
    for item in [
        "<b>Dualité simulation / terrain</b> — chaque module fonctionne en mode simulation "
        "(paramètres ajustables, données générées) ET en mode données réelles (import CSV). "
        "Cette dualité permet de passer de l'abstraction mathématique à la pratique de terrain.",
        "<b>Progression de l'interprétation</b> — les résultats sont accompagnés "
        "d'interprétations automatiques en langage naturel, évitant la surcharge cognitive "
        "des étudiants débutants.",
        "<b>Mode Enseignant intégré</b> — formules mathématiques LaTeX, notes pédagogiques "
        "avancées et erreurs fréquentes apparaissent en mode Enseignant, enrichissant le "
        "cours magistral sans alourdir l'interface étudiant.",
        "<b>Reproductibilité</b> — chaque simulation utilise une graine aléatoire fixable, "
        "garantissant des résultats identiques entre sessions de TP.",
        "<b>Export immédiat</b> — résumés PDF et données CSV exportables depuis chaque "
        "module pour prolonger l'analyse dans R, Python ou Excel.",
    ]:
        story.append(Paragraph(f"• {item}", s["bullet"]))

    story.append(spacer(0.25))
    story.append(Paragraph(
        "ORNI-LAB couvre deux grandes disciplines de l'ornithologie quantitative : "
        "la biostatistique (tests d'hypothèses, régression, modèles mixtes, domaine vital) "
        "et la dynamique des populations (croissance, structures d'âge, CMR, occupation, "
        "distance sampling, PVA). L'ensemble constitue un cursus complet du L3 au M2, "
        "adaptable à des publics de biologistes, d'écologues ou de gestionnaires "
        "d'espaces naturels.", s["body"]))

    story.append(spacer(0.4))

    # ── 2. Architecture ───────────────────────────────────────────────────────
    story.append(Paragraph("2. Architecture technique", s["h1"]))
    story.append(hr())
    story.append(Paragraph(
        "L'application est construite en Python 3.11 avec le framework Streamlit. "
        "L'architecture suit un patron MVC simplifié où chaque module est un renderer "
        "indépendant recevant un contexte partagé.", s["body"]))

    story.append(spacer(0.2))
    story.append(generic_table(
        ["Couche", "Rôle", "Fichiers principaux"],
        [
            ["Interface",       "Navigation, session state, mise en page",   "app/main.py, app/config.py"],
            ["Modules",         "18 simulateurs/analyseurs spécialisés",     "modules/*.py"],
            ["UI partagée",     "Composants visuels réutilisables",          "utils/ui.py"],
            ["Export",          "Génération PDF (ReportLab) et CSV",        "core/export.py"],
            ["Simulations",     "Moteur PVA stochastique",                   "simulations/pva_engine.py"],
            ["Données",         "Valeurs par défaut et datasets d'exemple",  "data/examples.py"],
            ["Tests",           "Suite de 28 tests unitaires (pytest)",      "tests/test_models.py"],
        ],
        s,
        col_widths=[3 * cm, 5.5 * cm, 6 * cm],
    ))

    story.append(spacer(0.25))
    story.append(Paragraph("<b>Pattern render(context)</b>", s["h2"]))
    story.append(Paragraph(
        "Chaque module expose une unique fonction render(context: dict). "
        "Le dictionnaire context contient les données partagées par tous les modules :", s["body"]))
    for item in [
        "<b>context['data']</b> — DataFrame pandas chargé depuis le CSV sidebar (None si simulation)",
        "<b>context['numeric_columns']</b> — liste des colonnes numériques détectées",
        "<b>context['categorical_columns']</b> — liste des colonnes catégorielles",
        "<b>context['teacher_mode']</b> — booléen activant les notes pédagogiques",
    ]:
        story.append(Paragraph(f"• {item}", s["bullet"]))

    story.append(spacer(0.2))
    story.append(Paragraph("<b>Gestion d'erreurs</b>", s["h2"]))
    story.append(Paragraph(
        "Depuis la version 2.0, app/main.py encapsule chaque appel renderer() dans un "
        "bloc try/except. Toute exception non gérée dans un module s'affiche comme un "
        "message d'erreur avec traceback complet dans un expander, sans planter "
        "l'application globale.", s["body"]))

    story.append(spacer(0.4))

    # ── 3. Installation ───────────────────────────────────────────────────────
    story.append(Paragraph("3. Installation et configuration", s["h1"]))
    story.append(hr())

    story.append(Paragraph("<b>Prérequis système</b>", s["h2"]))
    for item in [
        "Python 3.10 ou supérieur (recommandé : 3.11)",
        "pip ou conda (gestionnaire de paquets)",
        "Système d'exploitation : Windows 10/11, macOS 12+, ou Linux Ubuntu 20.04+",
        "RAM : 4 Go minimum, 8 Go recommandés pour les simulations PVA intensives",
        "Espace disque : ~500 Mo pour l'environnement virtuel complet",
    ]:
        story.append(Paragraph(f"• {item}", s["bullet"]))

    story.append(spacer(0.2))
    story.append(Paragraph("<b>Installation des dépendances</b>", s["h2"]))
    story.append(Paragraph(
        "Depuis le répertoire racine du projet, exécuter :", s["body"]))
    for line in [
        "pip install streamlit>=1.40",
        "pip install numpy scipy pandas statsmodels",
        "pip install plotly reportlab",
    ]:
        story.append(Paragraph(line, s["code"]))

    story.append(spacer(0.2))
    story.append(Paragraph("<b>Lancement de l'application</b>", s["h2"]))
    story.append(Paragraph(
        "Trois méthodes de lancement sont disponibles :", s["body"]))
    for item in [
        "<b>Raccourci bureau</b> — double-clic sur ORNI-LAB.lnk (créé par installer_raccourci.ps1)",
        "<b>Batch Windows</b> — double-clic sur ORNI-LAB.bat (libère le port 8501, lance Streamlit, "
        "ouvre le navigateur automatiquement)",
        "<b>Lancement silencieux</b> — double-clic sur ORNI-LAB_silencieux.vbs (sans fenêtre "
        "CMD visible, idéal pour une utilisation en salle TP)",
        "<b>Ligne de commande</b> — python -m streamlit run app/main.py --server.port 8501",
    ]:
        story.append(Paragraph(f"• {item}", s["bullet"]))

    story.append(spacer(0.2))
    story.append(note_box(
        "L'application est accessible à l'adresse http://localhost:8501 dans tout "
        "navigateur web moderne. Aucune connexion internet n'est requise après installation.", s))

    story.append(spacer(0.4))

    # ── 4. Guide d'utilisation ────────────────────────────────────────────────
    story.append(Paragraph("4. Guide d'utilisation détaillé", s["h1"]))
    story.append(hr())

    story.append(Paragraph("4.1  Démarrage et navigation", s["h2"]))
    story.append(Paragraph(
        "Au démarrage, la page d'accueil présente deux cartes de section cliquables : "
        "Biostatistique (bleu) et Dynamique des populations (vert). Un clic sur une carte "
        "ouvre la section et affiche la liste des modules dans la sidebar gauche. "
        "Le bouton ← Accueil permet de revenir à tout moment à la page principale.", s["body"]))

    story.append(spacer(0.15))
    story.append(Paragraph("4.2  Chargement de données CSV", s["h2"]))
    story.append(Paragraph(
        "La zone de chargement CSV se trouve en haut de la sidebar. L'application "
        "supporte les encodages UTF-8, UTF-8 BOM, Latin-1, CP1252 et UTF-16. "
        "Le séparateur (virgule, point-virgule, tabulation) est détecté automatiquement "
        "via csv.Sniffer. Une fois chargé, le fichier est utilisé par tous les modules "
        "simultanément.", s["body"]))
    for item in [
        "Les colonnes avec ≥ 70% de valeurs numériques sont classées comme numériques",
        "Les virgules décimales sont converties automatiquement en points",
        "Les valeurs manquantes (NA, N/A, null, -, ?) sont normalisées en NaN",
        "Chaque module propose un bouton de téléchargement du template CSV adapté",
    ]:
        story.append(Paragraph(f"• {item}", s["bullet"]))

    story.append(spacer(0.15))
    story.append(Paragraph("4.3  Mode Étudiant / Enseignant", s["h2"]))
    story.append(Paragraph(
        "Le mode s'active depuis la sidebar avec le bouton bascule. "
        "En mode Étudiant (défaut) : résultats, graphiques et interprétations automatiques. "
        "En mode Enseignant : s'ajoutent les formules mathématiques, les notes "
        "pédagogiques sur les choix méthodologiques, et les pièges classiques "
        "des étudiants mis en évidence.", s["body"]))

    story.append(spacer(0.15))
    story.append(Paragraph("4.4  Exports PDF et CSV", s["h2"]))
    story.append(Paragraph(
        "Chaque module propose en bas de page un ou plusieurs boutons d'export. "
        "Le PDF contient un résumé des résultats avec interprétation, généré par "
        "ReportLab (core/export.py). Le CSV exporte les données utilisées "
        "(simulées ou importées) pour une analyse complémentaire.", s["body"]))

    story.append(PageBreak())


# ══════════════════════════════════════════════════════════════════════════════
# IMPORT DES DONNÉES DE MODULES ET DES FONCTIONS DE BUILD
# ══════════════════════════════════════════════════════════════════════════════
from _doc_biostat import BIOSTAT_MODULES
from _doc_dynpop  import DYNPOP_MODULES
from _doc_build   import (
    annexes_techniques, glossaire, references_section, closing_banner,
)


# ══════════════════════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════
def build_pdf() -> None:
    s = make_styles()
    story: list = []

    # ── Couverture ────────────────────────────────────────────────────────────
    cover_page(story, s)

    # ── Table des matières ────────────────────────────────────────────────────
    table_of_contents(story, s)

    # ── Sections 1-4 : Introduction, architecture, installation, guide ────────
    intro_and_guide(story, s)

    # ── Section 5 : Biostatistique ────────────────────────────────────────────
    story += section_banner("Section 5 — Biostatistique (8 modules)", GREEN_DARK, s)

    for i, mod in enumerate(BIOSTAT_MODULES):
        story += module_card(
            num=mod["num"], title=mod["title"], tag=mod["tag"],
            tag_color=BLUE,
            description=mod["description"],
            methodology=mod["methodology"],
            formulas=mod["formulas"],
            algorithm=mod["algorithm"],
            ornithology=mod["ornithology"],
            inputs=mod["inputs"],
            outputs=mod["outputs"],
            interpretation=mod["interpretation"],
            pitfalls=mod["pitfalls"],
            importance=mod["importance"],
            key_ref=mod["key_ref"],
            s=s,
        )
        if i < len(BIOSTAT_MODULES) - 1 and i % 2 == 1:
            story.append(PageBreak())

    story.append(PageBreak())

    # ── Section 6 : Dynamique des populations ────────────────────────────────
    story += section_banner("Section 6 — Dynamique des populations (10 modules)", GREEN_MID, s)

    for i, mod in enumerate(DYNPOP_MODULES):
        story += module_card(
            num=mod["num"], title=mod["title"], tag=mod["tag"],
            tag_color=GREEN_DARK,
            description=mod["description"],
            methodology=mod["methodology"],
            formulas=mod["formulas"],
            algorithm=mod["algorithm"],
            ornithology=mod["ornithology"],
            inputs=mod["inputs"],
            outputs=mod["outputs"],
            interpretation=mod["interpretation"],
            pitfalls=mod["pitfalls"],
            importance=mod["importance"],
            key_ref=mod["key_ref"],
            s=s,
        )
        if i < len(DYNPOP_MODULES) - 1 and i % 2 == 1:
            story.append(PageBreak())

    story.append(PageBreak())

    # ── Section 7 : Annexes techniques ───────────────────────────────────────
    annexes_techniques(
        story, s,
        hr=hr, spacer=spacer,
        colored_box=colored_box, warning_box=warning_box, note_box=note_box,
        generic_table=generic_table, section_banner=section_banner,
        GREEN_DARK=GREEN_DARK, BLUE=BLUE, PANEL=PANEL,
        CORAL_BG=CORAL_BG, CORAL=CORAL,
    )

    # ── Section 8 : Glossaire ─────────────────────────────────────────────────
    glossaire(story, s, hr=hr, spacer=spacer,
               section_banner=section_banner, GREEN_DARK=GREEN_DARK)
    story.append(PageBreak())

    # ── Section 9 : Références ────────────────────────────────────────────────
    references_section(story, s, hr=hr, spacer=spacer,
                        section_banner=section_banner)

    # ── Pied de page final ────────────────────────────────────────────────────
    closing_banner(story, s, spacer=spacer, GREEN_DARK=GREEN_DARK, white=white)

    # ── Construction du PDF ───────────────────────────────────────────────────
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2.0 * cm,
        bottomMargin=2.2 * cm,
        title="ORNI-LAB — Documentation Technique Complète",
        author="Abdoulaye Diop",
        subject="Laboratoire interactif de modélisation ornithologique — 18 modules",
    )
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"\n  Documentation générée : {OUT.resolve()}\n")


if __name__ == "__main__":
    build_pdf()
