from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from datetime import datetime
import random

# Создания приложения
app = Flask(__name__)

def init_db():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        # Аудитории
        cur.execute('''CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            building TEXT DEFAULT ' ',
            floor INTEGER DEFAULT 2
        )''')
        # Бронирования
        cur.execute('''CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY,
            room_id INTEGER,
            booked_by TEXT,
            purpose TEXT,
            start_date TEXT,
            end_date TEXT
        )''')
        # Жалобы / проблемы
        cur.execute('''CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY,
            room_id INTEGER,
            problem_text TEXT,
            urgency INTEGER,
            status TEXT DEFAULT 'active',
            created_date TEXT DEFAULT CURRENT_DATE
        )''')
        # Статистика проблем по месяцам
        cur.execute('''CREATE TABLE IF NOT EXISTS problems_stats (
            month TEXT PRIMARY KEY,
            count INTEGER
        )''')
        
        # Аудитории
        rooms_list = [
            (1, "Minecraft", 2),
            (2, "YouTube", 2),
            (3, "Microsoft", 2),
            (4, "Roblox", 2),
            (5, "Adobe", 2),
            (6, "Android", 2),
            (7, "JS & HTML & CSS", 2),
            (8, "Python", 3)
        ]
        
        for room_id, name, floor in rooms_list:
            cur.execute("INSERT OR IGNORE INTO rooms (id, name, building, floor) VALUES (?, ?, ?, ?)", 
                        (room_id, name, "Главный корпус", floor))
        
        # Заполняем статистику рандомными данными
        cur.execute("SELECT COUNT(*) FROM problems_stats")
        if cur.fetchone()[0] == 0:
            months = ['янв', 'фев', 'мар', 'апр', 'май', 'июн']
            for m in months:
                cur.execute("INSERT INTO problems_stats (month, count) VALUES (?, ?)", (m, random.randint(2, 10)))
        conn.commit()
init_db()

# Функция определения статуса аудиторий
def get_room_status(room_id):
    today = datetime.now().strftime('%Y-%m-%d')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT start_date, end_date, booked_by, purpose FROM bookings WHERE room_id = ?", (room_id,))
        bookings = cur.fetchall()
    for start, end, booked_by, purpose in bookings:
        if start <= today <= end:
            return 'busy', booked_by, purpose, start, end
        elif start > today:
            return 'booked_future', booked_by, purpose, start, end
    return 'free', None, None, None, None
# busy - если сегодня дата поподает в интервал бронирования
# booked_future - если бронирование начинаеться позже чем завтра
# free - если нет активных бронирований

# Главная страница
@app.route('/')
def index():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        # Получаем статистику проблем по месяцам
        stats = cur.execute("SELECT month, count FROM problems_stats ORDER BY rowid LIMIT 6").fetchall()
        # Получаем последнюю активную проблему
        last = cur.execute('''SELECT r.name, c.problem_text, c.urgency 
                              FROM complaints c JOIN rooms r ON c.room_id = r.id 
                              WHERE c.status = 'active' 
                              ORDER BY c.created_date DESC LIMIT 1''').fetchone()
    months = [s[0] for s in stats]
    counts = [s[1] for s in stats]
    return render_template('index.html', months=months, counts=counts, last_problem=last)
