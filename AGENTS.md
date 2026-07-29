# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A base Python project used as a proving ground for a **dual development workflow**: the same code,
tests, and tooling are driven both by **uv** (Python-only, PyPI tools) and by **Nix** (hermetic,
adds cross-language tools). Keep both workflows working when changing dependencies, tooling, or CI.

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

## Comment & Markdown Style Guidelines

These rules apply to comments in all source files (Python, Lua, Nix, shell, etc.) as well as to prose text in
Markdown files.

### Rule 1: Comments are prose

Comments and Markdown prose should be treated as continuous text formatted as paragraphs, with proper punctuation
and capitalization. Even a single-sentence comment must start with a capital letter and end with punctuation
(`.`, `!`, or `?`).

**Exceptions:**

- If the comment starts with a backtick-quoted code reference, the capitalization follows the identifier's own casing.
- If the last word of a comment is a URL, do not append a trailing dot — URL pickers may misparse it.
  Start a new line for the next sentence instead.

**Good:**

```lua
-- By default, only LazyVim plugins will be lazy-loaded. Your custom plugins will load during startup.
-- If you know what you're doing, you can set this to `true` to have all your custom plugins lazy-loaded by default.
lazy = true,
version = false, -- Always use the latest git commit.
```

```lua
enabled = true,
-- `bullet = true` and `right_pad = 2` makes line same width rendered and unrendered.
bullet = true,
right_pad = 2,
```

```lua
clangd = {
  -- See https://www.lazyvim.org/extras/lang/clangd
  cmd = {
```

**Bad:**

```lua
-- Do not add "v" mode: it might conflict with other keymaps   ← missing dot
mode = { "i", "n", "t" },
```

```lua
{ "folke/tokyonight.nvim", opts = { style = "night" } }, -- moon, storm, night, day   ← not a sentence
```

### Rule 2: Line length ≤ 120 characters

No comment line may exceed 120 characters. When a sentence does not fit, split it at a meaningful boundary —
after a comma, or before a conjunction such as "and", "or", "which". A sentence that fits within 120 chars
may still be split across lines.

**Good:**

```lua
-- `LazyVim` defaults for `<leader><space>` find files and `<leader>/` live grep open in a "root" directory.
```

```lua
-- `LazyVim` defaults for `<leader><space>` find files and
-- `<leader>/` live grep open in a "root" directory.
```

```lua
-- For example, in cases with nested projects inside one repo,
-- `lsp` detector correctly recognizes root of each sub-project, whereas I need a root of entire project.
```

**Bad:**

```lua
-- For example, in cases with nested projects inside one repo, `lsp` detector correctly recognizes root of each sub-project, whereas I need a root of entire project.
```

```lua
-- For example, in cases with nested projects inside one repo, `lsp` detector correctly recognizes root of each
-- sub-project, whereas I need a root of entire project.   ← split at a bad boundary
```

### Rule 3: One sentence per line (generally)

Different sentences should generally each start on their own line. Two short sentences may share a line if together
they fit within 120 characters. A sentence must never be split across a line boundary with another sentence mixed in.

**Good:**

```lua
-- `LazyVim` defaults for `<leader><space>` find files and `<leader>/` live grep open in a "root" directory.
-- This `root` directory has a rather complicated algorithm,
-- which defaults to `{ "lsp", { ".git", "lua" }, "cwd" }` and does not work for me well.
-- For example, in cases with nested projects inside one repo,
-- `lsp` detector correctly recognizes root of each sub-project, whereas I need a root of entire project.
```

```lua
-- Setup is very cumbersome. At the end the problem was in a very slow performance.
```

**Bad:**

```lua
-- `LazyVim` defaults for `<leader><space>` find files and
-- `<leader>/` live grep open in a "root" directory. This `root` directory has a rather complicated algorithm,
-- which defaults to `{ "lsp", { ".git", "lua" }, "cwd" }` and does not work for me well. For example,
-- in cases with nested projects inside one repo, `lsp` detector correctly recognizes root of each sub-project,
-- whereas I need a root of entire project.
```

## Commit Messages

- Use [Conventional Commits](https://www.conventionalcommits.org) subjects, e.g. `fix(utils): ...`,
  `refactor(nix): ...`, `build(deps): ...`, `ci: ...`, `docs: ...`, `chore: ...`.
- Keep the body short: 2–4 lines, and no line longer than 100 characters.
- Write the body as prose, following the comment style above: full sentences, one per line.
- Keep commits atomic. If a refactor reindents a file, commit the reindentation separately from the
  logic change so the diff stays reviewable.
