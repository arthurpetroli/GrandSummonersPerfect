from app.models.enums import CompStyle, ContentMode
from app.models.schemas import TeamBuilderRequest, UserRosterRequest
from app.services.recommendation import recommend_teams


def test_recommendation_returns_ranked_items() -> None:
    payload = TeamBuilderRequest(
        mode=ContentMode.CREST_PALACE,
        boss_id="boss_crest_nova_ashdrake",
        desired_style=CompStyle.SUSTAIN,
        roster=UserRosterRequest(
            unit_ids=["unit_hart", "unit_cestina", "unit_vox", "unit_fen"],
            equip_ids=["equip_true_flambardo", "equip_lesser_demonheart"],
        ),
    )

    result = recommend_teams(payload)
    assert len(result.recommendations) > 0
    assert result.recommendations[0].score >= result.recommendations[-1].score


def test_recommendation_low_fit_when_roster_missing_core() -> None:
    payload = TeamBuilderRequest(
        mode=ContentMode.RAID,
        boss_id="boss_raid_abyss_core",
        desired_style=CompStyle.NUKE,
        roster=UserRosterRequest(unit_ids=["unit_sanstone", "unit_fen"]),
    )
    result = recommend_teams(payload)
    assert len(result.recommendations) > 0
    assert result.recommendations[0].fit in {"medium", "low"}
