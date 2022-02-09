import pytest

from conftest import AuthActions
from flask import Flask
from flaskr.db import get_db
from flask.testing import FlaskClient
from http import HTTPStatus


def test_index(client: FlaskClient, auth: AuthActions) -> None:
    response = client.get("/")
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get("/")
    assert b"Log Out" in response.data
    assert b"test title" in response.data
    assert b"by test on 2018-01-01" in response.data
    assert b"test\nbody" in response.data
    assert b'href="/1/update"' in response.data


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client: FlaskClient, path: str) -> None:
    response = client.post(path)
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"] == "http://localhost/auth/login"


def test_author_required(app: Flask, client: FlaskClient, auth: AuthActions) -> None:
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute("UPDATE post SET author_id = 2 WHERE id = 1")

    auth.login()
    # current user can't modify other user's post
    assert client.post("/1/update").status_code == HTTPStatus.FORBIDDEN
    assert client.post("/1/delete").status_code == HTTPStatus.FORBIDDEN
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get("/").data


@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client: FlaskClient, auth: AuthActions, path: str) -> None:
    auth.login()
    assert client.post(path).status_code == HTTPStatus.NOT_FOUND


def test_create(client: FlaskClient, auth: AuthActions, app: Flask) -> None:
    auth.login()
    assert client.get("/create").status_code == HTTPStatus.OK

    client.post("/create", data={"title": "created", "body": ""})

    with app.app_context():
        db = get_db()
        count = db.execute("SELECT COUNT(id) FROM post").fetchone()[0]
        assert count == 2


def test_update(client: FlaskClient, auth: AuthActions, app: Flask) -> None:
    auth.login()
    assert client.get("/1/update").status_code == HTTPStatus.OK

    client.post("/1/update", data={"title": "updated", "body": ""})

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post["title"] == "updated"


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client: FlaskClient, auth: AuthActions, path: str) -> None:
    auth.login()
    response = client.post(path, data={"title": "", "body": ""})
    assert b"Title is required." in response.data


def test_delete(client: FlaskClient, auth: AuthActions, app: Flask) -> None:
    auth.login()
    response = client.post("/1/delete")
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"] == "http://localhost/"

    with app.app_context():
        db = get_db()
        post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
        assert post is None
