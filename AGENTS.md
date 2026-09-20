# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A base Python project used as a proving ground for a **dual development workflow**:
the same code, tests, and tooling are driven both by **uv** (Python-only, PyPI tools)
and by **Nix** (hermetic, adds cross-language tools).
Keep both workflows working when changing dependencies, tooling, or CI.

## Commands

Every command has a uv form and a Nix form. Nix provides extra tools (nixfmt, shellcheck, gitleaks,
statix, prettier, stylua, markdownlint) that uv cannot.

```bash
# Tests
uv run --frozen pytest                                                     # full suite (xdist -n=5, 90% coverage gate)
nix develop --ignore-env --command pytest                                  # same, in the Nix devshell
uv run --frozen pytest tests/test_utils/test_x.py::test_name -o addopts="" # single test

# Format / lint (orchestrated by ./repo.py, a Typer CLI)
uv run --frozen ./repo.py format         # apply formatters (ruff, mdformat, + nix tools if in shell)
uv run --frozen ./repo.py format --check # check only (this is what CI runs)
uv run --frozen ./repo.py lint           # ruff check + mypy (+ nix-only checks if in shell)

# Nix package / flake
nix build       # builds the wheel and runs pytest via pytestCheckHook
nix flake check # same build as a flake check
```

Running a **single test** requires `-o addopts=""`: the default `addopts` forces `-n=5` (xdist) and
`--cov-fail-under=90`, so any subset otherwise fails the coverage gate.

`./repo.py format`/`lint` **gate nix-only steps on the `IN_NIX_SHELL` env var**. Under uv (var unset)
they run only the PyPI-available tools and `_logger.warning` that the rest were skipped; the full set
(gitleaks, shellcheck, markdownlint, statix, nixfmt, shfmt, prettier, stylua) runs only inside
`nix develop`. CI runs `./repo.py format --check` and `lint` in both a uv job and a Nix job for this reason.

## Architecture

- **CLI layering** (`src/python_experiments/`): `__main__.py` only calls `_cli.app` (a Typer app);
  real logic lives in `utils.py`. `repo.py` at the repo root is a *separate* Typer CLI (the repo task
  runner), not part of the package — it imports helpers from `python_experiments.utils`.

- **Subprocess coverage is load-bearing.** Tests spawn processes through `utils.run_shell`, and
  `_cli.py`/`__main__.py` are covered **only** via the subprocess in `tests/test_cli`. Two mechanisms
  cooperate: `[tool.coverage.run] patch = ["subprocess"]` (works under uv) and the root
  `sitecustomize.py` + `COVERAGE_PROCESS_START` exported by the Nix `shellHook` (needed under Nix).
  They are **not** redundant — see the docstring in `sitecustomize.py` for the `.pth`-vs-`PYTHONPATH`
  reason. Do not delete either without reading it; removing them silently drops coverage to ~81% in
  the Nix devshell and fails the gate.

- **`flake.nix` reads `pyproject.toml`.** `project.dependencies` are mapped to `python3Packages.<name>`
  by string-splitting the version specifier, and the build runs the nixpkgs runtime-deps check. This
  means **runtime-dep floors in `pyproject.toml` must stay ≤ the versions nixpkgs ships** (currently
  typer 0.24, click 8.3.1, rich 14.3.x), or `nix build` fails. Keep version currency in `uv.lock`,
  not in pyproject floors. `flake.nix` is single-system (`x86_64-linux`) and pinned to `pkgs.python3`.

## Conventions

- **ruff `select = ["ALL"]`** and **mypy `strict`**; line length 120. New code must pass both with
  no new ignores where avoidable.
- Python dependency versions live in the `test` and `lint` groups (`dev` re-includes both). CI runs
  plain `uv run --frozen pytest` (the default `dev` group), so both groups are installed.

Comment/prose and commit-message style are covered in the two sections below.
