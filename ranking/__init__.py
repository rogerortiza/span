__app_name__ = "ranking"
__version__ = "1.0"


(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    ID_ERROR,
    MISSING_TEAM_ERROR,
    NO_SCORE_ERROR,
    SAME_TEAM_ERROR,
) = range(10)

ERRORS = {
    DIR_ERROR: "Config directory error",
    FILE_ERROR: "Config file error",
    DB_READ_ERROR: "Database read error",
    DB_WRITE_ERROR: "Database write error",
    ID_ERROR: "Ranking id error",
    MISSING_TEAM_ERROR: "You must provide two teams",
    NO_SCORE_ERROR: "You must provide the score for both teams",
    SAME_TEAM_ERROR: "Teams should be different, please try again!",
}
