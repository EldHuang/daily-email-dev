from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from flask_wtf.csrf import CSRFProtect

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from forms import *

# =============== Initialize SQLAlchemy + Flask + Boostrap + Argon2id Hasher =============== #

class Base(DeclarativeBase):
  pass
db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///application.db"
db.init_app(app)

bootstrap = Bootstrap5(app)

ph = PasswordHasher()

app.config['SECRET_KEY'] = '*@tkQdMMe^}ZW8_KUqTvj!wcr9=_Up8h3zpKpeT=we-xbRY,%.'
csrf = CSRFProtect(app)

# =============== Configure Users Database =============== #

class User(db.Model):
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
    # Replaces check_password_hash() with argon2

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
        username = registerForm.username.data
        email = registerForm.email.data
        password = ph.hash(registerForm.password.data)

        new_user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

    return render_template("register.html", registerForm=registerForm)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True, port=3000)