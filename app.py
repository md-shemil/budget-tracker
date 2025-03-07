from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this for security

# Configure Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:2005@localhost:3306/transaction'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    address = db.Column(db.String(255), nullable=True)

# Transaction Model
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    note = db.Column(db.String(255), nullable=True)
    amount = db.Column(db.Float, nullable=False)

# 🚀 Route: Login Page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == '2005':
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

# 🚀 Route: Logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# 🚀 Route: Home Page
@app.route('/home')
def home():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# 🚀 Route: User Profile
@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    user = User.query.first()  # Fetch the first user
    if not user:
        user = User(name="Default User", email="user@example.com", phone="1234567890", address="N/A")
        db.session.add(user)
        db.session.commit()

    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.phone = request.form['phone']
        user.address = request.form['address']
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_profile'))

    return render_template('user_profile.html', user=user)

# 🚀 Route: Transaction History
@app.route('/transaction_history')
def transaction_history():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    transactions = Transaction.query.all()
    return render_template('transaction_history.html', transactions=transactions)

# 🚀 Route: Register a New Transaction
@app.route('/transaction_form', methods=['GET', 'POST'])
def transaction_form():
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        type = request.form['type']
        category = request.form['category']
        note = request.form['note']
        amount = float(request.form['amount'])

        new_transaction = Transaction(type=type, category=category, note=note, amount=amount)
        db.session.add(new_transaction)
        db.session.commit()

        flash('Transaction added successfully!', 'success')
        return redirect(url_for('transaction_history'))

    return render_template('transaction_form.html')

# 🚀 Route: Delete Transaction
@app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    transaction = Transaction.query.get(transaction_id)
    if transaction:
        db.session.delete(transaction)
        db.session.commit()
        flash('Transaction deleted successfully!', 'success')
    else:
        flash('Transaction not found!', 'danger')

    return redirect(url_for('transaction_history'))

# 🚀 Run App
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
