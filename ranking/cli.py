import typer
from typing import List, Optional
from pathlib import Path
from ranking import __app_name__, __version__, ERRORS, config, database, ranking

app = typer.Typer()

@app.command()
def init(db_path: str = typer.Option(str(database.DEFAULT_DB_FILE_PATH), "--db_path", "-db", prompt="Ranking database location?"),) -> None:
    """ Initialize the Ranking database """
    app_init_error = config.init_app(db_path)
    if app_init_error:
        typer.secho(f"Creating config file failed with '{ERRORS[app_init_error]}'", fg=typer.colors.RED)
        raise typer.Exit(1)

    db_init_error = database.init_database(Path(db_path))
    if db_init_error:
        typer.secho(f"Creating database failed with '{ERRORS[db_init_error]}'", fg=typer.colors.RED)
        raise typer.Exit(1)
    else:
        typer.secho(f"The Ranking database is {db_path}", fg=typer.colors.GREEN)

@app.command()
def add(match: str = typer.Argument(...)) -> None:
    """ Add a new match into Ranking database """
    ranking_controller = get_rankin_controller()
    match_added, error = ranking_controller.add(match)

    if error:
        typer.secho(f"Adding match failed with '{ERRORS[error]}'", fg=typer.colors.RED)
        raise typer.Exit(1)
    else:
        typer.secho("Match was added succesfully", fg=typer.colors.GREEN)


def get_rankin_controller() -> ranking.RankingController:
    if config.CONFIG_DIR_PATH.exists():
        db_path = database.get_database_path(config.CONFIG_FILE_PATH)
    else:
        typer.secho("Config file not found. Please, run 'ranking init' command", fg=typer.colors.RED)
        raise typer.Exit(1)
    
    if db_path.exists():
        return ranking.RankingController(db_path)
    else:
        typer.secho("Ranking database not found. Please, run 'ranking init' command", fg=typer.colors.RED)
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
