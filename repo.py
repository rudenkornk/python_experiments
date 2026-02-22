#!/usr/bin/env python3

"""Tiny helper to manage this repository."""

# ruff: noqa: D103

import logging
from pathlib import Path
from typing import Annotated

import typer

from python_experiments.utils import run_shell, setup_logger, typer_exit

_logger = logging.getLogger(__name__)
_repo_path = Path(__file__).parent


app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Simple script to manage this repository.",
)


@app.callback()
def setup_app() -> None:
    logging.getLogger().setLevel(logging.INFO)
    setup_logger()


def git_files(repo_path: Path, *ext: str) -> list[str]:
    return run_shell(
        ["git", "ls-files", *[f"*{e}" for e in ext]], capture_output=True, cwd=repo_path
    ).stdout.splitlines()


def _check_leaked_credentials(repo_path: Path) -> None:
    # In order to properly check for leaked credentials,
    # we have to iterate over all commits in the repo.
    # Pinning first commit ensures, that if the check is run on some shallow cloned repo,
    # it will throw an error.
    first_commit = "1712e58cb568cc877c1115ff57e82ed05ee97d66"

    if run_shell(["git", "cat-file", "-e", first_commit], check=False).returncode:
        _logger.error("Looks like git history is shallow and credential check cannot be performed.")
        raise RuntimeError

    run_shell(["gitleaks", "git"], cwd=repo_path)


@app.command()
@typer_exit
def lint() -> None:
    """Lint code."""
    run_shell(["ruff", "check"], cwd=_repo_path)
    run_shell(["mypy", _repo_path])

    _check_leaked_credentials(_repo_path)
    run_shell(["yamllint", "--strict", _repo_path / ".github"])

    if sh_files := git_files(_repo_path, ".sh"):
        run_shell(["shellcheck", *sh_files], cwd=_repo_path)

    run_shell(["typos"], cwd=_repo_path)

    run_shell(["markdownlint-cli2", "."], cwd=_repo_path)
    run_shell(["statix", "check", _repo_path])


@app.command(name="format")
@typer_exit
def format_code(
    *,
    check: Annotated[
        bool,
        typer.Option("-c", "--check", help="Only check if code is formatted."),
    ] = False,
) -> None:
    """Format codebase."""
    check_arg = ["--check"] if check else []
    diff_arg = ["--diff"] if check else []
    dry_run_arg = ["--dry-run"] if check else []
    write_arg = ["--write"] if not check else []
    run_shell(["ruff", "format", *check_arg], cwd=_repo_path)
    run_shell(["ruff", "check", "--fix", "--unsafe-fixes", *diff_arg], cwd=_repo_path)

    statix_res = run_shell(["statix", "fix", *dry_run_arg, _repo_path], cwd=_repo_path, capture_output=check)
    if check and statix_res.stdout.strip():
        raise RuntimeError(statix_res.stdout)

    run_shell(["nixfmt", "--verify", "--strict", *check_arg, *git_files(_repo_path, ".nix")], cwd=_repo_path)

    run_shell(["mdformat", *git_files(_repo_path, ".md"), *check_arg], cwd=_repo_path)
    run_shell(["shfmt", *write_arg, *diff_arg, _repo_path])
    run_shell(["prettier", *write_arg, _repo_path, *check_arg], cwd=_repo_path)
    run_shell(["stylua", _repo_path, *check_arg], cwd=_repo_path)


if __name__ == "__main__":
    app()
