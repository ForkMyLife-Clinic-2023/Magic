# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.

from telebot.async_telebot import AsyncTeleBot
bot = AsyncTeleBot('6659670636:AAFPGljPDglDRV2pI2wCI3Zg1YxLMxyMmEM')



# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    if message.from_user.username:
        print(message.text,"from",message.from_user.username)

    else:
        if message.from_user.last_name: 
            print(message.text,"from",message.from_user.firs_name,message.from_user.last_name)
        else:
            print(message.text,"from",message.from_user.firs_name)
    await bot.reply_to(message, """\
Blekanov is The Clown\
""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    if message.from_user.username:
        print(message.text,"from",message.from_user.username)

    else:
        if message.from_user.last_name: 
            print(message.text,"from",message.from_user.firs_name,message.from_user.last_name)
        else:
            print(message.text,"from",message.from_user.firs_name)

    await bot.reply_to(message, message.text)


import asyncio
asyncio.run(bot.polling())