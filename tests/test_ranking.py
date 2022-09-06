import json
import pytest
from typer.testing import CliRunner
from ranking import (
    MISSING_TEAM_ERROR,
    NO_SCORE_ERROR,
    SAME_TEAM_ERROR,
    SUCCESS,
    __app_name__,
    __version__,
    cli,
    ranking,
)

runner = CliRunner()


def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


@pytest.fixture
def mock_matches_json(tmp_path):
    matches = [
        {
            "team_1": {"name": "lions", "goals": 3},
            "team_2": {"name": "snakes", "goals": 3},
        },
        {
            "team_1": {"name": "tarantulas", "goals": 1},
            "team_2": {"name": "FC awesome", "goals": 0},
        },
        {
            "team_1": {"name": "lions", "goals": 1},
            "team_2": {"name": "FC awesome", "goals": 1},
        },
        {
            "team_1": {"name": "tarantulas", "goals": 3},
            "team_2": {"name": "snakes", "goals": 1},
        },
        {
            "team_1": {"name": "lions", "goals": 4},
            "team_2": {"name": "grouches", "goals": 0},
        },
    ]

    db_file = tmp_path / "ranking.json"

    with db_file.open("w") as db:
        json.dump(matches, db, indent=4)
    return db_file


test_match_1 = {
    "match": "Lions 3, Snakes 3",
    "teams": {
        "team_1": {"name": "Lions", "goals": 3},
        "team_2": {"name": "Snakes", "goals": 3},
    },
}

test_match_2 = {
    "match": "Lions 1,",
    "error": "Lions 1,",
}

test_match_3 = {
    "match": "Lions aa, Giants 4",
    "error": "Lions aa, Giants 4",
}

test_match_4 = {
    "match": "Lions 1, Lions 1",
    "error": "Lions 1, Lions 1",
}


@pytest.mark.parametrize(
    "match, expected",
    [
        pytest.param(
            test_match_1["match"],
            (test_match_1["teams"], SUCCESS),
        ),
    ],
)
def test_add(mock_matches_json, match, expected):
    ranking_controller = ranking.RankingController(mock_matches_json)
    assert ranking_controller.add(match) == expected
    read = ranking_controller._db_handler.read_matches()
    assert len(read.matches_list) == 6


@pytest.mark.parametrize(
    "match, expected",
    [
        pytest.param(
            test_match_2["match"],
            (test_match_2["error"], MISSING_TEAM_ERROR),
        ),
        pytest.param(
            test_match_3["match"],
            (test_match_3["error"], NO_SCORE_ERROR),
        ),
        pytest.param(
            test_match_4["match"],
            (test_match_4["error"], SAME_TEAM_ERROR),
        ),
    ],
)
def test_add_failures(mock_matches_json, match, expected):
    ranking_controller = ranking.RankingController(mock_matches_json)
    assert ranking_controller.add(match) == expected
    read = ranking_controller._db_handler.read_matches()
    assert len(read.matches_list) == 5


def test_show_all_matches(mock_matches_json):
    ranking_controller = ranking.RankingController(mock_matches_json)
    matches, error = ranking_controller.get_all_matches()
    assert len(matches) == 5
    assert error == 0


def test_show_table_ranking(mock_matches_json):
    ranking_controller = ranking.RankingController(mock_matches_json)
    table_rank, error = ranking_controller.show_table_ranking()
    table_expected, error_expected = ranking.CurrentRank(
        {"tarantulas": 6, "lions": 5, "FC awesome": 1, "snakes": 1, "grouches": 0},
        SUCCESS,
    )
    assert table_rank == table_expected
    assert error == error_expected
