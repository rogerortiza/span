from typing import Any, Dict, NamedTuple
from pathlib import Path
from ranking.database import DatabaseHandler

class CurrentRanking(NamedTuple):
    matches: Dict[str, Any]
    error: int

class RankingController:
    def __init__(self, db_path: Path) -> None:
        self._db_handler = DatabaseHandler(db_path)

