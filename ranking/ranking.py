import typer
from typing import Any, Dict, List, NamedTuple
from pathlib import Path
from ranking import DB_READ_ERROR
from ranking.database import DatabaseHandler

class CurrentRanking(NamedTuple):
    matches: Dict[str, Any]
    error: int

class RankingController:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add(self, match: str) -> CurrentRanking:
        """ Add a new match to the Ranking database """
        teams = match.split(",")
        team_1 = teams[0].strip()
        team_2 = teams[1].strip()

        if not team_1 or not team_2:
            typer.secho("You must provide two teams", fg=typer.colors.YELLOW)
            raise typer.Exit(1)

        team_1_values = team_1.split(" ")
        team_2_values = team_2.split(" ")
        
        team_1_score = team_1_values.pop()
        team_2_score = team_2_values.pop()

        if not team_1_score.isnumeric() or not team_2_score.isnumeric():
            typer.secho(f"You must provide the score for both teams", fg=typer.colors.YELLOW)
            raise typer.Exit(1)

        team_1_name = " ".join(team_1_values)
        team_2_name = " ".join(team_2_values)

        match = {
            "team_1": {
                "name": team_1_name,
                "goals": int(team_1_score)
            },
            "team_2": {
                "name": team_2_name,
                "goals": int(team_2_score)
            }
        }

        read = self._db_handler.read_matches()

        if read.error == DB_READ_ERROR:
            return CurrentRanking(match, read.error)
        
        read.matches_list.append(match)

        write = self._db_handler.write_matches(read.matches_list)

        return CurrentRanking(match, write.error)
