from app.estimator import estimate_tree_age_and_co2


def test_estimator_returns_core_metrics():
    result = estimate_tree_age_and_co2(
        "Azadirachta indica", 55, 25, 10, family="Meliaceae", genus="Azadirachta"
    )
    assert result["estimated_age_years"] > 0
    assert result["agb_kg"] >= 0
    assert result["co2_kg_per_year"] >= 0
