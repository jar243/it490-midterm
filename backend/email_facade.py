from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from typing import Union


class EmailFacade:
    def __init__(self, sender_addr: str) -> None:
        self._sender = sender_addr

    def send(self, recipients: Union[list[str], str], subject: str, body: str):
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = f'"Movie World" <{self._sender}>'
        txt = MIMEText(body)
        msg.attach(txt)

        with smtplib.SMTP("localhost") as smtp:
            smtp.sendmail(
                from_addr=self._sender,
                to_addrs=recipients,
                msg=msg.as_string(),
            )


if __name__ == "__main__":
    email = EmailFacade("alerts@movieworld.com")
    email.send("johnarezk@gmail.com", "Reset your Password", "Testing123")
