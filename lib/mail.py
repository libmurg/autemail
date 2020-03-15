import ssl
import smtplib
import imaplib
import email


class MailBot:
    """
    Sending and receiving mail
    
    This contains all methods to interact with smtp and imap servers
    """

    # Configs - should not need to change
    ssl_port = 465
    smtp_server = "smtp.gmail.com"
    imap_server = "imap.gmail.com"

    @classmethod
    def read_email(cls, pp, email_id):
        with imaplib.IMAP4_SSL(cls.imap_server) as im:
            im.login(pp.bot_email, pp.bot_pass)
            im.select("inbox")

            email_id_bytes = str.encode(str(email_id))
            _, response = im.fetch(email_id_bytes, "(RFC822)")
            try:
                return email.message_from_bytes(response[0][1])
            except TypeError:
                return None

    @classmethod
    def send_email(cls, pp, msg):
        context = ssl.create_default_context()
        msg["From"] = pp.bot_email

        with smtplib.SMTP_SSL(cls.smtp_server, cls.ssl_port, context=context) as server:
            server.login(pp.bot_email, pp.bot_pass)
            server.send_message(msg)

    @classmethod
    def get_email_ids(cls, pp):
        with imaplib.IMAP4_SSL(cls.imap_server) as im:
            im.login(pp.bot_email, pp.bot_pass)
            im.select("inbox")
            _, email_ids = im.search(None, "ALL")
            return [int(i) for i in email_ids[0].split()]


class PrepBot:
    """
    Prepares/decodes an email.message.EmailMessage instance
    """

    @staticmethod
    def decipher_payload(msg):
        msg_pl = msg.get_payload()
        if isinstance(msg_pl, str):
            return msg_pl
        elif type(msg_pl) == list:
            return msg_pl[0].get_payload()

    @staticmethod
    def decipher_sender(msg):
        msg_sender = msg["From"]
        msg_sender_email = msg_sender.split("<")[-1].replace(">", "")
        msg_sender_name = msg_sender.split("<")[0].strip()
        return (msg_sender_name, msg_sender_email)

    @staticmethod
    def construct_msg(recipient_email, text, subject=None):
        # Prepare message
        msg = email.message.EmailMessage()
        msg["Subject"] = subject
        msg["To"] = recipient_email
        msg.set_content(text)
        return msg

    @staticmethod
    def construct_fwd_email(msg, recipient_email, pre_text=""):
        msg_text = PrepBot.decipher_payload(msg)

        new_msg_text = (
            f"{pre_text} \r\n\r\n ----------------------- \r\n\r\n {msg_text}"
        )
        new_msg_subject = f"AutoFW: {msg['Subject']}"

        fw_msg = PrepBot.construct_msg(
            recipient_email=recipient_email, text=new_msg_text, subject=new_msg_subject
        )
        return fw_msg


class ScanBot:
    """
    Searches for hallmarks
    """

    @staticmethod
    def scan_text(msg, srchtxt):
        msgtxt = PrepBot.decipher_payload(msg)
        return srchtxt.lower() in msgtxt.lower()

    @staticmethod
    def scan_sender(msg, srchtxt, how="email"):
        (sender_name, sender_email) = PrepBot.decipher_sender(msg)
        if how == "email":
            return srchtxt.lower() in sender_email.lower()
        elif how == "name":
            return srchtxt.lower() in sender_name.lower()
