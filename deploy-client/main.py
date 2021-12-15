from enum import Enum
from typing import Optional

import typer
from pydantic import BaseModel

from broker import Reply, send_msg
from config import app as config_app

# SHARED CLASSES


class BuildStatus(str, Enum):
    PRODUCTION = "production"
    REVIEW = "review"
    DENIED = "denied"


class Branch(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    DMZ = "dmz"


class VersionReply(Reply):
    version: tuple[int, int]

    @property
    def version_str(self):
        return f"v{'.'.join(self.version)}"


# DEVELOPMENT

dev_app = typer.Typer(short_help="Development Commands")


@dev_app.command(short_help="Get active app version in QA")
def push_build(
    major: bool = typer.Option(True, help="If the build is a major release")
):
    pass


# QUALITY ASSURANCE


qa_app = typer.Typer(short_help="Quality Assurance Commands")


@qa_app.command(short_help="Get active app version in QA")
def version(branch: Branch):
    reply_dict = send_msg("qa.active-version", {"branch": branch.value})
    reply = VersionReply(**reply_dict)
    typer.echo(f"Active {branch.value} QA version: {reply.version_str}")


@qa_app.command(short_help="Approve QA version and push to production")
def approve(branch: Branch):
    reply_dict = send_msg("qa.approve", {"branch": branch.value})
    reply = VersionReply(**reply_dict)
    typer.echo(f"Approved {branch.value} {reply.version_str}, pushing to production")


@qa_app.command(short_help="Deny QA version and return to development")
def deny(branch: Branch):
    reply_dict = send_msg("qa.deny", {"branch": branch.value})
    reply = VersionReply(**reply_dict)
    typer.echo(f"Denied {branch.value} {reply.version_str}, returning to development")


# PRODUCTION


prod_app = typer.Typer(short_help="Production Commands")


@prod_app.command(short_help="Get active app version in production")
def version(branch: Branch):
    reply_dict = send_msg("prod.active-version", {"branch": branch.value})
    reply = VersionReply(**reply_dict)
    typer.echo(f"Active {branch.value} PROD version: {reply.version_str}")


@prod_app.command(short_help="Rollback to last approved production version")
def rollback(branch: Branch):
    reply_dict = send_msg("prod.rollback", {"branch": branch.value})
    reply = VersionReply(**reply_dict)
    typer.echo(f"Rolling back {branch.value} PROD version to {reply.version_str}")


# MAIN APP


app = typer.Typer()


class BuildData(BaseModel):
    version_major: int
    version_minor: int
    branch: Branch
    status: BuildStatus

    @property
    def version(self):
        return f"{self.major}.{self.minor}"


class ListReply(Reply):
    builds: list[BuildData]


@app.command("list", short_help="List builds in deployment server")
def list_builds(
    branch: Optional[Branch] = typer.Option(
        None, help="Limit results to specific branch"
    ),
    max: int = typer.Option(5, help="Set max results displayed"),
):
    reply_dict = send_msg("list-builds")
    reply = ListReply(**reply_dict)
    results: list[BuildData] = []
    for build in reply.builds:
        if branch is not None and build.branch == branch:
            continue
        results.append(build)
        if len(results) == max:
            break
    header = "| BRANCH   | VERSION | STATUS     |"
    seperator = f"|{'-'*(len(header)-2)}|"
    rows = [
        " ".join(
            [
                "|",
                f"{build.branch.value[:8]:<8}",
                "|",
                f"{build.version.value[:7]:<7}",
                "|",
                f"{build.status.value[:10]:<7}",
                "|",
            ]
        )
        for build in results
    ]
    table_str = "\n".join([seperator, header, seperator] + rows + [seperator])
    typer.echo(table_str)


app.add_typer(config_app, name="set")
app.add_typer(dev_app, name="dev")
app.add_typer(qa_app, name="qa")
app.add_typer(prod_app, name="prod")


if __name__ == "__main__":
    app()
