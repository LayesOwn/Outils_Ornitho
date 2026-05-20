# Guide d'installation et de prise en main — ORNI-LAB

## 1. Prérequis

| Logiciel | Version minimale | Vérification |
|----------|-----------------|--------------|
| Python | 3.10 | `python --version` |
| pip | inclus avec Python | `pip --version` |
| Navigateur web | Chrome, Firefox, Edge | — |

> Python peut être téléchargé sur **python.org**. Cocher "Add Python to PATH" lors de l'installation.

---

## 2. Installation

### Option A — Lancement automatique (Windows, recommandé)

Double-cliquer sur **`ORNI-LAB.bat`** à la racine du projet.

Le fichier bat effectue automatiquement :
- Détection de Python sur le système
- Vérification des dépendances (Streamlit, etc.)
- Ouverture de l'application dans le navigateur par défaut

### Option B — Lancement manuel (PowerShell / Terminal)

```powershell
# Se placer dans le dossier du projet
cd "C:\...\Outils_Ornitho"

# Créer un environnement virtuel (recommandé, une seule fois)
python -m venv .venv
.venv\Scripts\activate

# Installer les dépendances (une seule fois)
pip install -r requirements.txt

# Lancer l'application
python -m streamlit run app.py
```

L'application s'ouvre automatiquement sur `http://localhost:8501`

---

## 3. Interface — Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                    ORNI-LAB                                  │
├───────────────┬─────────────────────────────────────────────┤
│  BARRE        │                                              │
│  LATÉRALE     │         ZONE PRINCIPALE                     │
│               │                                              │
│ Mode :        │  ┌──────────────────────────────────────┐   │
│ [Étudiant]    │  │  Visualisation interactive (Plotly)  │   │
│ [Enseignant]  │  └──────────────────────────────────────┘   │
│               │                                              │
│ Section :     │  ┌──────────────────────────────────────┐   │
│ ○ Biostat     │  │  Métriques numériques                │   │
│ ○ Dynamique   │  └──────────────────────────────────────┘   │
│               │                                              │
│ Module :      │  ┌──────────────────────────────────────┐   │
│ [Liste]       │  │  Interprétation guidée               │   │
│               │  └──────────────────────────────────────┘   │
│ Paramètres :  │                                              │
│ [Sliders]     │  [Exporter CSV]    [Exporter PDF]           │
└───────────────┴─────────────────────────────────────────────┘
```

### Éléments de l'interface

| Élément | Description |
|---------|-------------|
| **Barre latérale** | Choix du mode, de la section, du module et des paramètres |
| **Zone principale** | Graphique interactif, métriques, interprétation |
| **Sliders** | Modifier un paramètre en temps réel |
| **Boutons export** | Télécharger les données (CSV) ou le résumé (PDF) |

---

## 4. Choisir son mode

### Mode Étudiant
- Interface épurée
- Graphiques et métriques clés
- Interprétation biologique guidée
- **Recommandé pour les TP**

### Mode Enseignant
- Tout ce qui est en mode Étudiant, **plus** :
  - Formules mathématiques (LaTeX)
  - Notes pédagogiques et discussion
  - Hypothèses implicites du modèle
  - Limites de chaque approche
- **Recommandé pour préparer un cours ou animer une séance**

---

## 5. Importer ses données CSV

ORNI-LAB accepte des fichiers CSV avec :
- Séparateurs : virgule `,`, point-virgule `;`, tabulation `\t`
- Décimales : point `.` ou virgule `,`
- Encodage : UTF-8, Latin-1

**Procédure :**
1. Dans la barre latérale, cliquer sur "Parcourir" (section Analyse CSV)
2. Sélectionner votre fichier `.csv`
3. Le module détecte automatiquement le séparateur et l'encodage
4. Les colonnes numériques et catégoriques sont identifiées automatiquement

**Format attendu :**
```
site,espece,comptage,habitat,annee
A,Fauvette,12,foret,2023
A,Merle,8,foret,2023
B,Fauvette,3,prairie,2023
```

---

## 6. Utiliser un graphique Plotly

Les graphiques sont interactifs :

| Action | Effet |
|--------|-------|
| Clic + glisser | Zoomer sur une zone |
| Double-clic | Réinitialiser le zoom |
| Survol (hover) | Afficher les valeurs exactes |
| Clic sur légende | Masquer/afficher une série |
| Icônes en haut à droite | Télécharger le graphique en PNG |

---

## 7. Exporter les résultats

### Export CSV
- Contient les données simulées ou analysées
- Compatible Excel, R, Python
- Utile pour recalculer ou tracer hors ORNI-LAB

### Export PDF
- Résumé compact : paramètres + résultats clés + interprétation
- Format A4 paysage, polices standard
- Les symboles scientifiques (λ, α, β) sont normalisés

---

## 8. Résolution de problèmes fréquents

| Problème | Solution |
|----------|----------|
| L'app ne se lance pas | Vérifier que Python est dans le PATH |
| Page blanche | Attendre 10 s ou rafraîchir le navigateur (F5) |
| Erreur `ModuleNotFoundError` | Relancer `pip install -r requirements.txt` |
| CSV non reconnu | Vérifier le séparateur et l'encodage du fichier |
| PDF vide | Certains modules nécessitent une simulation lancée avant l'export |
| Port 8501 occupé | Fermer l'autre session Streamlit ou changer de port : `streamlit run app.py --server.port 8502` |
