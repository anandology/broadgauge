import web
import logging
import pynliner
from envelopes import Envelope

from .template import render_template

logger = logging.getLogger(__name__)

def sendmail_with_template(template, to, subject, headers=None, **kwargs):
    """
    Sends an email with the selected html template.
    html templates can be found inside the broadguage/templates
    directory. 

    Params:
    =======
    template: str
    Link to the html file to be used as template. The html
    file is parsed by Jinja Templating before sending to the
    recipient. 

    Keyword Args:
    =============
    to: str
    Recipient's email
    
    sub: str
    Subject of the mail

    P.S: Other keywords are sent to Jinja Templating Language for 
    direct parsing, as it is.
    
    Example:
    >>> from sendmail import sendmail
    >>> sendmail("emails/trainers/welcome.html",to=..."some_email.com", 
                               sub="Hey Friend!", variable1=var, variable2=var2)
    Email sent to some_email.com
    """
    html = render_template(template, **kwargs)

    # inline CSS to make mail clients happy
    html = pynliner.fromString(html)

    return sendmail(to_address=to, 
                    subject=subject, 
                    message_html=html,
                    headers=headers,
                    **kwargs)


def sendmail(to_address, subject, 
        message_text=None, message_html=None, 
        reply_to=None, headers=None, 
        **kwargs):
    if not web.config.get('smtp_server'):
        logger.warn("smtp_server not configured, mail won't be sent.")
        return

    headers = dict(headers or {})
    if reply_to:
        headers['Reply-To'] = reply_to

    envelope = Envelope(
        from_addr=web.config.from_address,
        to_addr=to_address,
        subject=subject,
        html_body=message_html,
        text_body=message_text,
        headers=headers
    )
    server = web.config.smtp_server
    port = int(web.config.get('smtp_port', 25))
    username = web.config.smtp_username
    password = web.config.get('smtp_password')
    tls = web.config.get('smtp_starttls', False)

    return envelope.send(
            host=server,
            port=port,
            login=username,
            password=password,
            tls=tls)
    