import json
from pathlib import Path
from typing import Optional

import typer
from pydantic import BaseModel

CONFIG_FILE = Path.home() / ".it490-deploy-client" / "config.json"


class ClientConfig(BaseModel):
    server_host: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    rabbit_port: int = 5672
    sftp_port: int = 22

    class Config:
        validate_assignment = True


def read_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as fl:
            return ClientConfig(**json.load(fl))
    else:
        return ClientConfig()


def write_config(cfg: ClientConfig):
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    with open(CONFIG_FILE, "w") as fl:
        json.dump(cfg.dict(), fl, indent=4)


app = typer.Typer(short_help="Configure Client")


@app.command()
def host(server_host: str):
    cfg = read_config()
    cfg.server_host = server_host
    write_config(cfg)
    typer.echo(f"Set host to {server_host}")


@app.command()
def credentials(
    username: str,
    password: str = typer.Option(
        ..., prompt=True, confirmation_prompt=True, hide_input=True
    ),
):
    cfg = read_config()
    cfg.username = username
    cfg.password = password
    write_config(cfg)
    typer.echo(f"Set credentials to {username}:*********")
