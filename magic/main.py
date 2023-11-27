import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from model_client.client import LLMClient
from aiohttp.client import ClientSession

TOKEN = '6659670636:AAFPGljPDglDRV2pI2wCI3Zg1YxLMxyMmEM'#getenv("BOT_TOKEN")
STARTING_MESSAGE = ("Здравствуйте, это __COMPANY_NAME__. "
   "Ранее вы воспользовались нашими услугами, поэтому мы просим вас оценить качество "
   "предоставленного сервиса от одного до пяти, где пять – «точно порекомендовал бы ваш __COMPANY_TYPE__», "
   "один – «точно не порекомендовал бы ваш __COMPANY_TYPE__»."
)

class SetupConf(StatesGroup):
    choosing_company = State()
    choosing_type = State()
    ready = State()

dp = Dispatcher()

builder = InlineKeyboardBuilder()
builder.row(types.InlineKeyboardButton(
    text="End call", callback_data='[call_ends]')
)
# @dp.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
#     """This handler receives messages with `/start` command

#     Args:
#         message (Message): messages with `/start` command
#     """
#     await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")

@dp.message(StateFilter(None), Command("start"))
async def command_config(message: Message, state: FSMContext) -> None:
    await message.answer(
    text="Company: "
    )
    await state.set_state(SetupConf.choosing_company)

@dp.message(Command("start"))
async def command_config(message: Message, state: FSMContext) -> None:
    state.clear()
    await message.answer(
    text="Company: "
    )
    await state.set_state(SetupConf.choosing_company)

@dp.message(
    SetupConf.choosing_company
)
async def company_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_company=message.text)
    await message.answer(
        text="Type: "
    )
    await state.set_state(SetupConf.choosing_type)

@dp.message(
    SetupConf.choosing_type
)
async def type_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_type=message.text)
    await state.update_data(modelClient=LLMClient('GigaR:500k-exp', ClientSession()))
    data = await state.get_data()
    await state.update_data(last_bot_message=await message.answer(
        text=STARTING_MESSAGE.replace(
                "__COMPANY_NAME__", data['chosen_company']
            ).replace(
                "__COMPANY_TYPE__", data['chosen_type']
            ),
        reply_markup=builder.as_markup()
        )
    )
    await state.set_state(SetupConf.ready)

# @dp.message(StateFilter(None), Command("curr"))
# async def command_curr(message: Message, state: FSMContext) -> None:
#     if message.from_user.id == 1048797336:
#         data = await state.get_data()
#         await message.reply(
#         text=data['chosen_company']+' '+data['chosen_type']
#         )

@dp.message(StateFilter(SetupConf.ready))
async def echo_handler(message: types.Message, state: FSMContext) -> None:
    """Handler will forward receive a message back to the sender if message is text

    Args:
        message (types.Message): Any type of message
    """
    data = await state.get_data()
    responce = await data['modelClient'].request_model(data['chosen_company'], data['chosen_type'], message.text)
    await data['last_bot_message'].edit_reply_markup(reply_markup=None)
    await state.update_data(last_bot_message=await message.answer(
        text=responce.content, reply_markup=builder.as_markup()
        )
    )

@dp.callback_query(F.data == '[call_ends]')
async def end_call(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    responce = await data['modelClient'].request_model(data['chosen_company'], data['chosen_type'], '[call_ends]')
    content = str(responce.content).split('\n',1)
    score = content[0]
    text = content[1]
    await callback.message.answer(
        text=f"Оценка: {score}\nСаммари: {text}"
        )
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None) 
    await callback.answer()



async def main() -> None:
    global bot
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
