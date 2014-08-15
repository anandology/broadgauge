import web
import pynliner
from envelopes import Envelope

from .template import render_template

def sendmail(template, to, subject, headers=None, **kwargs):
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
    if not web.config.get('smtp_server'):
        # TODO: log warn message
        return

    html = render_template(template, **kwargs)

    # inline CSS to make mail clients happy
    html = pynliner.fromString(html)

    envelope = Envelope(
        from_addr=web.config.from_address,
        to_addr=to,
        subject=subject,
        html_body=html,
        headers=headers
    )

    server = web.config.smtp_server
    port = int(web.config.get('smtp_port', 25))
    username = web.config.smtp_username
    password = web.config.get('smtp_password')
    tls = web.config.get('smtp_starttls', False)

    result = envelope.send(
                host=server,
                port=port,
                login=username,
                password=password,
                tls=tls)
    return result