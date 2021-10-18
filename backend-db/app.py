from pydantic import BaseSettings
from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine
import pika


# DATABASE MODELS


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    password_hash: str


# CONFIG MODELS


class EnvConfig(BaseSettings):
    broker_host: str
    broker_port: int = 5672
    broker_user: str
    broker_password: str
    broker_vhost: str
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str
    mysql_password: str

    class Config:
        env_file = "config.env"
        env_file_encoding = "utf-8"


def create_rmq_channel(cfg: EnvConfig):
    conn_params = pika.ConnectionParameters(
        host=cfg.broker_host,
        port=cfg.broker_port,
        virtual_host=cfg.broker_vhost,
        credentials=pika.PlainCredentials(cfg.broker_user, cfg.broker_password),
    )
    rmq_conn = pika.BlockingConnection(conn_params)
    return rmq_conn.channel()


def main():
    # LOAD CONFIG FROM ENVIRONMENT
    cfg = EnvConfig()

    # CONNECT TO RABBITMQ
    rmq_channel = create_rmq_channel(cfg)
    rmq_channel.exchange_declare("db")
    rmq_channel.queue_declare("users")
    rmq_channel.queue_bind("users", "db", "users")
    rmq_channel.queue_declare("auth")
    rmq_channel.queue_bind("auth", "db", "auth")
    rmq_channel.queue_declare("movies")
    rmq_channel.queue_bind("movies", "db", "movies")

    # SETUP MYSQL ENGINE
    db_engine = create_engine(
        f"mysql+pymysql://{cfg.mysql_user}:{cfg.mysql_password}@{cfg.mysql_host}:{cfg.mysql_port}/appdb"
    )
    SQLModel.metadata.create_all(db_engine)


if __name__ == "__main__":
    main()
