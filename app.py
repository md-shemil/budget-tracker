from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import mysql.connector
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)
app.secret_key = 'secretkey'

# Database Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2005",
    database="budget_tracker"
)
cursor = db.cursor()

# ------------------ INDEX ------------------
@app.route('/')
def index():
    return redirect(url_for('login'))

# ------------------ LOGIN ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE user_id=%s AND password=%s", (user_id, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user[2]
            session['username'] = user[1]
            flash("Login Successful", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid Credentials", "danger")

    return render_template('login.html')

# ------------------ SIGNUP ------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        user_id = request.form['user_id']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for('signup'))

        cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        if cursor.fetchone():
            flash("User ID already taken", "danger")
            return redirect(url_for('signup'))

        cursor.execute(
            "INSERT INTO users (username, user_id, email, phone, password) VALUES (%s, %s, %s, %s, %s)",
            (username, user_id, email, phone, password)
        )
        db.commit()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

# ------------------ HOME ------------------
@app.route('/home')
def home():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor.execute("SELECT * FROM transactions WHERE user_id = %s ORDER BY date DESC", (user_id,))
        transactions = cursor.fetchall()

        cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id = %s AND type = 'Income'", (user_id,))
        total_income = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id = %s AND type = 'Expense'", (user_id,))
        total_expense = cursor.fetchone()[0] or 0

        balance = total_income - total_expense

        return render_template('home.html',
                               username=session['username'],
                               transactions=transactions,
                               total_income=total_income,
                               total_expense=total_expense,
                               balance=balance)
    else:
        flash("Please login to continue", "danger")
        return redirect(url_for('login'))

# ------------------ ADD TRANSACTION ------------------
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    if 'user_id' in session:
        user_id = session['user_id']
        desc = request.form['description']
        amt = float(request.form['amount'])
        t_type = request.form['type']
        today = date.today()

        # Check current balance before adding expense
        if t_type == 'Expense':
            cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id = %s AND type = 'Income'", (user_id,))
            total_income = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id = %s AND type = 'Expense'", (user_id,))
            total_expense = cursor.fetchone()[0] or 0

            balance = total_income - total_expense

            # Prevent adding expense if it exceeds the available balance
            if amt > balance:
                # Insert a notification into the notifications table
                notification_message = f"Attempted expense of {amt} exceeds available balance."
                cursor.execute("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (user_id, notification_message))
                db.commit()

                flash("Insufficient balance to add this expense", "danger")
                return redirect(url_for('home'))

        cursor.execute("INSERT INTO transactions (user_id, date, description, amount, type) VALUES (%s, %s, %s, %s, %s)",
                       (user_id, today, desc, amt, t_type))
        db.commit()

        # Insert a notification after successful transaction
        if t_type == 'Expense':
            notification_message = f"Expense of {amt} added successfully."
            cursor.execute("INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (user_id, notification_message))
            db.commit()

        flash("Transaction Added!", "success")
        return redirect(url_for('home'))
    else:
        flash("Please login first", "danger")
        return redirect(url_for('login'))


# ------------------ ADD LOAN ------------------
@app.route('/add_loan', methods=['GET', 'POST'])
def add_loan():
     
    if 'user_id' not in session:
        flash("Please login to continue", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        lender_name = request.form['lender_name']
        amount = float(request.form['amount'])
        interest_rate = float(request.form['interest_rate'])
        due_date = request.form['due_date']
        description = request.form['description']
        user_id = session['user_id']

        cursor.execute("INSERT INTO loans (user_id, lender_name, amount, remaining_amount, interest_rate, due_date, description) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (user_id, lender_name, amount, amount, interest_rate, due_date, description))
        db.commit()
        flash("Loan added successfully!", "success")
        return redirect(url_for('account'))
    if 'user_id' in session:
        user_id = session['user_id']
        cursor.execute("SELECT username, email, phone, user_id, password FROM users WHERE user_id=%s", (user_id,))
        user = cursor.fetchone()

        # Get user loans
        cursor.execute("SELECT * FROM loans WHERE user_id = %s", (user_id,))
        loans = cursor.fetchall()
    


    return render_template('add_loan.html',user=user, loans=loans)

@app.route('/income')
def income():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor.execute("SELECT * FROM transactions WHERE user_id = %s ORDER BY date DESC", (user_id,))
        transactions = cursor.fetchall()
        return render_template('income.html', transactions=transactions)
    else:
        flash("Please login to continue", "danger")
        return redirect(url_for('login'))

@app.route('/expense')
def expense():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor.execute("SELECT * FROM transactions WHERE user_id = %s ORDER BY date DESC", (user_id,))
        transactions = cursor.fetchall()
        return render_template('expense.html', transactions=transactions)
    else:
        flash("Please login to continue", "danger")
        return redirect(url_for('login'))


# ------------------ LOAN OVERVIEW ------------------
@app.route('/account')
def account():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor.execute("SELECT username, email, phone, user_id, password FROM users WHERE user_id=%s", (user_id,))
        user = cursor.fetchone()

        # Get user loans
        cursor.execute("SELECT * FROM loans WHERE user_id = %s", (user_id,))
        loans = cursor.fetchall()

        return render_template('account.html', user=user, loans=loans)
    else:
        flash("Please login to continue", "danger")
        return redirect(url_for('login'))

@app.route('/account_authenticate', methods=['GET', 'POST'])
def account_authenticate():
    if 'user_id' not in session:
        flash("Please login to continue", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        user_id = session['user_id']
        current_password = request.form['current_password']

        cursor.execute("SELECT password FROM users WHERE user_id=%s", (user_id,))
        result = cursor.fetchone()

        if result and result[0] == current_password:
            return redirect(url_for('account_edit'))
        else:
            flash("Invalid password", "danger")
            return redirect(url_for('account_authenticate'))

    return render_template('account_authenticate.html')

@app.route('/account_edit', methods=['GET', 'POST'])
def account_edit():
    if 'user_id' not in session:
        flash("Please login to continue", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        cursor.execute("UPDATE users SET username=%s, email=%s, phone=%s, password=%s WHERE user_id=%s",
                       (username, email, phone, password, user_id))
        db.commit()
        flash("Account details updated successfully!", "success")
        return redirect(url_for('account'))

    cursor.execute("SELECT username, email, phone FROM users WHERE user_id=%s", (user_id,))
    user = cursor.fetchone()
    return render_template('account_edit.html', user=user)

# ------------------ UPDATE LOAN ------------------
@app.route('/update_loan/<int:loan_id>', methods=['GET', 'POST'])
def update_loan(loan_id):
    if 'user_id' not in session:
        flash("Please login to continue", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Fetch loan details
    cursor.execute("SELECT * FROM loans WHERE id = %s AND user_id = %s", (loan_id, user_id))
    loan = cursor.fetchone()

    if request.method == 'POST':
        payment = float(request.form['payment'])

        cursor.execute("SELECT remaining_amount FROM loans WHERE id = %s", (loan_id,))
        current_remaining = cursor.fetchone()[0]

        new_remaining = max(0, current_remaining - payment)

        cursor.execute("UPDATE loans SET remaining_amount = %s WHERE id = %s", (new_remaining, loan_id))
        db.commit()
        flash("Loan updated successfully!", "success")
        return redirect(url_for('account'))

    return render_template('update_loan.html', loan=loan)

# ------------------ DOWNLOAD PDF ------------------
@app.route('/download_pdf')
def download_pdf():
    if 'user_id' not in session:
        flash("Please login to continue", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    username = session['username']

    cursor.execute("SELECT * FROM transactions WHERE user_id = %s ORDER BY date DESC", (user_id,))
    transactions = cursor.fetchall()

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, f"Transaction History for {username}")

    p.setFont("Helvetica", 12)
    y = height - 80
    p.drawString(50, y, "Date")
    p.drawString(150, y, "Description")
    p.drawString(320, y, "Amount")
    p.drawString(420, y, "Type")
    y -= 20

    for t in transactions:
        if y < 50:
            p.showPage()
            y = height - 50
        p.drawString(50, y, str(t[2]))       # Date
        p.drawString(150, y, t[3])           # Description
        p.drawString(320, y, str(t[4]))      # Amount
        p.drawString(420, y, t[5])           # Type
        y -= 20

    p.save()
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers['Content-Disposition'] = 'attachment; filename=transactions.pdf'
    response.mimetype = 'application/pdf'
    return response



@app.route('/loan/<int:loan_id>/paid', methods=['POST'])
def mark_loan_paid(loan_id):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='2005',
        database='budget_tracker'
    )
    cursor = conn.cursor()

    # Fetch loan details
    cursor.execute("SELECT amount, description FROM loans WHERE id = %s", (loan_id,))
    loan = cursor.fetchone()
    if not loan:
        flash("Loan not found.", "error")
        return redirect(url_for('add_loan'))

    amount, description = loan
    user_id = session['user_id']

    # Get the current balance
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id = %s AND type = 'Income'", (user_id,))
    total_income = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id = %s AND type = 'Expense'", (user_id,))
    total_expense = cursor.fetchone()[0] or 0

    balance = total_income - total_expense

    # Check if the user has enough balance to pay off the loan
    if amount > balance:
        flash("Insufficient balance to mark the loan as paid.", "danger")
        return redirect(url_for('add_loan'))

    # Add the loan amount to expenses if balance is sufficient
    cursor.execute(
        "INSERT INTO transactions (user_id, date, description, amount, type) VALUES (%s, NOW(), %s, %s, %s)",
        (user_id, "Loan repayment: " + description, amount, "Expense")
    )

    # Optionally: delete or archive loan
    cursor.execute("DELETE FROM loans WHERE id = %s", (loan_id,))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Loan marked as paid and added to expenses.", "success")
    return redirect(url_for('add_loan'))


#----------------notification------------------
@app.route('/notifications')
def notifications():
    if 'user_id' in session:
        user_id = session['user_id']
        
        # Fetch notifications from the database for the logged-in user
        cursor.execute("SELECT id, user_id, message, timestamp FROM notifications WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))
        notifications = cursor.fetchall()
        
        # Debugging: Check if notifications are being fetched correctly
        print("Fetched notifications:", notifications)
        
        return render_template('notifications.html', notifications=notifications)
    else:
        flash("Please log in to continue", "danger")
        return redirect(url_for('login'))

# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for('login'))

# ------------------ MAIN ------------------
if __name__ == '__main__':
    app.run(debug=True)
