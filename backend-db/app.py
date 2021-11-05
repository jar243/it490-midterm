import warnings

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.exc import SAWarning

from broker import run_rabbit_app
from db import DatabaseFacade
from env import EnvConfig

db: DatabaseFacade

# constants

USERNAME_FIELD = Field(regex=r"^[\w\-]{3,}$")
DISPLAY_NAME_FIELD = Field(regex=r"^[\w\-' ]{3,}$")
BIO_FIELD = Field(max_length=500)
PASSWORD_REGEX = Field(regex=r"^[\w\-&^/\\$#@!%*().,\"';:[\]{}]{5,30}$")


# shared models


class TokenRequest(BaseModel):
    token: str


# token.create


class TokenGenRequest(BaseModel):
    username: str = USERNAME_FIELD
    password: str = PASSWORD_REGEX


def handle_token_gen(req_body: dict):
    rq = TokenGenRequest(**req_body)
    token = db.generate_token(rq.username, rq.password)
    return {"token": token}


# token.get-user


def handle_token_get_user(req_body: dict):
    rq = TokenRequest(**req_body)
    user = db.get_token_user(rq.token)
    return user.dict(include={"username": ..., "display_name": ...})


# token.delete


def handle_token_delete(req_body: dict):
    rq = TokenRequest(**req_body)
    db.delete_token(rq.token)


# user.create


class UserCreateRequest(BaseModel):
    username: str = USERNAME_FIELD
    display_name: str = DISPLAY_NAME_FIELD
    email: EmailStr
    password: str = PASSWORD_REGEX


def handle_user_create(req_body: dict):
    rq = UserCreateRequest(**req_body)
    db.create_user(rq.email, rq.username, rq.display_name, rq.password)
    token = db.generate_token(rq.username, rq.password)
    return {"token": token}


# user.get


class UserGetPublicRequest(BaseModel):
    username: str = USERNAME_FIELD


def handle_user_get_public(req_body: dict):
    rq = UserGetPublicRequest(**req_body)
    user = db.get_user(rq.username)
    return user.dict(
        include={"username": ..., "display_name": ..., "bio": ..., "movie_ratings": ...}
    )


def handle_user_get_private(req_body: dict):
    rq = TokenRequest(**req_body)
    user = db.get_token_user(rq.token)
    return user.dict(exclude={"password_hash": ..., "password_salt": ...})


# user.update


class UserUpdateRequest(BaseModel):
    token: str
    display_name: str = DISPLAY_NAME_FIELD
    bio: str = BIO_FIELD


def handle_user_update(req_body: dict):
    rq = UserUpdateRequest(**req_body)
    user = db.get_token_user(rq.token)
    user.display_name = rq.display_name
    user.bio = rq.bio


# run app


def main():
    warnings.simplefilter("ignore", category=SAWarning)

    route_handlers = {
        "db.token.generate": handle_token_gen,
        "db.token.get-user": handle_token_get_user,
        "db.token.delete": handle_token_delete,
        "db.user.create": handle_user_create,
        "db.user.get.public": handle_user_get_public,
        "db.user.get.private": handle_user_get_private,
        "db.user.update": handle_user_update,
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
