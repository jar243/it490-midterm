from datetime import datetime, timedelta
import json
from typing import Any

import pika


class ChannelContext:
    def __init__(self, host: str, port: int, username: str, password: str):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def __enter__(self):
        cred = pika.PlainCredentials(self.username, self.password, True)
        params = pika.ConnectionParameters(
            host=self.host, port=self.port, credentials=cred
        )
        try:
            self.conn = pika.BlockingConnection(params)
        except:
            raise ConnectionError("Could not open connection to the broker server")
        self.channel = self.conn.channel()
        return self.channel

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.channel.is_open:
            self.channel.close()
        if self.conn.is_open:
            self.conn.close()


class Broker:
    def __init__(
        self, host: str, port: int, username: str, password: str, timeout: int = 5
    ):
        self._ctx = ChannelContext(host, port, username, password)
        self._timeout = timeout

    def send_msg(self, routing_key: str, body: dict) -> dict[str, Any]:
        body_str = json.dumps(body, seperators=(",", ":"))
        with self._ctx as channel:
            channel.basic_publish(
                "",
                routing_key,
                body_str,
                pika.BasicProperties(reply_to="amq.rabbitmq.reply-to"),
            )
            timeout = datetime.utcnow() + timedelta(seconds=self._timeout)
            while True:
                res = channel.basic_get("amq.rabbitmq.reply-to", True)
                if res[0] is None:
                    if datetime.utcnow() > timeout:
                        raise TimeoutError(
                            "Timed out while waiting for reply from server"
                        )
                    continue
                res_body: str = res[2]
                break
        reply_dict = json.loads(res_body)
        if not isinstance(reply_dict, dict):
            raise TypeError("Replies must be a dictionary")
        if not isinstance(reply_dict.get("is_error"), bool):
            raise RuntimeError('Replies must include a boolean "is_error"')
        if reply_dict["is_error"] and (
            not isinstance(reply_dict.get("error_msg"), str)
            or len(reply_dict["error_msg"]) == 0
        ):
            raise RuntimeError(
                'Replies that report an error must include "error_msg" of length greater than zero'
            )
        return reply_dict
