import configparser
import sqlite3
import psutil
import time
from datetime import datetime
import os

# Чтение конфигурации
config = configparser.ConfigParser()
config.read('config.ini')

prefix = config['Settings']['prefix']
poll_interval = int(config['Settings']['poll_interval'])
db_path = config['Settings']['db_path']
exclude_processes = config['Filters']['exclude_processes'].split()

# Создание базы данных
db_name = f"{prefix}_{datetime.now().strftime('%Y%m%d')}.db"
db_full_path = os.path.join(db_path, db_name)
conn = sqlite3.connect(db_full_path)
cursor = conn.cursor()

# Создание таблицы
cursor.execute('''
CREATE TABLE IF NOT EXISTS pmonitor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime TEXT,
    processname TEXT,
    username TEXT,
    synced INTEGER DEFAULT 0
)
''')


def get_active_processes():
    processes = []
    for proc in psutil.process_iter(['name', 'username']):
        try:
            pinfo = proc.as_dict(attrs=['name', 'username'])
            if pinfo['name'] not in exclude_processes:
                processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes


def main():
    while True:
        processes = get_active_processes()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for proc in processes:
            cursor.execute('''
            INSERT INTO pmonitor (datetime, processname, username)
            VALUES (?, ?, ?)
            ''', (current_time, proc['name'], proc['username']))

        conn.commit()
        time.sleep(poll_interval)


if __name__ == "__main__":
    main()
