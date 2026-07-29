"""Enable coverage measurement in subprocesses.

The test suite spawns subprocesses through `run_shell`,
and without starting coverage in each child interpreter their coverage is lost.
For example, `_cli.py` and `__main__.py` are exercised only via a subprocess in `test_cli`.
Python imports a `sitecustomize` module at startup from any `sys.path` entry, `PYTHONPATH` included,
so this hook runs in every child and starts coverage when `COVERAGE_PROCESS_START` is set.

Coverage's own `patch = ["subprocess"]` cannot replace this here.
That mechanism relies on the `a1_coverage.pth` file running at interpreter startup,
but Python's `site` module only scans real site-packages directories for `.pth` files,
never directories added via `PYTHONPATH`.
So it works under uv, where coverage lives in the venv's site-packages,
but does nothing in the Nix `mkShell` devshell, where every package is injected through `PYTHONPATH`.
Dropping this file there makes subprocess coverage fall to 0% and fails the coverage gate.
The hook must stay until the devshell exposes a real combined site-packages,
e.g. via `python.withPackages` or uv2nix, after which `patch` would suffice.
"""

import os

if "COVERAGE_PROCESS_START" in os.environ:
    import coverage

    coverage.process_startup()
