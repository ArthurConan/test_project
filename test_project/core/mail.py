import smtplib

from jinja2 import Template


class SendMail:
    def __init__(self):
        self.email_url = "mailhog:1025"

    def create_email_body(
        self, email_params: dict, template_text: str, template_params: dict
    ):
        template = Template(template_text)
        email_body = {
            "personalizations": email_params.get("personalizations"),
            "from": email_params.get("from"),
            "reply_to": email_params.get("reply_to"),
            "subject": email_params.get("subject"),
            "content": [
                {
                    "type": "text/html",
                    "value": template.render(
                        **template_params,
                    ),
                }
            ],
            "categories": email_params.get("categories"),
        }

        return email_body

    def send_request(self, data):
        try:
            smtpObj = smtplib.SMTP(self.email_url)
            smtpObj.sendmail("sender", "reciever", data)
            print("Successfully sent email")
        except Exception:
            print("Error: unable to send email")

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
