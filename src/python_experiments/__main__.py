"""Python experiments CLI entrypoint.

Should not contain any logic, only call CLI from dedicated module.
"""

from ._cli import app

if __name__ == "__main__":
    app()
