import logging
from typing import Annotated

import click
import typer

from python_experiments.utils import setup_logger, typer_exit

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Python experiments CLI.",
)

loglevel_map = {
    "s": logging.DEBUG - 5,
    "spam": logging.DEBUG - 5,
    "d": logging.DEBUG,
    "debug": logging.DEBUG,
    "v": logging.INFO - 5,
    "verbose": logging.INFO - 5,
    "i": logging.INFO,
    "info": logging.INFO,
    "n": logging.WARNING - 5,
    "notice": logging.WARNING - 5,
    "w": logging.WARNING,
    "warning": logging.WARNING,
    "u": logging.ERROR - 5,
    "success": logging.ERROR - 5,
    "e": logging.ERROR,
    "error": logging.ERROR,
    "c": logging.CRITICAL,
    "critical": logging.CRITICAL,
}


@app.callback()
def setup_app(
    *,
    loglevel: Annotated[
        str,
        typer.Option(
            "-l",
            "--log-level",
            click_type=click.Choice(list(loglevel_map.keys())),
            help="Logging level.",
            case_sensitive=False,
        ),
    ] = "info",
) -> None:
    logging.getLogger().setLevel(loglevel_map[loglevel])
    setup_logger()


@app.command("pass")
@typer_exit()
def pass_() -> None:
    pass
