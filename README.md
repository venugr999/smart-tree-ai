# Smart Tree AI 🌳

A Python/Flask application that combines image-based tree identification with a rule-based estimation pipeline for tree age, above-ground biomass and estimated CO₂ sequestration.

## What it does

1. Accepts a tree image from the browser.
2. Sends the image to the PlantNet identification API.
3. Uses the returned species, genus and family information in the estimation pipeline.
4. Estimates tree age from diameter and growth-rate references.
5. Estimates above-ground biomass using diameter, height and wood-density references.
6. Converts estimated biomass increment into annual and monthly CO₂ values.
7. Stores prediction records locally in CSV format for the demo application.

## Tech stack

- Python
- Flask
- Pandas / NumPy
- scikit-learn (data-enrichment utility)
- PlantNet API
- HTML / CSS / JavaScript

## Important methodology note

The project uses an external PlantNet API for species identification; it does **not** train a custom tree-classification model. The carbon-sequestration figures are estimates produced by the application's allometric/reference-table calculations and should not be treated as field-measured carbon accounting.

## Run locally

### 1. Create an environment

```bash
python -m venv .venv
```

Activate it and install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configure PlantNet

Copy `.env.example` to `.env` and set a valid PlantNet API key. Do not commit `.env`.

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Then edit `.env`:

```env
PLANTNET_API_KEY=your_key
```

### 3. Start the app

```bash
python -m app.main
```

Open `http://127.0.0.1:5000`.

## Deployment

The Flask application is configured for deployment on Vercel using the Python runtime and `api/index.py` entry point.

## Repository safety

The original project contained a hard-coded API credential and local runtime files. This public version removes credentials from source code and excludes runtime uploads, virtual environments, caches and prediction logs from Git.
