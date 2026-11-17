import logging
from typing import Annotated, Literal, TypeAlias

import typer

from python_experiments.utils import setup_logger

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

LogLevel: TypeAlias = Literal[tuple(loglevel_map)]  # type: ignore[valid-type]  # noqa: UP040


@app.callback()
def setup_app(
    *,
    loglevel: Annotated[
        LogLevel,
        typer.Option(
            "-l",
            "--log-level",
            help="Logging level.",
        ),
    ] = "info",
) -> None:
    logging.getLogger().setLevel(loglevel_map[loglevel])
    setup_logger()


@app.command("pass")
def pass_() -> None:
    pass
