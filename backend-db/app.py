import pika
from pydantic import BaseSettings

from db import init_db_engine

# CONFIG MODELS


class EnvConfig(BaseSettings):
    broker_host: str = "127.0.0.1"
    broker_port: int = 5672
    broker_user: str = "guest"
    broker_password: str = "guest"
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "devuser"
    mysql_password: str = "devpassword"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def create_rmq_channel(cfg: EnvConfig):
    conn_params = pika.ConnectionParameters(
        host=cfg.broker_host,
        port=cfg.broker_port,
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
    db_engine = init_db_engine(cfg)


if __name__ == "__main__":
    main()
