import pika
from pika.exchange_type import ExchangeType


class RabbitFacade:
    def __init__(self, host: str, port: int, username: str, password: str) -> None:
        # STEP 1: CONNECT TO RABBITMQ SERVER
        self._conn_params = pika.ConnectionParameters(
            host=host, port=port, credentials=pika.PlainCredentials(username, password)
        )
        self._conn = pika.BlockingConnection(self._conn_params)
        self._channel = self._conn.channel()

        # STEP 2: SETUP LOG EXCHANGE
        self._channel.exchange_declare("log", exchange_type=ExchangeType.fanout)
        res = self._channel.queue_declare("", auto_delete=True)
        self._log_channel: str = res.method.queue  # auto-generated queue name
        self._channel.queue_bind(self._log_channel, "log", "xxx")

        # STEP 3: SETUP DB EXCHANGE
        self._channel.queue_declare("db.auth")
        self._channel.queue_declare("db.users")
        self._channel.queue_declare("db.movies")

        # STEP 4: SETUP API EXCHANGE

    def publish_log(self, msg: str):
        pass
