from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"
@app.route('/')
def home():
    return render_template('index.html')

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    password TEXT,
                    role TEXT
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    date TEXT,
                    venue TEXT
                )''')

    c.execute('''CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    event_id INTEGER,
    team_name TEXT,
    members TEXT
)''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER,
    team_name TEXT,
    members TEXT
)''')

    conn.commit()
    conn.close()

init_db()

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = user[1]
            session['role'] = user[3]
            session['id'] = user[0]
            return redirect('/dashboard')
        else:
            return "Invalid Login"

    return render_template('login.html')


# ---------------- REGISTER USER ----------------
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  (username, password, role))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('register_user.html')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM events")
    events = c.fetchall()

    event_data = []

    for e in events:
        c.execute("SELECT COUNT(*) FROM participants WHERE event_id=?", (e[0],))
        count = c.fetchone()[0]

        event_data.append({
            'id': e[0],
            'title': e[1],
            'date': e[2],
            'venue': e[3],
            'count': count
        })

    conn.close()

    return render_template('dashboard.html', events=event_data)


# ---------------- CREATE EVENT ----------------
@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if session.get('role') != 'admin':
        return "Access Denied"

    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        venue = request.form['venue']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO events (title, date, venue) VALUES (?, ?, ?)",
                  (title, date, venue))
        conn.commit()
        conn.close()

        return redirect('/dashboard')

    return render_template('create_event.html')


# ---------------- REGISTER FOR EVENT ----------------
@app.route('/register_event/<int:event_id>')
def register_event(event_id):
    user_id = session.get('id')

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO participants (user_id, event_id) VALUES (?, ?)",
              (user_id, event_id))
    conn.commit()
    conn.close()

    return redirect('/dashboard')





# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/participants/<int:event_id>')
def participants(event_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("""
        SELECT team_name, members FROM participants
        WHERE event_id=?
    """, (event_id,))

    data = c.fetchall()
    conn.close()

    return render_template('participants.html', data=data)


# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)