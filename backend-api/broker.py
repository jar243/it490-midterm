import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Union

import pika
from pika.channel import Channel
from pika.exchange_type import ExchangeType
from pydantic import ValidationError

# GLOBAL VARIABLES

LOG_FILE = Path(".log")
LOGS_EXCHANGE = "logs"
channel: Channel
log_name: str


class UserError(Exception):
    pass


# PRIVATE CLASSES AND FUNCTIONS


HandlerCallable = Callable[[dict], Union[dict, None]]


def publish(channel: Channel, route_key: str, msg_body: Union[dict, None]):
    channel.basic_publish("", route_key, json.dumps(msg_body, separators=(",", ":")))


def reply_ok(channel: Channel, reply_queue: str, reply: Union[dict, None]):
    if isinstance(reply, dict):
        reply["is_error"] = False
    publish(channel, reply_queue, reply)


def reply_err(channel: Channel, reply_queue: str, err_msg: str):
    reply = {"is_error": True, "msg": err_msg}
    publish(channel, reply_queue, reply)


def publish_log(channel: Channel, log_msg: str):
    log_body = {
        "sender": log_name,
        "time": datetime.utcnow().isoformat(),
        "msg": log_msg,
    }
    channel.basic_publish(
        LOGS_EXCHANGE, "", json.dumps(log_body, separators=(",", ":"))
    )


def wrap_handler(handler: HandlerCallable):
    def wrap(channel: Channel, method, header: pika.BasicProperties, body: bytes):
        needs_reply = header.reply_to is not None
        reply_queue = str(header.reply_to) if needs_reply else ""
        try:
            parsed_body = json.loads(body)
            if not isinstance(parsed_body, dict):
                raise RuntimeError("Invalid request body")
            handler_reply = handler(parsed_body)
            if not isinstance(handler_reply, dict) and handler_reply is not None:
                raise RuntimeError("Handler must return dict or None")
            if needs_reply:
                reply_ok(channel, reply_queue, handler_reply)
        except Exception as exc:
            if needs_reply:
                err_msg = (
                    str(exc)
                    if isinstance(exc, (UserError, ValidationError))
                    else "Server Error"
                )
                reply_err(channel, reply_queue, err_msg)
            publish_log(channel, str(exc))

    return wrap


def declare_queue(channel: Channel, queue_name: str, handler: Callable):
    wrapped_handler = wrap_handler(handler)

    def callback(frame):
        channel.basic_consume(queue_name, wrapped_handler)

    channel.queue_declare(queue_name, callback=callback)


def declare_log_exchange(channel: Channel):
    def handle_log(rq: dict):
        log_str = " | ".join([rq["sender"], rq["time"], rq["msg"]]) + "\n"
        with open(LOG_FILE, "a") as fl:
            fl.write(log_str)

    def on_queue_declare(frame):
        log_queue_name: str = frame.method.queue  # auto-generated queue name
        channel.queue_bind(log_queue_name, LOGS_EXCHANGE)
        wrapped_handler = wrap_handler(handle_log)
        channel.basic_consume(log_queue_name, wrapped_handler)

    def on_exc_declare(frame):
        channel.queue_declare("", auto_delete=True, callback=on_queue_declare)

    channel.exchange_declare(
        LOGS_EXCHANGE, ExchangeType.fanout, callback=on_exc_declare
    )


def generate_connect_callback(route_handlers: dict[str, Callable]):
    def on_channel_open(new_channel):
        global channel
        channel = new_channel
        declare_log_exchange(channel)
        for route_name, handler in route_handlers.items():
            declare_queue(channel, route_name, handler)

    def on_connect(connection):
        connection.channel(on_open_callback=on_channel_open)

    return on_connect


# PUBLIC CLASSES AND FUNCTIONS


def run_rabbit_app(
    device_name: str,
    host: str,
    port: int,
    username: str,
    password: str,
    route_handlers: dict[str, Callable],
):
    global log_name
    log_name = device_name

    conn_params = pika.ConnectionParameters(
        host=host, port=port, credentials=pika.PlainCredentials(username, password)
    )
    connect_callback = generate_connect_callback(route_handlers)
    conn = pika.SelectConnection(conn_params, connect_callback)

    try:
        print("Starting RabbitMQ app...")
        conn.ioloop.start()
    except KeyboardInterrupt:
        print("Shutting down...")
        conn.close()
        conn.ioloop.start()