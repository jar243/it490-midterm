from pydantic import BaseSettings


class BackendDbSettings(BaseSettings):
    broker_host: str
    broker_port: int = 5672
    broker_user: str
    broker_password: str
    broker_vhost: str
    broker_exchange: str
    broker_queue: str
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str
    mysql_password: str

    class Config:
        env_file = "settings.env"
        env_file_encoding = "utf-8"


def main():
    settings = BackendDbSettings()


if __name__ == "__main__":
    main()
