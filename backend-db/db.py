import hashlib
import os
from typing import Optional
from datetime import datetime, timedelta
import re
import secrets

from pydantic import EmailStr
from sqlmodel import Field, SQLModel, create_engine, Session, select

from env import EnvConfig

# CONSTANTS

USERNAME_REGEX = r"^[\w\-]{3,}$"
DISPLAY_NAME_REGEX = r"^[\w\- ]{3,}$"
PASSWORD_REGEX = r"^[\w\-&^/\\$#@!%*().,\"';:[\]{}]{5,30}$"

# MODELS


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(primary_key=True)
    username: str = Field(regex=USERNAME_REGEX, primary_key=True)
    display_name: str = Field(regex=DISPLAY_NAME_REGEX)
    password_hash: bytes
    password_salt: bytes

    def check_password(self, password: str):
        test_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.password_salt, 100000
        )
        return test_hash == self.password_hash


class AuthToken(SQLModel, table=True):
    token: str = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    expiration_date: datetime = datetime.utcnow() + timedelta(1)


# CUSTOM EXCEPTION


class UserError(Exception):
    pass


# FACADE CLASS


class DatabaseFacade:
    def __init__(self, cfg: EnvConfig) -> None:
        self._engine = create_engine(
            f"mysql+pymysql://{cfg.mysql_user}:{cfg.mysql_password}@{cfg.mysql_host}:{cfg.mysql_port}/appdb"
        )
        SQLModel.metadata.create_all(self._engine)

    def create_user(self, email: str, username: str, display_name: str, password: str):
        if not re.match(PASSWORD_REGEX, password):
            raise UserError("Invalid password")
        pass_salt = os.urandom(32)
        pass_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), pass_salt, 100000
        )

        new_user = User(
            email=EmailStr(email),
            username=username,
            display_name=display_name,
            password_hash=pass_hash,
            password_salt=pass_salt,
        )
        with Session(self._engine) as session:
            session.add(new_user)
            session.commit()

    def generate_token(self, username: str, password: str):
        with Session(self._engine) as session:
            statement = select(User).where(User.username == username)
            results = session.exec(statement)
            target_user = results.first()
            if target_user is None:
                raise UserError("Username does not exist")
            if target_user.check_password(password) is False:
                raise UserError("Incorrect password")
            token_str = secrets.token_urlsafe(32)
            if not isinstance(target_user.id, int):
                raise RuntimeError("User was never assigned ID")
            new_token = AuthToken(token=token_str, user_id=target_user.id)
            session.add(new_token)
            session.commit()
        return token_str

    def get_token_user(self, token_str: str):
        with Session(self._engine) as session:
            statement = select(AuthToken, User).where(AuthToken.token == token_str)
            result = session.exec(statement).first()
            if result is None:
                return None
            token, user = result
            if datetime.utcnow() > token.expiration_date:
                session.delete(token)
                return None
        return user
