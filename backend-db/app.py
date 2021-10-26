import pika

from db import DatabaseFacade
from env import EnvConfig


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
    db = DatabaseFacade(cfg)


if __name__ == "__main__":
    main()
