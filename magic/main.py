import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold

TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()


class OperatingBot(StatesGroup):
    choose_company = State()


class CompaniesCallbackFactory(CallbackData, prefix="company"):
    name: str


def get_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Рога и копыта",
        callback_data=CompaniesCallbackFactory(name="Рога и копыта"),
    )
    builder.button(
        text="Биба и Боба", callback_data=CompaniesCallbackFactory(name="Биба и Боба")
    )
    builder.button(
        text="Лёлик и Болик",
        callback_data=CompaniesCallbackFactory(name="Лёлик и Болик"),
    )
    builder.adjust(3)
    return builder.as_markup()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with `/start` command

    Args:
        message (Message): messages with `/start` command
    """
    await message.answer(
        f"Hello, {hbold(message.from_user.full_name)}!\nTo open the menu, type /menu"
    )


@dp.message(Command("menu"))
async def command_menu_handler(message: Message) -> None:
    """This handler receives messages with `/menu` command
    and writes a message with choice of company

    Args:
        message (Message): messages with `/menu` command
    """
    await message.answer("Choose a company:", reply_markup=get_keyboard())


@dp.callback_query(CompaniesCallbackFactory.filter())
async def callbacks_switch_domen(
    callback: types.CallbackQuery,
    callback_data: CompaniesCallbackFactory,
    state: FSMContext,
):
    await callback.message.answer("switching domen to '{}'".format(callback_data.name))
    await state.update_data(chosen_company=callback_data.name)
    await state.set_state(OperatingBot.choose_company)
    await callback.answer()


@dp.message()
async def echo_handler(message: types.Message, state: FSMContext) -> None:
    """Handler will forward receive a message back to the sender

    Args:
        message (types.Message): Any type of message
    """
    cur_state = await state.get_state()
    if cur_state == "OperatingBot:choose_company":
        data = await state.get_data()
        await message.reply("{}: {}".format(data["chosen_company"], message.text))
    else:
        await message.reply(message.text)


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
