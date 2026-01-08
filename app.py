import os
import sqlite3
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_key_for_journal")
DB_NAME = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute('CREATE TABLE IF NOT EXISTS mood_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, mood TEXT NOT NULL, energy TEXT NOT NULL, note TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        conn.execute('CREATE TABLE IF NOT EXISTS journal_entries (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL, content TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log', methods=('GET', 'POST'))
def log_mood():
    if request.method == 'POST':
        mood = request.form['mood']
        energy = request.form['energy']
        note = request.form['note']
        today = date.today().isoformat()

        conn = get_db_connection()
        conn.execute('INSERT INTO mood_logs (date, mood, energy, note) VALUES (?, ?, ?, ?)',
                     (today, mood, energy, note))
        conn.commit()
        conn.close()
        flash('Mood logged successfully!')
        return redirect(url_for('dashboard'))

    return render_template('log_mood.html', date=date.today())

@app.route('/journal', methods=('GET', 'POST'))
def journal():
    conn = get_db_connection()
    if request.method == 'POST':
        content = request.form['content']
        existing_id = request.form.get('id')
        today = date.today().isoformat()
        
        if existing_id:
            conn.execute('UPDATE journal_entries SET content = ? WHERE id = ?', (content, existing_id))
        else:
            conn.execute('INSERT INTO journal_entries (date, content) VALUES (?, ?)', (today, content))
        conn.commit()
        conn.close()
        return redirect(url_for('journal'))

    entries = conn.execute('SELECT * FROM journal_entries ORDER BY date DESC').fetchall()
    conn.close()
    return render_template('journal.html', entries=entries)

@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()
    logs = conn.execute('SELECT * FROM mood_logs ORDER BY date ASC').fetchall()
    conn.close()

    mood_counts = {'Happy': 0, 'Neutral': 0, 'Stressed': 0, 'Tired': 0, 'Sad': 0}
    dates = []
    energies = []
    
    for log in logs:
        if log['mood'] in mood_counts:
            mood_counts[log['mood']] += 1
        dates.append(log['date'])
        energy_map = {'Low': 1, 'Medium': 2, 'High': 3}
        energies.append(energy_map.get(log['energy'], 0))

    insights = []
    if mood_counts['Stressed'] > mood_counts['Happy']:
        insights.append("Observation: You've reported feeling stressed more often than happy recently.")
    if mood_counts['Happy'] > 0 and logs and logs[-1]['mood'] == 'Happy':
        insights.append("Great! You ended your latest log on a happy note.")
    if not logs:
        insights.append("Start logging your mood to see insights here.")

    data = {
        'mood_counts': mood_counts,
        'dates': dates,
        'energies': energies,
        'insights': insights
    }
    
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)