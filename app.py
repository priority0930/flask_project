from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secret_key'
DATABASE = 'survey.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS survey (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT UNIQUE,
                 chosen TEXT)''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        session['name'] = request.form['name']
        return redirect(url_for('choose'))
    return render_template('home.html')

@app.route('/choose', methods=['GET', 'POST'])
def choose():
    if 'name' not in session:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        name = session['name']
        chosen = request.form['chosen']
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO survey (name, chosen) VALUES (?, ?)', (name, chosen))
        conn.commit()
        conn.close()
        return redirect(url_for('result'))
    
    return render_template('choose.html')

@app.route('/result')
def result():
    return render_template('result.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
