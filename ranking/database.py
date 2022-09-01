import configparser
from pathlib import Path
from ranking import DB_WRITE_ERROR, SUCCESS

DEFAULT_DB_FILE_PATH = Path.home().joinpath("ranking_db.json")

def get_database_path(config_file: Path) -> Path:
    """ Return the current path to the Ranking database """
    config_parser = configparser.ConfigParser()
    config_parser.read(config_file)

    return Path(config_parser["General"]["database"])

def init_database(db_path: Path) -> int:
    """ Create the Ranking database """
    try:
        db_path.write_text("[]")
        return SUCCESS
    except OSError:
        return DB_WRITE_ERROR