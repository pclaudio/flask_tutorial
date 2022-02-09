from flask import abort, Blueprint, flash, g, redirect, request, render_template, Response, url_for
from flaskr.auth import login_required
from flaskr.db import get_db
from http import HTTPStatus
from typing import Union

blueprint = Blueprint("blog", __name__)


def get_post(post_id: int, check_author: bool = True):
    post = get_db().execute(
        "SELECT * FROM post JOIN user ON post.author_id = user.id WHERE post.id = ?", (post_id, )
    ).fetchone()

    if post is None:
        abort(HTTPStatus.NOT_FOUND, f"Post id {post_id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(HTTPStatus.FORBIDDEN)

    return post


@blueprint.get("/")
def get_index() -> str:
    db = get_db()
    posts = db.execute("SELECT * FROM post JOIN user ON post.author_id = user.id ORDER BY created DESC").fetchall()

    return render_template("blog/index.html", posts=posts)


@blueprint.get("/create")
@login_required
def get_create() -> str:
    return render_template("blog/create.html")


@blueprint.post("/create")
@login_required
def post_create() -> Union[str, Response]:
    title = request.form["title"]
    body = request.form["body"]
    error = None

    if not title:
        error = "Title is required."

    if error is not None:
        flash(error, "error")
    else:
        db = get_db()
        db.execute("INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)", (title, body, g.user["id"]))

        return redirect(url_for("blog.get_index"))

    return render_template("blog/create.html")


@blueprint.get("/<int:post_id>/update")
@login_required
def get_update(post_id: int):
    post = get_post(post_id)

    return render_template('blog/update.html', post=post)


@blueprint.post("/<int:post_id>/update")
@login_required
def post_update(post_id: int) -> Union[str, Response]:
    post = get_post(post_id)

    title = request.form["title"]
    body = request.form["body"]
    error = None

    if not title:
        error = "Title is required."

    if error is not None:
        flash(error, "error")
    else:
        db = get_db()
        db.execute("UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, post_id))

        return redirect(url_for("blog.get_index"))

    return render_template('blog/update.html', post=post)


@blueprint.post("/<int:post_id>/delete")
@login_required
def post_delete(post_id: int) -> Response:
    post = get_post(post_id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (post["id"],))

    return redirect(url_for("blog.get_index"))
