from flask import Flask, render_template, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from flask_bootstrap import Bootstrap5

from forms import *

# =============== Initialize =============== #

# Create SQLAlchemy Base
class Base(DeclarativeBase): 
    pass
db = SQLAlchemy(model_class=Base)

# Init Flask
app = Flask(__name__)

# Add db to Flask
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///application.db"
db.init_app(app)

# Bootstrap + PasswordHasher Init
bootstrap = Bootstrap5(app)
ph = PasswordHasher()

# CSRF Protection
app.config['SECRET_KEY'] = '*@tkQdMMe^}ZW8_KUqTvj!wcr9=_Up8h3zpKpeT=we-xbRY,%.'
csrf = CSRFProtect(app)

# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# =============== Configure Users Database =============== #

class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Login Details
    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String)
    password: Mapped[int] = mapped_column(String)

class Canvas(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Canvas Details
    canvas_token: Mapped[str] = mapped_column(String, unique=True)
    send_email: Mapped[str] = mapped_column(String)
    app_password: Mapped[str] = mapped_column(String)

    # Send Time Details
    send_time: Mapped[int] = mapped_column(Integer)

with app.app_context():
    db.create_all()

# =============== App Routes =============== #
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():

    # Password Hasher
    # try:
    #     # Returns True if successful, or raises an error if mismatched
    #     return ph.verify(hash_from_db, password_attempt)
    # except VerifyMismatchError:
    #     return False

    return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    registerForm = RegisterForm()

    if registerForm.validate_on_submit():
        # Get Form Data
        username = registerForm.username.data
        email = registerForm.email.data
        password = ph.hash(registerForm.password.data)

        # Redirect to log in if user exists already
        exist = db.session.execute(db.select(User).where(User.username == username)).first()
        if exist is not None:
            return redirect(url_for("login"))

        # Creating + Append New User to db
        new_user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("dashboard"))

    return render_template("register.html", registerForm=registerForm)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    logout_user()

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, port=3000)