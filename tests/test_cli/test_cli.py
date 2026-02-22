from python_experiments.utils import run_shell


def test_cli() -> None:
    run_shell(["python", "-m", "python_experiments", "pass"])
