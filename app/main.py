import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from .estimator import estimate_tree_age_and_co2

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"
PREDICTIONS_FILE = DATA_DIR / "predictions.csv"

DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
CORS(app)

PLANTNET_API_KEY = os.getenv("PLANTNET_API_KEY")
PLANTNET_URL = "https://my-api.plantnet.org/v2/identify/all"


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/identify")
def identify():
    if not PLANTNET_API_KEY:
        return jsonify({"error": "PLANTNET_API_KEY is not configured."}), 500

    image = request.files.get("file")
    if not image or not image.filename:
        return jsonify({"error": "No image uploaded."}), 400

    try:
        response = requests.post(
            PLANTNET_URL,
            params={"api-key": PLANTNET_API_KEY},
            files={"images": (image.filename, image.stream, image.mimetype)},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return jsonify({"error": f"PlantNet request failed: {exc}"}), 502

    results = data.get("results", [])
    if not results:
        return jsonify({"error": "No species identified."}), 404

    top = results[0]
    species_data = top.get("species", {})
    return jsonify(
        {
            "species": species_data.get("scientificNameWithoutAuthor", "Unknown"),
            "family": species_data.get("family", {}).get("scientificNameWithoutAuthor", "Unknown"),
            "genus": species_data.get("genus", {}).get("scientificNameWithoutAuthor", "Unknown"),
            "confidence": round(float(top.get("score", 0)) * 100, 2),
        }
    )


@app.post("/estimate")
def estimate():
    payload = request.get_json(silent=True) or {}

    try:
        species = payload.get("species", "Unknown")
        family = payload.get("family", "Unknown")
        genus = payload.get("genus", "Unknown")
        diameter = float(payload.get("diameter_cm", 0))
        height = payload.get("height_m")
        canopy = payload.get("canopy_radius_m")
        height = float(height) if height not in (None, "") else None
        canopy = float(canopy) if canopy not in (None, "") else None

        result = estimate_tree_age_and_co2(
            species_name=species,
            diameter_cm=diameter,
            height_m=height,
            canopy_radius_m=canopy,
            family=family,
            genus=genus,
        )
    except (TypeError, ValueError) as exc:
        return jsonify({"error": f"Invalid input: {exc}"}), 400

    if "error" in result:
        return jsonify(result), 400

    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        **result,
        "family": family,
        "genus": genus,
        "diameter_cm": diameter,
        "height_m": height,
        "canopy_radius_m": canopy,
    }

    pd.DataFrame([record]).to_csv(
        PREDICTIONS_FILE,
        mode="a",
        header=not PREDICTIONS_FILE.exists(),
        index=False,
    )

    return jsonify(record)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
