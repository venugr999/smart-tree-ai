import math

GROWTH_RATES_SPECIES = {}
GROWTH_RATES_GENUS = {
    "Azadirachta": 2.0,
    "Ficus": 2.5,
    "Pinus": 2.2,
    "Picea": 1.8,
    "Betula": 2.6,
    "Mangifera": 1.8,
}
GROWTH_RATES_FAMILY = {
    "Meliaceae": 1.9,
    "Pinaceae": 2.0,
    "Betulaceae": 2.4,
    "Anacardiaceae": 1.8,
}

WOOD_DENSITY_GENUS = {
    "Azadirachta": 0.56,
    "Ficus": 0.45,
    "Pinus": 0.42,
    "Picea": 0.40,
    "Betula": 0.62,
    "Mangifera": 0.65,
}

DEFAULT_GROWTH_RATE = 2.0
DEFAULT_WOOD_DENSITY = 0.6
CARBON_FRACTION = 0.47
CO2_FROM_C = 3.67
ALLOMETRIC_COEFF = 0.0673
ALLOMETRIC_EXP = 0.976


def lookup_growth_rate(species: str, genus: str, family: str) -> float:
    species = (species or "").strip()
    genus = (genus or "").strip()
    family = (family or "").strip()
    if species in GROWTH_RATES_SPECIES:
        return GROWTH_RATES_SPECIES[species]
    if genus in GROWTH_RATES_GENUS:
        return GROWTH_RATES_GENUS[genus]
    if family in GROWTH_RATES_FAMILY:
        return GROWTH_RATES_FAMILY[family]
    return DEFAULT_GROWTH_RATE


def lookup_wood_density(genus: str, family: str) -> float:
    genus = (genus or "").strip()
    if genus in WOOD_DENSITY_GENUS:
        return WOOD_DENSITY_GENUS[genus]
    return DEFAULT_WOOD_DENSITY


def agb_from_dbh_height(dbh_cm: float, height_m: float, wood_density_gcm3: float) -> float:
    """Estimate above-ground biomass (kg) from DBH, height and wood density."""
    try:
        dbh = float(dbh_cm)
        h = float(height_m)
        rho = float(wood_density_gcm3)
    except Exception:
        return 0.0
    if dbh <= 0 or h <= 0:
        return 0.0
    value = ALLOMETRIC_COEFF * ((rho * (dbh ** 2) * h) ** ALLOMETRIC_EXP)
    return max(float(value), 0.0)


def estimate_tree_age_and_co2(
    species_name: str,
    diameter_cm: float,
    height_m: float = None,
    canopy_radius_m: float = None,
    family: str = None,
    genus: str = None,
):
    species = (species_name or "").strip()
    genus = (genus or "").strip()
    family = (family or "").strip()

    try:
        dbh = float(diameter_cm)
    except Exception:
        return {"error": "Invalid diameter_cm"}

    if dbh <= 0:
        return {"error": "Diameter must be greater than zero."}

    if height_m is None or (isinstance(height_m, str) and height_m.strip() == ""):
        height = max(1.0, 0.6 * dbh)
        height_note = "height_imputed"
    else:
        try:
            height = float(height_m)
            if height <= 0:
                return {"error": "Height must be greater than zero."}
            height_note = None
        except Exception:
            height = max(1.0, 0.6 * dbh)
            height_note = "height_imputed"

    growth_rate = lookup_growth_rate(species, genus, family)
    if growth_rate <= 0:
        growth_rate = DEFAULT_GROWTH_RATE

    rho = lookup_wood_density(genus, family)
    agb_now = agb_from_dbh_height(dbh, height, rho)

    dbh_prev = max(0.1, dbh - growth_rate)
    height_prev = max(1.0, height * (dbh_prev / dbh))
    agb_prev = agb_from_dbh_height(dbh_prev, height_prev, rho)
    biomass_increment = max(agb_now - agb_prev, 0.0)

    annual_co2_kg = biomass_increment * CARBON_FRACTION * CO2_FROM_C
    monthly_co2_kg = annual_co2_kg / 12.0
    estimated_age = round(dbh / growth_rate, 2)

    species_lower = species.lower()
    species_factor = 1.0
    if "ficus" in species_lower or "ficus" in genus.lower():
        species_factor = 1.3
    elif "neem" in species_lower or "azadirachta" in genus.lower():
        species_factor = 1.15
    elif "mangifera" in genus.lower() or "mango" in species_lower:
        species_factor = 1.1

    monthly_co2_kg *= species_factor
    annual_co2_kg *= species_factor

    monthly_co2_kg = round(min(monthly_co2_kg, 8.0), 3)
    annual_co2_kg = round(min(annual_co2_kg, 96.0), 3)

    result = {
        "species": species_name,
        "estimated_age_years": float(estimated_age),
        "agb_kg": round(agb_now, 3),
        "annual_biomass_increment_kg": round(biomass_increment, 3),
        "co2_kg_per_year": float(annual_co2_kg),
        "co2_kg_per_month": float(monthly_co2_kg),
        "growth_rate_cm_per_year": growth_rate,
        "wood_density_gcm3": rho,
    }
    if height_note:
        result["notes"] = height_note
    return result
