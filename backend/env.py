from pydantic import BaseSettings, EmailStr


class EnvConfig(BaseSettings):
    broker_host: str = "127.0.0.1"
    broker_port: int = 5672
    broker_user: str = "guest"
    broker_password: str = "guest"
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "devuser"
    mysql_password: str = "devpassword"
    email_addr: EmailStr = EmailStr("no-reply@movieworld.com")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
