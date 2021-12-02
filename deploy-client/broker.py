import json
from datetime import datetime, timedelta

import pika
import typer
from pydantic import BaseModel, ValidationError, root_validator

from config import read_config

TIMEOUT_SECONDS = 5


class Reply(BaseModel):
    is_error: bool
    error_msg: str = ""

    @root_validator
    def _check_err(cls, values: dict):
        is_error, error_msg = values.get("is_error"), values.get("error_msg", "")
        if is_error is True and len(error_msg):
            raise ValueError("Replies with errors must include error message")
        return values


class ChannelContext:
    def __enter__(self):
        cfg = read_config()
        if cfg.username is None or cfg.password is None:
            raise RuntimeError("No login credentials set")
        cred = pika.PlainCredentials(cfg.username, cfg.password, True)
        if cfg.server_host is None:
            raise RuntimeError("No server host set")
        params = pika.ConnectionParameters(
            host=cfg.server_host, port=cfg.rabbit_port, credentials=cred
        )
        try:
            self.conn = pika.BlockingConnection(params)
        except:
            raise ConnectionError("Could not connect to broker server")
        self.channel = self.conn.channel()
        return self.channel

    def __exit__(self):
        if self.channel.is_open:
            self.channel.close()
        if self.conn.is_open:
            self.conn.close()


def _send_msg(routing_key: str, body: dict):
    with ChannelContext() as channel:
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
                    raise TimeoutError("Timed out while waiting for reply from server")
                continue
            res_body: str = res[2]
            break
    reply_dict = json.loads(res_body)
    if not isinstance(reply_dict, dict):
        raise TypeError("Deployment server sent invalid reply")
    try:
        reply = Reply(**reply_dict)
    except ValidationError:
        raise TypeError("Deployment server sent invalid reply")
    if reply.is_error:
        raise RuntimeError(reply.error_msg)
    return reply_dict


def send_msg(routing_key: str, body: dict = {}):
    try:
        return _send_msg(routing_key, body)
    except Exception as exc:
        err_msg = str(exc)
        if len(err_msg) == 0:
            err_msg = type(exc).__name__
        typer.secho(f"Error: {err_msg}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)
