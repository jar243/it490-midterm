from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


def send_email(reciever: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg.attach(MIMEText(body))

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login("xxxxxxxx@gmail.com", "xxxxxxxxxxxxxxxx")
        smtp.sendmail(
            from_addr="xxxxxxxxxxxxxxx@gmail.com",
            to_addrs=reciever,
            msg=msg.as_string(),
        )


if __name__ == "__main__":
    send_email("xxxxx@xxxx.xxxx", "Testing 123", "Hello haha")
