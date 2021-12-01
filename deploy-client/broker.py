from datetime import datetime, timedelta
import pika
from config import read_config
import json

TIMEOUT_SECONDS = 5


class BrokerChannel:
    def __enter__(self):
        cfg = read_config()
        cred = pika.PlainCredentials(cfg.username, cfg.password, True)
        params = pika.ConnectionParameters(
            host=cfg.server_host, port=cfg.rabbit_port, credentials=cred
        )
        self.conn = pika.BlockingConnection(params)
        self.channel = self.conn.channel()
        return self.channel

    def __exit__(self):
        self.channel.__exit__()
        self.conn.__exit__()


def send_msg(routing_key: str, body: dict):
    with BrokerChannel() as channel:
        channel.basic_publish(
            "",
            routing_key,
            json.dumps(body, seperators=(",", ":")),
            pika.BasicProperties(reply_to="amq.rabbitmq.reply-to"),
        )
        timeout = datetime.utcnow() + timedelta(seconds=TIMEOUT_SECONDS)
        while True:
            res = channel.basic_get("amq.rabbitmq.reply-to", True)
            if res[0] is None:
                if datetime.utcnow() > timeout:
                    raise TimeoutError("Deployment server did not respond")
                continue
            res_body: str = res[2]
            break
    reply = json.loads(res_body)
    if not isinstance(reply, dict):
        raise TypeError("Deployment server sent invalid reply")
    return reply
