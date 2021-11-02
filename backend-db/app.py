import warnings

from sqlalchemy.exc import SAWarning


from pydantic import BaseModel

from broker import run_rabbit_app
from db import DatabaseFacade
from env import EnvConfig

db: DatabaseFacade


class LoginRequest(BaseModel):
    username: str
    password: str


def handle_login(req_body: dict):
    rq = LoginRequest(**req_body)
    token = db.generate_token(rq.username, rq.password)
    return {"token": token}


# App entrypoint
def main():
    warnings.simplefilter("ignore", category=SAWarning)

    route_handlers = {"db.auth.login": handle_login}

    cfg = EnvConfig()

    global db
    db = DatabaseFacade(cfg)

    run_rabbit_app(
        "backend-db",
        cfg.broker_host,
        cfg.broker_port,
        cfg.broker_user,
        cfg.broker_password,
        route_handlers,
    )


if __name__ == "__main__":
    main()
