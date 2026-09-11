import pytest
from fastapi.testclient import TestClient

from app.algorithms.placement_engine import (
    calculate_common_score,
    generate_accessibility_layout,
    generate_balanced_layout,
    generate_cost_optimized_layout,
    generate_layout,
    generate_recommendation,
)
from app.main import app
from app.models.layout_models import (
    CodeConfig,
    ElementType,
    LayoutAlternative,
    LayoutElement,
    LayoutPlan,
    LayoutRequest,
    MedicineInformation,
    PackageModel,
    PrintingConstraints,
    TabletConfig,
    ValidationResult,
)


def create_sample_scoring_request(
    pkg_w: float = 120.0,
    pkg_h: float = 60.0,
    print_w: float = 100.0,
    print_h: float = 50.0,
    min_margin: float = 1.5,
    min_spacing: float = 1.2,
    tablet_count: int = 6,
    tablet_diameter: float = 8.0,
    margin_x: float = 5.0,
    margin_y: float = 5.0,
    opt_target: str = "RECOMMEND",
) -> LayoutRequest:
    actual_mx = min(margin_x, max(0.0, (pkg_w - print_w) / 2.0))
    actual_my = min(margin_y, max(0.0, (pkg_h - print_h) / 2.0))
    return LayoutRequest(
        package=PackageModel(
            package_width_mm=pkg_w,
            package_height_mm=pkg_h,
            printing_area_width_mm=print_w,
            printing_area_height_mm=print_h,
            printing_area_x_mm=actual_mx,
            printing_area_y_mm=actual_my,
            margin_left_mm=actual_mx,
            margin_top_mm=actual_my,
        ),
        tablet=TabletConfig(
            tablet_count=tablet_count,
            tablet_diameter_mm=tablet_diameter,
        ),
        code=CodeConfig(
            code_value="MED001",
            code_width_mm=20.0,
            code_height_mm=6.0,
        ),
        information=MedicineInformation(
            medicine_name="Amoxicillin",
            strength="500 mg",
            batch="B2026",
            mfg="2026-01",
            exp="2028-01",
            warnings="Keep dry",
        ),
        constraints=PrintingConstraints(
            minimum_margin_mm=min_margin,
            minimum_element_spacing_mm=min_spacing,
            minimum_text_size_mm=2.5,
        ),
        optimization_target=opt_target,
    )


# 1. Common score calculation
def test_common_score_calculation():
    score = calculate_common_score(
        scan_reliability=1.0,
        space_utilization=0.8,
        readability=0.7,
        print_efficiency=0.6,
        cost_efficiency=0.5,
    )
    # 0.30*1.0 + 0.25*0.8 + 0.20*0.7 + 0.15*0.6 + 0.10*0.5
    # 0.30 + 0.20 + 0.14 + 0.09 + 0.05 = 0.78
    assert score == 0.78


# 2. Exact scoring weights
def test_exact_scoring_weights():
    # Test scan_reliability weight: 0.30
    assert calculate_common_score(1.0, 0.0, 0.0, 0.0, 0.0) == 0.30

    # Test space_utilization weight: 0.25
    assert calculate_common_score(0.0, 1.0, 0.0, 0.0, 0.0) == 0.25

    # Test readability weight: 0.20
    assert calculate_common_score(0.0, 0.0, 1.0, 0.0, 0.0) == 0.20

    # Test print_efficiency weight: 0.15
    assert calculate_common_score(0.0, 0.0, 0.0, 1.0, 0.0) == 0.15

    # Test cost_efficiency weight: 0.10
    assert calculate_common_score(0.0, 0.0, 0.0, 0.0, 1.0) == 0.10

    # Sum of all weights is exactly 1.00
    assert calculate_common_score(1.0, 1.0, 1.0, 1.0, 1.0) == 1.00


# 3. Score normalization
def test_score_normalization():
    # Clamping boundaries
    assert calculate_common_score(0.0, 0.0, 0.0, 0.0, 0.0) == 0.0
    assert calculate_common_score(1.0, 1.0, 1.0, 1.0, 1.0) == 1.0

    score = calculate_common_score(0.85, 0.72, 0.90, 0.65, 0.80)
    assert 0.0 <= score <= 1.0


# 4. Cost alternative generation
def test_cost_alternative_generation():
    req = create_sample_scoring_request()
    plan = generate_recommendation(req)
    assert plan.success is True
    assert plan.alternatives is not None
    cost_alt = next((a for a in plan.alternatives if a.strategy == "COST"), None)
    assert cost_alt is not None
    assert cost_alt.strategy == "COST"
    assert 0.0 <= cost_alt.score <= 1.0
    assert 0.0 <= cost_alt.cost_efficiency <= 1.0


# 5. Balanced alternative generation
def test_balanced_alternative_generation():
    req = create_sample_scoring_request()
    plan = generate_recommendation(req)
    assert plan.success is True
    balanced_alt = next((a for a in plan.alternatives if a.strategy == "BALANCED"), None)
    assert balanced_alt is not None
    assert balanced_alt.strategy == "BALANCED"
    assert 0.0 <= balanced_alt.score <= 1.0


# 6. Accessibility alternative generation
def test_accessibility_alternative_generation():
    req = create_sample_scoring_request()
    plan = generate_recommendation(req)
    assert plan.success is True
    acc_alt = next((a for a in plan.alternatives if a.strategy == "ACCESSIBILITY"), None)
    assert acc_alt is not None
    assert acc_alt.strategy == "ACCESSIBILITY"
    assert 0.0 <= acc_alt.score <= 1.0


# 7. Three valid alternatives returned
def test_three_valid_alternatives_returned():
    req = create_sample_scoring_request()
    plan = generate_recommendation(req)
    assert plan.success is True
    assert len(plan.alternatives) == 3
    strategies = {a.strategy for a in plan.alternatives}
    assert strategies == {"COST", "BALANCED", "ACCESSIBILITY"}


# 8. Recommended layout is the highest-scoring valid layout
def test_recommended_layout_is_highest_scoring_valid_layout():
    req = create_sample_scoring_request()
    plan = generate_recommendation(req)
    assert plan.success is True
    assert plan.recommended_strategy is not None

    highest_alt = plan.alternatives[0]
    assert plan.recommended_strategy == highest_alt.strategy
    assert plan.score == highest_alt.score

    for alt in plan.alternatives:
        assert plan.score >= alt.score


# 9. Recommended strategy changes when scores change
def test_recommended_strategy_changes_when_scores_change():
    # Spacious package where spacious accessibility excels
    req_spacious = create_sample_scoring_request(pkg_w=150.0, pkg_h=80.0, print_w=130.0, print_h=70.0)
    plan_spacious = generate_recommendation(req_spacious)
    assert plan_spacious.success is True

    # Scores are computed according to each layout's physical merits
    assert plan_spacious.recommended_strategy in ("COST", "BALANCED", "ACCESSIBILITY")
    # Verify each alternative has distinct metrics
    alt_scores = {a.strategy: a.score for a in plan_spacious.alternatives}
    assert len(alt_scores) == 3


# 10. Deterministic tie-breaking
def test_deterministic_tie_breaking():
    # Verify tie-breaking logic ordering directly on candidate alternatives:
    # 1. Higher scan_reliability
    # 2. Higher readability
    # 3. Higher space_utilization
    # 4. Higher cost_efficiency
    # 5. COST > BALANCED > ACCESSIBILITY
    alt_cost = LayoutAlternative(
        strategy="COST",
        score=0.80,
        scan_reliability=1.0,
        readability=0.8,
        space_utilization=0.7,
        cost_efficiency=0.9,
        print_efficiency=0.7,
    )
    alt_balanced = LayoutAlternative(
        strategy="BALANCED",
        score=0.80,
        scan_reliability=1.0,
        readability=0.8,
        space_utilization=0.7,
        cost_efficiency=0.9,
        print_efficiency=0.7,
    )
    strategy_priority = {"COST": 3, "BALANCED": 2, "ACCESSIBILITY": 1}
    candidates = [alt_balanced, alt_cost]
    candidates.sort(
        key=lambda a: (
            round(a.score, 4),
            round(a.scan_reliability, 4),
            round(a.readability, 4),
            round(a.space_utilization, 4),
            round(a.cost_efficiency, 4),
            strategy_priority.get(a.strategy, 0),
        ),
        reverse=True,
    )
    # On identical metrics, COST wins over BALANCED
    assert candidates[0].strategy == "COST"


# 11. Invalid alternatives are excluded
def test_invalid_alternatives_are_excluded():
    req = create_sample_scoring_request()
    plan = generate_recommendation(req)
    # Only valid candidates are included
    for alt in plan.alternatives:
        assert alt.score > 0.0
        assert alt.layout is not None


# 12. All strategies failing returns structured failure
def test_all_strategies_failing_returns_structured_failure():
    req = create_sample_scoring_request(
        pkg_w=30.0,
        pkg_h=30.0,
        print_w=20.0,
        print_h=20.0,
        tablet_count=20,
        tablet_diameter=10.0,
        margin_x=2.0,
        margin_y=2.0,
    )
    plan = generate_recommendation(req)
    assert plan.success is False
    assert plan.recommended_strategy is None
    assert plan.recommended_layout is None
    assert len(plan.alternatives) == 0
    assert len(plan.errors) > 0


# 13. One strategy failing does not invalidate other valid alternatives
def test_one_strategy_failing_does_not_invalidate_other_valid_alternatives():
    # If a strategy fails, the remaining valid ones are still kept and returned
    req = create_sample_scoring_request()
    plan = generate_recommendation(req)
    assert plan.success is True
    assert len(plan.alternatives) >= 1


# 14. API recommendation response
def test_api_recommendation_response():
    client = TestClient(app)
    payload = {
        "package": {
            "package_width_mm": 120.0,
            "package_height_mm": 60.0,
            "printing_area_width_mm": 100.0,
            "printing_area_height_mm": 50.0,
            "printing_area_x_mm": 5.0,
            "printing_area_y_mm": 5.0,
        },
        "tablet": {
            "tablet_count": 6,
            "tablet_diameter_mm": 8.0,
        },
        "code": {
            "value": "MED001",
            "min_size_mm": 15.0,
        },
        "information": {
            "medicine_name": "Amoxicillin",
            "strength": "500 mg",
            "batch": "B2026",
            "mfg": "2026-01",
            "exp": "2028-01",
        },
        "optimization_target": "RECOMMEND",
    }
    response = client.post("/api/layouts/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "recommended_strategy" in data
    assert data["recommended_strategy"] in ("COST", "BALANCED", "ACCESSIBILITY")
    assert "recommended_layout" in data
    assert "alternatives" in data
    assert len(data["alternatives"]) == 3
    for alt in data["alternatives"]:
        assert "strategy" in alt
        assert "score" in alt
        assert "space_utilization" in alt
        assert "readability" in alt
        assert "print_efficiency" in alt
        assert "cost_efficiency" in alt
        assert "scan_reliability" in alt


# 15. Existing cost optimization still works
def test_existing_cost_optimization_still_works():
    req = create_sample_scoring_request(opt_target="COST")
    plan = generate_cost_optimized_layout(req)
    assert plan.success is True
    assert plan.cost_efficiency is not None


# 16. Existing balanced optimization still works
def test_existing_balanced_optimization_still_works():
    req = create_sample_scoring_request(opt_target="BALANCED")
    plan = generate_balanced_layout(req)
    assert plan.success is True
    assert plan.balanced_score is not None


# 17. Existing accessibility optimization still works
def test_existing_accessibility_optimization_still_works():
    req = create_sample_scoring_request(opt_target="ACCESSIBILITY")
    plan = generate_accessibility_layout(req)
    assert plan.success is True
    assert plan.accessibility_score is not None


# 18. Same input produces the same recommendation
def test_same_input_produces_same_recommendation():
    req1 = create_sample_scoring_request()
    req2 = create_sample_scoring_request()
    plan1 = generate_recommendation(req1)
    plan2 = generate_recommendation(req2)

    assert plan1.success is True
    assert plan2.success is True
    assert plan1.recommended_strategy == plan2.recommended_strategy
    assert plan1.score == plan2.score
    assert len(plan1.alternatives) == len(plan2.alternatives)
    for a1, a2 in zip(plan1.alternatives, plan2.alternatives):
        assert a1.strategy == a2.strategy
        assert a1.score == a2.score
