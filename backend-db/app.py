from broker import RabbitFacade
from db import DatabaseFacade
from env import EnvConfig


def main():
    cfg = EnvConfig()

    rmq = RabbitFacade(
        cfg.broker_host, cfg.broker_port, cfg.broker_user, cfg.broker_password
    )

    db = DatabaseFacade(cfg)


if __name__ == "__main__":
    main()
