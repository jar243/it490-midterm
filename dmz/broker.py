import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Union

import pika
from pika.channel import Channel
from pika.exchange_type import ExchangeType
from pydantic import ValidationError

# GLOBAL VARIABLES

LOG_FILE = Path(__file__).parent.joinpath(".log")
LOGS_EXCHANGE = "logs"
LOG_NAME: str
channel: Channel


class UserError(Exception):
    pass


# PRIVATE CLASSES AND FUNCTIONS


HandlerCallable = Callable[[dict], Union[dict, None]]


def get_err_msg(exc: Exception):
    if isinstance(exc, UserError):
        return str(exc)
    elif isinstance(exc, ValidationError):
        return f"Invalid field(s): {', '.join([err['loc'][0] for err in exc.errors()])}"
    else:
        return "Server Error"


def publish(channel: Channel, route_key: str, msg_body: Union[dict, None]):
    channel.basic_publish("", route_key, json.dumps(msg_body, separators=(",", ":")))


def reply_ok(channel: Channel, reply_queue: str, reply: dict):
    reply["is_error"] = False
    publish(channel, reply_queue, reply)


def reply_err(channel: Channel, reply_queue: str, err_msg: str):
    reply = {"is_error": True, "msg": err_msg}
    publish(channel, reply_queue, reply)


def publish_log(channel: Channel, log_msg: str):
    log_body = {
        "sender": LOG_NAME,
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
            try:
                parsed_body = json.loads(body)
            except:
                raise UserError("Invalid message body")
            if not isinstance(parsed_body, dict):
                raise RuntimeError("Invalid request body")
            handler_reply = handler(parsed_body)
            if handler_reply is None:
                handler_reply = {}
            elif not isinstance(handler_reply, dict):
                raise ValueError("Handler must return a dict")
            if needs_reply:
                reply_ok(channel, reply_queue, handler_reply)
        except Exception as exc:
            if needs_reply:
                err_msg = get_err_msg(exc)
                reply_err(channel, reply_queue, err_msg)
            publish_log(channel, str(exc))

    return wrap


def declare_queue(channel: Channel, queue_name: str, handler: Callable):
    wrapped_handler = wrap_handler(handler)

    def callback(frame):
        channel.basic_consume(queue_name, wrapped_handler, auto_ack=True)

    channel.queue_declare(queue_name, callback=callback)


def declare_log_exchange(channel: Channel):
    def handle_log(rq: dict):
        log_str = f'{rq["sender"]} | {rq["time"]}\n{rq["msg"]}\n{"- "*39}-\n'
        with open(LOG_FILE, "a") as fl:
            fl.write(log_str)

    def on_queue_declare(frame):
        log_queue_name: str = frame.method.queue  # auto-generated queue name
        channel.queue_bind(log_queue_name, LOGS_EXCHANGE)
        wrapped_handler = wrap_handler(handle_log)
        channel.basic_consume(log_queue_name, wrapped_handler, auto_ack=True)

    def on_exc_declare(frame):
        channel.queue_declare("", auto_delete=True, callback=on_queue_declare)

    channel.exchange_declare(
        LOGS_EXCHANGE, ExchangeType.fanout, callback=on_exc_declare
    )


def generate_connect_callback(route_handlers: dict[str, Callable]):
    def on_channel_open(new_channel: Channel):
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
    global LOG_NAME
    LOG_NAME = device_name

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
