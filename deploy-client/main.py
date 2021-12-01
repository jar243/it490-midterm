import typer

from broker import send_msg, DeployReply
from config import app as config_app


# QUALITY ASSURANCE APP


qa_app = typer.Typer()


@qa_app.command()
def approve():
    res = send_msg("qa.approve")


@qa_app.command()
def deny():
    res = send_msg("qa.deny")


# PARENT APP


app = typer.Typer()
app.add_typer(config_app, name="set")
app.add_typer(qa_app, name="qa")


if __name__ == "__main__":
    app()
