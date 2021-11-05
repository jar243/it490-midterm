import hashlib
import re
import secrets
from datetime import datetime, timedelta
from typing import Optional

from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

from broker import UserError
from env import EnvConfig

# TABLE MODELS


class Movie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    year: int
    genre: str


class MovieRating(SQLModel, table=True):
    movie_id: int = Field(foreign_key="movie.id", primary_key=True)
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    user: Optional["User"] = Relationship(back_populates="movie_ratings")
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=350)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, sa_column_kwargs={"unique": True})
    display_name: str
    movie_ratings: list[MovieRating] = Relationship(back_populates="user")
    bio: str = Field(default="")

    email: EmailStr = Field(sa_column_kwargs={"unique": True})
    password_hash: bytes = Field(index=False)
    password_salt: bytes = Field(index=False)

    def check_password(self, password: str):
        test_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), self.password_salt, 100000
        )
        return test_hash == self.password_hash


class AuthToken(SQLModel, table=True):
    token: str = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    expiration_date: datetime = datetime.utcnow() + timedelta(1)


# FACADE CLASS


class DatabaseFacade:
    def __init__(self, cfg: EnvConfig) -> None:
        self._engine = create_engine(
            f"mysql+pymysql://{cfg.mysql_user}:{cfg.mysql_password}@{cfg.mysql_host}:{cfg.mysql_port}/appdb",
            echo=True,
        )
        SQLModel.metadata.create_all(self._engine)

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
                raise UserError("Invalid token")
            token, user = result
            if datetime.utcnow() > token.expiration_date:
                session.delete(token)
                session.commit()
                raise UserError("Invalid token")
        return user

    def delete_token(self, token_str: str):
        with Session(self._engine) as session:
            statement = select(AuthToken).where(AuthToken.token == token_str)
            token = session.exec(statement).first()
            if token is None:
                return
            session.delete(token)
            session.commit()

    def create_user(
        self, email: EmailStr, username: str, display_name: str, password: str
    ):
        pass_salt = secrets.token_bytes(32)
        pass_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), pass_salt, 100000
        )
        new_user = User(
            username=username,
            email=email,
            display_name=display_name,
            password_hash=pass_hash,
            password_salt=pass_salt,
        )
        with Session(self._engine) as session:
            session.add(new_user)
            try:
                session.commit()
            except IntegrityError as err:
                if err.orig.args[0] == 1062:
                    raise UserError("Username or email already in use")

    def get_user(self, username: str):
        with Session(self._engine) as session:
            statement = select(User).where(User.username == username)
            user = session.exec(statement).first()
            if user is None:
                raise UserError(f"Username {username} does not exist")
            return user

    def update_user(self, user: User):
        with Session(self._engine) as session:
            session.add(user)
            session.commit()
            session.refresh(user)

    def get_user_ratings(self, user: User):
        with Session(self._engine) as session:
            session.add(user)
            return [rating.dict() for rating in user.movie_ratings]
