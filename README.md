# FIFA 15 Player Intelligence

A machine learning–powered player similarity engine built on the FIFA 15 dataset.
Explore 16,155 players, discover who plays like whom, and understand the data that drives it all — through a modern interactive dashboard.

**[Live Demo →](https://share.streamlit.io)** &nbsp;·&nbsp; **[Dataset](https://www.kaggle.com/datasets/stefanoleone992/fifa-22-complete-player-dataset)**

---

## Overview

This project answers one question: *given a player, who plays most like them?*

Using cosine similarity and Euclidean distance on a StandardScaler pipeline, the system compares players across six core attributes — pace, shooting, passing, dribbling, defending, and physicality — then surfaces the closest matches. The full exploratory analysis is documented step-by-step in the accompanying notebook.

---

## Features

**Player Similarity Search**
Select any of the 14,380 outfield players. Get two ranked similarity lists — one built on directional likeness (cosine), one on raw statistical proximity (Euclidean) — displayed side by side for comparison.

**Exploratory Data Analysis Panel**
Five analytical sections covering rating distributions, market value relationships, inter-attribute correlations, league and nationality breakdowns, and a missing data deep-dive.

**Home Dashboard**
At-a-glance metrics, the top-10 rated players, position group distribution, peak age analysis, and a curated table of the dataset's most promising young talents.

---

## Technical Details

| Component | Details |
|---|---|
| Dataset | FIFA 15 · 16,155 players · 110 features |
| Preprocessing | `sklearn.pipeline.Pipeline` + `StandardScaler` |
| Similarity | `cosine_similarity` · `euclidean_distances` |
| Feature set | `pace` `shooting` `passing` `dribbling` `defending` `physic` `log(value)` |
| GK handling | Separate pipeline · goalkeeping-specific features |
| Caching | `@st.cache_data` on data load and model build |
| Visualization | Plotly (radar charts, scatter, heatmaps, histograms) |
| UI | Streamlit multi-page · custom CSS dark theme |

---

## Project Structure

```
fifa15dataset/
├── app.py                      Entry point
├── players_15.csv              Dataset (16,155 × 110)
├── requirements.txt
├── edafifa15.ipynb             Full EDA notebook (5 days of analysis)
├── pages/
│   ├── 1_🏠_Home.py            Overview dashboard
│   ├── 2_🔍_Player_Search.py   Similarity engine
│   └── 3_📊_EDA_Panel.py       Exploratory analysis
├── utils/
│   ├── data_loader.py          Data ingestion and caching
│   ├── similarity.py           Cosine and Euclidean functions
│   └── charts.py               Plotly chart library
└── assets/
    └── style.css               FIFA dark theme
```

---

## Getting Started

**Requirements:** Python 3.10+

```bash
# Clone
git clone https://github.com/alyboii/fifa15dataset.git
cd fifa15dataset/fifa15dataset

# Install dependencies
pip install -r requirements.txt

# Run
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Notebook

`edafifa15.ipynb` documents five days of structured analysis:

| Day | Focus |
|---|---|
| 1 | Dataset orientation · missing value analysis · data type fixes |
| 2 | Statistical distributions · correlations · position analysis |
| 3 | Financial data · peak age curve · young talent identification |
| 4 | Feature engineering · sklearn Pipeline · StandardScaler |
| 5 | Cosine similarity · Euclidean distance · model comparison |

Key findings documented inline — including why goalkeepers require a separate pipeline, why `log(value_eur)` outperforms the raw figure, and where the two similarity metrics diverge.

---

## Design

The interface follows a dark theme inspired by the FIFA game aesthetic — deep navy backgrounds, green and gold accents, and high-contrast typography built for readability at a glance.

Radar charts give an immediate visual sense of a player's profile. Side-by-side similarity columns make the difference between cosine and Euclidean immediately legible. Every section includes a brief explanation of the underlying methodology.

---

## About

**Stack:** Python · Pandas · NumPy · scikit-learn · Streamlit · Plotly  
**Author:** Ali · [GitHub](https://github.com/alyboii)
