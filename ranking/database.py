import configparser
import json
from typing import Any, Dict, List, NamedTuple
from pathlib import Path
from ranking import DB_READ_ERROR, DB_WRITE_ERROR, SUCCESS, JSON_ERROR

DEFAULT_DB_FILE_PATH = Path.home().joinpath("ranking_db.json")


def get_database_path(config_file: Path) -> Path:
    """Return the current path to the Ranking database"""
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)

    return Path(config_parser["General"]["database"])


def init_database(db_path: Path) -> int:
    """Create the Ranking database"""
    try:
        db_path.write_text("[]")
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR


class DBResponse(NamedTuple):
    """The response comming from the Ranking database.

    Args:
        NamedTuple (_type_): _description_
    """

    matches_list: List[Dict[str, Any]]
    error: int


class DatabaseHandler:
    """ To read and write in the database"""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def read_matches(self) -> DBResponse:
        """Read all the matches in the Ranking database.

        Returns:
            DBResponse: List of matches
        """
        try:
            with self._db_path.open("r") as db:
                try:
                    return DBResponse(json.load(db), SUCCESS)
                except json.JSONDecodeError:
                    return DBResponse([], JSON_ERROR)
        except OSError:
            return DBResponse([], DB_READ_ERROR)

    def write_matches(self, matches_list: List[Dict[str, Any]]) -> DBResponse:
        """Write macthes in the database.

        Args:
            matches_list (List[Dict[str, Any]]): List of matches including the new match

        Returns:
            DBResponse: List of matches
        """
        try:
            with self._db_path.open("w") as db:
                json.dump(matches_list, db, indent=4)
            return DBResponse(matches_list, SUCCESS)
        except OSError:
            return DBResponse(matches_list, DB_WRITE_ERROR)
