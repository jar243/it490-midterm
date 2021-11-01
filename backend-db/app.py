import warnings
import pika
from pika.channel import Channel

from sqlalchemy.exc import SAWarning

from broker import RabbitFacade
from db import DatabaseFacade
from env import EnvConfig

db: DatabaseFacade
channel: Channel

# Runs when connection is established
def on_connect(connection):
    connection.channel(on_open_callback=on_channel_open)


# Runs when channel opens
def on_channel_open(new_channel: Channel):
    global channel
    channel = new_channel
    channel.queue_declare("db.auth.login")
    channel.queue_declare("db.auth.logout")
    channel.queue_declare("db.users.create")
    channel.queue_declare("db.users.get")


# App entrypoint
def main():
    warnings.simplefilter("ignore", category=SAWarning)

    cfg = EnvConfig()

    global db
    db = DatabaseFacade(cfg)

    conn_params = pika.ConnectionParameters(
        host=cfg.broker_host,
        port=cfg.broker_port,
        credentials=pika.PlainCredentials(cfg.broker_user, cfg.broker_password),
    )
    conn = pika.SelectConnection(conn_params, on_connect)
    try:
        conn.ioloop.start()
    except KeyboardInterrupt:
        conn.close()
        conn.ioloop.start()


if __name__ == "__main__":
    main()
