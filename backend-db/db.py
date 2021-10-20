import hashlib
import os
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field, SQLModel, create_engine

# CONSTANTS

USERNAME_REGEX = r"^[A-Za-z0-9_-]{3,}$"

# MODELS


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(primary_key=True)
    username: str = Field(regex=USERNAME_REGEX, primary_key=True)
    display_name: str
    password_hash: bytes
    password_salt: bytes

    def check_password(self, test_password: str):
        test_hash = hashlib.pbkdf2_hmac(
            "sha256",
            test_password.encode("utf-8"),
            self.password_salt,
            100000,
        )
        return test_hash == self.password_hash

    @staticmethod
    def gen_hash_salt(password: str):
        pass_salt = os.urandom(32)
        pass_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            pass_salt,
            100000,
        )
        return (pass_hash, pass_salt)


class AuthToken(SQLModel, table=True):
    token: str = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")


# INIT


def init_db_engine(cfg):
    db_engine = create_engine(
        f"mysql+pymysql://{cfg.mysql_user}:{cfg.mysql_password}@{cfg.mysql_host}:{cfg.mysql_port}/appdb"
    )
    SQLModel.metadata.create_all(db_engine)
    return db_engine
