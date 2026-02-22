import asyncio
import re
from contextlib import suppress

import pytest

from python_experiments.utils import ContextLogger


def test_simple_context(*, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(1)

    msg = "task"
    postfix = "postinfo"
    with ContextLogger(msg=msg) as logger:
        logger.add_postfix(postfix)

    assert re.search(rf"\[STARTED\s*\] {msg}", caplog.text)
    assert re.search(rf"\[FINISHED\s*\] {msg} {postfix}", caplog.text)


def test_status_context(*, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(1)

    msg = "task"
    with ContextLogger(msg=msg, status=True):
        pass

    assert re.search(rf"\[STARTED\s*\] {msg}", caplog.text) is None
    assert re.search(rf"\[STATUS\s*\] {msg}", caplog.text)


def test_status(*, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(1)

    msg = "task"
    postfix = "postinfo"
    ContextLogger.status(msg, postfixes=[postfix])

    assert re.search(rf"\[STATUS\s*\] {msg}", caplog.text)


def test_exception_context(*, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(1)

    msg = "task"
    with suppress(RuntimeError), ContextLogger(msg=msg):
        raise RuntimeError

    assert re.search(rf"\[STARTED\s*\] {msg}", caplog.text)
    assert re.search(rf"\[EXCEPTION\s*\] {msg}", caplog.text)
    assert re.search(rf"\[FINISHED\s*\] {msg}", caplog.text) is None


def test_exception_status(*, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(1)

    msg = "task"
    with suppress(RuntimeError), ContextLogger(msg=msg, status=True):
        raise RuntimeError

    assert re.search(rf"\[STARTED\s*\] {msg}", caplog.text) is None
    assert re.search(rf"\[EXCEPTION\s*\] {msg}", caplog.text)
    assert re.search(rf"\[STATUS\s*\] {msg}", caplog.text) is None


async def test_async_simple_context(*, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(1)

    msg = "task"
    postfix = "postinfo"
    async with ContextLogger(msg=msg, ping=0.1) as logger:
        await asyncio.sleep(0.3)
        logger.add_postfix(postfix)

    assert re.search(rf"\[STARTED\s*\] {msg}", caplog.text)
    assert re.search(rf"\[IN PROGRESS\s*\] {msg}", caplog.text)
    assert re.search(rf"\[FINISHED\s*\] {msg} {postfix}", caplog.text)


async def test_async_exception_context(*, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(1)

    msg = "task"
    with suppress(RuntimeError):
        async with ContextLogger(msg=msg, ping=0.1):
            await asyncio.sleep(0.3)
            raise RuntimeError

    assert re.search(rf"\[STARTED\s*\] {msg}", caplog.text)
    assert re.search(rf"\[IN PROGRESS\s*\] {msg}", caplog.text)
    assert re.search(rf"\[EXCEPTION\s*\] {msg}", caplog.text)
    assert re.search(rf"\[FINISHED\s*\] {msg}", caplog.text) is None


@pytest.mark.xfail(
    raises=RuntimeError, strict=True, reason="ContextLogger does not support double-entry, it leads to UB."
)
def test_double_entrance() -> None:
    with ContextLogger(msg="") as logger, logger:
        pass
