from pydantic import BaseSettings
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine


# DATABASE MODELS


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    password_hash: str


# CONFIG MODELS


class EnvConfig(BaseSettings):
    # broker_host: str
    # broker_port: int = 5672
    # broker_user: str
    # broker_password: str
    # broker_vhost: str
    # broker_exchange: str
    # broker_queue: str
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str
    mysql_password: str

    class Config:
        env_file = "config.env"
        env_file_encoding = "utf-8"


def main():
    # LOAD CONFIG FROM ENVIRONMENT
    cfg = EnvConfig()

    # CONNECT TO RABBITMQ

    # SETUP MYSQL ENGINE
    db_engine = create_engine(
        f"mysql+pymysql://{cfg.mysql_user}:{cfg.mysql_password}@{cfg.mysql_host}:{cfg.mysql_port}/appdb"
    )
    SQLModel.metadata.create_all(db_engine)


if __name__ == "__main__":
    main()
