import configparser
import sqlite3
import psutil
import logging
import time
import os
import requests

from datetime import datetime


logging.basicConfig(filename='pmonitor.log', level=logging.ERROR, format='%(asctime)s %(levelname)s:%(message)s')

config = configparser.ConfigParser()
config.read('/etc/pmonitor/pmonitor.conf')

prefix = config['Settings']['prefix']
poll_interval = int(config['Settings']['poll_interval'])
db_path = config['Settings']['db_path']
exclude_processes = config['Filters']['exclude_processes'].split()
server_url = config['Settings']['server_url']

db_name = f"{prefix}_{datetime.now().strftime('%Y%m%d')}.db"
db_full_path = os.path.join(db_path, db_name)
conn = sqlite3.connect(db_full_path)
cursor = conn.cursor()

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


def sync_with_server():
    try:
        cursor.execute('SELECT id, datetime, processname, username FROM pmonitor WHERE synced = 0')
        unsynced_data = cursor.fetchall()
        if unsynced_data:
            response = requests.post(server_url, json=unsynced_data)
            if response.status_code == 200:
                cursor.execute('UPDATE pmonitor SET synced = 1 WHERE synced = 0')
                conn.commit()
    except requests.exceptions.RequestException as exc:
        logging.error(f'Failed to sync with server: {exc}')


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
        sync_with_server()
        time.sleep(poll_interval)


if __name__ == "__main__":
    main()
