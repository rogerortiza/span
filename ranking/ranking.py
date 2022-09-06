from operator import itemgetter
from typing import Any, Dict, List, NamedTuple, Tuple
from pathlib import Path
from ranking import (
    DB_READ_ERROR,
    MISSING_TEAM_ERROR,
    NO_SCORE_ERROR,
    SAME_TEAM_ERROR,
    SUCCESS,
)
from ranking.database import DatabaseHandler


class CurrentMatch(NamedTuple):
    match: Dict[str, Any]
    error: int


class CurrentMatches(NamedTuple):
    match: List[CurrentMatch]
    error: int


class CurrentRank(NamedTuple):
    table: Dict[str, int]
    error: int


class RankingController:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

    def add(self, match: str) -> CurrentMatch:
        """Adds a new match to the Ranking database.

        Args:
            match (str): It is a string with the name of
            both teams alongside their score, separated by a comma.
            Example: Lions 2, Snakes 3

        Returns:
            CurrentMatch: A match object
        """
        teams = match.split(",")
        team_1 = teams[0].strip()
        team_2 = teams[1].strip()

        if not team_1 or not team_2:
            return CurrentMatch(match, MISSING_TEAM_ERROR)

        team_1_values = team_1.split(" ")
        team_2_values = team_2.split(" ")

        team_1_score = team_1_values.pop()
        team_2_score = team_2_values.pop()

        if not team_1_score.isnumeric() or not team_2_score.isnumeric():
            return CurrentMatch(match, NO_SCORE_ERROR)

        team_1_name = " ".join(team_1_values)
        team_2_name = " ".join(team_2_values)

        if team_1_name == team_2_name:
            return CurrentMatch(match, SAME_TEAM_ERROR)

        match = {
            "team_1": {"name": team_1_name, "goals": int(team_1_score)},
            "team_2": {"name": team_2_name, "goals": int(team_2_score)},
        }

        read = self._db_handler.read_matches()

        if read.error == DB_READ_ERROR:
            return CurrentMatch(match, read.error)

        read.matches_list.append(match)

        write = self._db_handler.write_matches(read.matches_list)

        return CurrentMatch(match, write.error)

    def clean_db(self) -> None:
        """Removes all matches from the Ranking database

        Returns:
            None
        """
        write = self._db_handler.write_matches([])

        return CurrentMatches([], write.error)

    def get_all_matches(self) -> List[Dict[str, Any]]:
        """Return all the matches in the Ranking database

        Returns:
            List[Dict[str, Any]]: A list with all the matches
            registered in the Ranking database
        """
        read = self._db_handler.read_matches()

        if read.error:
            return CurrentMatches([], read.error)

        return CurrentMatches(read.matches_list, SUCCESS)

    def show_table_ranking(self) -> List[Tuple[str, int]]:
        """Return the table rank for the league.

        Returns:
            List[Tuple[str, int]]: The Ranking table. A list with
            all the teams ordered by points in descending order.
        """
        read = self._db_handler.read_matches()

        if read.error:
            return CurrentRank({}, read.error)

        ranking_points = self._calculate_points(read.matches_list)
        ranking_teams = sorted(ranking_points.items(), key=itemgetter(1), reverse=True)
        ranking = self._sort_ranking(ranking_teams)

        return CurrentRank(dict(ranking), SUCCESS)

    def _calculate_points(self, matches) -> Dict:
        """This method is a helper in order to calculate the points
        by each team

        Args:
            matches (List): All the matches in the Ranking database

        Returns:
            Dict: Teams with their points
        """
        result = {}

        for match in matches:
            team_1 = match["team_1"]
            team_2 = match["team_2"]

            if not team_1["name"] in result:
                result[team_1["name"]] = 0

            if not team_2["name"] in result:
                result[team_2["name"]] = 0

            if team_1["goals"] > team_2["goals"]:
                result[team_1["name"]] += 3

            if team_1["goals"] < team_2["goals"]:
                result[team_2["name"]] += 3

            if team_1["goals"] == team_2["goals"]:
                result[team_1["name"]] += 1
                result[team_2["name"]] += 1

        return result

    def _sort_ranking(self, result_sort):
        for key, team in enumerate(result_sort):
            if key == len(result_sort) - 1:
                break

            if team[1] == result_sort[key + 1][1]:
                temp = team
                if team[0] > result_sort[key + 1][0]:
                    result_sort[key] = result_sort[key + 1]
                    result_sort[key + 1] = temp
                    self._sort_ranking(result_sort)

        return result_sort
