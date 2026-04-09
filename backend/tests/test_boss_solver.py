from app.models.enums import CompStyle
from app.models.schemas import BossSolverRequest, UserRosterRequest
from app.services.recommendation import solve_boss


def test_boss_solver_answers_required_questions() -> None:
    response = solve_boss("boss_crest_nova_ashdrake")
    questions = {item.question for item in response.answers}
    assert "Preciso de accuracy?" in questions
    assert "Preciso de mitigacao?" in questions


def test_boss_solver_with_roster_returns_personalized_recommendations() -> None:
    payload = BossSolverRequest(
        desired_style=CompStyle.SUSTAIN,
        roster=UserRosterRequest(
            unit_ids=["unit_hart", "unit_cestina", "unit_vox", "unit_fen"],
            equip_ids=["equip_true_flambardo", "equip_lesser_demonheart"],
        ),
    )
    response = solve_boss("boss_crest_nova_ashdrake", payload)
    assert len(response.with_my_box) > 0
