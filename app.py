from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend suitable for web apps
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

DB_PATH = os.path.join('database', 'finance.db')

@app.route('/')
def home():
    return redirect('/register')  # default redirect to register

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            return "✅ Registration successful! <a href='/login'>Login now</a>"
        except sqlite3.IntegrityError:
            return "❌ Username already exists. Try another."
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch all categories
    cursor.execute("SELECT category_id, name, type FROM categories")
    categories = cursor.fetchall()

    # If POST request (add transaction)
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category_id = int(request.form['category'])
        date = request.form['date']
        note = request.form['note']

        cursor.execute(
            "INSERT INTO transactions (user_id, amount, category_id, date, note) VALUES (?, ?, ?, ?, ?)",
            (session['user_id'], amount, category_id, date, note)
        )
        conn.commit()

    # Handle filters (GET request)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    tx_type = request.args.get('type')

    query = '''
        SELECT t.amount, c.name, c.type, t.date, t.note
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = ?
    '''
    params = [session['user_id']]

    if start_date:
        query += " AND t.date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND t.date <= ?"
        params.append(end_date)
    if tx_type:
        query += " AND c.type = ?"
        params.append(tx_type)

    query += " ORDER BY t.date DESC"
    cursor.execute(query, params)
    transactions = cursor.fetchall()

    # Summary data
    cursor.execute('''
        SELECT c.type, SUM(t.amount)
        FROM transactions t
        JOIN categories c ON t.category_id = c.category_id
        WHERE t.user_id = ?
        GROUP BY c.type
    ''', (session['user_id'],))
    summary_data = dict(cursor.fetchall())
    income = summary_data.get('income', 0)
    expense = summary_data.get('expense', 0)

    # Pie chart
    if income > 0 or expense > 0:
        labels = []
        sizes = []
        if income > 0:
            labels.append("Income")
            sizes.append(income)
        if expense > 0:
            labels.append("Expense")
            sizes.append(expense)

        plt.clf()
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.axis('equal')
        plt.title("Income vs Expense")
        plt.savefig(os.path.join("static", "chart.png"))

    conn.close()

    return render_template("dashboard.html", username=session['username'],
                           income=income, expense=expense,
                           transactions=transactions, categories=categories)

@app.route("/add_transaction", methods=["POST"])
def add_transaction():
    if 'user_id' not in session:
        return redirect('/login')

    amount = request.form['amount']
    category_id = request.form['category_id']
    date = request.form['date']
    note = request.form['note']

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (user_id, amount, category_id, date, note)
        VALUES (?, ?, ?, ?, ?)
    """, (session['user_id'], amount, category_id, date, note))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
