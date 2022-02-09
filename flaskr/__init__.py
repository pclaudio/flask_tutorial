from flask import Flask
from http import HTTPStatus
from os import makedirs, path


def create_app(test_config=None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=path.join(app.instance_path, "flaskr.sqlite")
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        makedirs(app.instance_path)
    except OSError:
        pass

    @app.get("/hello")
    def hello() -> tuple[str, int]:
        return "Hello, World!", HTTPStatus.OK

    from flaskr import db
    db.init_app(app)

    from flaskr import auth
    app.register_blueprint(auth.blueprint)

    from flaskr import blog
    app.register_blueprint(blog.blueprint)
    app.add_url_rule("/", endpoint="index")

    return app
