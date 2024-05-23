from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import import_string
url_quote = import_string('werkzeug.urls:url_quote')
import random

app = Flask(__name__, template_folder='templates')
app.secret_key = 'fhjvnjkf7392839'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-user-collection.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)

with app.app_context():
    db.create_all()

class ATM():
    def __init__(self):
        self.current_balance = session.get('current_balance', 1000)
        self.pin = session.get('pin', "0000")

    def deposit(self, amount):
        self.current_balance += amount
        session['current_balance'] = self.current_balance

    def withdraw(self, amount):
        self.current_balance -= amount
        session['current_balance'] = self.current_balance

    def change_pin(self, pin):
        self.pin = pin
        session['pin'] = self.pin

@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        username = request.form["username"]
        password = request.form["password"]
        random_id = random.randint(1, 1000000000)
        with app.app_context():
            new_user = User(id=random_id, first_name=first_name, last_name=last_name, user_name=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return render_template("dashboard.html", current_balance=1000, pin="0000")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        user_name = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(user_name=user_name, password=password).first()
        if user:
            session['current_balance'] = 1000  # Initialize session with default balance
            session['pin'] = "0000"  # Initialize session with default PIN
            return render_template("dashboard.html", current_balance=1000, pin="0000")
        else:
            flash("Invalid Credentials")
            return render_template("index.html")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard_page():
    atm = ATM()
    return render_template("dashboard.html", current_balance=atm.current_balance, pin=str(atm.pin))

@app.route("/deposit", methods=["POST"])
def deposit_money():
    atm = ATM()
    amount = int(request.form["deposit_amount"])
    atm.deposit(amount)
    flash("Money deposited successfully!")
    return redirect(url_for("dashboard_page"))

@app.route("/withdraw", methods=["POST"])
def withdraw_money():
    atm = ATM()
    amount = int(request.form["withdraw_amount"])
    atm.withdraw(amount)
    flash("Money withdrawn successfully!")
    return redirect(url_for("dashboard_page"))

@app.route("/change_pin", methods=["POST"])
def change_pin():
    atm = ATM()
    new_pin = int(request.form["new_pin"])
    atm.change_pin(new_pin)
    flash("PIN changed successfully!")
    return redirect(url_for("dashboard_page"))

@app.route("/logout")
def logout():
    session.clear()  # Clear session data
    return redirect(url_for('home_page'))

if __name__ == "__main__":
    app.run(debug=True)
