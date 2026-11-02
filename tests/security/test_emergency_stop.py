import asyncio
import pytest

from backend.app.security.emergency_stop import EmergencyStop


@pytest.mark.asyncio
async def test_stop_cancels_registered_task():
    stop = EmergencyStop()
    started = asyncio.Event()

    async def worker():
        async with stop.register_current_task("t1"):
            started.set()
            await asyncio.sleep(60)

    task = asyncio.create_task(worker())
    await started.wait()
    assert await stop.stop() == 1
    with pytest.raises(asyncio.CancelledError):
        await task
    assert stop.is_stopped


@pytest.mark.asyncio
async def test_stopped_registry_rejects_new_work():
    stop = EmergencyStop()
    await stop.stop()
    with pytest.raises(asyncio.CancelledError):
        async with stop.register_current_task("t2"):
            pass
