import typer

from config import app as config_app


qa_app = typer.Typer()


@qa_app.command()
def approve():
    pass


@qa_app.command()
def deny():
    pass


app = typer.Typer()
app.add_typer(config_app, name="set")
app.add_typer(qa_app, name="qa")


if __name__ == "__main__":
    app()
