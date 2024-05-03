import sqlite3
import random
import string

connection = sqlite3.connect("bot_database.db")
cursor = connection.cursor()


def run_db():
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_name TEXT, user_id TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tasks (task_description TEXT, task_id text, task_creator TEXT, FOREIGN KEY(task_creator) REFERENCES users(user_id))")


def add_user(user_name, user_id):
    cursor.execute("INSERT INTO users (user_name, user_id) VALUES (?, ?)", (user_name, user_id))
    connection.commit()


def add_task(user_id, task_description):
    cursor.execute("INSERT INTO tasks (task_description, task_id, task_creator) VALUES (?, ?, ?)", (task_description,''.join(random.choice(string.ascii_letters + string.digits) for _ in range(15)), user_id))
    connection.commit()


def edit_task(user_id, task_id, new_description):
    tasks = get_user_tasks(user_id)
    if tasks is None:
        return -1
    else:
        try:
            task = tasks[task_id-1]
            cursor.execute(f'UPDATE tasks SET task_description="{new_description}" WHERE task_id="{task[1]}"')
            connection.commit()
            return 0
        except IndexError:
            return 1


def delete_task(user_id, task_id):
    tasks = get_user_tasks(user_id)
    if tasks is None:
        return -1
    else:
        try:
            task = tasks[task_id-1]
            cursor.execute(f'DELETE FROM tasks WHERE task_id="{task[1]}"')
            connection.commit()
            return 0
        except IndexError:
            return 1


def get_user(user_id):
    cursor.execute(f"""SELECT * FROM users WHERE user_id = ?""", (user_id,))
    users = cursor.fetchall()
    return users


def get_user_tasks(user_id):
    cursor.execute(f"""SELECT * FROM tasks WHERE task_creator = ?""", (user_id,))
    tasks = cursor.fetchall()
    return tasks