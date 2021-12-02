from enum import Enum

import typer

from broker import Reply, send_msg
from config import app as config_app


# SHARED CLASSES


class BuildType(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DMZ = "dmz"


# QUALITY ASSURANCE


class QaReply(Reply):
    version: str


qa_app = typer.Typer(short_help="Quality Assurance Commands")


@qa_app.command(short_help="Get active app version in QA")
def version(build: BuildType):
    reply_dict = send_msg("qa.active-version", {"build": build.value})
    reply = QaReply(**reply_dict)
    typer.echo(f"Active {build.value} QA version: {reply.version}")


@qa_app.command(short_help="Approve QA version and push to production")
def approve(build: BuildType):
    reply_dict = send_msg("qa.approve", {"build": build.value})
    reply = QaReply(**reply_dict)
    typer.echo(f"Approved {build.value} v{reply.version}, pushing to production")


@qa_app.command(short_help="Deny QA version and return to development")
def deny(build: BuildType):
    reply_dict = send_msg("qa.deny", {"build": build.value})
    reply = QaReply(**reply_dict)
    typer.echo(f"Denied {build.value} v{reply.version}, returning to development")


# MAIN APP


app = typer.Typer()
app.add_typer(config_app, name="set")
app.add_typer(qa_app, name="qa")


if __name__ == "__main__":
    app()
