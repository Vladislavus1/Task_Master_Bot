from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode
import db
import logging


logging.basicConfig(level=logging.INFO)

API_TOKEN = 'your_token'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def set_bot_commands():
    await bot.set_my_commands([
        types.BotCommand("start", "Start a bot"),
        types.BotCommand("help", "Help"),
        types.BotCommand("addtask", "<description> - Adds task with description"),
        types.BotCommand("viewtasks", "Shows a list of your tasks"),
        types.BotCommand("edit", "<task number> <new_description> - Edits a task"),
        types.BotCommand("deletetask", "<task number> - Deletes a task"),
    ])


async def on_startup(dispatcher):
    await set_bot_commands()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_name = message.from_user.username
    user_id = message.from_user.id
    user = db.get_user(user_id)
    if user is None:
        db.add_user(user_name, user_id)
        await message.answer_photo(photo="https://img.freepik.com/free-vector/time-management-marketers-teamwork-media-planning-media-representation-control-reach-your-client-best-media-plan_335657-23.jpg?w=1380&t=st=1714657541~exp=1714658141~hmac=703888b407e438333dc0bd46c34b1d658f476424a1c8ee46e4d67a5cfc297146", caption="<b>Welcome to <code>Task Master Bot(ver: <u>030524.1235</u>)</code></b>.\n\nThis bot created to help you with time management.", parse_mode=ParseMode.HTML)
    else:
        await message.answer(f"Welcome back, <b>{message.from_user.first_name}</b>!", parse_mode=ParseMode.HTML)


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Github", url="https://github.com/Vladislavus1/Task_Master_Bot")
        ],
        [
            InlineKeyboardButton(text="Official aiogram page", url="https://aiogram.dev")
        ]
    ], row_width=1)
    await message.answer_photo(photo="https://img.freepik.com/premium-vector/set-vector-isolated-illustration-task-management-clock_689336-160.jpg", caption="This bot was meticulously crafted to assist you with effective time management. It operates seamlessly through a set of intuitive commands accessible via the menu interface. Moreover, we take pride in its complete open-source nature, and you're invited to explore the underlying code on our GitHub repository.\n\n<u>Additional information:</u>", reply_markup=inline_keyboard, parse_mode=ParseMode.HTML)


@dp.message_handler(commands=['addtask'])
async def add_task(message: types.Message):
    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) == 1:
        await message.reply("<i>Please provide a description for the task.</i>", parse_mode=ParseMode.HTML)
    else:
        user_id = message.from_user.id
        new_description = command_parts[1]
        db.add_task(user_id, new_description)
        await message.reply(f"<i>Task added</i>", parse_mode=ParseMode.HTML)


@dp.message_handler(commands=['viewtasks'])
async def view_tasks(message: types.Message):
    user_id = message.from_user.id
    tasks = db.get_user_tasks(user_id)
    if tasks is None:
        await message.answer("<i>You have no tasks added.</i>", parse_mode=ParseMode.HTML)
    else:
        tasks = [f"{index+1}) <i>{task[0]}</i>\n" for index, task in enumerate(tasks)]
        await message.answer(f"""<b><u>Your tasks:</u></b>\n{''.join(tasks)}""", parse_mode=ParseMode.HTML)


@dp.message_handler(commands=['edit'])
async def edit_task(message: types.Message):
    command_parts = message.text.split(maxsplit=2)

    if len(command_parts) != 3:
        await message.reply("<i>Please provide both task ID and new description.</i>", parse_mode=ParseMode.HTML)
        return

    user_id = message.from_user.id
    task_id = int(command_parts[1])
    new_description = command_parts[2]
    result = db.edit_task(user_id, task_id, new_description)
    if result == 1:
        await message.reply(f"<i>You have no task with the same number.</i>", parse_mode=ParseMode.HTML)
    elif result == -1:
        await message.reply("<i>You have no tasks to edit.</i>", parse_mode=ParseMode.HTML)
    else:
        await message.reply(f"<i>Task <b>№{task_id}</b> edited: <b>{new_description}</b></i>", parse_mode=ParseMode.HTML)


@dp.message_handler(commands=['deletetask'])
async def delete_task(message: types.Message):
    command_parts = message.text.split(maxsplit=1)

    if len(command_parts) == 1:
        await message.reply("<i>Please provide task number.</i>", parse_mode=ParseMode.HTML)
        return

    user_id = message.from_user.id
    task_id = int(command_parts[1])
    result = db.delete_task(user_id, task_id)
    if result == 1:
        await message.reply("<i>You have no task with the same number.</i>", parse_mode=ParseMode.HTML)
    elif result == -1:
        await message.reply("<i>You have no tasks to delete.</i>", parse_mode=ParseMode.HTML)
    else:
        await message.reply(f"<i>Task <b>№{task_id}</b> deleted</i>", parse_mode=ParseMode.HTML)

if __name__ == '__main__':
    db.run_db()
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)