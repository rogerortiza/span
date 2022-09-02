import json
import pytest
from typer.testing import CliRunner
from ranking import __app_name__, __version__, cli, DB_READ_ERROR, SUCCESS, ranking

runner = CliRunner()


def test_version():
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout

@pytest.fixture
def mock_matches_json(tmp_path):
    matches = [
        {
            "team_1": {
                "name": "lions",
                "goals": 3
            },
            "team_2": {
                "name": "snakes",
                "goals": 3
            }
        },
        {
            "team_1": {
                "name": "tarantulas",
                "goals": 1
            },
            "team_2": {
                "name": "FC awesome",
                "goals": 0
            }
        },
        {
            "team_1": {
                "name": "lions",
                "goals": 1
            },
            "team_2": {
                "name": "FC awesome",
                "goals": 1
            }
        },
        {
            "team_1": {
                "name": "tarantulas",
                "goals": 3
            },
            "team_2": {
                "name": "snakes",
                "goals": 1
            }
        },
        {     
            "team_1": {
                "name": "lions",
                "goals": 4
            },
            "team_2": {
                "name": "grouches",
                "goals": 0
            }
        }
    ]

    db_file = tmp_path / "ranking.json"

    with db_file.open("w") as db:
        json.dump(matches, db, indent=4)
    return db_file


test_matches_1 = {
    "match_1": "Lions 3, Snakes 3",
    "match": {
        "team_1": {
            "name": "Lions",
            "goals": 3
        },
        "team_2": {
            "name": "Snakes",
            "goals": 3
        }
    }      
}

@pytest.mark.parametrize("match_1, expected", [
    pytest.param(
        test_matches_1["match_1"],
        (test_matches_1["match"], SUCCESS),
    )
])
def test_add(mock_matches_json, match_1, expected):
    ranking_controller = ranking.RankingController(mock_matches_json)
    assert ranking_controller.add(match_1) == expected
    read = ranking_controller._db_handler.read_matches()
    assert len(read.matches_list) == 6

def test_show_all_matches(mock_matches_json):
    ranking_controller = ranking.RankingController(mock_matches_json)
    matches = ranking_controller.get_all_matches()
    assert len(matches) == 5
