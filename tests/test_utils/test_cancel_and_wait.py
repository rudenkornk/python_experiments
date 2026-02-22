"""Test correct behaviour of cancel_and_wait util.

Proposed case here checks correct order of side effects.
"""

import asyncio

import pytest

from python_experiments.utils import cancel_and_wait


async def model_task(marker: list[str], *, suppress: bool) -> None:
    marker.append("model started")
    try:
        await asyncio.sleep(1)
    except asyncio.CancelledError:
        await asyncio.sleep(1)
        marker.append("model cancelled")
        if not suppress:
            raise
    marker.append("model finished")


async def test_cancel_and_wait() -> None:
    marker: list[str] = []
    task = asyncio.create_task(model_task(marker, suppress=False))
    await asyncio.sleep(0.5)
    await cancel_and_wait(task)
    assert marker == ["model started", "model cancelled"]


async def test_cancel_cancel_and_wait() -> None:
    marker: list[str] = []
    task = asyncio.create_task(model_task(marker, suppress=False))
    cancel_task = asyncio.create_task(cancel_and_wait(task))
    cancel_task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await cancel_task


async def test_cancel_and_wait_suppress() -> None:
    marker: list[str] = []
    task = asyncio.create_task(model_task(marker, suppress=True))
    await asyncio.sleep(0.5)
    with pytest.raises(RuntimeError):
        await cancel_and_wait(task)
