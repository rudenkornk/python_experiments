# `python_experiments`

<!-- markdownlint-disable link-fragments -->

<!-- mdformat-toc start --slug=gitlab --no-anchors --maxlevel=6 --minlevel=1 -->

- [`python_experiments`](#python_experiments)
  - [Development](#development)
    - [Using uv](#using-uv)
      - [Common Commands](#common-commands)
    - [Using Nix](#using-nix)
      - [Common Commands](#common-commands-1)

<!-- mdformat-toc end -->

<!-- markdownlint-enable link-fragments -->

## Development

This project supports two development workflows: **uv** for Python developers and **Nix** for reproducible, cross-language environments.

### Using uv

[uv](https://docs.astral.sh/uv/) is the only prerequisite for this workflow, making it accessible to Python developers unfamiliar with Nix.

#### Common Commands

```bash
uv run pytest
uv run ./repo.py format         # Format code.
uv run ./repo.py format --check # Check formatting without changes.
uv run ./repo.py lint           # Run linters.
uv sync                         # Install dependencies (automatic on first run).
```

**Note:** The uv workflow provides full testing support and includes formatting and linting tools available on PyPI.
Some Nix-specific tools (e.g., `nixfmt`, `shellcheck`) are not available in this mode.

### Using Nix

[Nix](https://nixos.org/) is the primary package manager and build system for this project.
It's the only prerequisite for this workflow.
While uv offers excellent reproducibility, Nix provides additional advantages:

- **Enhanced reproducibility:** hermetic builds with cryptographic hashing ensure identical environments across machines.
- **Broader tooling ecosystem:** access to formatters, linters, and development tools beyond PyPI.
- **Cross-language support:** single package manager for Python, shell scripts, configuration files, and more.

While these benefits are modest for a single project,
they become significant when managing diverse codebases --- especially in enterprise environments with varied technology stacks.
This experimental repository serves as a proving ground for such workflows.

#### Common Commands

```bash
nix develop --ignore-env                  # Enter development shell.
pytest                                    # Run tests (in dev shell).
./repo.py format                          # Format code (in dev shell).
./repo.py format --check                  # Check formatting (in dev shell).
./repo.py lint                            # Run linters (in dev shell).
nix build                                 # Build the package.
nix develop --ignore-env --command pytest # Run without entering shell.
```

All development dependencies --- Python packages, formatters, linters, and system tools—are provided by the Nix shell.
