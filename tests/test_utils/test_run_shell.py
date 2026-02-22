import logging
from pathlib import Path
from subprocess import CalledProcessError

import pytest

from python_experiments.utils import run_shell, shell_command


def test_shell_shlex() -> None:
    """Test shell_command with basic cases."""
    assert shell_command(["echo"]) == "echo"
    assert shell_command(["echo", "echo"]) == "echo echo"
    assert shell_command(["echo", "--arg1", "--arg2", "--arg3"]) == "echo --arg1 --arg2 --arg3"
    assert shell_command(["echo", "--path", Path()]) == "echo --path ."
    assert shell_command(["echo", "--path", Path('"xxx"')]) == "echo --path '\"xxx\"'"
    assert shell_command(["echo", "$AA"]) == "echo '$AA'"


def test_shell_command_extra_env() -> None:
    """Test shell_command with extra_env parameter."""
    assert shell_command(["echo"], extra_env={"A": "B"}) == "A=B echo"


def test_shell_command_extra_paths() -> None:
    """Test shell_command with extra_paths parameter."""
    command = shell_command(["echo"], extra_paths=[Path("path1"), Path("path2")])
    assert command == 'PATH="path1:path2:${PATH}" echo'


def test_shell_command_wrong_path() -> None:
    """Test shell_command with wrong PATH in extra_env."""
    with pytest.raises(ValueError, match="Do not pass PATH to extra_env"):
        shell_command(["echo"], extra_env={"PATH": "a"})


def test_shell_command_capture() -> None:
    """Test shell_command with capture_output parameter."""
    assert shell_command(["echo"], capture_output=True) == "echo &> CAPTURED"


def test_run_shell_basic_execution() -> None:
    """Test basic run_shell execution with simple command."""
    # Test simple echo command
    result = run_shell(["echo", "hello"], capture_output=True)
    assert result.returncode == 0
    assert result.stdout == "hello\n"


def test_run_shell_extra_env() -> None:
    """Test run_shell with extra_env parameter."""
    # Use a command that can check environment variables
    result = run_shell(["sh", "-c", "echo $TEST_VAR"], extra_env={"TEST_VAR": "test_value"}, capture_output=True)
    assert result.returncode == 0
    assert result.stdout == "test_value\n"


def test_run_shell_extra_paths(tmp_path: Path) -> None:
    """Test run_shell with extra_paths parameter."""
    # This is hard to test without side effects, so we'll just verify it doesn't crash

    custom_cmd = tmp_path / "custom_cmd"
    custom_cmd.write_text("#!/usr/bin/env bash\necho hello")
    custom_cmd.chmod(0o755)
    result = run_shell(["custom_cmd"], extra_paths=[tmp_path], capture_output=True)
    assert result.returncode == 0
    assert result.stdout == "hello\n"


def test_run_shell_cwd(tmp_path: Path) -> None:
    """Test run_shell with cwd parameter."""
    # Test with current directory
    result = run_shell(["pwd"], cwd=tmp_path, capture_output=True)
    assert result.returncode == 0
    assert Path(result.stdout.strip()) == tmp_path


def test_run_shell_check() -> None:
    """Test run_shell with check parameter."""
    # Test successful command with check=True (default)
    result = run_shell(["echo", "hello"], check=True)
    assert result.returncode == 0

    # Test with check=False - should not raise exception
    result = run_shell(["sh", "-c", "exit 1"], check=False)
    assert result.returncode == 1


def test_run_shell_loglevel(caplog: pytest.LogCaptureFixture) -> None:
    """Test run_shell with loglevel parameter."""
    caplog.set_level(logging.INFO)
    result = run_shell(["echo", "hello"], loglevel=logging.INFO)
    assert result.returncode == 0
    # Should have logged the command
    assert len(caplog.records) > 0
    assert "[RUNNING IN SHELL]" in caplog.text


def test_run_shell_error_handling() -> None:
    """Test run_shell error handling."""
    # Test that exception is raised when check=True (default) and command fails
    with pytest.raises(CalledProcessError):
        run_shell(["sh", "-c", "exit 1"])

    # Test that no exception is raised when check=False
    result = run_shell(["sh", "-c", "exit 1"], check=False)
    assert result.returncode == 1


def test_run_shell_colon_in_path() -> None:
    """Test run_shell error handling."""
    # Test that exception is raised when check=True (default) and command fails
    with pytest.raises(ValueError, match="Cannot handle colon in paths"):
        shell_command(["echo"], extra_paths=[Path("path/with:colon")])
