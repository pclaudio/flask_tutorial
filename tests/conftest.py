import pytest
import tempfile

from flaskr import create_app, Flask
from flaskr.db import get_db, init_db
from flask.testing import FlaskClient, FlaskCliRunner
from os import close, unlink
from os.path import dirname, join

with open(join(dirname(__file__), "data.sql"), "rb") as file:
    _data_sql = file.read().decode("utf8")


class AuthActions(object):
    def __init__(self, client: FlaskClient):
        self._client = client

    def login(self, username: str = "test", password: str = "test"):
        return self._client.post(
            "/auth/login",
            data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def app() -> Flask:
    db_file_descriptor, db_path = tempfile.mkstemp()

    app = create_app({
        "TESTING": True,
        "DATABASE": db_path
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    close(db_file_descriptor)
    unlink(db_path)


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def runner(app: Flask) -> FlaskCliRunner:
    return app.test_cli_runner()


@pytest.fixture
def auth(client):
    return AuthActions(client)
