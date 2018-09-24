from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(to, subject, text, cc=None, bcc=None, reply_to=None,
            html=None, pre=False, custom_headers=None):
    from wheremi_app import app
    gmail_user = app.config['EMAIL']
    gmail_pwd = app.config['EMAIL_PASSWORD']
    from_gmail_user = app.config['EMAIL_USER']

    msg = MIMEMultipart()

    msg['From'] = from_gmail_user
    msg['To'] = ",".join(to)
    msg['Subject'] = subject

    if cc:
        # cc gets added to the text header as well as list of recipients
        if type(cc) in [str, unicode]:
            msg.add_header('Cc', cc)
            cc = [cc]
        else:
            cc = ', '.join(cc)
            msg.add_header('Cc', cc)
        to += cc

    if bcc:
        # bcc does not get added to the headers, but is a recipient
        if type(bcc) in [str, unicode]:
            bcc = [bcc]
        to += bcc

    if reply_to:
        msg.add_header('Reply-To', reply_to)

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to
    # display.

    if pre:
        html = "<pre>%s</pre>" % text
    if html:
        msgAlternative = MIMEMultipart('alternative')
        msg.attach(msgAlternative)

        msgText = MIMEText(text)
        msgAlternative.attach(msgText)

        # We reference the image in the IMG SRC attribute by the ID we give it
        # below
        msgText = MIMEText(html, 'html')
        msgAlternative.attach(msgText)
    else:
        msg.attach(MIMEText(text))

    if custom_headers:
        for k, v in custom_headers.iteritems():
            msg.add_header(k, v)

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)

    mailServer.sendmail(gmail_user, to, msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()
