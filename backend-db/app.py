import warnings

from sqlalchemy.exc import SAWarning

from broker import RabbitFacade
from db import DatabaseFacade
from env import EnvConfig


def main():
    cfg = EnvConfig()
    warnings.simplefilter("ignore", category=SAWarning)

    # rmq = RabbitFacade(
    #     cfg.broker_host, cfg.broker_port, cfg.broker_user, cfg.broker_password
    # )

    db = DatabaseFacade(cfg)

    db.create_user("john@", "john", "John Test", "testing123")
    token = db.generate_token("john", "testing123")
    print(token)
    user = db.get_token_user(token)
    if user is not None:
        print(user.username)


if __name__ == "__main__":
    main()
