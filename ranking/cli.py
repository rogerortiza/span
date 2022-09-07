import typer
from typing import Dict, List, Optional, Any
from pathlib import Path
from ranking import __app_name__, __version__, ERRORS, config, database, ranking

app = typer.Typer()


@app.command()
def init(
    db_path: str = typer.Option(
        str(database.DEFAULT_DB_FILE_PATH),
        "--db_path",
        "-db",
        prompt="Ranking database location?",
    ),
) -> None:
    """Initialize the Ranking database"""
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(
            f"Creating config file failed with '{ERRORS[app_init_error]}'",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(
            f"Creating database failed with '{ERRORS[db_init_error]}'",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(f"The Ranking database is {db_path}", fg=typer.colors.GREEN)


@app.command(name="add")
def add(match: str = typer.Argument(...)) -> None:
    """**add** command -> Add a new match into Ranking database

    Args:
        match (str, optional): Receives an string with the name of
        the two teams with their goals. Defaults to typer.Argument(...).

    Raises:
        typer.Exit: 1
    """
    ranking_controller = get_rankin_controller()
    match_added, error = ranking_controller.add(match)

    if error:
        typer.secho(
            f"Adding match '{match_added}' failed with error: '{ERRORS[error]}'",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho("Match was added succesfully", fg=typer.colors.GREEN)


@app.command(name="all_matches")
def show_all_matches() -> None:
    """**all_matches** command -> Show all the matches registered in the Ranking database

    Raises:
        typer.Exit: _description_
        typer.Exit: _description_
    """
    ranking_controller = get_rankin_controller()
    matches_list, error = ranking_controller.get_all_matches()

    if error:
        typer.secho(
            f"Getting all matches failed with error: '{ERRORS[error]}'",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    if len(matches_list) == 0:
        typer.secho(
            "There are no matches in the Ranking database yet", fg=typer.colors.YELLOW
        )
        raise typer.Exit()

    typer.secho("\nMatches list:\n", fg=typer.colors.BLUE, bold=True)
    columns = ("ID.  ", "| Team 1    ", "| Team 2  ")
    headers = "".join(columns)
    typer.secho(headers, fg=typer.colors.BLUE, bold=True)
    typer.secho("-" * len(headers), fg=typer.colors.BLUE, bold=True)

    for id, match in enumerate(matches_list, 1):
        team_1, team_2 = match.values()
        typer.secho(
            f"{id}{(len(columns[0]) - len(str(id))) * ' '}"
            f"| {team_1['name']}{(len(columns[1]) - len(str(team_1['name'])) - 2 ) * ' '}"
            f"| {team_2['name']}",
            fg=typer.colors.BLUE,
            bold=True,
        )

    typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE, bold=True)


@app.command(name="show_table_rank")
def show_ranking() -> None:
    """Show the table rank

    Raises:
        typer.Exit: 1
    """
    ranking_controller = get_rankin_controller()
    matches_list, error = ranking_controller.show_table_ranking()

    if error:
        typer.secho(f"Getting table rank failed", fg=typer.colors.RED)
        raise typer.Exit(1)

    if len(matches_list) == 0:
        typer.secho(
            "There are no matches in the Ranking database yet", fg=typer.colors.YELLOW
        )
        raise typer.Exit()

    typer.secho("\nStandings:\n", fg=typer.colors.BLUE, bold=True)
    columns = ("ID.  ", "| Team        ", "| Points  ")
    headers = "".join(columns)
    typer.secho(headers, fg=typer.colors.BLUE, bold=True)
    typer.secho("-" * len(headers), fg=typer.colors.BLUE, bold=True)

    for id, match in enumerate(matches_list.items(), 1):
        typer.secho(
            f"{id}{(len(columns[0]) - len(str(id))) * ' '}"
            f"| {match[0]}{(len(columns[1]) - len(str(match[0])) - 2 ) * ' '}"
            f"| {match[1]}",
            fg=typer.colors.BLUE,
            bold=True,
        )

    typer.secho("-" * len(headers) + "\n", fg=typer.colors.BLUE, bold=True)


@app.command(name="clean")
def clean_db() -> None:
    ranking_controller = get_rankin_controller()
    _, error = ranking_controller.clean_db()

    if error:
        typer.secho(
            f"Deleting all matches failed with error: '{ERRORS[error]}'",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)
    else:
        typer.secho(
            "The Ranking database was deleted succesfully", fg=typer.colors.GREEN
        )


def get_rankin_controller() -> ranking.RankingController:
    """Every time the Ranking application runs, it needs to access the
    RankinController class and connect the CLI with the database. This Method
    checks if the database exists and returns the controller.

    Raises:
        typer.Exit: 1

    Returns:
        ranking.RankingController: The controller to communicates the CLI app with
        the database.
    """
    if config.CONFIG_DIR_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho(
            "Config file not found. Please, run 'ranking init' command",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)

    if db_path.exists():
        return ranking.RankingController(db_path)
    else:
        typer.secho(
            "Ranking database not found. Please, run 'ranking init' command",
            fg=typer.colors.RED,
        )
        raise typer.Exit(1)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
) -> None:
    return
