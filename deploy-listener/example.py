from broker import Broker


def example():
    # this is an example, unless there is a rabbitmq server
    # and deployment server running, the code will not be able to run

    rabbitmq_host = "127.0.0.1"
    rabbitmq_port = 5672
    username = "example"
    password = "example"

    # the broker class automatically handles the rabbitmq connection

    broker = Broker(rabbitmq_host, rabbitmq_port, username, password)

    # you can send messages with the "send_msg" method

    response = broker.send_msg("qa.check-for-update")

    # the response is a dictionary object
    # you can access data inside of it by its keys or get method

    key_example = response["key_example"]
    get_example = response.get("get_example")

    # a response always includes an "is_error" key that is True/False
    # if "is_error" is True, a "error_msg" is included that describes the error

    is_error = response.get("is_error")
    if is_error:
        error_msg = response.get("error_msg")
        raise RuntimeError(error_msg)

    # you can also include data when sending a message to the server

    data_payload = {"installed_version": 12}

    response = broker.send_msg("example.route.key", data_payload)


if __name__ == "__main__":
    example()
