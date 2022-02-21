import logging
import smtplib


class SendMail:
    def __init__(self):
        self.email_url = "mailhog:1025"

    def send_request(self, data):
        try:
            smtpObj = smtplib.SMTP(self.email_url)
            smtpObj.sendmail("sender", "reciever", data)
            logging.info("Successfully sent email")
        except Exception:
            logging.warning("Error: unable to send email")

    def send_notification_mail(
        self, user_email: str, data_mail: dict
    ):

        message = f"""From: From Bot <nomail@gmail.com>
        To: To Person <{user_email}>
        MIME-Version: 1.0
        Content-type: text/html
        Subject: Status issue

        Issue #{data_mail.get('issue_id')} for Project #{data_mail.get("project_id")}
        has changed status from {data_mail.get("from_status")} to {data_mail.get("to_status")}
        """

        return self.send_request(message)


mail = SendMail()
