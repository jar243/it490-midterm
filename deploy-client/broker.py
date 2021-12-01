import json
from datetime import datetime, timedelta
from typing import Optional

import pika
from pydantic import BaseModel, root_validator

from config import read_config

TIMEOUT_SECONDS = 5


class DeployReply(BaseModel):
    is_error: bool
    error_msg: Optional[str] = None

    @root_validator
    def check_err(cls, values: dict):
        is_error, error_msg = values.get("is_error"), values.get("error_msg")
        if is_error is True and error_msg is None:
            raise ValueError("Replys with errors must include error message")
        return values


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
