import warnings

from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.exc import SAWarning

from broker import run_rabbit_app
from db import DatabaseFacade
from env import EnvConfig

db: DatabaseFacade


# token.create


class TokenGenBody(BaseModel):
    username: str
    password: str


def handle_token_gen(req_body: dict):
    rq = TokenGenBody(**req_body)
    token = db.generate_token(rq.username, rq.password)
    return {"token": token}


# token.delete


class TokenDeleteBody(BaseModel):
    token: str


def handle_token_delete(req_body: dict):
    rq = TokenDeleteBody(**req_body)
    db.delete_token(rq.token)


# user.create


class UserCreateBody(BaseModel):
    username: str
    display_name: str
    email: EmailStr
    password: str


def handle_user_create(req_body: dict):
    rq = UserCreateBody(**req_body)
    db.create_user(rq.email, rq.username, rq.display_name, rq.password)


# run app


def main():
    warnings.simplefilter("ignore", category=SAWarning)

    route_handlers = {
        "db.token.generate": handle_token_gen,
        "db.token.delete": handle_token_delete,
        "db.user.create": handle_user_create,
    }

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
