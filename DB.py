import sqlite3
from datetime import datetime


def create_table_in_db_by_userid(user_id):
    connection_with_db = sqlite3.connect('database.db')
    work_cur = connection_with_db.cursor()

    work_cur.execute(f'CREATE TABLE IF NOT EXISTS user_{user_id}(request_date TEXT, request_answer TEXT);')
    connection_with_db.commit()


def add_data_to_db(user_id, data):
    connection_with_db = sqlite3.connect('database.db')
    work_cur = connection_with_db.cursor()

    date_time = datetime.strftime(datetime.now(), '%d/%m/%Y %H:%M:%S')
    for_write = (date_time, data)

    work_cur.execute(f'INSERT INTO user_{user_id} VALUES(?, ?);', for_write)
    connection_with_db.commit()


def print_db_info(user_id):
    connection_with_db = sqlite3.connect('database.db')
    work_cur = connection_with_db.cursor()

    work_cur.execute(f"SELECT * FROM user_{user_id};")
    all_results = work_cur.fetchall()
    return all_results


