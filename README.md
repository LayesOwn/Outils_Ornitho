# ORNI-LAB

Plateforme pédagogique scientifique interactive pour étudiants de Master en Ornithologie.

ORNI-LAB propose des simulateurs Streamlit pour explorer des concepts quantitatifs en écologie des oiseaux :

- croissance exponentielle et logistique ;
- matrices de Leslie ;
- corrélation et régression ;
- capture-marquage-recapture ;
- modèle prédateur-proie de Lotka-Volterra.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement

```bash
streamlit run app.py
```

## Architecture

```text
.
├── app.py
├── app/
│   ├── main.py
│   └── config.py
├── modules/
│   ├── growth.py
│   ├── leslie.py
│   ├── regression.py
│   ├── cmr.py
│   └── lotka_volterra.py
├── core/
│   └── export.py
├── data/
│   └── examples.py
├── assets/
├── reports/
├── database/
├── simulations/
├── utils/
│   └── ui.py
├── models/
├── exports/
├── notebooks/
└── tests/
```

Chaque fichier dans `modules/` est indépendant et expose une fonction `render(context)`.
Cette organisation permet d’ajouter facilement de futurs modules, y compris une IA pédagogique.

## Modes

- **Mode étudiant** : explications progressives, interprétations guidées, focus apprentissage.
- **Mode enseignant** : paramètres avancés, détails mathématiques, éléments de discussion.

## Export PDF

Les modules génèrent un résumé exportable en PDF depuis l’interface. L’export utilise `reportlab`.
