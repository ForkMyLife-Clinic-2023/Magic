from unittest.mock import AsyncMock

import pytest
from aiogram.utils.markdown import hbold

from magic.main import command_start_handler


@pytest.mark.asyncio
async def test_start_handler():
    message_mock = AsyncMock()
    await command_start_handler(message=message_mock)
    message_mock.answer.assert_called_with(
        f"Hello, {hbold(message_mock.from_user.full_name)}!"
    )
