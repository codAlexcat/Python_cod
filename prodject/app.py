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

# Аудитории
@app.route('/rooms')
def rooms():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        # список всех аудиторий из базы данных
        rooms_data = cur.execute("SELECT id, name, building, floor FROM rooms ORDER BY id").fetchall()
    rooms_list = []
    # Для каждой аудитории вызываем функцию для проверки статуса
    for room_id, name, building, floor in rooms_data:
        status, booked_by, purpose, start, end = get_room_status(room_id)
        # Считаем количество активных проблем если их больше 0
        cur2 = conn.cursor()
        cur2.execute("SELECT COUNT(*) FROM complaints WHERE room_id=? AND status='active'", (room_id,))
        # Проверяем, есть ли активные проблемы
        has_problems = cur2.fetchone()[0] > 0
        
        # Получаем все активные бронирования для этой аудитории (где дата окончания >= сегодня)
        cur3 = conn.cursor()
        cur3.execute("SELECT booked_by, purpose, start_date, end_date FROM bookings WHERE room_id=? AND end_date >= date('now') ORDER BY start_date", (room_id,))
        all_bookings = cur3.fetchall()
        # собираем все данные с словарь и добовляем в список
        rooms_list.append({
            'id': room_id,
            'name': name,
            'building': building,
            'floor': floor,
            'status': status,
            'booked_by': booked_by,
            'purpose': purpose,
            'start_date': start,
            'end_date': end,
            'is_working': not has_problems,
            'all_bookings': all_bookings
        })
        # Отоброжаем шаблон rooms.html и передаёт в него список аудиторий
    return render_template('rooms.html', rooms=rooms_list)

# Форма бронирования
@app.route('/book_room/<int:room_id>')
def book_form(room_id):
    # Находит название аудитории по ID. Если нет то перенопровляем на список аудиторий. Если есть то показываем форму бронирования 
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        room = cur.execute("SELECT name FROM rooms WHERE id=?", (room_id,)).fetchone()
    if not room:
        return redirect(url_for('rooms'))
    return render_template('book_form.html', room_id=room_id, room_name=room[0])

# Обработка бронирования
@app.route('/book', methods=['POST'])
def book_room():
    room_id = request.form['room_id']
    booked_by = request.form['booked_by']
    purpose = request.form['purpose']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO bookings (room_id, booked_by, purpose, start_date, end_date) VALUES (?,?,?,?,?)",
                    (room_id, booked_by, purpose, start_date, end_date))
        conn.commit()
    return redirect(url_for('rooms'))

# --- Список аудиторий для жалоб ---
@app.route('/complaints')
def complaints_list():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        rooms = cur.execute("SELECT id, name FROM rooms ORDER BY id").fetchall()
        print("rooms data:", rooms)  # Должно быть что-то вроде [(1, 'Аудитория 1'), (2, 'Аудитория 2'), ...]
    return render_template('complaints_list.html', rooms=rooms)

# --- Проблемы конкретной аудитории ---
@app.route('/room_complaints/<int:room_id>')
def room_complaints(room_id):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        room = cur.execute("SELECT name FROM rooms WHERE id=?", (room_id,)).fetchone()
        if not room:
            return redirect(url_for('complaints_list'))
        problems = cur.execute("SELECT id, problem_text, urgency, created_date FROM complaints WHERE room_id=? AND status='active' ORDER BY urgency DESC", (room_id,)).fetchall()
    return render_template('room_complaints.html', room_id=room_id, room_name=room[0], problems=problems)

# --- Добавление жалобы ---
@app.route('/add_complaint', methods=['POST'])
def add_complaint():
    room_id = request.form['room_id']
    problem_text = request.form['problem_text']
    urgency = request.form['urgency']
    current_month = datetime.now().strftime('%b').lower()
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO complaints (room_id, problem_text, urgency, status) VALUES (?,?,?, 'active')",
                    (room_id, problem_text, urgency))
        cur.execute("INSERT INTO problems_stats (month, count) VALUES (?, 1) ON CONFLICT(month) DO UPDATE SET count = count + 1", (current_month,))
        conn.commit()
    return redirect(url_for('room_complaints', room_id=room_id))

# --- Снятие проблемы ---
@app.route('/resolve_complaint', methods=['POST'])
def resolve_complaint():
    complaint_id = request.form['complaint_id']
    room_id = request.form['room_id']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("UPDATE complaints SET status='resolved' WHERE id=?", (complaint_id,))
        conn.commit()
    return redirect(url_for('room_complaints', room_id=room_id))

# --- Помощь ---
@app.route('/help')
def help_page():
    contacts = [
        {'role': 'Учебная часть', 'phone': '8-800-555-01-01', 'email': 'study@college.ru'},
        {'role': 'Ремонт проекторов', 'phone': '8-800-555-01-02', 'email': 'tech@college.ru'},
        {'role': 'Директор', 'phone': '8-800-555-01-03', 'email': 'director@college.ru'},
        {'role': 'Системный администратор', 'phone': '8-800-555-01-04', 'email': 'admin@college.ru'},
    ]
    return render_template('help.html', contacts=contacts)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
