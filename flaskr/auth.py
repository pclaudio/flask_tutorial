from flaskr.db import get_db
from flask import Blueprint, flash, g, redirect, request, render_template, Response, session, url_for
from functools import wraps
from sqlite3 import IntegrityError
from typing import Union
from werkzeug.security import check_password_hash, generate_password_hash

blueprint = Blueprint("auth", __name__, url_prefix="/auth")


@blueprint.get("/register")
def get_register() -> str:
    return render_template("auth/register.html")


@blueprint.post("/register")
def post_register() -> Union[str, Response]:
    username = request.form["username"]
    password = request.form["password"]
    db = get_db()
    error = None

    if not username:
        error = "Username is required."
    elif not password:
        error = "Password is required."

    if error is None:
        try:
            db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password)),
            )
        except IntegrityError:
            error = f"User {username} is already registered."
        else:
            return redirect(url_for("auth.get_login"))

    flash(error, "error")

    return render_template("auth/register.html")


@blueprint.get("/login")
def get_login() -> str:
    return render_template('auth/login.html')


@blueprint.post("/login")
def post_login() -> Union[str, Response]:
    username = request.form["username"]
    password = request.form["password"]
    db = get_db()
    error = None
    user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()

    if user is None:
        error = "Incorrect username."
    elif not check_password_hash(user["password"], password):
        error = "Incorrect password."

    if error is None:
        session.clear()
        session["user_id"] = user["id"]
        return redirect(url_for("index"))

    flash(error, "error")

    return render_template('auth/login.html')


@blueprint.get("/logout")
def get_logout() -> Response:
    session.clear()
    return redirect(url_for("index"))


@blueprint.before_app_request
def load_logged_in_user() -> None:
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.get_login"))

        return view(**kwargs)

    return wrapped_view
